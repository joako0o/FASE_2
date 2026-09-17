"""Diagnóstico postselección de (1,4), en cinco folds IA ya conocidos.

Reconstruye modelos idénticos, no optimiza ni entrena un híbrido. Explica
márgenes lineales, no causalidad ni cambios de probabilidad al borrar palabras.
Nunca lee las respuestas humanas; los ejemplos revisados son desarrollo IA.
"""
# ---- 1. Configuración del diagnóstico, separada de experimentos congelados ----
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

import config
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

BUSQUEDA = cargar_script("22_seleccionar_longitud_ngramas.py")
BASE = BUSQUEDA.ANTERIOR
RUTA_SALIDA = config.RUTA_DATOS / "evaluacion/influencias_ngramas_v1"
TOP_GLOBAL = 25
TOP_LOCAL = 5


# ---- 2. Coeficientes contrastivos y contribuciones locales exactas ----
def contrastes(modelo, etapa):
    if etapa == "A":
        assert list(modelo.classes_) == [0, 1]
        return {"relevante_vs_irrelevante": modelo.coef_[0],
                "irrelevante_vs_relevante": -modelo.coef_[0]}
    indices = {c: i for i, c in enumerate(modelo.classes_)}
    salida = {c + "_vs_resto": modelo.coef_[i] - np.delete(modelo.coef_, i, axis=0).mean(axis=0)
              for c, i in indices.items()}
    salida["hawkish_vs_dovish"] = modelo.coef_[indices["hawkish"]] - modelo.coef_[indices["dovish"]]
    salida["dovish_vs_hawkish"] = -salida["hawkish_vs_dovish"]
    return salida


def descomponer(fila, pesos, intercepto, vocabulario, frecuencias):
    indices, valores = fila.indices, fila.data
    aportes = valores * pesos[indices]
    detalle = []
    for signo, posiciones in [("a_favor", np.flatnonzero(aportes > 0)), ("en_contra", np.flatnonzero(aportes < 0))]:
        orden = sorted(posiciones, key=lambda j: (-abs(aportes[j]), vocabulario[indices[j]]))[:TOP_LOCAL]
        for rango, j in enumerate(orden, 1):
            detalle.append({"sentido": signo, "rango": rango, "termino": vocabulario[indices[j]],
                            "tfidf": float(valores[j]), "coef_contraste": float(pesos[indices[j]]),
                            "aporte": float(aportes[j]), "df_train": int(frecuencias[indices[j]])})
    suma = float(aportes.sum())
    return {"intercepto": float(intercepto), "suma_aportes": suma,
            "residuo_no_mostrado": suma - sum(t["aporte"] for t in detalle),
            "margen": suma + float(intercepto)}, detalle


def tabla_coeficientes(vector, modelo, matriz, reuniones, etapa, fold):
    presentes = matriz.copy()
    presentes.data[:] = 1
    documentos = np.asarray(presentes.sum(axis=0)).ravel().astype(int)
    frecuencia_reuniones = np.zeros(matriz.shape[1], dtype=int)
    reuniones = np.asarray(reuniones)
    for reunion in np.unique(reuniones):
        frecuencia_reuniones += np.asarray(presentes[reuniones == reunion].sum(axis=0)).ravel() > 0
    tabla = pd.DataFrame({"termino": vector.get_feature_names_out(), "df_train": documentos,
                          "reuniones_train": frecuencia_reuniones, "etapa": etapa, "fold": fold})
    for nombre, pesos in contrastes(modelo, etapa).items():
        tabla[nombre] = pesos
    return tabla


def resumir_coeficientes(tablas):
    # La unión de top positivos define qué términos se reportan. Se consultan
    # sus pesos en TODOS los folds donde existen, no solo donde entraron al top.
    tops, estabilidad, seleccionadas = [], [], []
    for etapa in ["A", "B"]:
        subtablas = [t for t in tablas if t.etapa.iloc[0] == etapa]
        columnas = [c for c in subtablas[0].columns if c not in {"termino", "df_train", "reuniones_train", "etapa", "fold"}]
        for contraste in columnas:
            terminos = set()
            for tabla in subtablas:
                top = tabla[tabla[contraste] > 0].sort_values([contraste, "termino"], ascending=[False, True]).head(TOP_GLOBAL)
                terminos.update(top.termino)
                top = top[["fold", "etapa", "termino", "df_train", "reuniones_train", contraste]].rename(columns={contraste: "coef_contraste"})
                top["contraste"], top["rango"] = contraste, range(1, len(top) + 1)
                tops.append(top)
            filas = pd.concat([t[t.termino.isin(terminos)][["fold", "etapa", "termino", "df_train", "reuniones_train", contraste]] for t in subtablas])
            filas = filas.rename(columns={contraste: "coef_contraste"}).assign(contraste=contraste)
            seleccionadas.append(filas)
            for termino, grupo in filas.groupby("termino", sort=True):
                pesos = grupo.coef_contraste
                estabilidad.append({"etapa": etapa, "contraste": contraste, "termino": termino,
                                    "folds_presente": len(grupo), "folds_positivo": int(pesos.gt(0).sum()),
                                    "folds_negativo": int(pesos.lt(0).sum()),
                                    "coef_medio": float(pesos.mean()), "coef_sd": float(pesos.std(ddof=0)),
                                    "coef_min": float(pesos.min()), "coef_max": float(pesos.max()),
                                    "df_train_min": int(grupo.df_train.min()), "df_train_max": int(grupo.df_train.max()),
                                    "reuniones_train_min": int(grupo.reuniones_train.min())})
    return pd.concat(tops, ignore_index=True), pd.concat(seleccionadas, ignore_index=True), pd.DataFrame(estabilidad)


# ---- 3. Reconstrucción de un fold, sin cambiar los parámetros seleccionados ----
def diagnosticar_fold(train, val, fold):
    modelo = BASE.BASELINE.entrenar_modelo(train, BASE.PARAMETROS_TFIDF, BASE.PARAMETROS_LR)
    relevantes = train.es_relevante.astype(str).eq("1")
    textos = train.loc[relevantes, "texto"]
    vector_b = TfidfVectorizer(**{**BASE.PARAMETROS_TFIDF, "ngram_range": (1, 4)})
    vector_b.fit(textos)
    matriz_b = vector_b.transform(textos)
    clasificador_b = LogisticRegression(**BASE.PARAMETROS_LR).fit(matriz_b, train.loc[relevantes, "etiqueta"])
    vector_a, clasificador_a = modelo["vector_a"], modelo["clasificador_a"]
    coeficientes = [tabla_coeficientes(vector_a, clasificador_a, vector_a.transform(train.texto), train.meeting_id, "A", fold),
                    tabla_coeficientes(vector_b, clasificador_b, matriz_b, train.loc[relevantes, "meeting_id"], "B", fold)]
    xa, xb = vector_a.transform(val.texto), vector_b.transform(val.texto)
    pred_a, pred_b = clasificador_a.predict(xa), clasificador_b.predict(xb)
    scores_a, scores_b = clasificador_a.decision_function(xa), clasificador_b.decision_function(xb)
    pred_final = np.where(pred_a == 0, "neutral", pred_b)
    indices = {c: i for i, c in enumerate(clasificador_b.classes_)}
    h, d = indices["hawkish"], indices["dovish"]
    casos, margenes, detalles = [], [], []
    for posicion, fila in enumerate(val.itertuples()):
        orden = np.argsort(scores_b[posicion])
        ganador, segundo = indices[pred_b[posicion]], int(orden[-2])
        caso = {"intervencion_id": fila.intervencion_id, "meeting_id": fila.meeting_id, "fold": fold,
                "etiqueta_ia": fila.etiqueta, "relevancia_ia": int(fila.es_relevante),
                "pred_a": int(pred_a[posicion]), "pred_b_sin_mascara": pred_b[posicion],
                "pred": pred_final[posicion], "acierto": fila.etiqueta == pred_final[posicion],
                "confusion_hd": {fila.etiqueta, pred_final[posicion]} == {"hawkish", "dovish"},
                "texto": fila.texto}
        casos.append(caso)
        explicaciones = [
            ("A", "relevante_vs_irrelevante", xa[posicion], clasificador_a.coef_[0], clasificador_a.intercept_[0], scores_a[posicion], 0),
            ("B", str(pred_b[posicion]) + "_vs_" + str(clasificador_b.classes_[segundo]), xb[posicion],
             clasificador_b.coef_[ganador] - clasificador_b.coef_[segundo],
             clasificador_b.intercept_[ganador] - clasificador_b.intercept_[segundo], scores_b[posicion, ganador] - scores_b[posicion, segundo], 1),
            ("HD", "hawkish_vs_dovish", xb[posicion], clasificador_b.coef_[h] - clasificador_b.coef_[d],
             clasificador_b.intercept_[h] - clasificador_b.intercept_[d], scores_b[posicion, h] - scores_b[posicion, d], 1)]
        for etapa, contraste, x, pesos, intercepto, esperado, idx_tabla in explicaciones:
            tabla = coeficientes[idx_tabla]
            valores, detalle = descomponer(x, pesos, intercepto, tabla.termino.to_numpy(), tabla.df_train.to_numpy())
            assert np.isclose(valores["margen"], esperado, rtol=1e-9, atol=1e-9)
            comunes = {"intervencion_id": fila.intervencion_id, "fold": fold, "etapa": etapa, "contraste": contraste,
                       "b_activa": bool(pred_a[posicion] == 1)}
            margenes.append({**comunes, **valores})
            detalles.extend({**comunes, **t} for t in detalle)
    return coeficientes, casos, margenes, detalles


# ---- 4. Protocolo, artefactos y comprobación contra predicciones congeladas ----
def ejecutar(salida=RUTA_SALIDA):
    salida = Path(salida)
    exigir_salidas_nuevas(salida)
    datos, mascara, _, fuentes = BUSQUEDA.cargar_insumos()
    ruta = BUSQUEDA.RUTA_SALIDA
    protocolo = json.loads((ruta / "protocolo.json").read_text())
    manifest = json.loads((ruta / "manifest.json").read_text())
    for nombre, huella in protocolo["sha256_insumos"].items():
        assert sha256(config.RUTA_REPO / nombre) == huella
    for nombre, huella in manifest["sha256_salidas"].items():
        assert sha256(ruta / nombre) == huella
    seleccion = json.loads((ruta / "seleccion.json").read_text())
    assert seleccion["ngram_max_b"] == 4
    anteriores = pd.read_csv(ruta / "predicciones_validacion.csv")
    anteriores = anteriores[anteriores.ngram_max.eq(4)]
    particiones, asignacion = BUSQUEDA.asignar_folds(datos, mascara)
    fuentes.update(protocolo["sha256_insumos"])
    fuentes.update({str(p.relative_to(config.RUTA_REPO)): sha256(p) for p in [Path(__file__), ruta / "manifest.json", ruta / "seleccion.json", ruta / "predicciones_validacion.csv"]})
    salida.mkdir(parents=True)
    escribir = BASE.ESCRITURA.escribir_json
    escribir(salida / "protocolo.json", {"fecha_utc": datetime.now(timezone.utc).isoformat(),
        "version": "influencias_ngramas_v1", "alcance": "Diagnóstico postselección del candidato (1,4), cinco folds IA; no híbrido ni nueva búsqueda.",
        "top_global": TOP_GLOBAL, "top_local_por_signo": TOP_LOCAL,
        "coef_global": "B: clase menos promedio de las otras; H-D explícito. A: margen relevante-irrelevante (binario).",
        "local": "TF-IDF por diferencia de coeficientes, más intercepto. Verificar margen exacto y residuo omitido. B es contrafactual descriptivo cuando A fuerza neutral.",
        "estabilidad": "Unión top 25 positivos por fold/contraste; pesos en todos los folds donde existe. Ausencia no se imputa como cero. Entrenamientos solapados: estabilidad descriptiva, no independencia.",
        "limites": "Desarrollo IA con 34 textos repetidos. Inspeccionar errores permite hipótesis, no confirmar un híbrido con la misma reserva. Pesos/contribuciones no son causalidad ni etiquetas semánticas.",
        "gold_abierto_o_predicho": False, "version_codebook": "v2", "sha256_insumos": fuentes})
    tablas, casos, margenes, detalles = [], [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for numero, train, val in particiones:
            coef, c, m, dt = diagnosticar_fold(datos.iloc[train], datos.iloc[val], numero)
            tablas.extend(coef); casos.extend(c); margenes.extend(m); detalles.extend(dt)
            print(f"Fold {numero}: {len(c)} casos explicados", flush=True)
    casos = pd.DataFrame(casos)
    columnas = ["intervencion_id", "meeting_id", "fold", "pred"]
    pd.testing.assert_frame_equal(casos[columnas].sort_values("intervencion_id").reset_index(drop=True),
                                  anteriores[columnas].sort_values("intervencion_id").reset_index(drop=True))
    assert casos.intervencion_id.is_unique and len(casos) == 793
    casos = casos.merge(asignacion[["intervencion_id", "texto_identico_en_train"]], on="intervencion_id", validate="one_to_one")
    tops, coef, estabilidad = resumir_coeficientes(tablas)
    for nombre, tabla in [("top_global.csv", tops), ("coeficientes_seleccionados.csv", coef), ("estabilidad.csv", estabilidad),
                           ("casos_validacion.csv", casos), ("margenes.csv", pd.DataFrame(margenes)), ("aportes_locales.csv", pd.DataFrame(detalles))]:
        tabla.to_csv(salida / nombre, index=False)
    resumen = {"n": len(casos), "errores_finales": int((~casos.acierto).sum()), "confusiones_hd": int(casos.confusion_hd.sum()),
               "errores_a": int(casos.pred_a.ne(casos.relevancia_ia).sum()),
               "forzados_neutral_a": int(casos.pred_a.eq(0).sum()),
               "errores_finales_a_cero": int((~casos.acierto & casos.pred_a.eq(0)).sum()),
               "predicciones_iguales_a_seleccion": True, "gold_abierto_o_predicho": False,
               "hibrido_entrenado": False, "modelo_reemplazado": False,
               "sha256_salidas": {p.name: sha256(p) for p in sorted(salida.iterdir()) if p.is_file()}}
    escribir(salida / "manifest.json", resumen)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return resumen


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=RUTA_SALIDA)
    ejecutar(parser.parse_args(argv).salida)


if __name__ == "__main__":
    main()
