"""Aplicar 13 correcciones aceptadas y separar referencia de entrenamiento.

Dos supervisiones TF-IDF, dos referencias de desarrollo y ninguna búsqueda.
No modifica resultados históricos, no abre respuestas de 306 ni ejecuta BETO.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import confusion_matrix

from utilidades import cargar_script, exigir_salidas_nuevas, sha256

PREV = cargar_script('31_evaluar_adjudicacion.py')
H = PREV.H
RAIZ = Path(__file__).resolve().parents[1]
AUDITORIA = RAIZ/'data/auditoria/revision_errores_adjudicada_v1'
ACEPTACION = AUDITORIA/'adjudicacion_cierre_66_v1/aceptacion.json'
PROPUESTAS = AUDITORIA/'tanda_4_largos_v1/resultados/revision_consolidada.csv'
SALIDA = RAIZ/'data/evaluacion/referencias_corregidas_v2'
PROTOCOLO = RAIZ/'docs/PROTOCOLO_REFERENCIAS_CORREGIDAS_V2.md'
INFORME = RAIZ/'docs/EVALUACION_REFERENCIAS_CORREGIDAS_V2.md'
SUPERVISIONES = ('seis_previas', 'seis_mas_trece')
REFERENCIAS = ('ia_original', 'corregida_v2')
escribir_json = PREV.escribir_json


def aplicar_correcciones(datos, asignacion, correcciones):
    """Vista nueva: validar ID/etiqueta/hash y no alterar texto o relevancia."""
    assert datos.intervencion_id.is_unique and asignacion.intervencion_id.is_unique
    assert correcciones.intervencion_id.is_unique
    assert set(datos.intervencion_id) == set(asignacion.intervencion_id)
    assert correcciones.etiqueta_corregida.isin(H.CLASES).all()
    filas = datos.set_index('intervencion_id')
    folds = asignacion.set_index('intervencion_id').fold_validacion
    salida = datos.copy(deep=True)
    for r in correcciones.itertuples():
        assert r.intervencion_id in filas.index, 'ID ajeno a desarrollo'
        f = filas.loc[r.intervencion_id]
        assert folds.loc[r.intervencion_id] in {1, 2, 3, 4, 5}, 'Esta capa es la revisión de validación'
        assert str(f.es_relevante) == '1', 'No adjudicar relevancia'
        assert f.etiqueta == r.etiqueta_ia_original, 'Etiqueta de origen discordante'
        assert r.etiqueta_corregida != r.etiqueta_ia_original
        assert hashlib.sha256(f.texto.encode()).hexdigest() == r.sha256_texto, 'Texto discordante'
        salida.loc[salida.intervencion_id.eq(r.intervencion_id), 'etiqueta'] = r.etiqueta_corregida
    pd.testing.assert_frame_equal(datos.drop(columns='etiqueta'), salida.drop(columns='etiqueta'))
    ids_cambiados = set(datos.loc[datos.etiqueta.ne(salida.etiqueta), 'intervencion_id'])
    assert ids_cambiados == set(correcciones.intervencion_id)
    return salida


def cargar():
    PREV.verificar_preparacion(PREV.SALIDA)
    manifest = json.loads((PREV.SALIDA/'manifest.json').read_text())
    for nombre, huella in manifest['sha256_salidas'].items():
        assert sha256(PREV.SALIDA/nombre) == huella, nombre
    aceptacion = json.loads(ACEPTACION.read_text())
    assert aceptacion['estado'] == 'aprobada_por_investigador'
    assert aceptacion['mensaje_usuario'] == 'corrige las referencias, e ittenta mandar el modelo en tu entorno'
    assert aceptacion['continuacion_usuario'] == 'sigue'
    assert aceptacion['evaluacion_independiente'] is False and aceptacion['ayuda_ia'] is True
    assert aceptacion['fuente_propuestas'] == str(PROPUESTAS.relative_to(RAIZ))
    assert sha256(PROPUESTAS) == aceptacion['sha256_fuente_propuestas']
    propuestas = pd.read_csv(PROPUESTAS, keep_default_na=False)
    elegidas = propuestas[propuestas.estado_revision.eq('referencia_cuestionable')]
    correcciones = pd.DataFrame(aceptacion['adjudicaciones'])
    assert len(correcciones) == len(elegidas) == 13
    assert set(correcciones.intervencion_id) == set(elegidas.intervencion_id)
    p = elegidas.set_index('intervencion_id')
    for r in correcciones.itertuples():
        q = p.loc[r.intervencion_id]
        assert (r.caso_revision, r.etiqueta_ia_original, r.etiqueta_corregida, r.sha256_texto,
                r.confianza_agente, r.archivo_evidencia) == (
            q.caso_revision, q.etiqueta_ia, q.postura_sugerida_agente, q.sha256_texto,
            q.confianza_revision, q.archivo_evidencia)
    original, seis, particiones, _, _, _ = PREV.cargar()
    asignacion = pd.read_csv(H.RUTA_SALIDA/'asignacion_folds.csv')
    nueva = aplicar_correcciones(seis, asignacion, correcciones)
    assert int(original.etiqueta.ne(seis.etiqueta).sum()) == 3
    assert int(original.etiqueta.ne(nueva.etiqueta).sum()) == 16
    ambiguos = set(propuestas.loc[propuestas.estado_revision.eq('ambigua'), 'intervencion_id'])
    assert len(ambiguos) == 12 and not ambiguos & set(correcciones.intervencion_id)
    pd.testing.assert_frame_equal(original[original.intervencion_id.isin(ambiguos)],
                                  nueva[nueva.intervencion_id.isin(ambiguos)])
    controles = []
    for fold, _, train, val in particiones:
        ids_t = set(original.iloc[train].intervencion_id)
        ids_v = set(original.iloc[val].intervencion_id)
        assert not ids_t & ids_v
        assert not set(original.iloc[train].meeting_id) & set(original.iloc[val].meeting_id)
        cambios_t = int(seis.iloc[train].etiqueta.ne(nueva.iloc[train].etiqueta).sum())
        cambios_v = int(seis.iloc[val].etiqueta.ne(nueva.iloc[val].etiqueta).sum())
        assert cambios_t == len(ids_t & set(correcciones.intervencion_id))
        assert cambios_v == len(ids_v & set(correcciones.intervencion_id))
        controles.append({'fold': fold, 'n_train': len(train), 'n_val': len(val),
                          'correcciones_nuevas_en_train': cambios_t, 'referencias_corregidas_en_val': cambios_v})
    assert sum(r['referencias_corregidas_en_val'] for r in controles) == 13
    vista = original[['intervencion_id', 'meeting_id', 'es_relevante']].copy()
    vista['fold_validacion'] = asignacion.fold_validacion
    vista['etiqueta_ia_original'] = original.etiqueta
    vista['etiqueta_seis_previas'] = seis.etiqueta
    vista['etiqueta_corregida_v2'] = nueva.etiqueta
    vista['correccion_nueva_aceptada'] = vista.intervencion_id.isin(correcciones.intervencion_id)
    return original, seis, nueva, particiones, vista, pd.DataFrame(controles)


def preparar(salida=SALIDA, informe=INFORME):
    salida, informe = Path(salida), Path(informe)
    exigir_salidas_nuevas(salida, informe)
    *_, vista, controles = cargar()
    fuentes = dict(PREV.verificar_preparacion(PREV.SALIDA)['sha256_insumos'])
    archivos = [Path(__file__), RAIZ/'tests/test_referencias_corregidas.py', PROTOCOLO,
                ACEPTACION, ACEPTACION.parent/'beto_disponibilidad.json', PROPUESTAS,
                PREV.SALIDA/'protocolo.json', PREV.SALIDA/'manifest.json',
                PREV.SALIDA/'predicciones_validacion.csv', PREV.SALIDA/'metricas.json',
                PROPUESTAS.parent/'manifest.json', RAIZ/'scripts/35_cerrar_revision_66.py',
                RAIZ/'docs/REVISION_ERRORES_CIERRE_66_V1.md']
    fuentes.update({str(p.relative_to(RAIZ)): sha256(p) for p in archivos})
    salida.mkdir(parents=True)
    vista.to_csv(salida/'referencias_desarrollo_v2.csv', index=False)
    controles.to_csv(salida/'control_folds.csv', index=False)
    escribir_json(salida/'protocolo.json', {
        'version': 'referencias_corregidas_v2', 'preparado_utc': datetime.now(timezone.utc).isoformat(),
        'sha256_insumos': fuentes,
        'sha256_preparacion': {p.name: sha256(p) for p in sorted(salida.glob('*.csv'))},
        'supervisiones': SUPERVISIONES, 'referencias': REFERENCIAS,
        'parametros_a': H.ANTERIOR.PARAMETROS_TFIDF, 'parametros_b': H.PARAMETROS_PALABRAS,
        'parametros_lr': H.ANTERIOR.PARAMETROS_LR, 'nuevas_correcciones_aceptadas': 13,
        'metricas_son_desarrollo_post_revision': True, 'beto_ejecutado': False,
        'python': platform.python_version(), 'numpy': np.__version__,
        'pandas': pd.__version__, 'sklearn': sklearn.__version__})
    print('Preparado: 13 correcciones nuevas, 12 ambiguos intactos, vista activa de 1352 filas.')
    print(controles.to_string(index=False))


def puntuar(predicciones):
    """Dos referencias para cada predicción: no confundir cambio de score con fit."""
    filas = []
    condiciones = {}
    for supervision in SUPERVISIONES:
        sub = predicciones[predicciones.supervision.eq(supervision)]
        assert len(sub) == 793 and sub.intervencion_id.is_unique
        condiciones[supervision] = {}
        for referencia in REFERENCIAS:
            columna = 'etiqueta_'+referencia
            puntos = []
            for fold, grupo in sub.groupby('fold', sort=True):
                m = H.metricas(grupo[columna], grupo.pred)
                filas.append({'supervision': supervision, 'referencia': referencia, 'fold': int(fold), **m})
                puntos.append(m)
            condiciones[supervision][referencia] = {
                'media_fold_f1_hd': float(np.mean([r['f1_hd'] for r in puntos])),
                'media_fold_macro_f1': float(np.mean([r['macro_f1'] for r in puntos])),
                'conjunto': H.metricas(sub[columna], sub.pred),
                'matriz': confusion_matrix(sub[columna], sub.pred, labels=H.CLASES).tolist()}
    base = predicciones[predicciones.supervision.eq('seis_previas')].set_index('intervencion_id')
    nueva = predicciones[predicciones.supervision.eq('seis_mas_trece')].set_index('intervencion_id').loc[base.index]
    for c in ['etiqueta_ia_original', 'etiqueta_corregida_v2', 'fold']:
        assert base[c].equals(nueva[c])
    bien = base.pred.eq(base.etiqueta_corregida_v2)
    ahora = nueva.pred.eq(nueva.etiqueta_corregida_v2)
    tabla = pd.DataFrame(filas)
    puntos = tabla[tabla.referencia.eq('corregida_v2')].pivot(index='fold', columns='supervision', values='f1_hd')
    deltas = puntos.seis_mas_trece - puntos.seis_previas
    c = condiciones
    resumen = {'condiciones': condiciones, 'orden_clases': list(H.CLASES),
        'delta_solo_referencia_control_fijo': c['seis_previas']['corregida_v2']['media_fold_f1_hd'] - c['seis_previas']['ia_original']['media_fold_f1_hd'],
        'delta_entrenamiento_referencia_corregida_fija': float(deltas.mean()),
        'deltas_entrenamiento_por_fold': {str(k): float(v) for k, v in deltas.items()},
        'folds_mejora_entrenamiento': int(deltas.gt(0).sum()),
        'predicciones_distintas': int(base.pred.ne(nueva.pred).sum()),
        'errores_corregidos_referencia_v2': int((~bien & ahora).sum()),
        'errores_nuevos_referencia_v2': int((bien & ~ahora).sum()),
        'correcciones_nuevas_aceptadas': 13, 'ambiguos_sin_modificar': 12,
        'cambios_efectivos_totales_vs_ia': 16, 'ajustes_por_fold': 10,
        'evaluacion_independiente': False, 'archivos_ia_originales_modificados': False,
        'modelo_persistido': False, 'beto_ejecutado': False, 'examen_306_abierto': False}
    return resumen, tabla


def redactar(r):
    lineas = ['# Referencias corregidas y ejecución local del TF-IDF', '',
        '**13 correcciones nuevas aplicadas en una referencia versionada; 12 ambiguos conservados. TF-IDF entrenado aquí; BETO sigue bloqueado por acceso a sus pesos.**', '',
        'La instrucción del investigador autoriza las 13 propuestas del cierre de 66. Las seis decisiones Rxx siguen vigentes: 19 decisiones aceptadas, 16 cambios efectivos respecto de IA. Las citas, razones y confianzas siguen atribuidas al agente; es adjudicación asistida post-predicción, no anotación humana independiente.', '',
        '## Comparación que separa referencias de entrenamiento', '',
        '| Supervisión de train | Referencia de validación | F1 H/D medio | Macro-F1 medio | Errores / 793 |',
        '|---|---|---:|---:|---:|']
    for s in SUPERVISIONES:
        for ref in REFERENCIAS:
            m = r['condiciones'][s][ref]
            lineas.append(f'| {s} | {ref} | {m["media_fold_f1_hd"]:.6f} | {m["media_fold_macro_f1"]:.6f} | {m["conjunto"]["errores"]} |')
    lineas += ['',
        f'- **Solo cambiar referencias**, dejando fijo el control: delta F1 H/D {r["delta_solo_referencia_control_fijo"]:+.6f}. No es mejora del modelo.',
        f'- **Volver a entrenar**, comparando contra la misma referencia corregida: delta F1 H/D {r["delta_entrenamiento_referencia_corregida_fija"]:+.6f}; mejora en {r["folds_mejora_entrenamiento"]}/5 folds.',
        f'- {r["predicciones_distintas"]} predicciones finales distintas; contra referencia v2, {r["errores_corregidos_referencia_v2"]} errores corregidos y {r["errores_nuevos_referencia_v2"]} nuevos.',
        '- Mismos folds purgados, textos, parámetros, puerta A, vocabularios e IDF. El control reproduce exactamente A/B/final de la variante adjudicada del experimento 31. No hubo búsqueda de hiperparámetros ni selección de etiquetas por puntuación.', '',
        '## Qué quedó corregido', '',
        '`data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv` es la vista activa para este experimento: 1.352 IDs con referencia IA, versión con seis decisiones y versión con seis más trece. El entrenamiento seis_mas_trece y la puntuación corregida_v2 leen esas decisiones verificadas. No es solo una lista de sugerencias.', '',
        'Los originales y resultados históricos no se sobrescriben. Los scripts históricos siguen usando sus versiones para reproducibilidad; cualquier experimento nuevo que quiera la referencia corregida debe consumir explícitamente esta vista verificada. No se alteró relevancia IA, codebook v2 ni referencia de los 12 ambiguos.', '',
        'Correcciones nuevas aceptadas (H hawkish, D dovish, N neutral):', '',
        '| Caso | ID | IA → corregida |', '|---|---|---|']
    abreviar = {'hawkish': 'H', 'dovish': 'D', 'neutral': 'N'}
    for a in json.loads(ACEPTACION.read_text())['adjudicaciones']:
        lineas.append(f'| {a["caso_revision"]} | {a["intervencion_id"]} | {abreviar[a["etiqueta_ia_original"]]} → {abreviar[a["etiqueta_corregida"]]} |')
    lineas += ['', '## Límites de interpretación', '',
        'Estas 793 observaciones ya se usaron en desarrollo y las 13 correcciones provienen de revisar desacuerdos después de ver predicciones. Mantener folds por reunión y excluir copias evita introducir la observación validada en su propio train, pero NO elimina el sesgo de la revisión post-predicción. Ni los nuevos scores ni sus diferencias estiman una mejora independiente o sobre todo el corpus.', '',
        'No hubo acceso a las 306 respuestas antiguas, test nuevo, refit final sobre todo el corpus ni reemplazo de un modelo de producción. Los ajustes por fold son efímeros. Se conservan las correcciones aceptadas aunque no eleven una métrica. Para afirmar generalización hará falta una evaluación realmente nueva y controlada, no reabrir aquel examen.', '',
        '## BETO: intento y bloqueo', '',
        'Se intentó acceder al checkpoint oficial dccuchile/bert-base-spanish-wwm-cased: API y config con urllib dieron TLS EOF; curl devolvió SSL_ERROR_SYSCALL, código 35. Dos CPU lógicas y sin nvidia-smi. No se desactivó TLS, no se descargaron pesos y BETO no se entrenó. El registro técnico está junto a la aceptación, en beto_disponibilidad.json. La limitación de acceso no mide la calidad de BETO.', '',
        '## Artefactos y reproducción', '',
        '- Aceptación: `data/auditoria/revision_errores_adjudicada_v1/adjudicacion_cierre_66_v1/aceptacion.json`.',
        '- Resultados: `data/evaluacion/referencias_corregidas_v2/`: referencias versionadas, control_folds, protocolo previo, predicciones, métricas por fold, resumen, manifiesto y verificación.',
        '- Las pruebas y el replay certifican integridad/reproducción, no verdad semántica ni independencia.', '',
        '```bash',
        'python scripts/36_evaluar_referencias_corregidas.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/36_evaluar_referencias_corregidas.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        '```', '',
        '[Protocolo previo](PROTOCOLO_REFERENCIAS_CORREGIDAS_V2.md) · [Evidencia de las 66 lecturas](REVISION_ERRORES_CIERRE_66_V1.md). La indicación histórica «pendientes de aceptación» en el cierre queda superada para estas 13 por la aceptación nueva, sin reescribir aquel informe.', '']
    return '\n'.join(lineas)


def ejecutar(salida=SALIDA, informe=INFORME):
    salida, informe = Path(salida), Path(informe)
    exigir_salidas_nuevas(informe, *[salida/n for n in [
        'predicciones_validacion.csv', 'resultados_folds.csv', 'metricas.json', 'manifest.json']])
    p = json.loads((salida/'protocolo.json').read_text())
    assert p['supervisiones'] == list(SUPERVISIONES) and p['referencias'] == list(REFERENCIAS)
    PREV.verificar_hashes(p['sha256_insumos'])
    for n, h in p['sha256_preparacion'].items():
        assert sha256(salida/n) == h, n
    original, seis, nueva, particiones, vista, controles = cargar()
    pd.testing.assert_frame_equal(vista, pd.read_csv(salida/'referencias_desarrollo_v2.csv', dtype={'es_relevante': str}))
    pd.testing.assert_frame_equal(controles, pd.read_csv(salida/'control_folds.csv'))
    predicciones = []
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        for fold, _, train, val in particiones:
            for supervision, datos in [('seis_previas', seis), ('seis_mas_trece', nueva)]:
                modelo = H.ajustar_modelos(datos.iloc[train], solo_base=True)['H0_historica']
                a, b, pred = H.predecir(modelo, original.iloc[val].texto.tolist())
                vocab = (modelo['vector_a'].vocabulary_, modelo['vista'].palabras.vocabulary_)
                idf = (modelo['vector_a'].idf_, modelo['vista'].palabras.idf_)
                if supervision == 'seis_previas':
                    puerta, vocab_previo, idf_previo = a, vocab, idf
                else:
                    np.testing.assert_array_equal(a, puerta)
                    assert vocab == vocab_previo
                    for x, y in zip(idf, idf_previo):
                        np.testing.assert_array_equal(x, y)
                tabla = original.iloc[val][['intervencion_id', 'meeting_id', 'es_relevante']].copy()
                tabla['etiqueta_ia_original'] = original.iloc[val].etiqueta
                tabla['etiqueta_corregida_v2'] = nueva.iloc[val].etiqueta
                tabla['fold'] = fold
                tabla['supervision'] = supervision
                tabla['pred_a'], tabla['pred_b'], tabla['pred'] = a, b, pred
                predicciones.append(tabla)
                print(f'Fold {fold}: {supervision} terminado.', flush=True)
                del modelo
    predicciones = pd.concat(predicciones, ignore_index=True)
    antiguo = pd.read_csv(PREV.SALIDA/'predicciones_validacion.csv')
    antiguo = antiguo[antiguo.variante.eq('adjudicada')]
    columnas = ['intervencion_id', 'meeting_id', 'fold', 'pred_a', 'pred_b', 'pred']
    control = predicciones[predicciones.supervision.eq('seis_previas')]
    ordenar = lambda t: t[columnas].sort_values('intervencion_id').reset_index(drop=True)
    pd.testing.assert_frame_equal(ordenar(control), ordenar(antiguo))
    resumen, folds = puntuar(predicciones)
    PREV.verificar_hashes(p['sha256_insumos'])
    predicciones.to_csv(salida/'predicciones_validacion.csv', index=False)
    folds.to_csv(salida/'resultados_folds.csv', index=False)
    escribir_json(salida/'metricas.json', resumen)
    informe.parent.mkdir(parents=True, exist_ok=True)
    with informe.open('x', encoding='utf-8') as archivo:
        archivo.write(redactar(resumen))
    escribir_json(salida/'manifest.json', {
        'finalizado_utc': datetime.now(timezone.utc).isoformat(),
        'sha256_salidas': {f.name: sha256(f) for f in sorted(salida.iterdir()) if f.is_file()},
        'sha256_informe': sha256(informe), 'ancla_31_reproducida': True,
        'evaluacion_independiente': False, 'beto_ejecutado': False})
    print(json.dumps({k: v for k, v in resumen.items() if k != 'condiciones'}, ensure_ascii=False, indent=2))
    return resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modos = parser.add_mutually_exclusive_group(required=True)
    modos.add_argument('--preparar', action='store_true')
    modos.add_argument('--ejecutar', action='store_true')
    parser.add_argument('--salida', type=Path, default=SALIDA)
    parser.add_argument('--informe', type=Path, default=INFORME)
    args = parser.parse_args()
    (preparar if args.preparar else ejecutar)(args.salida, args.informe)


if __name__ == '__main__':
    main()
