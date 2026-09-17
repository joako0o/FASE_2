"""Compara cuatro vistas B en desarrollo IA; sin gold, refit final ni modelo guardado.

Primero --preparar; después --ejecutar. El segundo paso exige protocolo y código
intactos. Para reproducir, usar otras rutas nuevas --salida y --informe.
"""
# ---- 1. Configuración y dependencias congeladas de la evaluación anterior ----
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import warnings

import numpy as np
import pandas as pd
import scipy
from scipy.sparse import hstack, csr_matrix
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

import config
import representaciones_contextuales as R
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

LONGITUD = cargar_script('22_seleccionar_longitud_ngramas.py')
ANTERIOR = LONGITUD.ANTERIOR
ESCRIBIR = ANTERIOR.ESCRITURA.escribir_json
VARIANTES = ('B0_base', 'B1_numeros', 'B2_contexto', 'B3_ambos')
RUTA_SALIDA = config.RUTA_DATOS / 'evaluacion/hibrido_contextual_v1'
RUTA_INFORME = config.RUTA_REPO / 'docs/EVALUACION_HIBRIDO_V1.md'
RUTA_PROTOCOLO = config.RUTA_REPO / 'docs/PROTOCOLO_HIBRIDO_V1.md'


# ---- 2. Preparación: verificar entradas y registrar protocolo antes de fit ----
def preparar(salida=RUTA_SALIDA, informe=RUTA_INFORME):
    salida, informe = Path(salida), Path(informe)
    exigir_salidas_nuevas(salida, informe)
    datos, mascara, _, fuentes = LONGITUD.cargar_insumos()
    _, asignacion = LONGITUD.asignar_folds(datos, mascara)
    # Todas las dependencias ejecutables y referencias históricas quedan ligadas.
    archivos = list((config.RUTA_REPO / 'scripts').glob('*.py')) + [RUTA_PROTOCOLO,
        config.RUTA_REPO / 'tests/test_hibrido_contextual.py',
        config.RUTA_REPO / 'docs/INVESTIGACION_HIBRIDO.md',
        LONGITUD.RUTA_SALIDA / 'predicciones_validacion.csv',
        LONGITUD.RUTA_SALIDA / 'asignacion_folds.csv']
    fuentes.update({str(p.relative_to(config.RUTA_REPO)): sha256(p) for p in archivos})
    # Hashes de archivos protegidos, no lectura de respuestas para aprender/evaluar.
    protegidos = json.loads((ANTERIOR.L.RUTA_VALIDACION / 'integridad_cierre.json').read_text())['sha256_fuentes']
    modelo = config.RUTA_REPO / 'modelos/tfidf_gold_v1.joblib'
    protegidos = {**protegidos, str(modelo.relative_to(config.RUTA_REPO)): sha256(modelo)}
    for nombre, huella in protegidos.items():
        assert sha256(config.RUTA_REPO / nombre) == huella, nombre
    fuentes.update(protegidos)
    salida.mkdir(parents=True)
    asignacion.to_csv(salida / 'asignacion_folds.csv', index=False)
    ESCRIBIR(salida / 'protocolo.json', {
        'version': 'hibrido_contextual_v1', 'fecha_preparacion_utc': datetime.now(timezone.utc).isoformat(),
        'sha256_insumos': fuentes, 'sha256_asignacion': sha256(salida / 'asignacion_folds.csv'),
        'variantes': VARIANTES, 'parametros_tfidf': ANTERIOR.PARAMETROS_TFIDF,
        'parametros_lr': ANTERIOR.PARAMETROS_LR, 'peso_bloques': 1,
        'criterio': 'Mayor media macro-F1; empate orden B0/B1/B2/B3. Sin adopción automática.',
        'tolerancias': {'delta_minimo': 0.01, 'folds_mejora_minimos': 3,
                        'perdida_recall_maxima': 0.02, 'perdida_conductual_maxima': 0.05},
        'casos_conductuales': R.CASOS_CONDUCTUALES, 'pares_invariantes': R.PARES_INVARIANTES,
        'versiones': {'numpy': np.__version__, 'pandas': pd.__version__,
                     'scikit_learn': sklearn.__version__, 'scipy': scipy.__version__},
        'gold_abierto_o_predicho': False, 'refit_final_o_reemplazo': False,
        'limite': 'Desarrollo reutilizado: 793 validación, 559 fijos en train, 34 copias; no confirmación.'})
    print(f'Protocolo congelado sin entrenar: {salida / "protocolo.json"}', flush=True)


def verificar_protocolo(salida):
    protocolo = json.loads((salida / 'protocolo.json').read_text())
    assert protocolo['variantes'] == list(VARIANTES)
    assert sha256(salida / 'asignacion_folds.csv') == protocolo['sha256_asignacion']
    for nombre, huella in protocolo['sha256_insumos'].items():
        assert sha256(config.RUTA_REPO / nombre) == huella, f'Fuente alterada: {nombre}'
    return protocolo


# ---- 3. Ajuste exclusivo en train; contexto vacío se conserva como cero ----
def ajustar_bloque(textos, numerico=False, contexto=False):
    parametros = {**ANTERIOR.PARAMETROS_TFIDF, 'ngram_range': (1, 4)}
    if contexto:
        parametros.pop('ngram_range')
        parametros.update(analyzer=R.AnalizadorContexto(numerico), lowercase=False, strip_accents=None)
    elif numerico:
        parametros = R.parametros_numericos(parametros)
    vector = TfidfVectorizer(**parametros)
    try:
        matriz = vector.fit_transform(textos)
    except ValueError as error:
        if contexto and ('empty vocabulary' in str(error) or 'no terms remain' in str(error).lower()):
            return None, csr_matrix((len(textos), 0))
        raise
    return vector, matriz


def transformar(vector, textos):
    return vector.transform(textos) if vector is not None else csr_matrix((len(textos), 0))


def predecir(a, vector_a, b, vector_b, vector_contexto, textos):
    pred_a = a.predict(vector_a.transform(textos))
    matriz = transformar(vector_b, textos)
    if vector_contexto is not None:
        matriz = hstack([matriz, transformar(vector_contexto, textos)], format='csr')
    pred_b = b.predict(matriz)
    return pred_a, pred_b, np.where(pred_a == 0, 'neutral', pred_b)


def evaluar_fold(train, val):
    inicio = time.perf_counter()
    vector_a = TfidfVectorizer(**ANTERIOR.PARAMETROS_TFIDF)
    a = LogisticRegression(**ANTERIOR.PARAMETROS_LR).fit(
        vector_a.fit_transform(train.texto), train.es_relevante.astype(str).eq('1').astype(int))
    relevantes = train.es_relevante.astype(str).eq('1')
    textos, y = train.loc[relevantes, 'texto'].tolist(), train.loc[relevantes, 'etiqueta']
    bloques = {num: ajustar_bloque(textos, num) for num in (False, True)}
    contextos = {num: ajustar_bloque(textos, num, True) for num in (False, True)}
    resultados, pruebas = {}, []
    sinteticos = [c[2] for c in R.CASOS_CONDUCTUALES]
    for indice, variante in enumerate(VARIANTES):
        numerico, contexto = indice in (1, 3), indice in (2, 3)
        vector, matriz = bloques[numerico]
        vector_ctx, matriz_ctx = contextos[numerico]
        if contexto:
            matriz = hstack([matriz, matriz_ctx], format='csr')
        b = LogisticRegression(**ANTERIOR.PARAMETROS_LR).fit(matriz, y)
        ctx = vector_ctx if contexto else None
        pa, pb, pred = predecir(a, vector_a, b, vector, ctx, val.texto.tolist())
        resultados[variante] = (pa, pb, pred, {
            'vocabulario_a': len(vector_a.vocabulary_), 'vocabulario_b': len(vector.vocabulary_),
            'vocabulario_contexto': matriz_ctx.shape[1] if contexto else 0})
        sa, sb, sp = predecir(a, vector_a, b, vector, ctx, sinteticos)
        for caso, ap, bp, pp in zip(R.CASOS_CONDUCTUALES, sa, sb, sp):
            codigo, fenomeno, texto, esperado = caso
            pruebas.append(dict(variante=variante, caso=codigo, fenomeno=fenomeno, texto=texto,
                                esperado=esperado, pred_a=int(ap), pred_b=bp, pred=pp, acierto=pp == esperado))
    return resultados, pruebas, time.perf_counter()-inicio


# ---- 4. Resumen pareado y criterios prácticos congelados, sin test nuevo ----
def resumir(predicciones, folds, pruebas, tolerancias):
    filas = []
    for variante in VARIANTES:
        sub = predicciones[predicciones.variante.eq(variante)]
        puntos = folds[folds.variante.eq(variante)]
        filas.append(dict(variante=variante, **ANTERIOR.metricas(sub.etiqueta, sub.pred),
                          macro_f1_media=float(puntos.macro_f1.mean()),
                          macro_f1_sd=float(puntos.macro_f1.std(ddof=1)),
                          acierto_conductual=float(pruebas[pruebas.variante.eq(variante)].acierto.mean())))
    tabla = pd.DataFrame(filas)
    base = tabla.iloc[0]
    pares = folds.pivot(index='fold', columns='variante', values='macro_f1')
    tabla['delta_media'] = tabla.macro_f1_media - base.macro_f1_media
    tabla['folds_mejora'] = [int((pares[v] > pares.B0_base).sum()) for v in VARIANTES]
    tabla['cumple_para_confirmar'] = (
        tabla.delta_media.ge(tolerancias['delta_minimo']) &
        tabla.folds_mejora.ge(tolerancias['folds_mejora_minimos']) &
        tabla.recall_hawkish.ge(base.recall_hawkish - tolerancias['perdida_recall_maxima']) &
        tabla.recall_dovish.ge(base.recall_dovish - tolerancias['perdida_recall_maxima']) &
        tabla.acierto_conductual.ge(base.acierto_conductual - tolerancias['perdida_conductual_maxima']))
    return tabla


def comparar_errores(predicciones):
    base = predicciones[predicciones.variante.eq('B0_base')].set_index('intervencion_id')
    filas = []
    for variante in VARIANTES:
        sub = predicciones[predicciones.variante.eq(variante)].set_index('intervencion_id').loc[base.index]
        bien, bien_base = sub.pred.eq(sub.etiqueta), base.pred.eq(base.etiqueta)
        filas.append(dict(variante=variante, errores=int((~bien).sum()),
            errores_hd=int((sub.etiqueta.isin(['hawkish', 'dovish']) & sub.pred.isin(['hawkish', 'dovish']) & ~bien).sum()),
            neutral_a_direccion=int((sub.etiqueta.eq('neutral') & ~bien).sum()),
            direccion_a_neutral=int((sub.pred.eq('neutral') & ~bien).sum()),
            corregidos=int((~bien_base & bien).sum()), nuevos=int((bien_base & ~bien).sum())))
    return pd.DataFrame(filas)


def construir_informe(tabla, errores, resumen):
    mejor = resumen['mejor_observado']
    elegibles = tabla.loc[tabla.cumple_para_confirmar, 'variante'].tolist()
    lineas = ['# Evaluación del híbrido contextual v1', '',
        f'**Mejor media observada: {mejor}.** Variantes que cumplen el criterio práctico para avanzar a confirmación: ' + (', '.join(elegibles) or '**ninguna**') + '.', '',
        'Comparación de desarrollo contra IA, no rendimiento humano ni confirmación independiente. No se reemplazó el modelo guardado.', '',
        '## Diseño congelado', '',
        '[Protocolo previo](PROTOCOLO_HIBRIDO_V1.md) y [fundamento externo](INVESTIGACION_HIBRIDO.md). Cuatro variantes, cinco folds históricos; 793 validaciones y 559 adicionales en train. A fija compartida; B se ajusta solo en train relevante. N-gramas 1–4, min_df=3, C=2. Sin diccionario direccional, calibración ni búsqueda adicional.', '',
        '**Alcance real:** la vista numérica conserva decimales/dígitos/unidad, pero no resuelve instrumento ni aritmética. La vista contextual selecciona frases candidatas y vecinas; no es un extractor fiable de respaldo, negación, emisor o tiempo. Conserva la vista completa. Añadir un bloque L2 de peso 1 cambia la geometría además de la representación.', '',
        '## Resultados', '',
        '| Variante | Macro-F1 medio | DE folds | Delta base | Mejora folds | F1 H | F1 D | Recall H | Recall D |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in tabla.itertuples():
        lineas.append(f'| {r.variante} | {r.macro_f1_media:.4f} | {r.macro_f1_sd:.4f} | {r.delta_media:+.4f} | {r.folds_mejora}/5 | {r.f1_hawkish:.4f} | {r.f1_dovish:.4f} | {r.recall_hawkish:.4f} | {r.recall_dovish:.4f} |')
    lineas += ['', '## Errores frente a IA y cambios frente a B0', '',
        '| Variante | Total | H↔D | N→dirección | Dirección→N | Corregidos | Nuevos |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in errores.itertuples():
        lineas.append(f'| {r.variante} | {r.errores} | {r.errores_hd} | {r.neutral_a_direccion} | {r.direccion_a_neutral} | {r.corregidos} | {r.nuevos} |')
    lineas += ['', '## Pruebas conductuales', '',
        '14 ejemplos inventados, fijados antes de ajustar, repetidos con cinco modelos de fold. No son 70 observaciones independientes ni etiquetas humanas. El acierto usa salida A+B; invariancia se calcula aparte, pues dos predicciones iguales pueden estar ambas equivocadas.', '',
        '| Variante | Acierto de clase (70 ejecuciones) | Invariancia (20 pares×fold) |', '|---|---:|---:|']
    for r in tabla.itertuples():
        lineas.append(f'| {r.variante} | {r.acierto_conductual:.1%} | {resumen["invariancia"][r.variante]:.1%} |')
    lineas += ['', 'Los CSV contienen resultados por caso/fenómeno y fold. No se retocaron los métodos para pasar estos ejemplos.', '',
        '## Extracción y controles', '',
        f'- Intervenciones de validación con ventana contextual: {resumen["cobertura_contexto"]}/793; sin candidato: {793-resumen["cobertura_contexto"]}. Sin candidato el bloque es cero, no se fuerza neutral.',
        f'- Fracción de caracteres seleccionados en validación: {resumen["fraccion_caracteres"]:.1%}. No es precisión del extractor: las ventanas son candidatos, no evidencia adjudicada.',
        f'- Textos con formatos numéricos potencialmente ambiguos (un separador y tres dígitos): {resumen["textos_numero_ambiguo"]}. No se resuelven automáticamente como miles.',
        '- Posiciones de todas las ventanas verificadas contra el original; sin truncamiento. B0 reproduce exactamente las 793 predicciones de (1,4); A es idéntica en las cuatro variantes.',
        '- Vocabularios/IDF aprendidos solo en train; no cambios de fuentes ni modelo previo. Tiempos de ejecución registrados aparte; no se guardan clasificadores.', '',
        '## Decisión y límites', '',
        'El criterio previo exige delta medio ≥0,01, mejora en ≥3 folds, caída de recall H/D ≤0,02 y caída de acierto conductual ≤0,05. Son tolerancias prácticas, no pruebas de significación. Mayor media por sí sola no autoriza adopción.',
        ('Alguna variante cumple: eso justifica proponer una confirmación separada, no afirmar mejora humana.' if elegibles else 'Ninguna variante cumple: mantener B0 como referencia. No ampliar esta búsqueda tras ver resultados. Un extractor más semántico o un transformer sería otra comparación que requiere autorización.'),
        '- Los 793 ya se usaron para selección y diagnóstico; los 17 errores H/D conocidos no son un test nuevo. Persisten 34 textos repetidos con train, aunque las reuniones estén separadas.',
        '- A permanece fija: cambiar B no corrige relevancia. Pasado, condiciones y referencias extranjeras no se descartan automáticamente; tampoco se resuelven plenamente.',
        '- Las 306 respuestas humanas no se examinaron ni predijeron. Sin refit final con 1.352 ni scoring completo. Una confirmación necesita otra evaluación y control prefijado de duplicados.', '',
        '## Artefactos y reproducción', '',
        'En `data/evaluacion/hibrido_contextual_v1/`: protocolo, asignación, predicciones, resultados por fold, comparación, errores, pruebas conductuales, invariancias, vistas/ventanas verificadas, métricas, tiempos y manifiesto. `reproducibilidad.json` registra los controles posteriores cuando se completa la repetición.', '',
        '```bash', 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/24_evaluar_hibrido_contextual.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/24_evaluar_hibrido_contextual.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md', '```', '']
    return '\n'.join(lineas)


# ---- 5. Ejecutar protocolo ya congelado y cerrar salidas sin sobrescribir ----
def ejecutar(salida=RUTA_SALIDA, informe=RUTA_INFORME):
    salida, informe = Path(salida), Path(informe)
    protocolo = verificar_protocolo(salida)
    assert {p.name for p in salida.iterdir()} == {'protocolo.json', 'asignacion_folds.csv'}, 'Carpeta ya ejecutada o parcial; usar otra nueva.'
    exigir_salidas_nuevas(informe)
    datos, mascara, anteriores, _ = LONGITUD.cargar_insumos()
    particiones, asignacion = LONGITUD.asignar_folds(datos, mascara)
    pd.testing.assert_frame_equal(asignacion, pd.read_csv(salida / 'asignacion_folds.csv'))
    predicciones, registros, pruebas, tiempos = [], [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        for numero, tr, va in particiones:
            resultados, conducta, segundos = evaluar_fold(datos.iloc[tr], datos.iloc[va])
            tiempos.append(dict(fold=numero, segundos=segundos))
            for variante, (pa, pb, pred, dimensiones) in resultados.items():
                sub = datos.iloc[va][['intervencion_id', 'meeting_id', 'etiqueta', 'es_relevante']].copy()
                sub['fold'], sub['variante'], sub['pred_a'], sub['pred_b'], sub['pred'] = numero, variante, pa, pb, pred
                predicciones.append(sub)
                fila = dict(fold=numero, variante=variante, n_train=len(tr), n_validacion=len(va),
                            **dimensiones, **ANTERIOR.metricas(sub.etiqueta, sub.pred))
                registros.append(fila)
                print(f'Fold {numero} {variante}: macro-F1={fila["macro_f1"]:.6f}', flush=True)
            pruebas.extend(dict(fold=numero, **p) for p in conducta)
    predicciones, folds, pruebas = pd.concat(predicciones, ignore_index=True), pd.DataFrame(registros), pd.DataFrame(pruebas)
    assert len(predicciones) == 4 * 793 and not predicciones.duplicated(['intervencion_id', 'variante']).any()
    assert predicciones.groupby('intervencion_id').pred_a.nunique().eq(1).all()
    base = predicciones[predicciones.variante.eq('B0_base')]
    columnas = ['intervencion_id', 'meeting_id', 'etiqueta', 'fold', 'pred']
    previo = anteriores[anteriores.variante.eq('ngramas_1_4')]
    pd.testing.assert_frame_equal(base[columnas].reset_index(drop=True), previo[columnas].reset_index(drop=True))
    tabla = resumir(predicciones, folds, pruebas, protocolo['tolerancias'])
    errores = comparar_errores(predicciones)
    invariancias = []
    for (fold, variante), sub in pruebas.groupby(['fold', 'variante']):
        indice = sub.set_index('caso')
        for primero, segundo in R.PARES_INVARIANTES:
            invariancias.append(dict(fold=fold, variante=variante, primero=primero, segundo=segundo,
                invariante=bool(indice.loc[primero, 'pred'] == indice.loc[segundo, 'pred']),
                ambos_correctos=bool(indice.loc[primero, 'acierto'] and indice.loc[segundo, 'acierto'])))
    invariancias = pd.DataFrame(invariancias)
    vistas, ventanas = [], []
    for fila in datos.loc[~mascara].itertuples():
        intervalos = R.extraer_ventanas(fila.texto)
        for inicio, fin in intervalos:
            fragmento = fila.texto[inicio:fin]
            assert fragmento and 0 <= inicio < fin <= len(fila.texto)
            ventanas.append(dict(intervencion_id=fila.intervencion_id, inicio=inicio, fin=fin, fragmento=fragmento))
        vistas.append(dict(intervencion_id=fila.intervencion_id, n_ventanas=len(intervalos), caracteres=len(fila.texto),
            caracteres_contexto=sum(fin-inicio for inicio, fin in intervalos),
            numero_ambiguo=bool(R.PATRON_AMBIGUO.search(fila.texto))))
    vistas, ventanas = pd.DataFrame(vistas), pd.DataFrame(ventanas)
    mejor = tabla.sort_values('macro_f1_media', ascending=False, kind='stable').iloc[0].variante
    resumen = dict(mejor_observado=mejor, variantes_para_confirmar=tabla.loc[tabla.cumple_para_confirmar, 'variante'].tolist(),
        clases=ANTERIOR.L.CLASES, matrices={v: confusion_matrix(s.etiqueta, s.pred, labels=ANTERIOR.L.CLASES).tolist()
                                          for v, s in predicciones.groupby('variante')},
        invariancia=invariancias.groupby('variante').invariante.mean().to_dict(),
        cobertura_contexto=int(vistas.n_ventanas.gt(0).sum()),
        fraccion_caracteres=float(vistas.caracteres_contexto.sum()/vistas.caracteres.sum()),
        textos_numero_ambiguo=int(vistas.numero_ambiguo.sum()),
        gold_abierto_o_predicho=False, refit_final_o_reemplazo=False, ancla_base_identica=True,
        textos_validacion_identicos_train=int(asignacion.texto_identico_en_train.sum()))
    tablas = dict(predicciones_validacion=predicciones, resultados_folds=folds, comparacion_variantes=tabla,
                  errores=errores, pruebas_conductuales=pruebas, invariancias=invariancias,
                  vistas_validacion=vistas, ventanas_validacion=ventanas)
    for nombre, contenido in tablas.items():
        contenido.to_csv(salida / (nombre + '.csv'), index=False)
    ESCRIBIR(salida / 'metricas.json', resumen)
    ESCRIBIR(salida / 'tiempos.json', tiempos)
    verificar_protocolo(salida)
    informe.parent.mkdir(parents=True, exist_ok=True)
    with informe.open('x', encoding='utf-8') as archivo:
        archivo.write(construir_informe(tabla, errores, resumen))
    ESCRIBIR(salida / 'manifest.json', {'fecha_fin_utc': datetime.now(timezone.utc).isoformat(),
        'sha256_salidas': {p.name: sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},
        'sha256_informe': sha256(informe)})
    print(tabla[['variante', 'macro_f1_media', 'delta_media', 'cumple_para_confirmar']].to_string(index=False))
    return resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    accion = parser.add_mutually_exclusive_group(required=True)
    accion.add_argument('--preparar', action='store_true')
    accion.add_argument('--ejecutar', action='store_true')
    parser.add_argument('--salida', type=Path, default=RUTA_SALIDA)
    parser.add_argument('--informe', type=Path, default=RUTA_INFORME)
    args = parser.parse_args()
    (preparar if args.preparar else ejecutar)(args.salida, args.informe)


if __name__ == '__main__':
    main()
