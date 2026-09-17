"""Busca el límite de n-gramas B entre 1 y 6 en los folds IA ya usados.

Nueva versión autorizada, no modificación del experimento léxico congelado.
Reutiliza las particiones, parámetros y métricas del script 21, sin diccionario,
sin abrir respuestas humanas, sin reajuste final ni reemplazo del modelo vigente.
"""
# ---- 1. Parámetros de esta búsqueda acotada y utilidades congeladas ----
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

import config
from utilidades import cargar_script, exigir_salidas_nuevas, norm, sha256

ANTERIOR = cargar_script("21_evaluar_lexico.py")
LONGITUDES = tuple(range(1, 7))
RUTA_SALIDA = config.RUTA_DATOS / "evaluacion/longitud_ngramas_v1"
RUTA_INFORME = config.RUTA_REPO / "docs/LONGITUD_NGRAMAS.md"


# ---- 2. Linaje y particiones: no se vuelve a construir/revisar el léxico ----
def cargar_insumos():
    ruta = ANTERIOR.L.RUTA_VALIDACION
    protocolo = json.loads((ruta / "protocolo_validacion.json").read_text())
    resumen = json.loads((ruta / "metricas.json").read_text())
    assert sha256(Path(ANTERIOR.__file__)) == protocolo["sha256_evaluador"]
    fuentes = {**protocolo["protocolo_descubrimiento"]["sha256_insumos"],
               **protocolo["sha256_dependencias"]}
    for nombre, huella in fuentes.items():
        assert sha256(config.RUTA_REPO / nombre) == huella, f"insumo alterado: {nombre}"
    for nombre, huella in resumen["sha256_salidas"].items():
        assert sha256(ruta / nombre) == huella, f"salida anterior alterada: {nombre}"
    datos = ANTERIOR.BASELINE.cargar_muestra()
    particion = pd.read_csv(ANTERIOR.L.RUTA_LEXICO / "particion.csv")
    assert sha256(ANTERIOR.L.RUTA_LEXICO / "particion.csv") == protocolo["sha256_particion"]
    pd.testing.assert_frame_equal(particion, ANTERIOR.L.particionar(datos))
    mascara = particion.rol.eq("descubrimiento_lexico").to_numpy()
    anteriores = pd.read_csv(ruta / "predicciones_validacion.csv")
    return datos, mascara, anteriores, fuentes


def asignar_folds(datos, mascara):
    particiones = list(ANTERIOR.particiones_validacion(datos, mascara))
    asignacion = datos[["intervencion_id", "meeting_id"]].copy()
    asignacion["fold_validacion"] = 0  # cero = grupo fijo, solo entra en train
    asignacion["texto_identico_en_train"] = False
    visitas = np.zeros(len(datos), dtype=int)
    for numero, train, val in particiones:
        asignacion.loc[val, "fold_validacion"] = numero
        textos_train = set(datos.iloc[train].texto.map(norm))
        asignacion.loc[val, "texto_identico_en_train"] = datos.iloc[val].texto.map(norm).isin(textos_train).to_numpy()
        visitas[val] += 1
    np.testing.assert_array_equal(visitas, (~mascara).astype(int))
    assert asignacion.groupby("meeting_id").fold_validacion.nunique().eq(1).all()
    return particiones, asignacion


# ---- 3. Entrenamiento por fold; A se calcula una sola vez para seis B ----
def evaluar_fold(train, val):
    modelo = ANTERIOR.BASELINE.entrenar_modelo(train, ANTERIOR.PARAMETROS_TFIDF, ANTERIOR.PARAMETROS_LR)
    relevancia = modelo["clasificador_a"].predict(modelo["vector_a"].transform(val.texto))
    relevantes = train.es_relevante.astype(str).eq("1")
    textos, etiquetas = train.loc[relevantes, "texto"], train.loc[relevantes, "etiqueta"]
    resultados = {}
    for longitud in LONGITUDES:
        if longitud == 1:
            vector, clasificador = modelo["vector_b"], modelo["clasificador_b"]
        else:
            vector = TfidfVectorizer(**{**ANTERIOR.PARAMETROS_TFIDF, "ngram_range": (1, longitud)})
            vector.fit(textos)
            clasificador = LogisticRegression(**ANTERIOR.PARAMETROS_LR).fit(vector.transform(textos), etiquetas)
        pred = np.where(relevancia == 0, "neutral", clasificador.predict(vector.transform(val.texto)))
        resultados[longitud] = (pred, {"vocabulario_a": len(modelo["vector_a"].vocabulary_),
                                     "vocabulario_b": len(vector.vocabulary_),
                                     "terminos_longitud_maxima_b": sum(len(t.split()) == longitud for t in vector.vocabulary_)})
    return resultados


def elegir(tabla):
    # Media sin redondear; solo un empate exacto favorece la menor longitud.
    return int(tabla.sort_values(["macro_f1_media", "ngram_max"], ascending=[False, True]).iloc[0].ngram_max)


def resumir(predicciones, folds):
    registros = []
    for longitud, sub in predicciones.groupby("ngram_max", sort=True):
        puntos = folds[folds.ngram_max.eq(longitud)]
        registros.append({"ngram_max": int(longitud), **ANTERIOR.metricas(sub.etiqueta, sub.pred),
                          "macro_f1_media": float(puntos.macro_f1.mean()),
                          "macro_f1_sd": float(puntos.macro_f1.std(ddof=1)),
                          "macro_f1_min": float(puntos.macro_f1.min()),
                          "macro_f1_max": float(puntos.macro_f1.max()),
                          "vocabulario_b_media": float(puntos.vocabulario_b.mean()),
                          "vocabulario_b_min": int(puntos.vocabulario_b.min()),
                          "vocabulario_b_max": int(puntos.vocabulario_b.max())})
    return pd.DataFrame(registros)


def verificar_anclas(predicciones, anteriores):
    # Los límites 1 y 4 tienen que reproducir exactamente la corrida anterior.
    for longitud, variante in [(1, "unigramas"), (4, "ngramas_1_4")]:
        columnas = ["intervencion_id", "meeting_id", "etiqueta", "fold", "pred"]
        actual = predicciones.loc[predicciones.ngram_max.eq(longitud), columnas].sort_values("intervencion_id").reset_index(drop=True)
        previo = anteriores.loc[anteriores.variante.eq(variante), columnas].sort_values("intervencion_id").reset_index(drop=True)
        pd.testing.assert_frame_equal(actual, previo)


# ---- 4. Informe: selección interna, no óptimo universal ni test nuevo ----
def construir_informe(tabla, resumen):
    ganador = resumen["seleccion"]["ngram_max_b"]
    mejor = tabla.set_index("ngram_max").loc[ganador]
    lineas = ["# Búsqueda del límite de n-gramas: 1–6", "",
              f"**Mejor límite observado: (1,{ganador})**, con macro-F1 medio **{mejor.macro_f1_media:.4f}**. Es el mejor entre seis límites con esta configuración, no un óptimo universal.", "",
              "## Diseño", "",
              "- Misma reserva IA de 793 intervenciones / 80 reuniones. Cinco folds: 1.193–1.194 para train y 158–159 para validación. Las 559 intervenciones del grupo de descubrimiento anterior siempre entran solo en train.",
              "- A (relevancia) fija en unigramas; solo cambia B (postura): (1,1), (1,2), (1,3), (1,4), (1,5), (1,6). Sin diccionario.",
              "- min_df=3, max_df=0,9, C=2, balanced, sublinear_tf y normalización/tokenizador estándar del baseline. No se cambian otros parámetros ni se amplía la búsqueda tras ver resultados.",
              "- Vocabularios, IDF y clasificadores se ajustan exclusivamente dentro del train de cada fold. A se comparte entre las seis variantes.",
              "- Selección por mayor macro-F1 medio sin redondear; empate exacto: menor longitud. El OOF conjunto no decide el ganador.", "",
              "## Resultados", "",
              "DE es desviación estándar muestral entre los cinco folds; no es un intervalo de confianza. F1 H/D y recall corresponden al OOF conjunto.", "",
              "| Límite | Macro-F1 medio | DE folds | Macro-F1 conjunto | F1 H | F1 D | Vocabulario B medio |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for r in tabla.itertuples():
        lineas.append(f"| (1,{r.ngram_max}) | {r.macro_f1_media:.4f} | {r.macro_f1_sd:.4f} | {r.macro_f1:.4f} | {r.f1_hawkish:.4f} | {r.f1_dovish:.4f} | {r.vocabulario_b_media:,.0f} |")
    lineas += ["", "| Límite | Precisión H | Recall H | Precisión D | Recall D |", "|---|---:|---:|---:|---:|"]
    for r in tabla.itertuples():
        lineas.append(f"| (1,{r.ngram_max}) | {r.precision_hawkish:.4f} | {r.recall_hawkish:.4f} | {r.precision_dovish:.4f} | {r.recall_dovish:.4f} |")
    lineas += ["", "## Estabilidad y lectura del resultado", ""]
    for referencia in [1, 4]:
        delta = resumen["diferencias_pareadas"][str(ganador)][str(referencia)]
        lineas.append(f"- Ganador frente a (1,{referencia}): diferencia media {delta['media']:+.4f}; mejora en {delta['positivos']}/5 folds y empeora en {delta['negativos']}/5.")
    orden = tabla.sort_values(["macro_f1_media", "ngram_max"], ascending=[False, True])
    segundo = orden.iloc[1]
    lineas += [f"- Diferencia con el segundo, (1,{int(segundo.ngram_max)}): {mejor.macro_f1_media - segundo.macro_f1_media:+.4f}. No demuestra superioridad estadística con cinco folds.",
               "- Más n-gramas no garantizan mejor resultado: aumentan el vocabulario y cambian los pesos TF-IDF. El tamaño mostrado es el del train relevante de B, no un vocabulario aprendido de validación.", "",
               "## Límites y qué queda decidido", "",
               "- Referencia IA: 69 hawkish / 49 dovish / 675 neutral. La accuracy y F1 neutral también quedan en el CSV, junto a todos los soportes.",
               f"- {resumen['textos_validacion_identicos_train']}/793 textos de validación son idénticos a alguno de su train tras normalizar espacios, aun con reuniones disjuntas. No se modifica la partición después de evaluar.",
               "- La reserva y los resultados de longitudes 1 y 4 ya eran conocidos; también se había seleccionado el baseline sobre las 1.352 IA. Esta búsqueda es desarrollo/selección interna adaptativa, no un test independiente. La puntuación máxima puede ser optimista.",
               "- No se abrieron ni predijeron las 306 respuestas humanas. Tampoco se usó el catálogo descriptivo completo ni el diccionario para construir características.",
               f"- Se deja (1,{ganador}) como candidato seleccionado de esta búsqueda. No se reajustó un modelo con las 1.352, no se puntuó el corpus y no se reemplazó TF-IDF v1. La confirmación independiente requiere otra evaluación y control de textos repetidos.", "",
               "## Artefactos y reproducción", "",
               "En `data/evaluacion/longitud_ngramas_v1/`: protocolo guardado antes de entrenar, asignación de folds, predicciones IA, resultados por fold, comparación, selección y manifiesto de hashes. Los límites 1 y 4 reproducen las predicciones del experimento anterior.", "",
               "```bash", "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/22_seleccionar_longitud_ngramas.py \\",
               "  --salida /ruta/nueva/evaluacion --informe /ruta/nueva/informe.md", "```", "",
               "Las rutas deben ser nuevas; no se sobrescriben resultados. La selección se limita a seis alternativas incluso si gana el extremo (1,6).", ""]
    return "\n".join(lineas)


# ---- 5. Congelar protocolo antes de entrenar; guardar sin sobrescritura ----
def ejecutar(salida=RUTA_SALIDA, informe=RUTA_INFORME):
    salida, informe = Path(salida), Path(informe)
    exigir_salidas_nuevas(salida, informe)
    datos, mascara, anteriores, fuentes = cargar_insumos()
    particiones, asignacion = asignar_folds(datos, mascara)
    for numero, _, val in particiones:
        previo = anteriores[anteriores.fold.eq(numero) & anteriores.variante.eq("unigramas")]
        assert set(datos.iloc[val].intervencion_id) == set(previo.intervencion_id)
    archivos = [Path(__file__), Path(ANTERIOR.__file__),
                ANTERIOR.L.RUTA_LEXICO / "particion.csv",
                ANTERIOR.L.RUTA_VALIDACION / "protocolo_validacion.json",
                ANTERIOR.L.RUTA_VALIDACION / "metricas.json",
                ANTERIOR.L.RUTA_VALIDACION / "predicciones_validacion.csv"]
    fuentes.update({str(p.relative_to(config.RUTA_REPO)): sha256(p) for p in archivos})
    salida.mkdir(parents=True)
    escribir = ANTERIOR.ESCRITURA.escribir_json
    escribir(salida / "protocolo.json", {
        "version": "longitud_ngramas_v1", "fecha_inicio_utc": datetime.now(timezone.utc).isoformat(),
        "longitudes_b": LONGITUDES, "parametros_tfidf_a": ANTERIOR.PARAMETROS_TFIDF,
        "parametros_lr": ANTERIOR.PARAMETROS_LR, "diccionario": False,
        "seleccion": "Mayor media macro-F1 no redondeada; empate exacto: menor longitud. No extender más allá de seis.",
        "particiones": "Idénticas a lexico_ngramas_v1: GroupKFold(5) sobre 793, 559 adicionales solo train.",
        "diagnosticos": "Macro-F1 medio/DE/min/max y conjunto; precisión/recall/F1/soporte, matrices, vocabulario B y diferencias pareadas frente a 1 y 4. No deciden el ganador.",
        "limites": "Nueva búsqueda autorizada tras conocer 1 y 4; reserva reutilizada y textos repetidos. Selección interna, no confirmación independiente; gold no se abre ni predice.",
        "sin_refit_final_ni_reemplazo": True, "version_codebook": "v2",
        "versiones": {"numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__},
        "sha256_insumos": fuentes})
    asignacion.to_csv(salida / "asignacion_folds.csv", index=False)
    predicciones, registros = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for numero, train, val in particiones:
            for longitud, (pred, dimensiones) in evaluar_fold(datos.iloc[train], datos.iloc[val]).items():
                sub = datos.iloc[val][["intervencion_id", "meeting_id", "etiqueta"]].copy()
                sub["ngram_max"], sub["fold"], sub["pred"] = longitud, numero, pred
                predicciones.append(sub)
                registro = {"fold": numero, "ngram_max": longitud, "n_train": len(train), "n_validacion": len(val),
                            **dimensiones, **ANTERIOR.metricas(sub.etiqueta, sub.pred)}
                registros.append(registro)
                print(f"Fold {numero} (1,{longitud}): macro-F1={registro['macro_f1']:.4f}; vocabulario B={dimensiones['vocabulario_b']}", flush=True)
    predicciones, folds = pd.concat(predicciones, ignore_index=True), pd.DataFrame(registros)
    assert not predicciones.duplicated(["intervencion_id", "ngram_max"]).any()
    for longitud, sub in predicciones.groupby("ngram_max"):
        assert set(sub.intervencion_id) == set(datos.loc[~mascara, "intervencion_id"])
    assert set(predicciones.ngram_max) == set(LONGITUDES)
    verificar_anclas(predicciones, anteriores)
    tabla = resumir(predicciones, folds)
    ganador = elegir(tabla)
    seleccion = {"ngram_max_b": ganador, "macro_f1_media": float(tabla.set_index("ngram_max").loc[ganador, "macro_f1_media"]),
                 "regla": "Mayor media no redondeada; empate exacto favorece menor longitud", "solo_seleccion_interna": True}
    pares = folds.pivot(index="fold", columns="ngram_max", values="macro_f1")
    diferencias = {}
    for longitud in LONGITUDES:
        diferencias[str(longitud)] = {}
        for referencia in [1, 4]:
            delta = pares[longitud] - pares[referencia]
            diferencias[str(longitud)][str(referencia)] = {"media": float(delta.mean()), "por_fold": delta.to_dict(),
                                                        "positivos": int(delta.gt(0).sum()), "negativos": int(delta.lt(0).sum())}
    resumen = {"seleccion": seleccion, "clases": ANTERIOR.L.CLASES,
               "matrices_confusion": {str(n): confusion_matrix(sub.etiqueta, sub.pred, labels=ANTERIOR.L.CLASES).tolist()
                                      for n, sub in predicciones.groupby("ngram_max")},
               "diferencias_pareadas": diferencias,
               "textos_validacion_identicos_train": int(asignacion.texto_identico_en_train.sum()),
               "anclas_1_y_4_identicas": True, "gold_abierto_o_predicho": False,
               "refit_final_o_reemplazo": False}
    predicciones.to_csv(salida / "predicciones_validacion.csv", index=False)
    folds.to_csv(salida / "resultados_folds.csv", index=False)
    tabla.to_csv(salida / "comparacion_longitudes.csv", index=False)
    escribir(salida / "seleccion.json", seleccion)
    escribir(salida / "metricas.json", resumen)
    informe.parent.mkdir(parents=True, exist_ok=True)
    with informe.open("x", encoding="utf-8") as archivo:
        archivo.write(construir_informe(tabla, resumen))
    escribir(salida / "manifest.json", {"fecha_fin_utc": datetime.now(timezone.utc).isoformat(),
                                       "sha256_salidas": {p.name: sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},
                                       "sha256_informe": sha256(informe)})
    print(tabla.to_string(index=False))
    print(f"Seleccionado (1,{ganador}). Informe: {informe}")
    return resumen


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=RUTA_SALIDA)
    parser.add_argument("--informe", type=Path, default=RUTA_INFORME)
    args = parser.parse_args(argv)
    ejecutar(args.salida, args.informe)


if __name__ == "__main__":
    main()
