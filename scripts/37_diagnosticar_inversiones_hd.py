"""Diagnóstico de diez inversiones H/D: reconstrucción exacta, no optimización."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

E = cargar_script('36_evaluar_referencias_corregidas.py')
RAIZ = E.RAIZ
BASE = RAIZ/'data/auditoria/inversiones_hd_v1'
LECTURAS = BASE/'lecturas_agente.json'
SALIDA = BASE/'resultados'
PROTOCOLO = RAIZ/'docs/PROTOCOLO_DIAGNOSTICO_INVERSIONES_HD_V1.md'
INFORME = RAIZ/'docs/DIAGNOSTICO_INVERSIONES_HD_V1.md'
TOP = 6
escribir_json = E.escribir_json


def seleccionar(predicciones, revision, aceptadas):
    assert predicciones.intervencion_id.is_unique and revision.intervencion_id.is_unique
    assert set(predicciones.supervision) == {'seis_mas_trece'}
    mascara = predicciones.apply(lambda r: {r.etiqueta_corregida_v2, r.pred} == {'hawkish', 'dovish'}, axis=1)
    inversiones = predicciones[mascara].copy()
    a = revision.set_index('intervencion_id')
    assert set(inversiones.intervencion_id) <= set(a.index)
    inversiones['estado_revision_previa'] = [a.loc[k].estado_revision for k in inversiones.intervencion_id]
    for r in inversiones.itertuples():
        previo = a.loc[r.intervencion_id]
        if r.estado_revision_previa == 'referencia_cuestionable':
            assert aceptadas.get(r.intervencion_id) == r.etiqueta_corregida_v2
        elif r.estado_revision_previa == 'referencia_respaldada':
            assert previo.postura_sugerida_agente == r.etiqueta_corregida_v2
        else:
            assert r.estado_revision_previa == 'ambigua'
    return (inversiones[inversiones.estado_revision_previa.ne('ambigua')].copy(),
            inversiones[inversiones.estado_revision_previa.eq('ambigua')].copy())


def validar_citas(lectura, texto):
    assert lectura['citas'] and len(set(lectura['citas'])) == len(lectura['citas'])
    for cita in lectura['citas']:
        assert 0 < len(cita) <= 300 and cita in texto, 'Cita no literal o excesiva'


def descomponer(x, pesos, intercepto, nombres, frecuencias):
    """Todos los features activos; signo positivo favorece la predicción errónea."""
    filas = []
    for j, valor in zip(x.indices, x.data):
        filas.append({'termino': str(nombres[j]), 'tfidf': float(valor),
            'coef_contraste': float(pesos[j]), 'aporte': float(valor*pesos[j]),
            **{f'df_train_{c}': int(v[j]) for c, v in frecuencias.items()}})
    filas.sort(key=lambda r: r['termino'])
    positivos = sorted([r for r in filas if r['aporte'] > 0], key=lambda r: (-r['aporte'], r['termino']))[:TOP]
    negativos = sorted([r for r in filas if r['aporte'] < 0], key=lambda r: (r['aporte'], r['termino']))[:TOP]
    suma = sum(r['aporte'] for r in filas)
    resumen = {'intercepto': float(intercepto), 'suma_aportes': float(suma),
        'margen': float(intercepto+suma), 'residuo_no_mostrado': float(suma-sum(r['aporte'] for r in positivos+negativos)),
        'top_a_favor_prediccion': positivos, 'top_a_favor_referencia': negativos}
    return resumen, filas


def cargar():
    p = json.loads((E.SALIDA/'protocolo.json').read_text())
    E.PREV.verificar_hashes(p['sha256_insumos'])
    m = json.loads((E.SALIDA/'manifest.json').read_text())
    for n, h in m['sha256_salidas'].items():
        assert sha256(E.SALIDA/n) == h, n
    original, _, corregida, particiones, _, _ = E.cargar()
    pred = pd.read_csv(E.SALIDA/'predicciones_validacion.csv')
    pred = pred[pred.supervision.eq('seis_mas_trece')].copy()
    revision = pd.read_csv(E.PROPUESTAS, keep_default_na=False)
    aceptacion = json.loads(E.ACEPTACION.read_text())['adjudicaciones']
    aceptadas = {r['intervencion_id']: r['etiqueta_corregida'] for r in aceptacion}
    seleccion, ambiguos = seleccionar(pred, revision, aceptadas)
    assert len(pred) == 793 and len(seleccion) == 10 and len(ambiguos) == 5
    d = json.loads(LECTURAS.read_text())
    assert d['autor'] == 'agente' and d['lectura_post_prediccion'] is True
    assert d['etiquetas_modificadas'] is False
    lecturas = {r['intervencion_id']: r for r in d['lecturas']}
    assert len(lecturas) == len(d['lecturas']) == 10
    assert set(lecturas) == set(seleccion.intervencion_id)
    corpus = original.set_index('intervencion_id')
    assert sum(len(corpus.loc[k].texto) for k in lecturas) == d['caracteres_leidos'] == 40937
    for k, lectura in lecturas.items():
        validar_citas(lectura, corpus.loc[k].texto)
    return original, corregida, particiones, pred, revision, seleccion, ambiguos, lecturas


def preparar(salida=SALIDA, informe=INFORME):
    salida, informe = Path(salida), Path(informe)
    exigir_salidas_nuevas(salida, informe)
    *_, seleccion, ambiguos, _ = cargar()
    fuentes = dict(json.loads((E.SALIDA/'protocolo.json').read_text())['sha256_insumos'])
    archivos = [LECTURAS, Path(__file__), PROTOCOLO, RAIZ/'tests/test_inversiones_hd.py',
        E.SALIDA/'protocolo.json', E.SALIDA/'manifest.json', E.SALIDA/'predicciones_validacion.csv',
        E.SALIDA/'referencias_desarrollo_v2.csv', E.PROPUESTAS, E.ACEPTACION]
    fuentes.update({str(p.relative_to(RAIZ)): sha256(p) for p in archivos})
    salida.mkdir(parents=True)
    seleccion.to_csv(salida/'seleccion.csv', index=False)
    ambiguos.to_csv(salida/'ambiguos_excluidos.csv', index=False)
    escribir_json(salida/'protocolo.json', {'preparado_utc': datetime.now(timezone.utc).isoformat(),
        'sha256_insumos': fuentes,
        'sha256_preparacion': {p.name: sha256(p) for p in sorted(salida.glob('*.csv'))},
        'seleccion': 'todas_las_inversiones_v2_menos_ambiguas', 'n': 10, 'ambiguos': 5,
        'top_por_signo': TOP, 'sonda': 'primera_cita_literal_preseleccionada_solo_B',
        'etiquetas_modificadas': False, 'beto_ejecutado': False, 'examen_306_abierto': False})
    print('Preparados diez casos completos y cinco ambiguos excluidos.', flush=True)


def redactar(casos, ambiguos, resumen):
    n = resumen['citas_primera_b_coincide_referencia']
    letras = {'hawkish': 'H', 'dovish': 'D', 'neutral': 'N'}
    lineas = ['# Diagnóstico de diez inversiones H/D', '',
        '**Se reconstruyó el TF-IDF corregido y se explicaron sus diez inversiones con referencias más claras. No se cambiaron etiquetas ni se probó un candidato nuevo.**', '',
        '## Qué se comprobó', '',
        '- Las 793 predicciones A/B/final coinciden exactamente con el experimento 36. Los errores siguen siendo 15 inversiones H↔D, 12 H/D→N y 24 N→H/D.',
        '- De las 15 inversiones, cinco conservan referencia ambigua y quedan aparte. Las diez examinadas son nueve respaldadas por el agente y una corrección aceptada: no son diez nuevos ejemplos humanos independientes.',
        '- Se releyeron **40.937 caracteres íntegros**. En los diez casos A=1: la inversión ocurre en el clasificador de postura B, no por forzar N desde relevancia.',
        '- Cada margen predicción−referencia se reconstruye exactamente como intercepto más aportes TF-IDF. Se guardan todos los términos activos; las tablas breves no ocultan su residuo.',
        f'- **Sonda de evidencia:** B coincide con la referencia en {n}/10 primeras citas aisladas, fijadas antes de obtener los coeficientes. En {10-n}/10 no coincide. No es una mejora de precisión: las citas fueron seleccionadas manualmente con conocimiento de la referencia.', '',
        'Si la cita aislada se reconoce, el contexto completo cambia la decisión del modelo, pero esto no demuestra que exista un extractor capaz de encontrarla. Si también falla aislada, no basta culpar a la longitud. Las frecuencias y pesos son asociaciones del train, no comprensión del objeto, tiempo o negación.', '',
        '## Resumen de casos', '',
        '| ID | Referencia → B texto completo | B primera cita | Margen error−referencia |',
        '|---|---|---|---:|']
    for c in casos:
        lineas.append(f'| {c["intervencion_id"]} | {letras[c["etiqueta_corregida_v2"]]} → {letras[c["pred"]]} | {letras[c["sonda"]["pred_b"]]} | {c["descomposicion"]["margen"]:.6f} |')
    lineas += ['', '## Evidencia y contribuciones por caso', '',
        'Un aporte positivo favorece la predicción errónea frente a la referencia; uno negativo favorece la referencia. No es una probabilidad ni el efecto causal de borrar esa palabra. Los n-gramas se solapan y el TF-IDF está normalizado. La sonda usa solo B, no la puerta A.', '']
    for c in casos:
        d = c['descomposicion']; lectura = c['lectura_agente']
        lineas += [f'### {c["intervencion_id"]} — {c["actor"]}', '',
            f'**Referencia {letras[c["etiqueta_corregida_v2"]]}; modelo {letras[c["pred"]]}; fold {c["fold"]}; {len(c["texto_completo"])} caracteres completos.**', '']
        for cita in lectura['citas']:
            lineas += ['> '+cita, '']
        lineas += [lectura['lectura'], '', '**Hipótesis previa:** '+lectura['hipotesis_a_contrastar'], '',
            '| Término activo | Aporte al margen error−referencia | df train H / D / N |', '|---|---:|---|']
        for r in d['top_a_favor_prediccion']+d['top_a_favor_referencia']:
            lineas.append(f'| {r["termino"]} | {r["aporte"]:+.6f} | {r["df_train_hawkish"]} / {r["df_train_dovish"]} / {r["df_train_neutral"]} |')
        lineas += ['', f'Intercepto: **{d["intercepto"]:+.6f}**; suma de todos los aportes: **{d["suma_aportes"]:+.6f}**; residuo de términos no mostrados: **{d["residuo_no_mostrado"]:+.6f}**. Margen final: **{d["margen"]:+.6f}**.', '',
            f'Primera cita aislada: B predice **{letras[c["sonda"]["pred_b"]]}**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.', '',
            '**Límite:** '+lectura['limite'], '']
    lineas += ['## Cinco inversiones ambiguas excluidas', '',
        'No se modifican estas referencias ni se convierten en neutral automáticamente. Son parte de las 15 inversiones numéricas, no errores semánticos inequívocos.', '',
        '| ID | Referencia → predicción |', '|---|---|']
    for r in ambiguos.to_dict('records'):
        lineas.append(f'| {r["intervencion_id"]} | {letras[r["etiqueta_corregida_v2"]]} → {letras[r["pred"]]} |')
    lineas += ['', '## Qué exigir al siguiente modelo', '',
        '1. Separar decisión respaldada de diagnóstico, pasado, alternativas y condiciones rechazadas.',
        '2. Resolver el objeto de reducir: tasa frente a estímulo; distinguir fiscal/extranjero de política monetaria chilena.',
        '3. Separar nivel y dirección: seguir expansivo no impide subir; subir menos no es recortar; mantener hoy no elimina un sesgo futuro explícito.',
        '4. Leer toda la intervención, sin tomar solo sus primeros 512 tokens ni entregar al modelo las citas elegidas por el agente.',
        '5. Medir H→D y D→H sobre soportes fijos, sin esconder inversiones en N; conservar matriz completa y guardas F1/recall.', '',
        'El siguiente ensayo contextual está diseñado, no ejecutado. Mantendría referencia v2, folds purgados y puerta A, comparando B TF-IDF con B BETO. El acceso a pesos sigue siendo el bloqueo documentado en 36; no se simula entrenamiento. La media de segmentos también puede diluir una conclusión, por lo que cambiar arquitectura no garantiza resolver estos diez ejemplos.', '',
        'Criterios de desarrollo previos a un nuevo candidato: +0,02 F1 H/D medio y mejora en ≥3/5 folds, pérdida macro ≤0,005 y recall H/D ≤0,02, además de menos inversiones sin aumentar H/D→N. Estos casos son diagnóstico conocido, no test nuevo. Una afirmación de generalización requerirá confirmación independiente posterior.', '',
        '## Reproducción y trazabilidad', '',
        'Artefactos en `data/auditoria/inversiones_hd_v1/`: lecturas manuales, selección, cinco excluidos, textos completos, aportes activos, scores/sondas, 793 predicciones reconstruidas, protocolo, hashes y verificación. Se preservan las opiniones previas y las referencias corregidas. No se abre el examen de 306 ni se cambia un checkpoint.', '',
        '```bash',
        'python scripts/37_diagnosticar_inversiones_hd.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/37_diagnosticar_inversiones_hd.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        '```', '', '[Protocolo previo](PROTOCOLO_DIAGNOSTICO_INVERSIONES_HD_V1.md) · [Referencia/modelo congelados](EVALUACION_REFERENCIAS_CORREGIDAS_V2.md)', '']
    return '\n'.join(lineas)


def ejecutar(salida=SALIDA, informe=INFORME):
    salida, informe = Path(salida), Path(informe)
    nombres = ['casos.json', 'aportes.csv', 'predicciones_reconstruidas.csv', 'resumen.json', 'manifest.json']
    exigir_salidas_nuevas(informe, *[salida/n for n in nombres])
    p = json.loads((salida/'protocolo.json').read_text())
    E.PREV.verificar_hashes(p['sha256_insumos'])
    assert p['top_por_signo'] == TOP
    for n, h in p['sha256_preparacion'].items():
        assert sha256(salida/n) == h
    original, corregida, particiones, pred, revision, seleccion, ambiguos, lecturas = cargar()
    pd.testing.assert_frame_equal(seleccion.reset_index(drop=True), pd.read_csv(salida/'seleccion.csv'))
    pd.testing.assert_frame_equal(ambiguos.reset_index(drop=True), pd.read_csv(salida/'ambiguos_excluidos.csv'))
    casos, aportes, reconstruidas = [], [], []
    previas = revision.set_index('intervencion_id')
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        for fold, _, train, val in particiones:
            modelo = E.H.ajustar_modelos(corregida.iloc[train], solo_base=True)['H0_historica']
            textos = original.iloc[val].texto.tolist()
            a, b, finales = E.H.predecir(modelo, textos)
            tabla = original.iloc[val][['intervencion_id', 'meeting_id']].copy()
            tabla['fold'], tabla['pred_a'], tabla['pred_b'], tabla['pred'] = fold, a, b, finales
            reconstruidas.append(tabla)
            vector, clf = modelo['vista'], modelo['clasificador']
            x = vector.transform(textos); scores = clf.decision_function(x)
            indices = {c: i for i, c in enumerate(clf.classes_)}
            tr = corregida.iloc[train]; tr = tr[tr.es_relevante.astype(str).eq('1')]
            xt = vector.transform(tr.texto.tolist())
            frecuencias = {c: np.asarray((xt[tr.etiqueta.eq(c).to_numpy()] > 0).sum(axis=0)).ravel() for c in E.H.CLASES}
            for j, fila in enumerate(original.iloc[val].itertuples()):
                k = fila.intervencion_id
                if k not in lecturas:
                    continue
                guardada = seleccion[seleccion.intervencion_id.eq(k)].iloc[0]
                ref = guardada.etiqueta_corregida_v2
                assert a[j] == 1 and {finales[j], ref} == {'hawkish', 'dovish'}
                ip, ir = indices[finales[j]], indices[ref]
                d, terminos = descomponer(x[j], clf.coef_[ip]-clf.coef_[ir],
                    clf.intercept_[ip]-clf.intercept_[ir], vector.palabras.get_feature_names_out(), frecuencias)
                esperado = scores[j, ip]-scores[j, ir]
                assert np.isclose(d['margen'], esperado, rtol=1e-9, atol=1e-9) and d['margen'] > 0
                cita = lecturas[k]['citas'][0]
                xq = vector.transform([cita]); sq = clf.decision_function(xq)[0]
                pq = str(clf.predict(xq)[0])
                aportes.extend({'intervencion_id': k, 'fold': fold, **r} for r in terminos)
                casos.append({'intervencion_id': k, 'actor': fila.actor, 'fecha': fila.fecha,
                    'fold': int(fold), 'etiqueta_ia_original': guardada.etiqueta_ia_original,
                    'etiqueta_corregida_v2': ref, 'pred_a': int(a[j]), 'pred': str(finales[j]),
                    'texto_completo': fila.texto, 'sha256_texto': hashlib.sha256(fila.texto.encode()).hexdigest(),
                    'revision_previa': previas.loc[k].to_dict(), 'lectura_agente': lecturas[k],
                    'scores_b': {c: float(scores[j, i]) for c, i in indices.items()},
                    'descomposicion': d, 'sonda': {'texto': cita, 'solo_b': True, 'pred_b': pq,
                        'scores_b': {c: float(sq[i]) for c, i in indices.items()},
                        'coincide_referencia': pq == ref}})
            print(f'Fold {fold}: reconstruido y explicado.', flush=True)
    reconstruidas = pd.concat(reconstruidas, ignore_index=True)
    columnas = ['intervencion_id', 'meeting_id', 'fold', 'pred_a', 'pred_b', 'pred']
    ordenar = lambda x: x[columnas].sort_values('intervencion_id').reset_index(drop=True)
    pd.testing.assert_frame_equal(ordenar(reconstruidas), ordenar(pred))
    assert len(casos) == 10 and len({c['intervencion_id'] for c in casos}) == 10
    resumen = {'casos': 10, 'ambiguos_excluidos': 5, 'caracteres_completos': sum(len(c['texto_completo']) for c in casos),
        'predicciones_reproducidas': len(reconstruidas), 'puerta_a_activa': sum(c['pred_a'] == 1 for c in casos),
        'citas_primera_b_coincide_referencia': sum(c['sonda']['coincide_referencia'] for c in casos),
        'sonda_predicciones': dict(Counter(c['sonda']['pred_b'] for c in casos)),
        'features_activos_exportados': len(aportes), 'ajustes_reconstruccion': 5,
        'etiquetas_modificadas': False, 'metricas_36_modificadas': False,
        'nuevo_candidato_evaluado': False, 'beto_ejecutado': False, 'examen_306_abierto': False}
    E.PREV.verificar_hashes(p['sha256_insumos'])
    escribir_json(salida/'casos.json', casos)
    escribir_json(salida/'resumen.json', resumen)
    pd.DataFrame(aportes).to_csv(salida/'aportes.csv', index=False)
    reconstruidas.to_csv(salida/'predicciones_reconstruidas.csv', index=False)
    informe.parent.mkdir(parents=True, exist_ok=True)
    with informe.open('x') as f:
        f.write(redactar(casos, ambiguos, resumen))
    escribir_json(salida/'manifest.json', {'finalizado_utc': datetime.now(timezone.utc).isoformat(),
        'sha256_salidas': {p.name: sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},
        'sha256_informe': sha256(informe), 'predicciones_36_reproducidas': True})
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return resumen


def main():
    p = argparse.ArgumentParser(description=__doc__)
    modos = p.add_mutually_exclusive_group(required=True)
    modos.add_argument('--preparar', action='store_true')
    modos.add_argument('--ejecutar', action='store_true')
    p.add_argument('--salida', type=Path, default=SALIDA)
    p.add_argument('--informe', type=Path, default=INFORME)
    a = p.parse_args()
    (preparar if a.preparar else ejecutar)(a.salida, a.informe)


if __name__ == '__main__':
    main()
