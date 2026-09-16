"""Segunda tanda: 16 intercambios H/D pendientes, sin cambiar la validación.

Reutiliza selección y validaciones de la tanda 1; los juicios semánticos vienen
de lecturas_agente.json y no se producen automáticamente por las predicciones.
"""
# ---- 1. Fuentes y utilidades congeladas; parámetros propios en un lugar ----
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from utilidades import cargar_script, norm, sha256

ANTERIOR=cargar_script('32_revisar_errores_nuevos.py')
RAIZ=Path(__file__).resolve().parents[1]
BASE=ANTERIOR.BASE/'tanda_2_hd_v1'
LECTURAS=BASE/'lecturas_agente.json'
SALIDA=BASE/'resultados'
INFORME=RAIZ/'docs/REVISION_INTERCAMBIOS_HD_TANDA_2_V1.md'
ESTADOS={'referencia_respaldada','referencia_cuestionable','ambigua'}


# ---- 2. Cobertura determinista y revisión, sin convertir propuestas en verdad ----
def pendientes_hd(inventario,ya_revisados):
    assert len(inventario)==len({r['intervencion_id'] for r in inventario})
    assert ya_revisados<={r['intervencion_id'] for r in inventario}
    seleccion=[]
    for fila in inventario:
        visitada=fila['intervencion_id'] in ya_revisados
        assert (fila['revision_cualitativa']!='pendiente')==visitada,'Cobertura previa incoherente'
        if not visitada and {fila['etiqueta_ia'],fila['pred_adjudicada']}=={'hawkish','dovish'}:
            seleccion.append(dict(fila))
    return sorted(seleccion,key=lambda r:r['intervencion_id'])


def validar_lectura(lectura,texto,etiqueta_ia):
    assert lectura['estado_revision'] in ESTADOS
    if lectura['estado_revision']=='referencia_cuestionable':
        assert lectura['postura_sugerida_agente'] in ANTERIOR.CLASES
        assert lectura['postura_sugerida_agente']!=etiqueta_ia
        # Reusar únicamente el control de dominio y citas de la primera tanda.
        ANTERIOR.validar_lectura({**lectura,'estado_revision':'referencia_respaldada'},texto)
    else:
        ANTERIOR.validar_lectura(lectura,texto)
        if lectura['estado_revision']=='referencia_respaldada':
            assert lectura['postura_sugerida_agente']==etiqueta_ia


def actualizar_cobertura(inventario,seleccion):
    identificadores={r['intervencion_id'] for r in seleccion}
    assert len(identificadores)==len(seleccion)
    assert identificadores<={r['intervencion_id'] for r in inventario if r['revision_cualitativa']=='pendiente'}
    return [{**r,'revision_cualitativa':'tanda_2_hd' if r['intervencion_id'] in identificadores else r['revision_cualitativa']} for r in inventario]


# ---- 3. Informe reproducible con propuestas separadas de la anotación IA ----
def redactar(casos,resumen):
    c=resumen['tanda_2'];total=resumen['acumulado']
    lineas=['# Revisión de intercambios H/D — segunda tanda', '',
        f'**16 casos adicionales leídos completos. Cobertura acumulada: {total["revisados"]}/66; quedan {total["pendientes"]}.**', '',
        f'En esta tanda: **{c["referencia_respaldada"]} referencias respaldadas, {c["referencia_cuestionable"]} cuestionables y {c["ambigua"]} ambiguas** según la lectura del agente. No son adjudicaciones humanas ni se han cambiado etiquetas.', '',
        'Se eligieron todos los intercambios H↔D que seguían pendientes, sin seleccionar por facilidad o confianza. Junto con cuatro de la tanda anterior, quedan revisados los 20 intercambios directos H/D de la evaluación actual. Los 43 restantes involucran neutralidad.', '',
        '## Tres etiquetas IA que propongo revisar', '',
        '| Caso | IA original | Modelo | Propuesta del agente | Fundamento |', '|---|---|---|---|---|']
    fundamentos={
        'RPM-2006-05-11:674:1':'Respalda continuar la normalización futura, aunque pausa hoy.',
        'RPM-2008-02-07:1684:1':'Conserva el sesgo alcista y posibles alzas futuras, aunque lo suaviza.',
        'RPM-2011-08-18:4280:1':'Mantención sin signo futuro expresado; no heredar posturas de otros participantes.'}
    for caso in casos:
        if caso['estado_revision']=='referencia_cuestionable':
            lineas.append(f'| {caso["caso_revision"]} — {caso["fecha"]}, {caso["actor"]} | {caso["etiqueta_ia"]} | {caso["pred_adjudicada"]} | **{caso["postura_sugerida_agente"]}** | {fundamentos[caso["intervencion_id"]]} |')
    lineas+=['', '**Las tres propuestas tienen confianza media y siguen pendientes de decisión del investigador.** No se cuentan como aciertos nuevos del modelo. En la propuesta N, la lectura cuestiona tanto el D de la referencia como el H del modelo.', '',
        '## Inventario de esta tanda', '',
        '| Caso | ID original | IA | Modelo | Lectura del agente |', '|---|---|---|---|---|']
    for caso in casos:
        lectura=caso['estado_revision'].replace('_',' ')
        lineas.append(f'| {caso["caso_revision"]} | {caso["intervencion_id"]} | {caso["etiqueta_ia"]} | {caso["pred_adjudicada"]} | {lectura} |')
    lineas+=['', '## Lecturas con evidencia', '',
        'Los códigos H01–H16 identifican esta revisión, no nuevos casos de la muestra humana R01–R30. Todas las citas de abajo fueron elegidas por el agente del texto completo. Se conservan aparte las citas, notas y confianzas IA originales.','']
    for caso in casos:
        propuesta=caso['postura_sugerida_agente'] or 'sin propuesta definitiva'
        lineas += [f'### {caso["caso_revision"]} — {caso["fecha"]}, {caso["actor"]}', '',
            f'**IA {caso["etiqueta_ia"]} / modelo {caso["pred_adjudicada"]}; {caso["estado_revision"].replace("_"," ")}; lectura: {propuesta}.**', '']
        for cita in caso['citas_agente']:lineas+=['> '+cita,'']
        lineas += [caso['lectura'],'','**Límite y acción:** '+caso['limite_y_accion'],'']
    lineas+=['## Hallazgos y cautelas', '',
        '- Hay errores de modelo ante decisiones explícitas: reducir de 5,25% a 5%, o subir 25 puntos a 2,75%/3,5%. No todo es un problema de anotación o de frases condicionales.',
        '- Mantener hoy con un sesgo alcista respaldado puede ser H; subir menos de lo contemplado sigue siendo un alza. Mantener sin dirección futura no se transforma automáticamente en D.',
        '- Reducir el estímulo no es reducir la TPM; consolidación fiscal no es subir la tasa. Son distinciones del contenido, no causas verificadas de las predicciones: no se calculan contribuciones léxicas en esta revisión.',
        '- Tres casos quedan ambiguos: respaldo a normalización con preferencia por pausa, mantención prolongada con alzas lejanas y negativa a recortar ahora con posibilidad futura. En este último la fuente termina una frase de manera defectuosa: no se inventa lo que falta.',
        '- No se transfiere entre intervenciones el pedido de un ministro al texto del acuerdo institucional. La unidad sigue siendo la intervención completa.', '',
        '## Cobertura acumulada y límites', '',
        f'- {total["revisados"]} revisados: {total["referencia_respaldada"]} referencias respaldadas, {total["referencia_cuestionable"]} cuestionables y {total["ambigua"]} casos ambiguos. No extrapolar estas proporciones: la selección priorizó errores nuevos e inversiones H/D.',
        f'- {total["pendientes"]} casos pendientes; inventario acumulado sin sobrescribir el inventario histórico de la primera tanda.',
        f'- {c["caracteres_textos"]} caracteres leídos en los 16 textos completos; {c["citas_agente_verificadas"]} extractos comprobados, cada uno ≤300 caracteres y literales tras normalizar solo espacios.',
        '- La lectura es del agente con acceso a las dos anotaciones/predicciones, no un nuevo test independiente. Las 793 filas ya son desarrollo reutilizado. No se alteran las métricas 60/66 ni se reentrena después de revisar sus errores.',
        '- Las seis adjudicaciones humanas previamente aceptadas siguen intactas. Estas propuestas nuevas sobre validación no heredan aquella aceptación. No se han abierto las 306 respuestas anteriores ni se importan correcciones canónicas.', '',
        '## Archivos y reproducción', '',
        '[Primera tanda](REVISION_ERRORES_NUEVOS_ADJUDICADA_V1.md) · [Evaluación de origen](EVALUACION_MODELO_ADJUDICADO_V1.md)', '',
        '`data/auditoria/revision_errores_adjudicada_v1/tanda_2_hd_v1/lecturas_agente.json` guarda las opiniones del agente; `resultados/` conserva textos, anotaciones originales, cobertura y hashes.', '',
        '```bash', 'python scripts/33_revisar_intercambios_hd.py --salida /ruta/nueva --informe /ruta/informe_nuevo.md', '```','']
    return '\n'.join(lineas)


# ---- 4. Generación exclusiva e integridad de las dos tandas ----
def ejecutar(salida=SALIDA,informe=INFORME):
    salida,informe=Path(salida),Path(informe)
    if salida.exists() or informe.exists():raise FileExistsError('No sobrescribir revisión existente')
    previo=json.loads((ANTERIOR.SALIDA/'manifest.json').read_text())
    for nombre,huella in previo['sha256_insumos'].items():assert sha256(RAIZ/nombre)==huella,nombre
    for nombre,huella in previo['sha256_salidas'].items():assert sha256(ANTERIOR.SALIDA/nombre)==huella,nombre
    inventario=ANTERIOR.leer_csv(ANTERIOR.SALIDA/'inventario_errores.csv')
    anteriores=json.loads((ANTERIOR.SALIDA/'casos_revisados.json').read_text())
    vistos={r['intervencion_id'] for r in anteriores}
    assert len(vistos)==len(anteriores)==7 and len(inventario)==66
    seleccion=pendientes_hd(inventario,vistos)
    assert len(seleccion)==16
    documento=json.loads(LECTURAS.read_text())
    assert documento['autor']=='agente' and documento['cambios_aplicados'] is False
    lecturas={r['intervencion_id']:r for r in documento['lecturas']}
    assert len(lecturas)==len(documento['lecturas'])==16
    assert set(lecturas)=={r['intervencion_id'] for r in seleccion}
    corpus={r['intervencion_id']:r for r in ANTERIOR.leer_csv(RAIZ/'data/L0/corpus.csv')}
    archivos_ia=sorted((RAIZ/'data/etiquetas').glob('etiquetas_*.csv'))
    etiquetas={}
    for archivo in archivos_ia:
        for fila in ANTERIOR.leer_csv(archivo):
            assert fila['intervencion_id'] not in etiquetas and fila['metodo']=='ia_ronda'
            etiquetas[fila['intervencion_id']]=fila
    casos=[]
    for numero,fila in enumerate(seleccion,1):
        identificador=fila['intervencion_id'];texto=corpus[identificador];etiqueta=etiquetas[identificador]
        assert etiqueta['etiqueta']==fila['etiqueta_ia']
        assert texto['meeting_id']==fila['meeting_id']
        lectura=lecturas[identificador]
        validar_lectura(lectura,texto['texto'],fila['etiqueta_ia'])
        casos.append({**fila,**lectura,'revision_cualitativa':'tanda_2_hd','caso_revision':f'H{numero:02d}',
            'fecha':texto['fecha'],'actor':texto['actor'],'cargo':texto['cargo'],
            'texto_completo':texto['texto'],'sha256_texto':hashlib.sha256(texto['texto'].encode()).hexdigest(),
            'anotacion_ia_original':etiqueta,'cita_ia_literal':bool(norm(etiqueta['frase_justificante'])) and norm(etiqueta['frase_justificante']) in norm(texto['texto'])})
    acumulado=actualizar_cobertura(inventario,seleccion)
    assert sum(r['revision_cualitativa']=='pendiente' for r in acumulado)==43
    assert not any(r['revision_cualitativa']=='pendiente' and {r['etiqueta_ia'],r['pred_adjudicada']}=={'hawkish','dovish'} for r in acumulado)
    conteo=Counter(r['estado_revision'] for r in casos)
    total=Counter(r['estado_revision'] for r in anteriores+casos)
    resumen={'tanda_2':{'revisados':len(casos),**{e:conteo[e] for e in sorted(ESTADOS)},
        'caracteres_textos':sum(len(r['texto_completo']) for r in casos),
        'citas_agente_verificadas':sum(len(r['citas_agente']) for r in casos),
        'citas_ia_literales':sum(r['cita_ia_literal'] for r in casos)},
        'acumulado':{'revisados':len(anteriores)+len(casos),'pendientes':43,**{e:total[e] for e in sorted(ESTADOS)},
            'intercambios_hd_revisados':20,'intercambios_hd_pendientes':0},
        'etiquetas_modificadas':0,'propuestas_nuevas_aceptadas_por_usuario':False,
        'entrenamiento_realizado':False,'metricas_recalculadas':False,'examen_306_abierto':False}
    fuentes=[LECTURAS,Path(__file__),RAIZ/'scripts/utilidades.py',RAIZ/'scripts/32_revisar_errores_nuevos.py',
        RAIZ/'tests/test_revision_intercambios_hd.py',ANTERIOR.SALIDA/'manifest.json',
        ANTERIOR.SALIDA/'inventario_errores.csv',ANTERIOR.SALIDA/'casos_revisados.json',
        RAIZ/'data/L0/corpus.csv',RAIZ/'docs/codebook_v2.md',RAIZ/'docs/ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md']+archivos_ia
    hashes={str(p.relative_to(RAIZ)):sha256(p) for p in fuentes}
    salida.mkdir(parents=True)
    with (salida/'inventario_acumulado.csv').open('x',encoding='utf-8',newline='') as archivo:
        escritor=csv.DictWriter(archivo,fieldnames=list(acumulado[0]));escritor.writeheader();escritor.writerows(acumulado)
    ANTERIOR.escribir_json(salida/'casos_revisados.json',casos)
    ANTERIOR.escribir_json(salida/'resumen.json',resumen)
    informe.parent.mkdir(parents=True,exist_ok=True)
    with informe.open('x',encoding='utf-8') as archivo:archivo.write(redactar(casos,resumen))
    for nombre,huella in hashes.items():assert sha256(RAIZ/nombre)==huella,nombre
    ANTERIOR.escribir_json(salida/'manifest.json',{'registrado_utc':datetime.now(timezone.utc).isoformat(),
        'sha256_insumos':hashes,'sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir())},
        'sha256_informe':sha256(informe),'etiquetas_y_metricas_originales_intactas':True})
    print(json.dumps(resumen,ensure_ascii=False,indent=2))
    return resumen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path,default=SALIDA)
    parser.add_argument('--informe',type=Path,default=INFORME)
    opciones=parser.parse_args()
    ejecutar(opciones.salida,opciones.informe)


if __name__=='__main__':main()
