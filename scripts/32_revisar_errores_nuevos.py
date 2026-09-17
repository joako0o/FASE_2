"""Audita siete errores nuevos frente a IA; las lecturas son del agente, no reglas.

Separa la selección reproducible por predicciones de los juicios cualitativos
registrados en lecturas_agente.json. No entrena ni modifica anotaciones.
"""
# ---- 1. Fuentes congeladas y controles de integridad ----
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from utilidades import norm, sha256

RAIZ=Path(__file__).resolve().parents[1]
MODELO=RAIZ/'data/evaluacion/adjudicacion_modelo_v1'
BASE=RAIZ/'data/auditoria/revision_errores_adjudicada_v1'
LECTURAS=BASE/'lecturas_agente.json'
SALIDA=BASE/'resultados'
INFORME=RAIZ/'docs/REVISION_ERRORES_NUEVOS_ADJUDICADA_V1.md'
CLASES={'hawkish','dovish','neutral'}


def leer_csv(ruta):
    with Path(ruta).open(encoding='utf-8',newline='') as archivo:
        return list(csv.DictReader(archivo))


def escribir_json(ruta,valor):
    with Path(ruta).open('x',encoding='utf-8') as archivo:
        json.dump(valor,archivo,ensure_ascii=False,indent=2,allow_nan=False)
        archivo.write('\n')


# ---- 2. Elegir casos sin alterar etiquetas para que coincidan con el modelo ----
def seleccionar(predicciones):
    assert {r['variante'] for r in predicciones}=={'original','adjudicada'}
    condiciones={}
    for variante in ['original','adjudicada']:
        filas=[r for r in predicciones if r['variante']==variante]
        condiciones[variante]={r['intervencion_id']:r for r in filas}
        assert len(filas)==len(condiciones[variante]),'IDs repetidos'
        assert all(r['etiqueta'] in CLASES and r['pred'] in CLASES for r in filas)
    original,actual=condiciones['original'],condiciones['adjudicada']
    assert set(original)==set(actual),'Distinta población'
    errores=[]
    for identificador in sorted(actual):
        antes,ahora=original[identificador],actual[identificador]
        for campo in ['meeting_id','etiqueta','fold']:
            assert antes[campo]==ahora[campo],f'Referencia o fold alterados: {identificador}'
        if ahora['pred']==ahora['etiqueta']:
            continue
        nuevo=antes['pred']==antes['etiqueta']
        errores.append({'intervencion_id':identificador,'meeting_id':ahora['meeting_id'],
            'fold':int(ahora['fold']),'etiqueta_ia':ahora['etiqueta'],
            'pred_original':antes['pred'],'pred_adjudicada':ahora['pred'],
            'es_error_nuevo':nuevo,'revision_cualitativa':'tanda_1_nuevos' if nuevo else 'pendiente'})
    return errores,[r for r in errores if r['es_error_nuevo']]


def validar_lectura(lectura,texto):
    assert lectura['estado_revision'] in {'referencia_respaldada','ambigua'}
    if lectura['estado_revision']=='ambigua':
        assert lectura['postura_sugerida_agente'] is None,'No convertir duda en etiqueta definitiva'
    else:
        assert lectura['postura_sugerida_agente'] in CLASES
    assert lectura['citas_agente']
    for cita in lectura['citas_agente']:
        assert 0<len(cita)<=300
        assert norm(cita) in norm(texto),'Cita del agente no literal'


# ---- 3. Reporte: separar evidencia, interpretación y cobertura pendiente ----
def redactar(casos,resumen):
    lineas=['# Revisión de etiquetas en los siete errores nuevos', '',
        '**Primera tanda: 7 de los 66 desacuerdos actuales. Quedan 59 casos sin revisión cualitativa en esta unidad.**', '',
        'Un error en la métrica significa desacuerdo con la etiqueta IA; no prueba por sí solo que el modelo o la referencia estén equivocados. Se leyeron los siete textos completos y sus anotaciones IA originales.', '',
        f'**Lectura del agente: {resumen["referencias_respaldadas"]} referencias D respaldadas y {resumen["casos_ambiguos"]} casos ambiguos. Ninguna corrección de etiqueta aprobada o aplicada.**', '',
        '| Caso | ID original | Etiqueta IA | Modelo adjudicado | Revisión del agente |', '|---|---|---|---|---|']
    for caso in casos:
        estado='D respaldada; discrepo del modelo' if caso['estado_revision']=='referencia_respaldada' else 'Ambigua; no corregir aún'
        lineas.append(f'| {caso["caso_revision"]} | {caso["intervencion_id"]} | {caso["etiqueta_ia"]} | {caso["pred_adjudicada"]} | {estado} |')
    lineas+=['','En los siete, el modelo original coincidía con IA. La selección es por deterioro observado, no una muestra aleatoria del corpus. Mi lectura conoce las etiquetas y predicciones: no es un segundo anotador ciego ni verdad adjudicada por el investigador.','']
    for caso in casos:
        lineas += [f'## {caso["caso_revision"]} — {caso["fecha"]}, {caso["actor"]}', '',
            f'**IA: {caso["etiqueta_ia"]}; modelo actual: {caso["pred_adjudicada"]}.**', '',
            '**Evidencia seleccionada por el agente:**','']
        for cita in caso['citas_agente']:lineas+=['> '+cita,'']
        lineas += [caso['lectura'],'','**Límite y acción:** '+caso['limite_y_accion'],'']
    lineas+=['## Qué concluyo y qué no', '',
        '- No hay base para atribuir los siete errores nuevos a siete anotaciones incorrectas. Cuatro contienen una recomendación o rechazo de dirección suficientemente claros para respaldar D en esta lectura.',
        '- Los otros tres no se convierten en aciertos del modelo: siguen siendo disputables. En dos reaparece la tensión entre normalización y pausa táctica; en el de enero de 2005 debe aclararse la dirección y posiblemente cotejarse la transcripción.',
        '- Una cita literal no garantiza que represente lo decisivo: por ejemplo, citar solo mantener en octubre de 2006 omite su recomendación explícita sobre el sesgo futuro.',
        '- La revisión señala contradicciones entre salida y texto, no identifica causalmente qué palabras produjeron cada predicción. No se entrenó otro modelo ni se calcularon aquí contribuciones léxicas.',
        '- No corregir validación para que suba el score, ni usar esta revisión para ajustar y luego presentar esas mismas 793 filas como test intacto. Son desarrollo reutilizado. Las 306 respuestas anteriores no se abren.',
        '- Los 59 desacuerdos restantes quedan en el inventario con estado pendiente; no se extrapola el balance de esta tanda a todos los errores.', '',
        '## Estado operativo', '',
        'Se conservan las anotaciones IA, las adjudicaciones humanas ya aprobadas y las métricas originales (60/66 errores). No se generan etiquetas canónicas nuevas. Antes de una corrección haría falta decisión explícita por caso, y en el caso de dirección incierta comprobar la fuente si es necesario.', '',
        '## Trazabilidad', '',
        f'- {resumen["caracteres_textos_revisados"]} caracteres de texto completo en los siete casos; {resumen["citas_agente_verificadas"]} extractos adicionales comprobados tras normalizar únicamente espacios, todos ≤300 caracteres.',
        '- `lecturas_agente.json` contiene juicios cualitativos manuales del agente, no clasificaciones obtenidas por una regla automática. El script 32 verifica selección, IDs, citas y hashes.',
        '- `resultados/inventario_errores.csv`: los 66 desacuerdos, distinguiendo siete nuevos y 59 pendientes de esta revisión.',
        '- `resultados/casos_revisados.json`: textos completos, cita/confianza/nota IA de origen, lectura separada del agente y predicciones; no sobrescribe ninguna fuente.',
        '- [Evaluación que origina la selección](EVALUACION_MODELO_ADJUDICADO_V1.md).', '',
        '```bash', 'python scripts/32_revisar_errores_nuevos.py --salida /ruta/nueva --informe /ruta/informe_nuevo.md', '```','']
    return '\n'.join(lineas)


# ---- 4. Ejecución exclusiva con comprobación de fuentes/salidas ----
def ejecutar(salida=SALIDA,informe=INFORME):
    salida,informe=Path(salida),Path(informe)
    if salida.exists() or informe.exists():raise FileExistsError('No sobrescribir revisión existente')
    protocolo=json.loads((MODELO/'protocolo.json').read_text())
    for nombre,huella in protocolo['sha256_insumos'].items():assert sha256(RAIZ/nombre)==huella,nombre
    manifiesto=json.loads((MODELO/'manifest.json').read_text())
    for nombre,huella in manifiesto['sha256_salidas'].items():assert sha256(MODELO/nombre)==huella,nombre
    predicciones=leer_csv(MODELO/'predicciones_validacion.csv')
    errores,nuevos=seleccionar(predicciones)
    assert len(predicciones)==1586 and len(errores)==66 and len(nuevos)==7
    documento=json.loads(LECTURAS.read_text())
    assert documento['autor']=='agente' and documento['cambios_aplicados'] is False
    lecturas={r['intervencion_id']:r for r in documento['lecturas']}
    assert len(lecturas)==len(documento['lecturas'])==7
    assert set(lecturas)=={r['intervencion_id'] for r in nuevos}
    corpus={r['intervencion_id']:r for r in leer_csv(RAIZ/'data/L0/corpus.csv')}
    archivos_ia=sorted((RAIZ/'data/etiquetas').glob('etiquetas_*.csv'))
    etiquetas={}
    for ruta in archivos_ia:
        for fila in leer_csv(ruta):
            assert fila['intervencion_id'] not in etiquetas
            assert fila['metodo']=='ia_ronda'
            etiquetas[fila['intervencion_id']]=fila
    casos=[]
    for numero,registro in enumerate(nuevos,1):
        identificador=registro['intervencion_id'];fuente=corpus[identificador]
        etiqueta=etiquetas[identificador];lectura=lecturas[identificador]
        assert etiqueta['etiqueta']==registro['etiqueta_ia']
        assert fuente['meeting_id']==registro['meeting_id']
        validar_lectura(lectura,fuente['texto'])
        casos.append({**registro,**lectura,'caso_revision':f'E{numero:02d}',
            'actor':fuente['actor'],'fecha':fuente['fecha'],'cargo':fuente['cargo'],
            'texto_completo':fuente['texto'],'sha256_texto':hashlib.sha256(fuente['texto'].encode()).hexdigest(),
            'cita_ia_original':etiqueta['frase_justificante'],'nota_ia_original':etiqueta['nota'],
            'confianza_ia_original':etiqueta['confianza'],
            'cita_ia_literal':bool(norm(etiqueta['frase_justificante'])) and norm(etiqueta['frase_justificante']) in norm(fuente['texto'])})
    conteo=Counter(c['estado_revision'] for c in casos)
    resumen={'errores_totales_modelo_adjudicado':len(errores),'revisados':len(casos),'pendientes':len(errores)-len(casos),
        'referencias_respaldadas':conteo['referencia_respaldada'],'casos_ambiguos':conteo['ambigua'],
        'caracteres_textos_revisados':sum(len(c['texto_completo']) for c in casos),
        'citas_agente_verificadas':sum(len(c['citas_agente']) for c in casos),
        'citas_ia_literales':sum(c['cita_ia_literal'] for c in casos),
        'etiquetas_modificadas':0,'metricas_recalculadas_con_lecturas':False,'entrenamiento_realizado':False,
        'procedencia':'revision_cualitativa_agente_no_ciega_pendiente_adjudicacion'}
    fuentes=[LECTURAS,Path(__file__),RAIZ/'tests/test_revision_errores_nuevos.py',
        RAIZ/'data/L0/corpus.csv',RAIZ/'docs/codebook_v2.md',
        RAIZ/'docs/ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md',
        MODELO/'protocolo.json',MODELO/'manifest.json',MODELO/'predicciones_validacion.csv']+archivos_ia
    hashes={str(p.relative_to(RAIZ)):sha256(p) for p in fuentes}
    salida.mkdir(parents=True)
    with (salida/'inventario_errores.csv').open('x',encoding='utf-8',newline='') as archivo:
        escritor=csv.DictWriter(archivo,fieldnames=list(errores[0]));escritor.writeheader();escritor.writerows(errores)
    escribir_json(salida/'casos_revisados.json',casos)
    escribir_json(salida/'resumen.json',resumen)
    informe.parent.mkdir(parents=True,exist_ok=True)
    with informe.open('x',encoding='utf-8') as archivo:archivo.write(redactar(casos,resumen))
    for nombre,huella in hashes.items():assert sha256(RAIZ/nombre)==huella,nombre
    escribir_json(salida/'manifest.json',{'registrado_utc':datetime.now(timezone.utc).isoformat(),
        'sha256_insumos':hashes,'sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir())},
        'sha256_informe':sha256(informe),'etiquetas_y_modelo_intactos':True})
    print(json.dumps(resumen,ensure_ascii=False,indent=2))
    return resumen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path,default=SALIDA)
    parser.add_argument('--informe',type=Path,default=INFORME)
    opciones=parser.parse_args()
    ejecutar(opciones.salida,opciones.informe)


if __name__=='__main__':main()
