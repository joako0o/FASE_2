"""Tanda 4: leer los 13 restantes y consolidar las 66 revisiones sin adjudicarlas.

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

ANTERIOR=cargar_script('34_revisar_neutralidad.py')
VALIDADOR=ANTERIOR.ANTERIOR
UTIL=ANTERIOR.UTIL
RAIZ=Path(__file__).resolve().parents[1]
BASE=ANTERIOR.BASE.parent/'tanda_4_largos_v1'
LECTURAS=BASE/'lecturas_agente.json'
SALIDA=BASE/'resultados'
INFORME=RAIZ/'docs/REVISION_ERRORES_CIERRE_66_V1.md'
NUMERO_CASOS=13


# ---- 2. Cierre completo de la cola congelada, sin muestreo nuevo ----
def seleccionar_restantes(inventario,corpus,cola):
    assert len(inventario)==len({r['intervencion_id'] for r in inventario})
    pendientes=[dict(r) for r in inventario if r['revision_cualitativa']=='pendiente']
    pendientes.sort(key=lambda r:(len(corpus[r['intervencion_id']]['texto']),r['intervencion_id']))
    esperada=[{**r,'actor':corpus[r['intervencion_id']]['actor'],
        'n_caracteres':len(corpus[r['intervencion_id']]['texto'])} for r in pendientes]
    assert cola==esperada,'La cola no coincide íntegramente con el inventario/corpus'
    assert len(pendientes)==NUMERO_CASOS
    for fila in pendientes:
        assert fila['etiqueta_ia']=='neutral' and fila['pred_adjudicada']!='neutral'
    return pendientes


def actualizar_cobertura(inventario,seleccion):
    ids={r['intervencion_id'] for r in seleccion}
    assert len(ids)==len(seleccion)
    assert ids=={r['intervencion_id'] for r in inventario if r['revision_cualitativa']=='pendiente'}
    return [{**r,'revision_cualitativa':'tanda_4_largos' if r['intervencion_id'] in ids else r['revision_cualitativa']} for r in inventario]


def verificar_manifiesto(carpeta):
    m=json.loads((carpeta/'manifest.json').read_text())
    for nombre,huella in m.get('sha256_insumos',{}).items():assert sha256(RAIZ/nombre)==huella,nombre
    for nombre,huella in m['sha256_salidas'].items():assert sha256(carpeta/nombre)==huella,nombre


# ---- 3. Consolidación de opiniones, sin sustituir referencias ni evidencia ----
def consolidar(todos):
    assert len(todos)==len({r['intervencion_id'] for r in todos})
    carpetas={'tanda_1_nuevos':UTIL.SALIDA,'tanda_2_hd':VALIDADOR.SALIDA,
        'tanda_3_neutralidad':ANTERIOR.SALIDA,'tanda_4_largos':SALIDA}
    campos=['caso_revision','intervencion_id','fecha','actor','etiqueta_ia','pred_adjudicada',
        'estado_revision','postura_sugerida_agente','confianza_revision','sha256_texto','lectura','limite_y_accion']
    filas=[]
    for caso in todos:
        filas.append({**{k:caso[k] for k in campos},
            'citas_agente':json.dumps(caso['citas_agente'],ensure_ascii=False),
            'archivo_evidencia':str((carpetas[caso['revision_cualitativa']]/'casos_revisados.json').relative_to(RAIZ)),
            'nuevas_correcciones_aceptadas':False,'cambios_aplicados':False})
    return filas


def redactar(casos,todos,resumen):
    t=resumen['tanda_4'];a=resumen['acumulado']
    abreviar={'hawkish':'H','dovish':'D','neutral':'N',None:'—'}
    propuestas=[r for r in todos if r['estado_revision']=='referencia_cuestionable']
    ambiguos=[r for r in todos if r['estado_revision']=='ambigua']
    lineas=['# Revisión de etiquetas — cierre de los 66 desacuerdos','',
        f'**66/66 intervenciones leídas completas: {a["referencia_respaldada"]} referencias respaldadas, {a["referencia_cuestionable"]} cuestionables y {a["ambigua"]} ambiguas según el agente.** No quedan textos por leer en esta lista. Sí quedan propuestas sin adjudicar y dudas sin resolver.','',
        'No todos los desacuerdos son errores de anotación. La revisión detecta tanto predicciones que no siguen la postura expresada como referencias que parecen omitirla. IA y modelo no se tratan como verdad. Las opiniones son posteriores a conocer ambos, no una nueva referencia humana independiente.','',
        '## Resultado de las cuatro tandas','',
        '| Tanda | Textos completos | Referencia respaldada | Cuestionable | Ambigua |',
        '|---|---:|---:|---:|---:|',
        '| 1 — errores nuevos | 7 | 4 | 0 | 3 |',
        '| 2 — intercambios H/D | 16 | 10 | 3 | 3 |',
        '| 3 — pendientes más cortos | 30 | 19 | 5 | 6 |',
        f'| 4 — últimos textos largos | {t["revisados"]} | {t["referencia_respaldada"]} | {t["referencia_cuestionable"]} | {t["ambigua"]} |',
        f'| **Total** | **66** | **{a["referencia_respaldada"]}** | **{a["referencia_cuestionable"]}** | **{a["ambigua"]}** |','',
        '- **Respaldada:** la referencia IA sigue siendo defendible frente al modelo, según la lectura del agente.',
        '- **Cuestionable:** existe una propuesta alternativa concreta; no es una corrección aplicada.',
        '- **Ambigua:** no se fija alternativa definitiva; no es una cuarta clase ni se transforma en N.',
        f'- Se leyeron {a["caracteres_textos"]:,} caracteres originales en total, incluidos {t["caracteres_textos"]:,} de la última tanda. Cobertura completa de estos 66 desacuerdos, no revisión de las 793 referencias ni estimación de prevalencia en todo el corpus.','',
        '## Lista única de las 13 propuestas pendientes','',
        'H = hawkish; D = dovish; N = neutral. Hxx/Nxx/Lxx identifican las tandas 2/3/4, no las seis adjudicaciones Rxx ya aceptadas. La aceptación anterior no se extiende a estas 13 propuestas.','',
        '| Caso | ID | Actor | IA → propuesta | Modelo | Confianza del agente |',
        '|---|---|---|---|---|---|']
    for r in propuestas:
        lineas.append(f'| {r["caso_revision"]} | {r["intervencion_id"]} | {r["actor"]} | **{abreviar[r["etiqueta_ia"]]} → {abreviar[r["postura_sugerida_agente"]]}** | {abreviar[r["pred_adjudicada"]]} | {r["confianza_revision"]} |')
    lineas+=['',
        'H13 (comunicado de agosto de 2011) y N19 (De Ramón, agosto de 2015) tienen propuestas que contradicen también al modelo. No se fuerza coincidencia con sus predicciones. La confianza es cualitativa del agente, no probabilidad calibrada.','',
        'Las razones y citas de Hxx están en la [tanda 2](REVISION_INTERCAMBIOS_HD_TANDA_2_V1.md); las de Nxx en la [tanda 3](REVISION_NEUTRALIDAD_TANDA_3_V1.md); las de Lxx, más abajo. El CSV consolidado reúne las explicaciones y evidencias de las cuatro tandas sin reescribir los juicios anteriores.','',
        '## Qué aporta la lectura de los textos largos','',
        '- **Relajamiento futuro explícito:** García, diciembre de 2008, aclara que se debate su magnitud y momento, no su conveniencia. Marfán, junio de 2013, prefiere una combinación futura con reducción de tasas, aunque vota mantener hoy.',
        '- **Duración del estímulo:** Naudon, junio de 2015, pide prolongarlo respecto de lo previsto; García, agosto de 2009, rechaza retirarlo y defiende tasa mínima prolongada. No se infiere D del nivel bajo por sí solo.',
        '- **Normalización respaldada:** Valdés, marzo de 2005, apoya continuar la estrategia de alzas y pausas; el menú inmediato no agota su postura. La propuesta H conserva cautela por el marco técnico.',
        '- **No toda exposición larga es direccional:** opciones condicionales, diagnósticos y balances sin preferencia dominante pueden respaldar N. No se cuentan menciones a inflación, alzas o bajas como votos.',
        f'- **Cadena guardada:** A=1 en {t["puerta_a_igual_1"]}/13 y final=B en {t["salida_final_igual_b"]}/13 de esta tanda. No hay neutralidad forzada por la puerta de relevancia. Esto no identifica causalmente qué términos determinaron B.','',
        '## Lecturas de las 13 intervenciones restantes','',
        'Se siguió toda la cola congelada de la tanda 3, sin nueva selección. Cada texto se leyó íntegro; el último, de 14.172 caracteres, en dos partes contiguas. No se repararon errores de OCR ni se importaron tasas/sesgos desde otras intervenciones.','']
    for r in casos:
        lineas += [f'### {r["caso_revision"]} — {r["fecha"]}, {r["actor"]}','',
            f'**{r["intervencion_id"]}: IA {abreviar[r["etiqueta_ia"]]}, modelo {abreviar[r["pred_adjudicada"]]}; {r["estado_revision"].replace("_"," ")}; lectura {abreviar[r["postura_sugerida_agente"]]}; confianza {r["confianza_revision"]}.**','']
        for cita in r['citas_agente']:lineas+=['> '+cita,'']
        lineas += [r['lectura'],'','**Límite y acción:** '+r['limite_y_accion'],'']
    lineas+=['## Los 12 ambiguos, ya leídos pero no resueltos','',
        'Se conserva la opinión anterior y la propuesta nula. Completar cobertura no equivale a eliminar incertidumbre.','',
        '| Caso | ID | Actor | Límite registrado en su tanda |','|---|---|---|---|']
    for r in ambiguos:
        limite=r['limite_y_accion'].replace('|','\\|').replace('\n',' ')
        lineas.append(f'| {r["caso_revision"]} | {r["intervencion_id"]} | {r["actor"]} | {limite} |')
    lineas+=['','## Alcance y siguiente decisión','',
        'La revisión cualitativa de la lista está cerrada. Un paso posterior razonable es decidir sobre las 13 propuestas y tratar separadamente los 12 ambiguos. No hace falta repetir las 30 anotaciones humanas ni las seis aceptaciones previas. Este cierre no aplica ninguna corrección.','',
        'No hubo entrenamiento, modificación de etiquetas canónicas, recalculo de métricas, cambio del codebook v2 ni apertura de las 306 respuestas antiguas. La validación de 793 es desarrollo reutilizado y no vuelve a ser test intacto. Reetiquetarla según opiniones post-predicción y mostrar un score mayor no demostraría mejora del modelo.','',
        '## Integridad y reproducción','',
        f'En esta tanda se verificaron {t["citas_agente_verificadas"]} extractos propios literales tras normalizar espacios, todos ≤300 caracteres. Las {t["citas_ia_literales"]} citas IA son literales y se conservan junto con sus notas y procedencia. Una cita literal no certifica que represente la postura completa.', '',
        '[Tanda 1](REVISION_ERRORES_NUEVOS_ADJUDICADA_V1.md) · [Tanda 2](REVISION_INTERCAMBIOS_HD_TANDA_2_V1.md) · [Tanda 3](REVISION_NEUTRALIDAD_TANDA_3_V1.md) · [Evaluación congelada](EVALUACION_MODELO_ADJUDICADO_V1.md)','',
        'Artefactos separados en `data/auditoria/revision_errores_adjudicada_v1/tanda_4_largos_v1/`:','',
        '- `lecturas_agente.json`: 13 opiniones manuales, no adjudicaciones.',
        '- `resultados/casos_revisados.json`: 13 textos completos, SHA256, anotaciones IA originales y predicciones A/B/final.',
        '- `resultados/revision_consolidada.csv`: 66 opiniones, citas, propuestas separadas, límites y rutas a los textos completos. No es un importador de etiquetas.',
        '- `resultados/inventario_acumulado.csv`, `pendientes.json`, `resumen.json` y `manifest.json`: cierre de cobertura, conteos y trazabilidad.',
        '- `verificacion.json`: resultado de pruebas, reproducción temporal y comprobación de archivos anteriores. Las pruebas certifican integridad, no verdad semántica.','',
        '```bash','python3 scripts/35_cerrar_revision_66.py --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'python3 -m unittest discover -s tests -p "test_revision_cierre_66.py" -v','```','']
    return '\n'.join(lineas)


# ---- 4. Generación exclusiva: textos completos, anotaciones originales y A/B ----
def ejecutar(salida=SALIDA,informe=INFORME):
    salida,informe=Path(salida),Path(informe)
    if salida.exists() or informe.exists():raise FileExistsError('No sobrescribir revisión existente')
    for carpeta in [UTIL.MODELO,UTIL.SALIDA,VALIDADOR.SALIDA,ANTERIOR.SALIDA]:verificar_manifiesto(carpeta)
    inventario=UTIL.leer_csv(ANTERIOR.SALIDA/'inventario_acumulado.csv')
    previos=sum([json.loads((p/'casos_revisados.json').read_text()) for p in [UTIL.SALIDA,VALIDADOR.SALIDA,ANTERIOR.SALIDA]],[])
    assert len(previos)==len({r['intervencion_id'] for r in previos})==53
    assert {r['intervencion_id'] for r in inventario if r['revision_cualitativa']!='pendiente'}=={r['intervencion_id'] for r in previos}
    filas_corpus=UTIL.leer_csv(RAIZ/'data/L0/corpus.csv')
    corpus={r['intervencion_id']:r for r in filas_corpus};assert len(corpus)==len(filas_corpus)
    cola=json.loads((ANTERIOR.SALIDA/'pendientes.json').read_text())
    seleccion=seleccionar_restantes(inventario,corpus,cola)
    assert len(inventario)==66 and len(seleccion)==13
    documento=json.loads(LECTURAS.read_text())
    assert documento['autor']=='agente' and documento['cambios_aplicados'] is False
    lecturas={r['intervencion_id']:r for r in documento['lecturas']}
    assert len(lecturas)==len(documento['lecturas'])==13
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
        VALIDADOR.validar_lectura(lectura,texto['texto'],fila['etiqueta_ia'])
        casos.append({**fila,**lectura,'revision_cualitativa':'tanda_4_largos','caso_revision':f'L{numero:02d}',
            'fecha':texto['fecha'],'actor':texto['actor'],'cargo':texto['cargo'],
            'texto_completo':texto['texto'],'sha256_texto':hashlib.sha256(texto['texto'].encode()).hexdigest(),
            'anotacion_ia_original':etiqueta,'pred_a':int(pred['pred_a']),'pred_b':pred['pred_b'],
            'cita_ia_literal':bool(norm(etiqueta['frase_justificante'])) and norm(etiqueta['frase_justificante']) in norm(texto['texto'])})
    acumulado=actualizar_cobertura(inventario,seleccion)
    pendientes=[]
    todos=previos+casos
    assert len(todos)==len({r['intervencion_id'] for r in todos})==66
    assert {r['intervencion_id'] for r in todos}=={r['intervencion_id'] for r in inventario}
    consolidado=consolidar(todos)
    conteo=Counter(r['estado_revision'] for r in casos);total=Counter(r['estado_revision'] for r in previos+casos)
    resumen={'tanda_4':{'revisados':len(casos),**{e:conteo[e] for e in sorted(VALIDADOR.ESTADOS)},
        'caracteres_textos':sum(len(r['texto_completo']) for r in casos),
        'citas_agente_verificadas':sum(len(r['citas_agente']) for r in casos),
        'citas_ia_literales':sum(r['cita_ia_literal'] for r in casos),
        'puerta_a_igual_1':sum(r['pred_a']==1 for r in casos),'salida_final_igual_b':sum(r['pred_adjudicada']==r['pred_b'] for r in casos)},
        'acumulado':{'revisados':len(previos)+len(casos),'pendientes':len(pendientes),
            **{e:total[e] for e in sorted(VALIDADOR.ESTADOS)},'caracteres_pendientes':0,'caracteres_textos':sum(len(r['texto_completo']) for r in todos)},
        'criterio_seleccion':'todos_los_13_pendientes_de_tanda_3_sin_omitir' ,
        'etiquetas_modificadas':0,'nuevas_propuestas_aceptadas':False,'entrenamiento_realizado':False,'metricas_recalculadas':False,'examen_306_abierto':False}
    assert resumen['tanda_4']['caracteres_textos']==105621
    assert resumen['tanda_4']['puerta_a_igual_1']==resumen['tanda_4']['salida_final_igual_b']==13
    fuentes=[LECTURAS,Path(__file__),RAIZ/'scripts/utilidades.py',
        RAIZ/'scripts/34_revisar_neutralidad.py',RAIZ/'scripts/33_revisar_intercambios_hd.py',
        RAIZ/'scripts/32_revisar_errores_nuevos.py',RAIZ/'tests/test_revision_cierre_66.py',RAIZ/'data/L0/corpus.csv',
        RAIZ/'docs/codebook_v2.md',RAIZ/'docs/ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md',
        UTIL.MODELO/'predicciones_validacion.csv',UTIL.MODELO/'manifest.json',
        ANTERIOR.SALIDA/'inventario_acumulado.csv',ANTERIOR.SALIDA/'pendientes.json']+archivos_ia
    for etapa in [UTIL,VALIDADOR,ANTERIOR]:
        fuentes.extend([etapa.SALIDA/'casos_revisados.json',etapa.SALIDA/'manifest.json',etapa.INFORME])
    hashes={str(p.relative_to(RAIZ)):sha256(p) for p in fuentes}
    salida.mkdir(parents=True)
    with (salida/'inventario_acumulado.csv').open('x',encoding='utf-8',newline='') as archivo:
        escritor=csv.DictWriter(archivo,fieldnames=list(acumulado[0]));escritor.writeheader();escritor.writerows(acumulado)
    with (salida/'revision_consolidada.csv').open('x',encoding='utf-8',newline='') as archivo:
        escritor=csv.DictWriter(archivo,fieldnames=list(consolidado[0]));escritor.writeheader();escritor.writerows(consolidado)
    for nombre,valor in [('casos_revisados.json',casos),('pendientes.json',pendientes),('resumen.json',resumen)]:UTIL.escribir_json(salida/nombre,valor)
    informe.parent.mkdir(parents=True,exist_ok=True)
    with informe.open('x',encoding='utf-8') as archivo:archivo.write(redactar(casos,todos,resumen))
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
