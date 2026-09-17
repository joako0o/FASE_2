"""Fase B: reentrena el TF-IDF histórico con supervisión v3 en los folds fijados."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import platform
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer, strip_accents_unicode
from sklearn.linear_model import LogisticRegression

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / 'data/evaluacion/tfidf_supervision_v3_fase_b'
CLASES = ['hawkish', 'dovish', 'neutral']
PARAMETROS_A = {'strip_accents': 'unicode', 'lowercase': True, 'ngram_range': (1, 1),
                'min_df': 3, 'max_df': .9, 'sublinear_tf': True}
PARAMETROS_B = {**PARAMETROS_A, 'ngram_range': (1, 4)}
PARAMETROS_LR = {'class_weight': 'balanced', 'max_iter': 2000,
                 'random_state': 20260915, 'C': 2.0}


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def clave_texto(texto):
    return strip_accents_unicode(' '.join(str(texto).split()).lower())


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write('\n')


def division(a, b):
    return a / b if b else 0.0


def medir(reales, predichas):
    matriz = [[sum(r == real and p == pred for r, p in zip(reales, predichas))
               for pred in CLASES] for real in CLASES]
    por_clase = {}
    for i, clase in enumerate(CLASES):
        vp, soporte = matriz[i][i], sum(matriz[i])
        total_predicho = sum(fila[i] for fila in matriz)
        precision, recall = division(vp, total_predicho), division(vp, soporte)
        por_clase[clase] = {'precision': precision, 'recall': recall,
                            'f1': division(2 * precision * recall, precision + recall),
                            'soporte': soporte}
    return {
        'filas': len(reales),
        'accuracy': division(sum(a == b for a, b in zip(reales, predichas)), len(reales)),
        'macro_f1': sum(por_clase[c]['f1'] for c in CLASES) / 3,
        'f1_hd': (por_clase['hawkish']['f1'] + por_clase['dovish']['f1']) / 2,
        'por_clase': por_clase,
        'matriz_orden_h_d_n': matriz,
        'errores': sum(a != b for a, b in zip(reales, predichas)),
        'h_d_cruzados': matriz[0][1] + matriz[1][0],
        'direccion_a_neutral': matriz[0][2] + matriz[1][2],
        'neutral_a_direccion': matriz[2][0] + matriz[2][1],
    }


def metricas_completas(tabla, prediccion):
    resultado = medir(tabla.etiqueta_v3.tolist(), tabla[prediccion].tolist())
    por_fold = {}
    for fold, grupo in tabla.groupby('fold', sort=True):
        por_fold[str(fold)] = medir(grupo.etiqueta_v3.tolist(), grupo[prediccion].tolist())
    resultado['media_folds_f1_hd'] = sum(x['f1_hd'] for x in por_fold.values()) / 5
    resultado['media_folds_macro_f1'] = sum(x['macro_f1'] for x in por_fold.values()) / 5
    resultado['por_fold'] = por_fold
    return resultado


def cargar_datos():
    rutas = {
        'corpus': RAIZ/'data/L0/corpus.csv',
        'referencia_v3': RAIZ/'data/evaluacion/referencia_v3/referencia_v3.csv',
        'referencia_v2': RAIZ/'data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv',
        'folds': RAIZ/'data/evaluacion/clasificadores_hd_v1/asignacion_folds.csv',
        'predicciones_historicas': RAIZ/'data/evaluacion/referencias_corregidas_v2/predicciones_validacion.csv',
        'protocolo_historico': RAIZ/'data/evaluacion/referencias_corregidas_v2/protocolo.json',
        'protocolo_v3': RAIZ/'docs/PROTOCOLO_COMPARACION_V3.md',
        'script_fase_b': Path(__file__),
        'requirements': RAIZ/'requirements.txt',
    }
    corpus = pd.read_csv(rutas['corpus'], dtype=str, keep_default_na=False).set_index('intervencion_id')
    referencia = pd.read_csv(rutas['referencia_v3'], dtype=str, keep_default_na=False)
    referencia = referencia[referencia.coleccion.eq('ia_base_v2')].set_index('intervencion_id')
    v2 = pd.read_csv(rutas['referencia_v2'], dtype=str, keep_default_na=False).set_index('intervencion_id')
    folds = pd.read_csv(rutas['folds'], dtype={'fold_validacion': int}).set_index('intervencion_id')
    congeladas = pd.read_csv(rutas['predicciones_historicas'], dtype=str, keep_default_na=False)
    congeladas = congeladas[congeladas.supervision.eq('seis_mas_trece')].set_index('intervencion_id')
    ids = list(referencia.index)
    if len(ids) != len(set(ids)) or len(ids) != 1352:
        raise ValueError('La cohorte IA base v3 debe tener 1.352 IDs únicos')
    if not set(ids) <= set(corpus.index) & set(v2.index) & set(folds.index):
        raise ValueError('ID IA base ausente en una fuente histórica')
    datos = corpus.loc[ids, ['meeting_id', 'texto']].copy()
    datos['etiqueta_v2'] = v2.loc[ids, 'etiqueta_corregida_v2']
    datos['relevancia_v2'] = v2.loc[ids, 'es_relevante']
    datos['etiqueta_v3'] = referencia.loc[ids, 'etiqueta_v3']
    datos['relevancia_v3'] = referencia.loc[ids, 'es_relevante_v3']
    datos['fold_validacion'] = folds.loc[ids, 'fold_validacion']
    datos['intervencion_id'] = datos.index
    hashes_texto = datos.texto.map(lambda x: hashlib.sha256(x.encode()).hexdigest())
    if not hashes_texto.equals(referencia.loc[ids, 'sha256_texto']):
        raise ValueError('El texto del corpus no coincide con la referencia v3')
    if not (datos.etiqueta_v2.equals(referencia.loc[ids, 'etiqueta_previa_v3']) and
            datos.relevancia_v2.equals(referencia.loc[ids, 'es_relevante_previa_v3'])):
        raise ValueError('La capa previa de v3 no coincide con la referencia histórica v2')
    protocolo = json.loads(rutas['protocolo_historico'].read_text(encoding='utf-8'))
    parametros_a = {**protocolo['parametros_a'], 'ngram_range': tuple(protocolo['parametros_a']['ngram_range'])}
    parametros_b = {**protocolo['parametros_b'], 'ngram_range': tuple(protocolo['parametros_b']['ngram_range'])}
    if (parametros_a, parametros_b, protocolo['parametros_lr']) != (PARAMETROS_A, PARAMETROS_B, PARAMETROS_LR):
        raise ValueError('Los parámetros no coinciden con el protocolo histórico')
    if Counter(datos.fold_validacion) != Counter({0: 559, 1: 158, 2: 159, 3: 159, 4: 159, 5: 158}):
        raise ValueError('Asignación histórica de folds distinta')
    if len(congeladas) != 793 or set(congeladas.index) != set(datos.loc[datos.fold_validacion.gt(0)].index):
        raise ValueError('Predicciones congeladas no coinciden con validación')
    return datos, congeladas, rutas


def ajustar_predecir(train, val, version):
    vector_a = TfidfVectorizer(**PARAMETROS_A)
    modelo_a = LogisticRegression(**PARAMETROS_LR).fit(
        vector_a.fit_transform(train.texto), train['relevancia_'+version].astype(int))
    pred_a = modelo_a.predict(vector_a.transform(val.texto))
    relevantes = train['relevancia_'+version].eq('1')
    vector_b = TfidfVectorizer(**PARAMETROS_B)
    modelo_b = LogisticRegression(**PARAMETROS_LR).fit(
        vector_b.fit_transform(train.loc[relevantes, 'texto']),
        train.loc[relevantes, 'etiqueta_'+version])
    pred_b = modelo_b.predict(vector_b.transform(val.texto))
    final = np.where(pred_a == 0, 'neutral', pred_b)
    dimensiones = {
        'n_train': len(train), 'n_train_relevante': int(relevantes.sum()),
        'clases_train': train['etiqueta_'+version].value_counts().to_dict(),
        'relevancia_train': train['relevancia_'+version].value_counts().to_dict(),
        'vocabulario_a': len(vector_a.vocabulary_), 'vocabulario_b': len(vector_b.vocabulary_),
        'iteraciones_a': modelo_a.n_iter_.tolist(), 'iteraciones_b': modelo_b.n_iter_.tolist(),
    }
    return pred_a, pred_b, final, dimensiones


def ejecutar(salida=SALIDA):
    salida = Path(salida)
    nombres = ['predicciones.csv', 'comparacion_casos.csv', 'errores_fase_b.csv', 'metricas.json',
               'ejecucion_folds.json', 'protocolo.json', 'resumen.md', 'verificacion.json', 'manifest.json']
    if salida.exists() or any((salida/n).exists() for n in nombres):
        raise FileExistsError('No sobrescribir la fase B v3')
    datos, congeladas, rutas = cargar_datos()
    predicciones, ejecuciones = [], []
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        for fold in range(1, 6):
            val = datos[datos.fold_validacion.eq(fold)].copy()
            train_previo = datos[~datos.fold_validacion.eq(fold)].copy()
            claves_val = set(val.texto.map(clave_texto))
            train = train_previo[~train_previo.texto.map(clave_texto).isin(claves_val)].copy()
            if set(train.meeting_id) & set(val.meeting_id) or set(train.texto.map(clave_texto)) & claves_val:
                raise ValueError(f'Contaminación de train en fold {fold}')
            resultados = {}
            for version in ['v2', 'v3']:
                a, b, final, dimensiones = ajustar_predecir(train, val, version)
                resultados[version] = (a, b, final)
                ejecuciones.append({'fold': fold, 'supervision': version,
                                    'n_train_antes_purga': len(train_previo),
                                    'n_retirados_copia': len(train_previo)-len(train),
                                    'n_validacion': len(val), **dimensiones})
            a2, b2, p2 = resultados['v2']
            ancla = congeladas.loc[val.index]
            if not (np.array_equal(a2.astype(str), ancla.pred_a.to_numpy()) and
                    np.array_equal(b2.astype(str), ancla.pred_b.to_numpy()) and
                    np.array_equal(p2.astype(str), ancla.pred.to_numpy())):
                raise ValueError(f'No se reprodujo exactamente el modelo histórico en fold {fold}')
            a3, b3, p3 = resultados['v3']
            for i, (_, fila) in enumerate(val.iterrows()):
                predicciones.append({
                    'intervencion_id': fila.intervencion_id, 'meeting_id': fila.meeting_id,
                    'fold': fold, 'etiqueta_v3': fila.etiqueta_v3,
                    'es_relevante_v3': fila.relevancia_v3,
                    'pred_a_historica': str(a2[i]), 'pred_b_historica': b2[i],
                    'pred_historica': p2[i], 'pred_a_v3': str(a3[i]),
                    'pred_b_v3': b3[i], 'pred_v3': p3[i],
                })
            print(f'Fold {fold}: ancla v2 exacta; entrenamiento v3 terminado.', flush=True)
    tabla = pd.DataFrame(predicciones).sort_values(['fold', 'intervencion_id']).reset_index(drop=True)
    tabla['cambio_pred_a'] = tabla.pred_a_historica.ne(tabla.pred_a_v3)
    tabla['cambio_pred_b'] = tabla.pred_b_historica.ne(tabla.pred_b_v3)
    tabla['cambio_pred_final'] = tabla.pred_historica.ne(tabla.pred_v3)
    tabla['acierto_fase_a'] = tabla.pred_historica.eq(tabla.etiqueta_v3)
    tabla['acierto_fase_b'] = tabla.pred_v3.eq(tabla.etiqueta_v3)
    tabla['efecto_reentrenamiento'] = np.select(
        [tabla.acierto_fase_a & ~tabla.acierto_fase_b, ~tabla.acierto_fase_a & tabla.acierto_fase_b],
        ['acierto_a_error', 'error_a_acierto'], default='sin_cambio')
    fase_a, fase_b = metricas_completas(tabla, 'pred_historica'), metricas_completas(tabla, 'pred_v3')
    metricas = {
        'version': salida.name, 'fase': 'B_supervision_v3', 'n_ia_base': 1352, 'n_validacion': 793,
        'fase_a_congelada_contra_v3': fase_a, 'fase_b_reentrenada_contra_v3': fase_b,
        'delta_b_menos_a': {k: fase_b[k]-fase_a[k] for k in
                            ['accuracy', 'macro_f1', 'f1_hd', 'media_folds_f1_hd', 'errores']},
        'predicciones_finales_cambiadas': int(tabla.cambio_pred_final.sum()),
        'predicciones_relevancia_cambiadas': int(tabla.cambio_pred_a.sum()),
        'predicciones_clase_cambiadas': int(tabla.cambio_pred_b.sum()),
        'efecto_en_aciertos': dict(Counter(tabla.efecto_reentrenamiento)),
        'evaluacion_independiente': False, 'modelo_persistido': False,
        'ia_nueva_89_incluida': False, 'pre2000_incluido': False, 'sinteticos_incluidos': False,
    }
    salida.mkdir(parents=True)
    tabla.to_csv(salida/'predicciones.csv', index=False, lineterminator='\n')
    cambios = tabla[tabla.cambio_pred_final].copy()
    cambios.to_csv(salida/'comparacion_casos.csv', index=False, lineterminator='\n')
    errores = tabla[~tabla.acierto_fase_b].copy()
    errores['tipo_error'] = np.where(
        ((errores.etiqueta_v3.eq('hawkish') & errores.pred_v3.eq('dovish')) |
         (errores.etiqueta_v3.eq('dovish') & errores.pred_v3.eq('hawkish'))), 'inversion_h_d',
        np.where(errores.etiqueta_v3.eq('neutral'), 'neutral_a_direccion', 'direccion_a_neutral'))
    errores.to_csv(salida/'errores_fase_b.csv', index=False, lineterminator='\n')
    guardar_json(salida/'metricas.json', metricas)
    guardar_json(salida/'ejecucion_folds.json', ejecuciones)
    guardar_json(salida/'protocolo.json', {
        'operacion': 'Mismos 1.352 IDs, folds, purga, arquitectura, parámetros y selección histórica; solo supervisión v3.',
        'parametros_a': PARAMETROS_A, 'parametros_b': PARAMETROS_B, 'parametros_lr': PARAMETROS_LR,
        'regla_final': 'neutral si puerta de relevancia A=0; en otro caso predicción multiclase B',
        'fuentes_sha256': {nombre: sha256(ruta) for nombre, ruta in rutas.items()},
        'python': platform.python_version(), 'numpy': np.__version__,
        'pandas': pd.__version__, 'sklearn': sklearn.__version__,
        'busqueda_hiperparametros': False, 'refit_global': False,
    })
    guardar_json(salida/'verificacion.json', {
        'ancla_v2_reproducida_exactamente_793': True,
        'conteos_train_por_fold': [x['n_train'] for x in ejecuciones if x['supervision']=='v3'],
        'conteos_validacion_por_fold': [x['n_validacion'] for x in ejecuciones if x['supervision']=='v3'],
        'ids_validacion_unicos': tabla.intervencion_id.nunique(),
        'sin_reuniones_ni_copias_train_validacion': True,
        'entrenamiento_v3_ejecutado': True,
    })
    resumen = "# Fase B — TF-IDF reentrenado con supervisión v3\n\n"
    resumen += "Se conservaron los 1.352 IDs IA-base, 793 validaciones, cinco folds, purga, arquitectura y parámetros históricos. Solo cambió etiqueta/relevancia de supervisión a v3. El ancla v2 se reprodujo exactamente antes del ajuste v3.\n\n"
    resumen += "| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for nombre, m in [('A congelada→v3', fase_a), ('B entrenada v3→v3', fase_b)]:
        resumen += f"| {nombre} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    resumen += "\nEsta sigue siendo evaluación de desarrollo reutilizada, no una prueba independiente. No se añadieron las 89 IA nuevas, pre-2000 ni sintéticos.\n"
    with (salida/'resumen.md').open('x', encoding='utf-8') as archivo:
        archivo.write(resumen)
    guardar_json(salida/'manifest.json', {'sha256_salidas': {
        nombre: sha256(salida/nombre) for nombre in nombres if nombre != 'manifest.json'}})
    return metricas


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, default=SALIDA)
    args = parser.parse_args()
    print(json.dumps(ejecutar(args.salida), ensure_ascii=False, indent=2))
