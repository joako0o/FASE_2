"""Piloto de enriquecimiento con 100 frases WCB (99 utilizables para B).

Preparar antes de ejecutar. Sin adquisición de test externo/humano, traducción
automática durante el ajuste, refit final ni persistencia de clasificadores.
"""
# ---- 1. Configuración y utilidades históricas, sin modificar versiones previas ----
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import time
import warnings

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer, strip_accents_unicode
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

import config
from utilidades import cargar_script, exigir_salidas_nuevas, norm, sha256

LONGITUD = cargar_script('22_seleccionar_longitud_ngramas.py')
ANTERIOR = LONGITUD.ANTERIOR
ESCRIBIR = ANTERIOR.ESCRITURA.escribir_json
VARIANTES = ('B0_base', 'E1_ingles', 'E2_espanol')
RUTA_EXTERNOS = config.RUTA_DATOS / 'externos/wcb_chile_piloto_v1'
RUTA_SALIDA = config.RUTA_DATOS / 'evaluacion/wcb_chile_piloto_v1'
RUTA_PROTOCOLO = config.RUTA_REPO / 'docs/PROTOCOLO_WCB_PILOTO_V1.md'
RUTA_INFORME = config.RUTA_REPO / 'docs/EVALUACION_WCB_PILOTO_V1.md'
REVISION_HF = 'c1ead3f6011bbc358d3ef94b598238b78b7b45fa'


# ---- 2. Auditoría de exportación y traducción; sin relabel ni test externo ----
def normalizar_copia(texto):
    return strip_accents_unicode(norm(texto).lower())


def numeros(texto):
    return re.findall(r'[+-]?\d+(?:[.,]\d+)?', texto.replace('−', '-').replace('–', '-'))


def auditar_externos(externos, datos):
    assert list(externos.columns) == ['row_idx', 'source_id', 'year', 'stance_label', 'texto_en', 'texto_es']
    assert externos.row_idx.tolist() == list(range(100)), 'Selección distinta de 0–99'
    assert externos.source_id.is_unique and externos.source_id.between(0, 999).all()
    assert externos.year.between(2018, 2024).all()
    assert externos.stance_label.isin(['hawkish', 'dovish', 'neutral', 'irrelevant']).all()
    normalizados_ia = set(datos.texto.map(normalizar_copia))
    for columna in ('texto_en', 'texto_es'):
        assert externos[columna].map(lambda t: isinstance(t, str) and bool(t.strip())).all()
        textos = externos[columna].map(normalizar_copia)
        assert textos.is_unique, f'Copias externas en {columna}'
        assert not set(textos) & normalizados_ia, f'Solape IA–externo en {columna}'
    for fila in externos.itertuples():
        assert numeros(fila.texto_en) == numeros(fila.texto_es), f'Cifras/signos cambiados: {fila.row_idx}'
        assert fila.texto_en.count('%') == fila.texto_es.count('%'), f'Porcentajes cambiados: {fila.row_idx}'
    usados = externos[externos.stance_label.ne('irrelevant')]
    assert set(usados.stance_label) == set(ANTERIOR.L.CLASES)
    return {'n_externos': len(externos), 'n_para_b': len(usados),
            'clases_fuente': externos.stance_label.value_counts().to_dict(),
            'anios': externos.year.value_counts().sort_index().to_dict(),
            'duplicados_internos_en_es': 0, 'solapes_exactos_ia_en_es': 0,
            'numeros_signos_porcentajes_preservados': True,
            'normalizacion_solapes': 'Espacios, minúsculas y acentos; no equivalencia semántica.',
            'test_externo_abierto': False, 'otras_semillas_auditadas': False,
            'traduccion': 'Agente IA, no oficial, no ciega; congelada antes del fit.',
            'fuente': 'Captura de columnas de API train 5768, filas 0–99; no descarga binaria Parquet.',
            'revision_hf_observada': REVISION_HF}


def preparar(salida=RUTA_SALIDA, informe=RUTA_INFORME):
    salida, informe = Path(salida), Path(informe)
    exigir_salidas_nuevas(salida, informe)
    datos, mascara, _, fuentes = LONGITUD.cargar_insumos()
    _, asignacion = LONGITUD.asignar_folds(datos, mascara)
    externos = pd.read_csv(RUTA_EXTERNOS / 'muestra.tsv', sep='\t', keep_default_na=False)
    auditoria = auditar_externos(externos, datos)
    archivos = list((config.RUTA_REPO / 'scripts').glob('*.py')) + list(RUTA_EXTERNOS.iterdir()) + [
        RUTA_PROTOCOLO, config.RUTA_REPO / 'tests/test_wcb_piloto.py',
        LONGITUD.RUTA_SALIDA / 'predicciones_validacion.csv',
        LONGITUD.RUTA_SALIDA / 'asignacion_folds.csv',
        config.RUTA_REPO / 'modelos/tfidf_gold_v1.joblib']
    fuentes.update({str(p.relative_to(config.RUTA_REPO)): sha256(p) for p in archivos if p.is_file()})
    protegidos = json.loads((ANTERIOR.L.RUTA_VALIDACION / 'integridad_cierre.json').read_text())['sha256_fuentes']
    fuentes.update(protegidos)
    for nombre, huella in fuentes.items():
        assert sha256(config.RUTA_REPO / nombre) == huella, nombre
    salida.mkdir(parents=True)
    asignacion.to_csv(salida / 'asignacion_folds.csv', index=False)
    ESCRIBIR(salida / 'auditoria_externos.json', auditoria)
    ESCRIBIR(salida / 'protocolo.json', {
        'version': 'wcb_chile_piloto_v1', 'fecha_preparacion_utc': datetime.now(timezone.utc).isoformat(),
        'variantes': VARIANTES, 'sha256_insumos': fuentes,
        'sha256_asignacion': sha256(salida / 'asignacion_folds.csv'),
        'sha256_auditoria': sha256(salida / 'auditoria_externos.json'),
        'parametros_tfidf_b': {**ANTERIOR.PARAMETROS_TFIDF, 'ngram_range': (1, 4)},
        'parametros_lr': ANTERIOR.PARAMETROS_LR, 'peso_individual_externo': 1,
        'tolerancias': {'delta_media_minimo': .01, 'folds_mejora_minimos': 3, 'perdida_recall_maxima': .02},
        'seleccion': 'Mayor media macro-F1; empate orden de variantes. E1 es control, no adoptable.',
        'versiones': {'python': platform.python_version(), 'numpy': np.__version__,
                     'pandas': pd.__version__, 'scipy': scipy.__version__, 'scikit_learn': sklearn.__version__},
        'gold_abierto_o_predicho': False, 'test_externo_abierto': False,
        'refit_final_o_reemplazo': False, 'limite': 'Piloto 100 train externos; 793 IA reutilizados; no confirmación.'})
    print('Preparado sin entrenar:', salida, auditoria['clases_fuente'], flush=True)


def verificar_protocolo(salida):
    protocolo = json.loads((salida / 'protocolo.json').read_text())
    assert protocolo['variantes'] == list(VARIANTES)
    assert sha256(salida / 'asignacion_folds.csv') == protocolo['sha256_asignacion']
    assert sha256(salida / 'auditoria_externos.json') == protocolo['sha256_auditoria']
    for nombre, huella in protocolo['sha256_insumos'].items():
        assert sha256(config.RUTA_REPO / nombre) == huella, nombre
    return protocolo


# ---- 3. Ajuste por fold; externos solo en B, A compartida ----
def componer_train_b(train, externos, variante):
    assert variante in VARIANTES
    relevantes = train.es_relevante.astype(str).eq('1')
    textos = train.loc[relevantes, 'texto'].tolist()
    etiquetas = train.loc[relevantes, 'etiqueta'].tolist()
    if variante != 'B0_base':
        sub = externos[externos.stance_label.ne('irrelevant')]
        columna = 'texto_en' if variante == 'E1_ingles' else 'texto_es'
        textos += sub[columna].tolist()
        etiquetas += sub.stance_label.tolist()
    return textos, etiquetas


def cobertura(vector, textos):
    analizar = vector.build_analyzer()
    cantidad, presentes = 0, 0
    for texto in textos:
        terminos = analizar(texto)
        cantidad += len(terminos)
        presentes += sum(t in vector.vocabulary_ for t in terminos)
    return presentes / cantidad if cantidad else 0.0


def evaluar_fold(train, val, externos):
    vector_a = TfidfVectorizer(**ANTERIOR.PARAMETROS_TFIDF)
    a = LogisticRegression(**ANTERIOR.PARAMETROS_LR).fit(
        vector_a.fit_transform(train.texto), train.es_relevante.astype(str).eq('1').astype(int))
    pred_a = a.predict(vector_a.transform(val.texto))
    resultados = {}
    for variante in VARIANTES:
        textos, etiquetas = componer_train_b(train, externos, variante)
        vector = TfidfVectorizer(**{**ANTERIOR.PARAMETROS_TFIDF, 'ngram_range': (1, 4)})
        b = LogisticRegression(**ANTERIOR.PARAMETROS_LR).fit(vector.fit_transform(textos), etiquetas)
        pred_b = b.predict(vector.transform(val.texto))
        conteo = Counter(etiquetas)
        dimensiones = {'n_train_b': len(textos), 'n_externos_b': 0 if variante == 'B0_base' else len(externos[externos.stance_label.ne('irrelevant')]),
                       'vocabulario_a': len(vector_a.vocabulary_), 'vocabulario_b': len(vector.vocabulary_),
                       'cobertura_rasgos_validacion': cobertura(vector, val.texto),
                       **{f'peso_clase_{c}': len(etiquetas)/(len(conteo)*conteo[c]) for c in ANTERIOR.L.CLASES}}
        resultados[variante] = (pred_a.copy(), pred_b, np.where(pred_a == 0, 'neutral', pred_b), dimensiones)
    return resultados


# ---- 4. Comparación y reporte; no elegir otra métrica tras conocer resultados ----
def resumir(predicciones, folds, tolerancias):
    filas = []
    base = predicciones[predicciones.variante.eq('B0_base')].set_index('intervencion_id')
    puntos_base = folds[folds.variante.eq('B0_base')].set_index('fold').macro_f1
    for variante in VARIANTES:
        sub = predicciones[predicciones.variante.eq(variante)].set_index('intervencion_id').loc[base.index]
        puntos = folds[folds.variante.eq(variante)].set_index('fold').macro_f1
        bien, bien_base = sub.pred.eq(sub.etiqueta), base.pred.eq(base.etiqueta)
        filas.append({'variante': variante, **ANTERIOR.metricas(sub.etiqueta, sub.pred),
            'macro_f1_media': float(puntos.mean()), 'macro_f1_sd': float(puntos.std(ddof=1)),
            'delta_media': float((puntos-puntos_base).mean()), 'folds_mejora': int((puntos>puntos_base).sum()),
            'errores': int((~bien).sum()), 'corregidos': int((~bien_base & bien).sum()), 'nuevos': int((bien_base & ~bien).sum()),
            'errores_hd': int((~bien & sub.etiqueta.isin(['hawkish','dovish']) & sub.pred.isin(['hawkish','dovish'])).sum()),
            'neutral_a_direccion': int((~bien & sub.etiqueta.eq('neutral')).sum()),
            'direccion_a_neutral': int((~bien & sub.pred.eq('neutral')).sum())})
    tabla = pd.DataFrame(filas)
    base = tabla.iloc[0]
    tabla['cumple_para_confirmar'] = (tabla.variante.eq('E2_espanol') &
        tabla.delta_media.ge(tolerancias['delta_media_minimo']) &
        tabla.folds_mejora.ge(tolerancias['folds_mejora_minimos']) &
        tabla.recall_hawkish.ge(base.recall_hawkish - tolerancias['perdida_recall_maxima']) &
        tabla.recall_dovish.ge(base.recall_dovish - tolerancias['perdida_recall_maxima']))
    return tabla


def construir_informe(tabla, resumen):
    es = tabla[tabla.variante.eq('E2_espanol')].iloc[0]
    lineas = ['# Piloto: añadir datos de WCB Chile al TF-IDF', '',
        f'**Mejor media observada: {resumen["mejor_observado"]}.** El entrenamiento con la traducción española cambia la media de macro-F1 en **{es.delta_media:+.4f}** respecto de la referencia.', '',
        '**Alcance: 100 frases externas seleccionadas, 99 utilizadas en B; no las 700 ni las 1.000 completas.** Se mantienen etiquetas WCB, sin armonizar con nuestro codebook. Traducción del agente IA, no español oficial ni revisión humana.', '',
        '## Diseño y procedencia', '',
        '[Protocolo congelado](PROTOCOLO_WCB_PILOTO_V1.md). [Datos, atribución, traducción y límites](../data/externos/wcb_chile_piloto_v1/README.md).',
        '- Primeras 100 filas de train 5768, fuente pública con revisión HF registrada. 28 H / 30 D / 41 N / 1 irrelevant. El único irrelevant se conserva en el archivo, pero no se utiliza para B. No se añade nada a A.',
        '- Mismos cinco folds IA: 793 intervenciones evaluadas y 559 adicionales solo en train. A unigramas fija compartida; B n-gramas 1–4, C=2/min_df=3. Vocabulario, IDF y regresión ajustados exclusivamente con el train de cada variante.',
        '- E1 incorpora los 99 textos ingleses como control. E2 incorpora los mismos ejemplos traducidos. Igual peso individual y etiquetas. Balanced se recalcula, por lo que cambia también el peso de las clases: el control inglés no es un efecto lingüístico puro.',
        '- No se descargó ni inspeccionó val/test externo. No se contaron las tres semillas como ejemplos distintos; sus solapes completos no se auditaron. No se abrió/predijo el gold humano.', '',
        '## Resultados sobre las mismas 793 intervenciones IA', '',
        '| Variante | Macro-F1 medio | DE | Delta base | Mejora folds | Macro-F1 conjunto | Accuracy |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in tabla.itertuples():
        lineas.append(f'| {r.variante} | {r.macro_f1_media:.4f} | {r.macro_f1_sd:.4f} | {r.delta_media:+.4f} | {r.folds_mejora}/5 | {r.macro_f1:.4f} | {r.accuracy:.4f} |')
    lineas += ['', '| Variante | F1 H | F1 D | Recall H | Recall D | Errores | H↔D | N→dirección | Dirección→N | Corregidos | Nuevos |',
               '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in tabla.itertuples():
        lineas.append(f'| {r.variante} | {r.f1_hawkish:.4f} | {r.f1_dovish:.4f} | {r.recall_hawkish:.4f} | {r.recall_dovish:.4f} | {r.errores} | {r.errores_hd} | {r.neutral_a_direccion} | {r.direccion_a_neutral} | {r.corregidos} | {r.nuevos} |')
    lineas += ['', '## Lectura y decisión', '',
        ('E2 cumple el umbral práctico prefijado para proponer confirmación separada; no demuestra mejora humana ni autoriza adopción.' if es.cumple_para_confirmar else 'E2 **no cumple** el criterio práctico prefijado para avanzar a confirmación. No adoptar esta importación ni ampliar tamaño/pesos después de ver el resultado.'),
        'El criterio exige ≥0,01 de mejora media, al menos tres folds mejores y pérdidas de recall H/D ≤0,02. No son pruebas de significación. La métrica principal se fijó antes de ajustar; no sustituirla por otra más favorable.',
        '**No equivale a descartar el dataset completo.** Solo se prueba esta muestra, traducción, combinación, peso y versión de etiquetas. Un resultado favorable también seguiría limitado por la evaluación IA reutilizada y por la traducción.', '',
        '## Compatibilidad y calidad', '',
        '- Diferencia de unidad: frases recientes de minutas frente a intervenciones completas históricas. Los fragmentos pueden depender de antecedentes ausentes.',
        '- Diferencia de criterio: WCB asigna D a una frase de recesión argentina (source_id 217) y H a una subida de la Fed (434), mientras nuestro R3 requiere vínculo con política doméstica. También hay diagnósticos de consumo etiquetados D sin recomendación explícita. No se corrigieron etiquetas ni se eligieron solo los ejemplos convenientes.',
        '- El esquema publicado no incluye enlace directo por fila al español oficial. No se realizó alineación con originales. La traducción fue realizada por el agente que pudo ver las etiquetas; no es una revisión independiente y puede introducir sesgos.',
        '- Se verificó que cifras/signos y cantidad de porcentajes se conservaran; no hay duplicados exactos normalizados dentro de la muestra ni contra las 1.352 IA. Esto no certifica traducción ni excluye duplicados semánticos.',
        '- Captura local de columnas desde la respuesta de API, no copia binaria Parquet verificada independientemente. La respuesta no quedó fijada por revisión; se registra el SHA observado de la ficha y el hash de la muestra congelada. Persisten riesgos de transcripción.',
        '- Licencia de los datos externos y su traducción: CC BY-NC-SA 4.0, atribuida en su carpeta. No se mezclaron con anotaciones canónicas ni se guardaron modelos derivados.', '',
        '## Controles y límites de evaluación', '',
        '- B0 reproduce exactamente las 793 predicciones históricas de (1,4); A da idénticas predicciones entre variantes. No se sustituye el modelo unigramas guardado del examen humano.',
        '- Persisten 34 textos IA repetidos con su train, aunque reuniones disjuntas. La comparación es desarrollo adaptativo, no test independiente; los folds comparten training y externos.',
        '- Usar texto de 2018–2024 para evaluar 2005–2015 es un experimento retrospectivo; no una demostración de pronóstico histórico sin información futura.',
        '- No se reajustó con todas las 1.352 ni se puntuó el corpus completo. La repetición y los tests se registran después en `reproducibilidad.json`; no prueban la exactitud de la traducción.', '',
        '## Archivos y repetición', '',
        '`data/evaluacion/wcb_chile_piloto_v1/`: protocolo previo, auditoría de la muestra, asignaciones, 2.379 predicciones, 15 resultados por fold, comparación, matrices, tiempos y manifiesto. Las tablas contienen soporte por clase, vocabulario, cobertura de ocurrencias de rasgos (no comprensión semántica) y pesos de clases.', '',
        '```bash', 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/25_evaluar_wcb_piloto.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/25_evaluar_wcb_piloto.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md', '```', '']
    return '\n'.join(lineas)


# ---- 5. Ejecución protegida y salidas nuevas, nunca modelos persistidos ----
def ejecutar(salida=RUTA_SALIDA, informe=RUTA_INFORME):
    salida, informe = Path(salida), Path(informe)
    protocolo = verificar_protocolo(salida)
    assert {p.name for p in salida.iterdir()} == {'protocolo.json','asignacion_folds.csv','auditoria_externos.json'}, 'Carpeta ya ejecutada o parcial'
    exigir_salidas_nuevas(informe)
    datos, mascara, anteriores, _ = LONGITUD.cargar_insumos()
    externos = pd.read_csv(RUTA_EXTERNOS / 'muestra.tsv', sep='\t', keep_default_na=False)
    auditar_externos(externos, datos)
    particiones, asignacion = LONGITUD.asignar_folds(datos, mascara)
    pd.testing.assert_frame_equal(asignacion, pd.read_csv(salida / 'asignacion_folds.csv'))
    predicciones, registros, tiempos = [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        for numero, tr, va in particiones:
            inicio = time.perf_counter()
            resultados = evaluar_fold(datos.iloc[tr], datos.iloc[va], externos)
            tiempos.append({'fold':numero,'segundos':time.perf_counter()-inicio})
            for variante, (pa, pb, pred, dimensiones) in resultados.items():
                sub = datos.iloc[va][['intervencion_id','meeting_id','etiqueta','es_relevante']].copy()
                sub['fold'],sub['variante'],sub['pred_a'],sub['pred_b'],sub['pred'] = numero,variante,pa,pb,pred
                predicciones.append(sub)
                fila = {'fold':numero,'variante':variante,'n_train_ia':len(tr),'n_validacion':len(va),
                        **dimensiones,**ANTERIOR.metricas(sub.etiqueta,sub.pred)}
                registros.append(fila)
                print(f'Fold {numero} {variante}: macro-F1={fila["macro_f1"]:.6f}',flush=True)
    predicciones, folds = pd.concat(predicciones,ignore_index=True), pd.DataFrame(registros)
    assert len(predicciones)==2379 and not predicciones.duplicated(['intervencion_id','variante']).any()
    assert predicciones.groupby('intervencion_id').pred_a.nunique().eq(1).all()
    columnas = ['intervencion_id','meeting_id','etiqueta','fold','pred']
    pd.testing.assert_frame_equal(predicciones[predicciones.variante.eq('B0_base')][columnas].reset_index(drop=True),
                                  anteriores[anteriores.variante.eq('ngramas_1_4')][columnas].reset_index(drop=True))
    tabla = resumir(predicciones,folds,protocolo['tolerancias'])
    resumen = {'mejor_observado':tabla.sort_values('macro_f1_media',ascending=False,kind='stable').iloc[0].variante,
               'espanol_cumple':bool(tabla.set_index('variante').loc['E2_espanol','cumple_para_confirmar']),
               'clases':ANTERIOR.L.CLASES,
               'matrices':{v:confusion_matrix(s.etiqueta,s.pred,labels=ANTERIOR.L.CLASES).tolist() for v,s in predicciones.groupby('variante')},
               'n_externos':len(externos),'n_externos_b':int(externos.stance_label.ne('irrelevant').sum()),
               'ancla_base_identica':True,'textos_ia_repetidos_train':int(asignacion.texto_identico_en_train.sum()),
               'gold_abierto_o_predicho':False,'test_externo_abierto':False,'refit_final_o_reemplazo':False}
    for nombre, contenido in [('predicciones_validacion',predicciones),('resultados_folds',folds),('comparacion_variantes',tabla)]:
        contenido.to_csv(salida / (nombre+'.csv'),index=False)
    ESCRIBIR(salida / 'metricas.json',resumen)
    ESCRIBIR(salida / 'tiempos.json',tiempos)
    verificar_protocolo(salida)
    informe.parent.mkdir(parents=True,exist_ok=True)
    with informe.open('x',encoding='utf-8') as archivo:
        archivo.write(construir_informe(tabla,resumen))
    ESCRIBIR(salida / 'manifest.json',{'fecha_fin_utc':datetime.now(timezone.utc).isoformat(),
        'sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},'sha256_informe':sha256(informe)})
    print(tabla[['variante','macro_f1_media','delta_media','cumple_para_confirmar']].to_string(index=False))
    return resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    accion = parser.add_mutually_exclusive_group(required=True)
    accion.add_argument('--preparar',action='store_true')
    accion.add_argument('--ejecutar',action='store_true')
    parser.add_argument('--salida',type=Path,default=RUTA_SALIDA)
    parser.add_argument('--informe',type=Path,default=RUTA_INFORME)
    args=parser.parse_args()
    (preparar if args.preparar else ejecutar)(args.salida,args.informe)


if __name__=='__main__':
    main()
