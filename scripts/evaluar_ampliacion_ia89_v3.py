"""Fase C: compara TF-IDF v3 base contra ampliación separada con 89 IA nuevas."""
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

from entrenar_tfidf_supervision_v3 import (
    RAIZ, ajustar_predecir, cargar_datos, clave_texto, metricas_completas, sha256)

SALIDA = RAIZ/'data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c'


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write('\n')


def cargar_nuevos():
    ref_path = RAIZ/'data/evaluacion/referencia_v3/referencia_v3.csv'
    corpus_path = RAIZ/'data/L0/corpus.csv'
    referencia = pd.read_csv(ref_path, dtype=str, keep_default_na=False)
    referencia = referencia[referencia.coleccion.eq('ia_nueva_v1')].set_index('intervencion_id')
    corpus = pd.read_csv(corpus_path, dtype=str, keep_default_na=False).set_index('intervencion_id')
    if len(referencia) != 89 or not referencia.index.is_unique or not set(referencia.index) <= set(corpus.index):
        raise ValueError('Se esperaban 89 IA nuevas únicas presentes en L0')
    nuevos = corpus.loc[referencia.index, ['meeting_id', 'texto']].copy()
    nuevos['etiqueta_v3'] = referencia.etiqueta_v3
    nuevos['relevancia_v3'] = referencia.es_relevante_v3
    nuevos['intervencion_id'] = nuevos.index
    hashes = nuevos.texto.map(lambda x: hashlib.sha256(x.encode()).hexdigest())
    if not hashes.equals(referencia.sha256_texto):
        raise ValueError('Texto de IA nueva distinto de referencia v3')
    if Counter(nuevos.etiqueta_v3) != Counter({'dovish': 34, 'hawkish': 30, 'neutral': 25}):
        raise ValueError('Distribución IA nueva distinta')
    if set(nuevos.relevancia_v3) != {'1'}:
        raise ValueError('Las 89 IA nuevas debían ser relevantes')
    return nuevos, {'referencia_v3': ref_path, 'corpus': corpus_path}


def ejecutar(salida=SALIDA):
    salida = Path(salida)
    nombres = ['predicciones.csv', 'comparacion_casos.csv', 'errores_fase_c.csv',
               'inclusion_ia89_por_fold.csv', 'metricas.json', 'ejecucion_folds.json',
               'protocolo.json', 'resumen.md', 'verificacion.json', 'manifest.json']
    if salida.exists():
        raise FileExistsError('No sobrescribir la fase C v3')
    base, _, fuentes_base = cargar_datos()
    nuevos, fuentes_nuevos = cargar_nuevos()
    fase_b_path = RAIZ/'data/evaluacion/tfidf_supervision_v3_fase_b/predicciones.csv'
    fase_b = pd.read_csv(fase_b_path, dtype=str, keep_default_na=False).set_index('intervencion_id')
    if len(fase_b) != 793 or not fase_b.index.is_unique:
        raise ValueError('Ancla fase B inválida')
    predicciones, auditoria, ejecuciones = [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy()
            train_previo = base[~base.fold_validacion.eq(fold)].copy()
            claves_val = set(val.texto.map(clave_texto))
            train = train_previo[~train_previo.texto.map(clave_texto).isin(claves_val)].copy()
            extra = nuevos.copy()
            extra['excluir_reunion'] = extra.meeting_id.isin(set(val.meeting_id))
            extra['excluir_texto'] = extra.texto.map(clave_texto).isin(claves_val)
            extra['incluido'] = ~(extra.excluir_reunion | extra.excluir_texto)
            extra['fold'] = fold
            auditoria.append(extra[['fold', 'intervencion_id', 'meeting_id', 'etiqueta_v3',
                                    'excluir_reunion', 'excluir_texto', 'incluido']])
            incluidos = extra[extra.incluido].copy()
            ampliado = pd.concat([train, incluidos.reindex(columns=train.columns)], ignore_index=True)
            resultados = {}
            for condicion, conjunto in [('fase_b_base', train), ('fase_c_mas_89', ampliado)]:
                a, b, final, dimensiones = ajustar_predecir(conjunto, val, 'v3')
                resultados[condicion] = (a, b, final)
                ejecuciones.append({'fold': fold, 'condicion': condicion,
                                    'n_ia_nueva_incluida': 0 if condicion=='fase_b_base' else len(incluidos),
                                    'ia_nueva_por_clase': {} if condicion=='fase_b_base' else incluidos.etiqueta_v3.value_counts().to_dict(),
                                    **dimensiones})
            a0, b0, p0 = resultados['fase_b_base']
            ancla = fase_b.loc[val.index]
            if not (np.array_equal(a0.astype(str), ancla.pred_a_v3.to_numpy()) and
                    np.array_equal(b0.astype(str), ancla.pred_b_v3.to_numpy()) and
                    np.array_equal(p0.astype(str), ancla.pred_v3.to_numpy())):
                raise ValueError(f'No se reprodujo fase B en fold {fold}')
            a1, b1, p1 = resultados['fase_c_mas_89']
            for i, (_, fila) in enumerate(val.iterrows()):
                predicciones.append({
                    'intervencion_id': fila.intervencion_id, 'meeting_id': fila.meeting_id,
                    'fold': fold, 'etiqueta_v3': fila.etiqueta_v3,
                    'es_relevante_v3': fila.relevancia_v3,
                    'pred_a_fase_b': str(a0[i]), 'pred_b_fase_b': b0[i], 'pred_fase_b': p0[i],
                    'pred_a_fase_c': str(a1[i]), 'pred_b_fase_c': b1[i], 'pred_fase_c': p1[i],
                })
            print(f'Fold {fold}: fase B exacta; +{len(incluidos)} IA nuevas.', flush=True)
    tabla = pd.DataFrame(predicciones).sort_values(['fold', 'intervencion_id']).reset_index(drop=True)
    tabla['cambio_pred_a'] = tabla.pred_a_fase_b.ne(tabla.pred_a_fase_c)
    tabla['cambio_pred_b'] = tabla.pred_b_fase_b.ne(tabla.pred_b_fase_c)
    tabla['cambio_pred_final'] = tabla.pred_fase_b.ne(tabla.pred_fase_c)
    tabla['acierto_b'] = tabla.pred_fase_b.eq(tabla.etiqueta_v3)
    tabla['acierto_c'] = tabla.pred_fase_c.eq(tabla.etiqueta_v3)
    tabla['efecto_ampliacion'] = np.select(
        [tabla.acierto_b & ~tabla.acierto_c, ~tabla.acierto_b & tabla.acierto_c],
        ['acierto_a_error', 'error_a_acierto'], default='sin_cambio')
    bmet, cmet = metricas_completas(tabla.rename(columns={'pred_fase_b':'pred_b_eval'}), 'pred_b_eval'), metricas_completas(tabla.rename(columns={'pred_fase_c':'pred_c_eval'}), 'pred_c_eval')
    metricas = {
        'version': salida.name, 'fase': 'C_ampliacion_89_ia_reales_v3',
        'fase_b_base': bmet, 'fase_c_mas_89': cmet,
        'delta_c_menos_b': {k: cmet[k]-bmet[k] for k in
                            ['accuracy', 'macro_f1', 'f1_hd', 'media_folds_f1_hd', 'errores']},
        'predicciones_finales_cambiadas': int(tabla.cambio_pred_final.sum()),
        'predicciones_relevancia_cambiadas': int(tabla.cambio_pred_a.sum()),
        'predicciones_clase_cambiadas': int(tabla.cambio_pred_b.sum()),
        'efecto_en_aciertos': dict(Counter(tabla.efecto_ampliacion)),
        'n_ia_nueva_total': 89,
        'n_ia_nueva_por_fold': [int(x.incluido.sum()) for x in auditoria],
        'evaluacion_independiente': False, 'modelo_persistido': False,
        'pre2000_incluido': False, 'sinteticos_incluidos': False,
    }
    salida.mkdir(parents=True)
    tabla.to_csv(salida/'predicciones.csv', index=False, lineterminator='\n')
    tabla[tabla.cambio_pred_final].to_csv(salida/'comparacion_casos.csv', index=False, lineterminator='\n')
    errores = tabla[~tabla.acierto_c].copy()
    errores['tipo_error'] = np.where(
        ((errores.etiqueta_v3.eq('hawkish') & errores.pred_fase_c.eq('dovish')) |
         (errores.etiqueta_v3.eq('dovish') & errores.pred_fase_c.eq('hawkish'))), 'inversion_h_d',
        np.where(errores.etiqueta_v3.eq('neutral'), 'neutral_a_direccion', 'direccion_a_neutral'))
    errores.to_csv(salida/'errores_fase_c.csv', index=False, lineterminator='\n')
    pd.concat(auditoria, ignore_index=True).to_csv(salida/'inclusion_ia89_por_fold.csv', index=False, lineterminator='\n')
    guardar_json(salida/'metricas.json', metricas)
    guardar_json(salida/'ejecucion_folds.json', ejecuciones)
    fuentes = {**fuentes_base, **fuentes_nuevos, 'fase_b_predicciones': fase_b_path,
               'script_fase_c': Path(__file__)}
    guardar_json(salida/'protocolo.json', {
        'operacion': 'Añadir solo las 89 IA nuevas v3 al train permitido de cada fold; fase B inalterada.',
        'purga': 'Excluir IA nueva con reunión o texto normalizado presente en validación.',
        'busqueda_hiperparametros': False, 'validacion_real_sin_cambios': True,
        'fuentes_sha256': {nombre: sha256(ruta) for nombre, ruta in fuentes.items()},
        'python': platform.python_version(), 'numpy': np.__version__,
        'pandas': pd.__version__, 'sklearn': sklearn.__version__,
    })
    guardar_json(salida/'verificacion.json', {
        'fase_b_reproducida_exactamente_793': True,
        'ids_validacion_unicos': tabla.intervencion_id.nunique(),
        'ids_ia_nueva_unicos': nuevos.intervencion_id.nunique(),
        'incluidos_por_fold': metricas['n_ia_nueva_por_fold'],
        'copias_textuales_incluidas': 0, 'reuniones_validacion_incluidas': 0,
        'ia_nueva_no_usada_en_validacion': True,
    })
    resumen = "# Fase C — ampliación TF-IDF v3 con 89 IA reales\n\n"
    resumen += "La fase B se reprodujo exactamente. Las 89 IA nuevas entraron solo al train permitido después de purga por reunión/texto; la validación sigue siendo la misma colección real de 793 IDs.\n\n"
    resumen += "| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for nombre, m in [('B base v3', bmet), ('C base+89', cmet)]:
        resumen += f"| {nombre} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    resumen += "\nNo es una evaluación independiente. No se usaron datos sintéticos ni pre-2000.\n"
    with (salida/'resumen.md').open('x', encoding='utf-8') as archivo:
        archivo.write(resumen)
    guardar_json(salida/'manifest.json', {'sha256_salidas': {
        nombre: sha256(salida/nombre) for nombre in nombres if nombre != 'manifest.json'}})
    return metricas


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, default=SALIDA)
    print(json.dumps(ejecutar(parser.parse_args().salida), ensure_ascii=False, indent=2))
