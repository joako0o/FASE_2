"""Compara cuatro variantes en validación IA con descubrimiento léxico separado.

El diccionario se congela antes de ejecutar este script. Descubrimiento entra
solo en train; la reserva IA aporta los cinco folds de validación. No se lee el
Excel humano ni se recalculan métricas sobre gold. No cambia el modelo vigente.

Uso: python scripts/21_evaluar_lexico.py [--lexico carpeta] [--salida carpeta_nueva]
"""

# ---- 1. Configuración fija y dependencias ----
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import sklearn
import scipy
from scipy.sparse import csr_matrix, hstack
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import GroupKFold

import config
import lexico_ngramas as L
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

BASELINE = cargar_script("15_baseline_tfidf.py")
ESCRITURA = cargar_script("18_seleccionar_tfidf.py")
VARIANTES = [(1, False, "unigramas"), (1, True, "unigramas_lexico"),
             (4, False, "ngramas_1_4"), (4, True, "ngramas_1_4_lexico")]
PARAMETROS_TFIDF = {**BASELINE.PARAMS_TFIDF, "ngram_range": (1, 1), "min_df": 3}
PARAMETROS_LR = {**BASELINE.PARAMS_LR, "C": 2.0}


# ---- 2. Verificaciones antes de cualquier entrenamiento ----
def cargar_insumos(ruta):
    datos = BASELINE.cargar_muestra()
    particion = pd.read_csv(ruta / "particion.csv")
    assert datos.intervencion_id.tolist() == particion.intervencion_id.tolist()
    assert datos.meeting_id.tolist() == particion.meeting_id.tolist()
    pd.testing.assert_frame_equal(particion, L.particionar(datos))
    descubrimiento = particion.rol.eq("descubrimiento_lexico").to_numpy()
    assert not set(datos.loc[descubrimiento, "meeting_id"]) & set(datos.loc[~descubrimiento, "meeting_id"])
    candidatos = pd.read_csv(ruta / "candidatos_revision.csv")
    diccionario = pd.read_csv(ruta / "diccionario_v1.csv", keep_default_na=False)
    L.validar_diccionario(diccionario, candidatos)
    protocolo = json.loads((ruta / "protocolo.json").read_text())
    for archivo, huella in protocolo["sha256_insumos"].items():
        assert sha256(config.RUTA_REPO / archivo) == huella, f"insumo de descubrimiento alterado: {archivo}"
    extraccion = json.loads((ruta / "extraccion_manifest.json").read_text())
    for archivo, huella in extraccion["sha256_archivos"].items():
        assert sha256(ruta / archivo) == huella, f"extracción alterada: {archivo}"
    revision = json.loads((ruta / "revision_manifest.json").read_text())
    assert sha256(ruta / "diccionario_v1.csv") == revision["sha256_diccionario"]
    assert sha256(ruta / "contextos_revision.csv") == revision["sha256_contextos"]
    assert sha256(ruta / "candidatos_revision.csv") == revision["sha256_candidatos"]
    assert protocolo["evaluacion_prefijada"]["variantes"] == [v[2] for v in VARIANTES]
    contextos = pd.read_csv(ruta / "contextos_revision.csv")
    assert set(contextos.intervencion_id) <= set(datos.loc[descubrimiento, "intervencion_id"])
    return datos, descubrimiento, diccionario, protocolo


def particiones_validacion(datos, descubrimiento):
    reserva = np.flatnonzero(~descubrimiento)
    fijos = np.flatnonzero(descubrimiento)
    for numero, (train, validacion) in enumerate(GroupKFold(n_splits=5).split(reserva, groups=datos.iloc[reserva].meeting_id), 1):
        indices_train = np.concatenate([fijos, reserva[train]])
        indices_val = reserva[validacion]
        assert not set(indices_train) & set(indices_val)
        assert not set(datos.iloc[indices_train].meeting_id) & set(datos.iloc[indices_val].meeting_id)
        assert descubrimiento[indices_val].sum() == 0
        yield numero, indices_train, indices_val


# ---- 3. Ajuste dentro de fold; solo B recibe el diccionario ----
def predecir_variantes(train, validacion, diccionario):
    modelo_a_b = BASELINE.entrenar_modelo(train, PARAMETROS_TFIDF, PARAMETROS_LR)
    pred_a = modelo_a_b["clasificador_a"].predict(modelo_a_b["vector_a"].transform(validacion.texto))
    relevantes = train.es_relevante.astype(str).eq("1")
    textos_train = train.loc[relevantes, "texto"]
    y_train = train.loc[relevantes, "etiqueta"]
    senales_train = csr_matrix(L.matriz_senales(textos_train.tolist(), diccionario))
    senales_val = csr_matrix(L.matriz_senales(validacion.texto.tolist(), diccionario))
    salidas = {}
    for longitud in [1, 4]:
        if longitud == 1:
            vector = modelo_a_b["vector_b"]
        else:
            vector = TfidfVectorizer(**{**PARAMETROS_TFIDF, "ngram_range": (1, longitud)})
            vector.fit(textos_train)
        x_train = vector.transform(textos_train)
        x_val = vector.transform(validacion.texto)
        for _, agregar, nombre in [v for v in VARIANTES if v[0] == longitud]:
            if agregar:
                clasificador = LogisticRegression(**PARAMETROS_LR).fit(hstack([x_train, senales_train], format="csr"), y_train)
                pred_b = clasificador.predict(hstack([x_val, senales_val], format="csr"))
            elif longitud == 1:
                pred_b = modelo_a_b["clasificador_b"].predict(x_val)
            else:
                pred_b = LogisticRegression(**PARAMETROS_LR).fit(x_train, y_train).predict(x_val)
            salidas[nombre] = np.where(pred_a == 0, "neutral", pred_b)
    return salidas


def metricas(reales, pred):
    precision, recall, f1, soporte = precision_recall_fscore_support(reales, pred, labels=L.CLASES, zero_division=0)
    return {"accuracy": float(accuracy_score(reales, pred)), "macro_f1": float(f1.mean()),
            **{f"f1_{c}": float(f) for c, f in zip(L.CLASES, f1)},
            **{f"recall_{c}": float(r) for c, r in zip(L.CLASES, recall)},
            **{f"precision_{c}": float(p) for c, p in zip(L.CLASES, precision)},
            **{f"n_{c}": int(n) for c, n in zip(L.CLASES, soporte)}}


# ---- 4. Informe generado sin inspeccionar ni alterar el test humano ----
def construir_informe(resumen, tabla, revisado):
    lineas = ["# N-gramas y diccionario de señales: revisión y validación IA", "",
              "## Qué se hizo", "",
              f"- De las 1.352 intervenciones IA, {resumen['n_descubrimiento']} de {resumen['reuniones_descubrimiento']} reuniones se reservaron para construir y revisar el léxico.",
              f"- Las otras {resumen['n_validacion']} intervenciones aportaron cinco folds de validación por reunión. Descubrimiento se agrega solo al train de cada fold.",
              "- Umbral prefijado: n-gramas de 1–4 palabras en al menos 5 intervenciones y 3 reuniones distintas.",
              f"- Catálogo de descubrimiento: {resumen['n_catalogo_descubrimiento']} n-gramas. Revisados por IA: {len(revisado)} candidatos, con hasta 3 contextos cada uno; no revisión humana ni lectura de todas las ocurrencias.",
              "- Priorización por frecuencia y asociación relativa H/D, sin asignar la dirección automáticamente por esa asociación.",
              "- No se leyó el Excel humano, no se volvió a predecir gold y no se reemplazó TF-IDF v1.", "",
              "## Diccionario revisado", "", "| Categoría | Cantidad |", "|---|---:|"]
    lineas += [f"| {c} | {n} |" for c, n in revisado.senal.value_counts().items()]
    lineas += ["", "### Señales direccionales", "", "| Expresión | Señal | Precaución / razón |", "|---|---|---|"]
    lineas += [f"| {r.ngrama} | {r.senal} | {r.justificacion} |" for r in revisado[revisado.senal.isin(["restrictiva", "expansiva"])].itertuples()]
    lineas += ["", "**Asociación no es significado:** `impulso monetario` es contextual (puede retirarse o ampliarse); `vota por mantener` depende del menú/ciclo; `Marfán agradece` es cortesía, aunque aparezca asociado a dovish.", "",
               "Las características son cuatro indicadores binarios (restrictiva/expansiva afirmada/negada) añadidos a B. Negación izquierda de hasta tres tokens; no invierte etiquetas. La coincidencia más larga evita solapamientos. No resuelve negación posterior, atribución, pasado, menú o condicionales.", "",
               "## Comparación sobre la misma reserva IA", "",
               "A (relevancia) queda fijo; B usa unigramas o n-gramas 1–4, sin/con diccionario. C=2, min_df=3, balanced, sin nueva búsqueda. TF-IDF usa el tokenizador estándar del baseline; el léxico conserva tokens de una letra y límites de oración.", "",
               "| Variante | Macro-F1 medio folds | Macro-F1 OOF conjunto | F1 H | F1 D | Recall H | Recall D |",
               "|---|---:|---:|---:|---:|---:|---:|"]
    for r in tabla.itertuples():
        lineas.append(f"| {r.variante} | {r.macro_f1_media:.4f} | {r.macro_f1:.4f} | {r.f1_hawkish:.4f} | {r.f1_dovish:.4f} | {r.recall_hawkish:.4f} | {r.recall_dovish:.4f} |")
    lineas += ["", "### Diferencia de añadir el diccionario (media de folds)", ""]
    for nombre, diferencia in resumen["diferencias_pareadas"].items():
        lineas.append(f"- {nombre}: **{diferencia['delta_macro_f1_media']:+.4f}**; mejora en {diferencia['folds_positivos']}/5 folds, empeora en {diferencia['folds_negativos']}/5.")
    lineas += ["", "## Interpretación y límites", "",
               "Soporte de validación: " + ", ".join(f"{c}: {int(tabla.iloc[0]['n_' + c])}" for c in L.CLASES) + ".",
               "Esta es una comparación exploratoria interna, no un nuevo test humano. La reserva no se usó para extraer/revisar el léxico, pero pertenece al training IA sobre el que ya se eligió el baseline anterior. No interpretar pequeñas diferencias como significativas con solo cinco folds.",
               "No comparar directamente estos números con 0,7264 de la búsqueda previa (otra composición de train/validación) ni con el recall humano 55,1 % / 53,1 %. No se midió una mejora humana en esta sesión.",
               "Los umbrales de frecuencia dejan fuera expresiones poco comunes, aunque puedan ser importantes. Los candidatos no revisados NO reciben automáticamente una etiqueta semántica.",
               f"- Cobertura de señales en reserva: {resumen['cobertura_senales_validacion']['alguna_senal']}/{resumen['n_validacion']} intervenciones.",
               f"- El catálogo completo de las 1.352, generado solo después de congelar y validar, tiene {resumen['n_catalogo_completo']} n-gramas que superan los mismos umbrales. Es descriptivo: no se usó para modificar esta versión.",
               "- Los datos, etiquetas, codebook y examen humano anteriores permanecen intactos. No hay adopción automática de la variante con mayor puntuación.", "",
               "## Archivos útiles", "",
               "- `data/lexico/ngramas_v1/diccionario_v1.csv`: 73 decisiones con categoría y justificación.",
               "- `contextos_revision.csv`: ejemplos y sus IDs de descubrimiento.",
               "- `catalogo_descubrimiento.csv` / `candidatos_revision.csv`: frecuencias, reuniones, TF-IDF medio y asociaciones usadas en revisión.",
               "- `data/evaluacion/lexico_ngramas_v1/catalogo_training_completo.csv`: catálogo completo descriptivo.",
               "- `catalogo_revisado.csv` en esa carpeta: catálogo completo enlazado con categorías revisadas; el resto queda `no_revisado`.",
               "- `comparacion_variantes.csv`, `resultados_folds.csv`, `predicciones_validacion.csv`, `metricas.json`: evaluación y cobertura.",
               "- Los manifiestos registran hashes de diccionario, partición, entradas y salidas. No se sobrescriben versiones anteriores.", "",
               "Para repetir: script 20 hacia una carpeta nueva; conservar la revisión v1 y sus hashes; script 21 con `--lexico` y `--salida` nuevos. Las decisiones de revisión son un artefacto manual del agente, no una etiqueta que el script vuelva a generar.", ""]
    return "\n".join(lineas)


# ---- 5. Ejecución, artefactos y catálogo descriptivo posterior ----
def ejecutar(ruta_lexico=L.RUTA_LEXICO, salida=L.RUTA_VALIDACION, informe=None):
    ruta_lexico, salida = Path(ruta_lexico), Path(salida)
    informe = Path(informe) if informe else config.RUTA_REPO / "docs/LEXICO_NGRAMAS.md"
    exigir_salidas_nuevas(salida, informe)
    datos, descubrimiento, diccionario, protocolo = cargar_insumos(ruta_lexico)
    salida.mkdir(parents=True)
    dependencias = ["scripts/15_baseline_tfidf.py", "scripts/18_seleccionar_tfidf.py",
                    "scripts/utilidades.py", "scripts/config.py",
                    "data/muestras/piloto_300_tandas.csv", "data/muestras/escalado_tandas.csv",
                    "data/muestras/gold_ciego_300.csv"]
    ESCRITURA.escribir_json(salida / "protocolo_validacion.json", {
        "fecha_inicio_utc": datetime.now(timezone.utc).isoformat(),
        "protocolo_descubrimiento": protocolo,
        "sha256_diccionario_congelado": sha256(ruta_lexico / "diccionario_v1.csv"),
        "sha256_particion": sha256(ruta_lexico / "particion.csv"),
        "sha256_evaluador": sha256(Path(__file__)), "sha256_lexico_codigo": sha256(config.RUTA_REPO / "scripts/lexico_ngramas.py"),
        "sha256_dependencias": {p: sha256(config.RUTA_REPO / p) for p in dependencias},
        "sha256_revision_manifest": sha256(ruta_lexico / "revision_manifest.json"),
        "version_codebook": "v2", "parametros_tfidf_base": PARAMETROS_TFIDF,
        "parametros_lr": PARAMETROS_LR,
        "versiones": {"numpy": np.__version__, "pandas": pd.__version__,
                      "scikit_learn": sklearn.__version__, "scipy": scipy.__version__},
        "regla": "Ningún cambio de diccionario/parámetros tras esta validación; gold humano no se usa.",
    })
    salidas, folds = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for numero, train, val in particiones_validacion(datos, descubrimiento):
            variantes = predecir_variantes(datos.iloc[train], datos.iloc[val], diccionario)
            for nombre, pred in variantes.items():
                filas = datos.iloc[val][["intervencion_id", "meeting_id", "etiqueta"]].copy()
                filas["variante"], filas["fold"], filas["pred"] = nombre, numero, pred
                salidas.append(filas)
                resultado = {"fold": numero, "variante": nombre, "n_train": len(train), "n_validacion": len(val),
                             **metricas(filas.etiqueta, filas.pred)}
                folds.append(resultado)
                print(f"Fold {numero} {nombre}: macroF1={resultado['macro_f1']:.4f}", flush=True)
    oof, por_fold = pd.concat(salidas, ignore_index=True), pd.DataFrame(folds)
    assert not oof.duplicated(["intervencion_id", "variante"]).any()
    assert set(oof.intervencion_id) == set(datos.loc[~descubrimiento, "intervencion_id"])
    assert not set(oof.intervencion_id) & set(datos.loc[descubrimiento, "intervencion_id"])
    resumenes, matrices = [], {}
    for _, _, nombre in VARIANTES:
        sub = oof[oof.variante.eq(nombre)]
        assert len(sub) == int((~descubrimiento).sum())
        resultado = {"variante": nombre, **metricas(sub.etiqueta, sub.pred),
                     "macro_f1_media": float(por_fold.loc[por_fold.variante.eq(nombre), "macro_f1"].mean())}
        resumenes.append(resultado)
        matrices[nombre] = confusion_matrix(sub.etiqueta, sub.pred, labels=L.CLASES).tolist()
    tabla = pd.DataFrame(resumenes)
    diferencias = {}
    for nombre in ["unigramas", "ngramas_1_4"]:
        pares = por_fold.pivot(index="fold", columns="variante", values="macro_f1")
        delta = pares[nombre + "_lexico"] - pares[nombre]
        diferencias[nombre] = {"delta_macro_f1_media": float(delta.mean()), "por_fold": delta.to_dict(),
                              "folds_positivos": int(delta.gt(0).sum()), "folds_negativos": int(delta.lt(0).sum())}
    # Solo ahora se genera el catálogo completo. No alimenta la revisión ni CV.
    completo = L.construir_catalogo(datos)
    completo.to_csv(salida / "catalogo_training_completo.csv", index=False)
    revisado = completo.merge(diccionario[["ngrama", "senal", "justificacion"]], on="ngrama", how="left", validate="one_to_one")
    revisado["senal"] = revisado.senal.fillna("no_revisado")
    revisado.to_csv(salida / "catalogo_revisado.csv", index=False)
    oof.to_csv(salida / "predicciones_validacion.csv", index=False)
    por_fold.to_csv(salida / "resultados_folds.csv", index=False)
    tabla.to_csv(salida / "comparacion_variantes.csv", index=False)
    senales = L.matriz_senales(datos.loc[~descubrimiento, "texto"].tolist(), diccionario)
    resumen = {"fecha_fin_utc": datetime.now(timezone.utc).isoformat(), "n_descubrimiento": int(descubrimiento.sum()),
               "reuniones_descubrimiento": datos.loc[descubrimiento, "meeting_id"].nunique(),
               "n_validacion": int((~descubrimiento).sum()), "n_catalogo_descubrimiento": len(pd.read_csv(ruta_lexico / "catalogo_descubrimiento.csv")),
               "n_catalogo_completo": len(completo), "revision": diccionario.senal.value_counts().to_dict(),
               "comparacion": tabla.to_dict("records"), "diferencias_pareadas": diferencias,
               "clases_matrices": L.CLASES, "matrices_confusion": matrices,
               "cobertura_senales_validacion": {"alguna_senal": int(senales.any(axis=1).sum()),
                                                **{c: int(senales[:, i].sum()) for i, c in enumerate(L.COLUMNAS_SENALES)}},
               "gold_leido_o_predicho": False, "modelo_vigente_reemplazado": False,
               "sha256_salidas": {p.name: sha256(p) for p in sorted(salida.iterdir()) if p.is_file()}}
    ESCRITURA.escribir_json(salida / "metricas.json", resumen)
    informe.parent.mkdir(parents=True, exist_ok=True)
    with informe.open("x", encoding="utf-8") as archivo:
        archivo.write(construir_informe(resumen, tabla, diccionario))
    print(tabla[["variante", "macro_f1_media", "macro_f1", "f1_hawkish", "f1_dovish"]].to_string(index=False))
    print(f"Informe: {informe}")
    return resumen


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lexico", type=Path, default=L.RUTA_LEXICO)
    parser.add_argument("--salida", type=Path, default=L.RUTA_VALIDACION)
    parser.add_argument("--informe", type=Path)
    args = parser.parse_args(argv)
    ejecutar(args.lexico, args.salida, args.informe)


if __name__ == "__main__":
    main()
