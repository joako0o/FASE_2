"""Tanda 3: ampliar cobertura con los 30 pendientes más cortos, sin truncarlos.

Los juicios son lecturas manuales del agente. El código valida cobertura,
evidencia y procedencia; no entrena ni convierte propuestas en etiquetas finales.
"""
# ---- 1. Fuentes y parámetros; reutilización de validadores congelados ----
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from utilidades import cargar_script, norm, sha256

ANTERIOR=cargar_script('33_revisar_intercambios_hd.py')
UTIL=ANTERIOR.ANTERIOR
RAIZ=Path(__file__).resolve().parents[1]
BASE=ANTERIOR.BASE.parent/'tanda_3_neutralidad_v1'
LECTURAS=BASE/'lecturas_agente.json'
SALIDA=BASE/'resultados'
INFORME=RAIZ/'docs/REVISION_NEUTRALIDAD_TANDA_3_V1.md'
NUMERO_CASOS=30


# ---- 2. Selección por presupuesto, sin usar el resultado cualitativo ----
def seleccionar_cortos(inventario,corpus,limite=NUMERO_CASOS):
    assert isinstance(limite,int) and limite>0
    assert len(inventario)==len({r['intervencion_id'] for r in inventario})
    pendientes=[dict(r) for r in inventario if r['revision_cualitativa']=='pendiente']
    for fila in pendientes:
        assert fila['intervencion_id'] in corpus
        assert fila['etiqueta_ia']!=fila['pred_adjudicada']
        assert 'neutral' in {fila['etiqueta_ia'],fila['pred_adjudicada']}
    pendientes.sort(key=lambda r:(len(corpus[r['intervencion_id']]['texto']),r['intervencion_id']))
    return pendientes[:limite],pendientes[limite:]


def actualizar_cobertura(inventario,seleccion):
    ids={r['intervencion_id'] for r in seleccion}
    assert len(ids)==len(seleccion)
    assert ids<={r['intervencion_id'] for r in inventario if r['revision_cualitativa']=='pendiente'}
    return [{**r,'revision_cualitativa':'tanda_3_neutralidad' if r['intervencion_id'] in ids else r['revision_cualitativa']} for r in inventario]


def verificar_manifiesto(carpeta):
    m=json.loads((carpeta/'manifest.json').read_text())
    for nombre,huella in m.get('sha256_insumos',{}).items():assert sha256(RAIZ/nombre)==huella,nombre
    for nombre,huella in m['sha256_salidas'].items():assert sha256(carpeta/nombre)==huella,nombre


# ---- 3. Informe: diagnósticos, propuestas pendientes y cobertura explícita ----
def redactar(casos,pendientes,resumen):
    actual=resumen['tanda_3'];total=resumen['acumulado']
    lineas=['# Revisión de neutralidad — tercera tanda', '',
        f'**30 casos adicionales leídos completos; cobertura acumulada {total["revisados"]}/66. Quedan {total["pendientes"]} intervenciones largas.**', '',
        'Para abarcar más casos se ordenaron los 43 pendientes por longitud del texto original y después por ID. Se leyeron los 30 más cortos íntegramente. Es una selección por presupuesto, no una muestra aleatoria ni una evaluación representativa; los casos largos quedan explícitamente pendientes.', '',
        f'**Esta tanda: {actual["referencia_respaldada"]} referencias respaldadas, {actual["referencia_cuestionable"]} cuestionables y {actual["ambigua"]} ambiguas, según el agente.** No se han aceptado ni aplicado nuevas correcciones.', '',
        '## Cinco etiquetas que propongo revisar', '',
        '| Caso | ID | IA | Modelo | Propuesta del agente | Confianza del agente |', '|---|---|---|---|---|---|']
    for caso in casos:
        if caso['estado_revision']=='referencia_cuestionable':
            lineas.append(f'| {caso["caso_revision"]} | {caso["intervencion_id"]} | {caso["etiqueta_ia"]} | {caso["pred_adjudicada"]} | **{caso["postura_sugerida_agente"]}** | {caso["confianza_revision"]} |')
    lineas+=['', 'Las propuestas no heredan la aceptación de las seis adjudicaciones humanas anteriores. En particular, el caso de Beltrán de Ramón de agosto de 2015 se propone D: contradice tanto N de la referencia como H del modelo. No se fuerza la referencia a coincidir con la predicción.', '',
        '## Hallazgos principales', '',
        '- Hay errores incluso en textos de 132 y 195 caracteres con instrucciones explícitas de subir. «Mantiene su votación consistente en subir» no significa mantener la tasa.',
        f'- Comprobación de la cadena de predicción guardada: A=1 en {actual["puerta_a_igual_1"]}/{actual["revisados"]}; la salida final coincide con B en los 30. Estas discrepancias no se deben a que la puerta de relevancia haya forzado neutralidad. No identifica qué palabras causaron cada fallo de B.',
        '- Varias referencias N son defendibles: balance de riesgos, estabilidad sin signo futuro, o diagnóstico sin recomendación. No todo N es una etiqueta comodín.',
        '- Otras N omiten respaldo a normalización, alzas futuras o rechazo argumentado de subir. Hay que revisar el texto completo, no solo una cita sobre mantener.',
        '- Un nivel de llegada como 3,5% no indica por sí solo subir o bajar si no consta la tasa de partida. «Mantener el sesgo» tampoco revela su signo si no se especifica. No traer de otra intervención esos datos tácitamente.',
        '- Los casos ambiguos conservan propuesta nula: eso es estado de revisión, no cuarta clase ni conversión automática a N.', '',
        '## Lecturas de los 30 casos', '',
        'Los códigos N01–N30 son identificadores de esta tanda, no etiquetas de postura. Citas y explicaciones son del agente, no del investigador. La confianza expresada es cualitativa y no calibrada.','']
    for caso in casos:
        propuesta=caso['postura_sugerida_agente'] or 'sin propuesta definitiva'
        lineas += [f'### {caso["caso_revision"]} — {caso["fecha"]}, {caso["actor"]}', '',
            f'**{caso["intervencion_id"]}: IA {caso["etiqueta_ia"]}, modelo {caso["pred_adjudicada"]}; {caso["estado_revision"].replace("_"," ")}; lectura {propuesta}.**', '']
        for cita in caso['citas_agente']:lineas+=['> '+cita,'']
        lineas += [caso['lectura'],'','**Límite y acción:** '+caso['limite_y_accion'],'']
    lineas+=['## Cobertura acumulada', '',
        f'- {total["revisados"]} casos revisados: {total["referencia_respaldada"]} referencias respaldadas, {total["referencia_cuestionable"]} cuestionables y {total["ambigua"]} ambiguas. Son opiniones posteriores a conocer etiquetas/predicciones, no adjudicación independiente.',
        '- Los 20 intercambios directos H/D ya estaban cubiertos por las dos primeras tandas. Las métricas de validación permanecen intactas: no se calculan nuevos aciertos sustituyendo etiquetas por opiniones del agente.',
        '- No hubo entrenamiento, importación canónica o acceso a las 306 respuestas antiguas. La validación de 793 sigue siendo desarrollo reutilizado; no se presenta como test intacto después de examinarla.',
        f'- En esta tanda: {actual["caracteres_textos"]} caracteres íntegros; {actual["citas_agente_verificadas"]} extractos propios literales tras normalizar espacios, cada uno ≤300 caracteres. Las citas IA originales se conservaron, sin corregirlas.', '',
        '## Los 13 pendientes, sin revisión cualitativa todavía', '',
        '| ID | Actor | Caracteres |', '|---|---|---:|']
    for fila in pendientes:
        lineas.append(f'| {fila["intervencion_id"]} | {fila["actor"]} | {fila["n_caracteres"]} |')
    lineas += ['', '## Reproducción y artefactos', '',
        '[Tanda 1](REVISION_ERRORES_NUEVOS_ADJUDICADA_V1.md) · [Tanda 2](REVISION_INTERCAMBIOS_HD_TANDA_2_V1.md) · [Evaluación original](EVALUACION_MODELO_ADJUDICADO_V1.md)', '',
        '`data/auditoria/revision_errores_adjudicada_v1/tanda_3_neutralidad_v1/lecturas_agente.json` contiene la lectura manual. `resultados/` conserva textos completos, anotaciones IA, A/B/final, inventario acumulado y hashes. Las pruebas verifican selección/integridad/citas, no certifican la verdad semántica de las opiniones.', '',
        '```bash','python scripts/34_revisar_neutralidad.py --salida /ruta/nueva --informe /ruta/informe_nuevo.md','```','']
    return '\n'.join(lineas)


# ---- 4. Generación exclusiva: textos completos, anotaciones originales y A/B ----
def ejecutar(salida=SALIDA,informe=INFORME):
    salida,informe=Path(salida),Path(informe)
    if salida.exists() or informe.exists():raise FileExistsError('No sobrescribir revisión existente')
    for carpeta in [UTIL.MODELO,UTIL.SALIDA,ANTERIOR.SALIDA]:verificar_manifiesto(carpeta)
    inventario=UTIL.leer_csv(ANTERIOR.SALIDA/'inventario_acumulado.csv')
    previos=json.loads((UTIL.SALIDA/'casos_revisados.json').read_text())+json.loads((ANTERIOR.SALIDA/'casos_revisados.json').read_text())
    assert len(previos)==len({r['intervencion_id'] for r in previos})==23
    assert {r['intervencion_id'] for r in inventario if r['revision_cualitativa']!='pendiente'}=={r['intervencion_id'] for r in previos}
    filas_corpus=UTIL.leer_csv(RAIZ/'data/L0/corpus.csv')
    corpus={r['intervencion_id']:r for r in filas_corpus};assert len(corpus)==len(filas_corpus)
    seleccion,restantes=seleccionar_cortos(inventario,corpus)
    assert len(inventario)==66 and len(seleccion)==30 and len(restantes)==13
    documento=json.loads(LECTURAS.read_text())
    assert documento['autor']=='agente' and documento['cambios_aplicados'] is False
    lecturas={r['intervencion_id']:r for r in documento['lecturas']}
    assert len(lecturas)==len(documento['lecturas'])==30
    assert set(lecturas)=={r['intervencion_id'] for r in seleccion}
    filas_pred=[r for r in UTIL.leer_csv(UTIL.MODELO/'predicciones_validacion.csv') if r['variante']=='adjudicada']
    predicciones={r['intervencion_id']:r for r in filas_pred};assert len(predicciones)==len(filas_pred)==793
    archivos_ia=sorted((RAIZ/'data/etiquetas').glob('etiquetas_*.csv'))
    etiquetas={}
    for archivo in archivos_ia:
        for fila in UTIL.leer_csv(archivo):
            assert fila['metodo']=='ia_ronda' and fila['intervencion_id'] not in etiquetas
            etiquetas[fila['intervencion_id']]=fila
    casos=[]
    for numero,fila in enumerate(seleccion,1):
        identificador=fila['intervencion_id'];texto=corpus[identificador];etiqueta=etiquetas[identificador];pred=predicciones[identificador]
        assert texto['meeting_id']==fila['meeting_id']==pred['meeting_id']
        assert fila['etiqueta_ia']==etiqueta['etiqueta']==pred['etiqueta']
        assert fila['pred_adjudicada']==pred['pred'] and str(fila['fold'])==pred['fold']
        assert pred['pred']==('neutral' if pred['pred_a']=='0' else pred['pred_b'])
        lectura=lecturas[identificador]
        ANTERIOR.validar_lectura(lectura,texto['texto'],fila['etiqueta_ia'])
        casos.append({**fila,**lectura,'revision_cualitativa':'tanda_3_neutralidad','caso_revision':f'N{numero:02d}',
            'fecha':texto['fecha'],'actor':texto['actor'],'cargo':texto['cargo'],
            'texto_completo':texto['texto'],'sha256_texto':hashlib.sha256(texto['texto'].encode()).hexdigest(),
            'anotacion_ia_original':etiqueta,'pred_a':int(pred['pred_a']),'pred_b':pred['pred_b'],
            'cita_ia_literal':bool(norm(etiqueta['frase_justificante'])) and norm(etiqueta['frase_justificante']) in norm(texto['texto'])})
    acumulado=actualizar_cobertura(inventario,seleccion)
    pendientes=[{**r,'actor':corpus[r['intervencion_id']]['actor'],'n_caracteres':len(corpus[r['intervencion_id']]['texto'])} for r in restantes]
    conteo=Counter(r['estado_revision'] for r in casos);total=Counter(r['estado_revision'] for r in previos+casos)
    resumen={'tanda_3':{'revisados':len(casos),**{e:conteo[e] for e in sorted(ANTERIOR.ESTADOS)},
        'caracteres_textos':sum(len(r['texto_completo']) for r in casos),
        'citas_agente_verificadas':sum(len(r['citas_agente']) for r in casos),
        'citas_ia_literales':sum(r['cita_ia_literal'] for r in casos),
        'puerta_a_igual_1':sum(r['pred_a']==1 for r in casos),'salida_final_igual_b':sum(r['pred_adjudicada']==r['pred_b'] for r in casos)},
        'acumulado':{'revisados':len(previos)+len(casos),'pendientes':len(pendientes),
            **{e:total[e] for e in sorted(ANTERIOR.ESTADOS)},'caracteres_pendientes':sum(r['n_caracteres'] for r in pendientes)},
        'criterio_seleccion':'longitud_original_ascendente_id_ascendente_30_pendientes',
        'etiquetas_modificadas':0,'nuevas_propuestas_aceptadas':False,'entrenamiento_realizado':False,'metricas_recalculadas':False,'examen_306_abierto':False}
    assert resumen['tanda_3']['caracteres_textos']==72911
    assert resumen['tanda_3']['puerta_a_igual_1']==resumen['tanda_3']['salida_final_igual_b']==30
    fuentes=[LECTURAS,Path(__file__),RAIZ/'scripts/utilidades.py',RAIZ/'scripts/33_revisar_intercambios_hd.py',
        RAIZ/'scripts/32_revisar_errores_nuevos.py',RAIZ/'tests/test_revision_neutralidad.py',RAIZ/'data/L0/corpus.csv',
        RAIZ/'docs/codebook_v2.md',RAIZ/'docs/ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md',
        UTIL.MODELO/'predicciones_validacion.csv',UTIL.MODELO/'manifest.json',UTIL.SALIDA/'casos_revisados.json',
        UTIL.SALIDA/'manifest.json',ANTERIOR.SALIDA/'casos_revisados.json',ANTERIOR.SALIDA/'inventario_acumulado.csv',ANTERIOR.SALIDA/'manifest.json']+archivos_ia
    hashes={str(p.relative_to(RAIZ)):sha256(p) for p in fuentes}
    salida.mkdir(parents=True)
    with (salida/'inventario_acumulado.csv').open('x',encoding='utf-8',newline='') as archivo:
        escritor=csv.DictWriter(archivo,fieldnames=list(acumulado[0]));escritor.writeheader();escritor.writerows(acumulado)
    for nombre,valor in [('casos_revisados.json',casos),('pendientes.json',pendientes),('resumen.json',resumen)]:UTIL.escribir_json(salida/nombre,valor)
    informe.parent.mkdir(parents=True,exist_ok=True)
    with informe.open('x',encoding='utf-8') as archivo:archivo.write(redactar(casos,pendientes,resumen))
    for nombre,huella in hashes.items():assert sha256(RAIZ/nombre)==huella,nombre
    UTIL.escribir_json(salida/'manifest.json',{'registrado_utc':datetime.now(timezone.utc).isoformat(),
        'sha256_insumos':hashes,'sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir())},
        'sha256_informe':sha256(informe),'etiquetas_y_metricas_originales_intactas':True})
    print(json.dumps(resumen,ensure_ascii=False,indent=2))
    return resumen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path,default=SALIDA)
    parser.add_argument('--informe',type=Path,default=INFORME)
    opciones=parser.parse_args();ejecutar(opciones.salida,opciones.informe)


if __name__=='__main__':main()
