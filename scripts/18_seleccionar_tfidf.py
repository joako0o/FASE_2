"""Selecciona hiperparámetros solo con IA, reajusta y congela predicciones gold.

Este proceso NO abre el Excel humano ni su procedencia. Usa sus IDs reservados
(del canónico sin respuestas) para excluirlos de entrenamiento y recuperar texto.
El script 19 compara las predicciones ya guardadas en un proceso posterior.

Uso: python scripts/18_seleccionar_tfidf.py [--salida carpeta_nueva]
No sobrescribe experimentos previos ni ajusta parámetros a resultados humanos.
"""

# ---- 1. Protocolo acotado y explícito, previo a ver el test ----
import argparse
from datetime import datetime, timezone
from itertools import product
import json
from pathlib import Path
import platform
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import f1_score

import config
from utilidades import cargar_script, exigir_salidas_nuevas, norm, sha256

BASELINE = cargar_script("15_baseline_tfidf.py")
RUTA_EXPERIMENTO = config.RUTA_DATOS / "evaluacion" / "tfidf_gold_v1"
RUTA_MODELO = config.RUTA_REPO / "modelos" / "tfidf_gold_v1.joblib"
NGRAMAS = [(1, 1), (1, 2)]
MIN_DF = [2, 3]
REGULARIZACION_C = [0.5, 1.0, 2.0]


def ahora():
    return datetime.now(timezone.utc).isoformat()


def escribir_json(ruta, contenido):
    """Creación exclusiva: ningún resultado de un test se reemplaza silenciosamente."""
    with Path(ruta).open("x", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=2, allow_nan=False)
        archivo.write("\n")


def configuraciones():
    return [{"candidato": i, "ngram_max": ngrama[1], "min_df": minimo, "C": c}
            for i, (ngrama, minimo, c) in enumerate(product(NGRAMAS, MIN_DF, REGULARIZACION_C), 1)]


def parametrizar(candidato):
    """Mismos parámetros compartidos en A/B; lo no buscado queda como baseline."""
    tfidf = {**BASELINE.PARAMS_TFIDF, "ngram_range": (1, int(candidato["ngram_max"])),
             "min_df": int(candidato["min_df"])}
    regresion = {**BASELINE.PARAMS_LR, "C": float(candidato["C"])}
    return tfidf, regresion


def elegir_configuracion(resultados):
    """Media macro-F1 de folds; empate exacto: unigramas, mayor min_df, menor C."""
    assert len(resultados) and resultados.macro_f1_media.notna().all()
    return resultados.sort_values(["macro_f1_media", "ngram_max", "min_df", "C"],
                                   ascending=[False, True, False, True], kind="stable").iloc[0]


# ---- 2. Búsqueda sin datos humanos ----
def buscar_configuracion(datos, candidatos):
    resumenes, detalle, asignacion = [], [], None
    # Una falta de convergencia detiene el experimento, no cambia el protocolo.
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for candidato in candidatos:
            tfidf, regresion = parametrizar(candidato)
            oof = BASELINE.evaluar_oof(datos, tfidf, regresion)
            if asignacion is None:
                asignacion = oof[["intervencion_id", "meeting_id", "fold"]].copy()
            else:
                assert np.array_equal(asignacion.fold, oof.fold), "folds diferentes entre candidatos"
            puntuaciones = []
            for fold, validacion in oof.groupby("fold", sort=True):
                macro_f1 = float(f1_score(validacion.etiqueta, validacion.pred,
                                          labels=BASELINE.CLASES, average="macro", zero_division=0))
                puntuaciones.append(macro_f1)
                detalle.append({"candidato": candidato["candidato"], "fold": int(fold),
                                "n_train": len(datos) - len(validacion), "n_validacion": len(validacion),
                                "reuniones_validacion": validacion.meeting_id.nunique(), "macro_f1": macro_f1})
            fila = {**candidato, "macro_f1_media": float(np.mean(puntuaciones)),
                    "macro_f1_desviacion_folds": float(np.std(puntuaciones, ddof=1)),
                    "macro_f1_oof_conjunto": float(f1_score(oof.etiqueta, oof.pred,
                                                           labels=BASELINE.CLASES, average="macro"))}
            resumenes.append(fila)
            print(f"Candidato {candidato['candidato']:02d}: ngram={tfidf['ngram_range']} "
                  f"min_df={tfidf['min_df']} C={regresion['C']} "
                  f"macroF1 validación={fila['macro_f1_media']:.4f}", flush=True)
    return pd.DataFrame(resumenes), pd.DataFrame(detalle), asignacion


def cargar_textos_reservados(datos):
    """Solo IDs y texto de L0. El Excel devuelto nunca es una entrada del fit/predict."""
    marco = pd.read_csv(config.RUTA_MUESTRAS / "gold_ciego_300.csv",
                        usecols=["orden", "intervencion_id"], dtype={"intervencion_id": str})
    assert len(marco) == 306 and marco.intervencion_id.is_unique
    assert not set(marco.intervencion_id) & set(datos.intervencion_id)
    corpus = pd.read_csv(config.RUTA_L0 / "corpus.csv", usecols=["intervencion_id", "texto", "meeting_id"])
    test = marco.merge(corpus, on="intervencion_id", how="left", validate="one_to_one")
    assert test.texto.notna().all()
    test["texto_repetido_training"] = test.texto.map(norm).isin(set(datos.texto.map(norm)))
    test["reunion_en_training"] = test.meeting_id.isin(set(datos.meeting_id))
    return test


# ---- 3. Selección congelada, reajuste completo y predicciones antes del test ----
def ejecutar(salida=RUTA_EXPERIMENTO, ruta_modelo=RUTA_MODELO):
    salida, ruta_modelo = Path(salida), Path(ruta_modelo)
    exigir_salidas_nuevas(salida, ruta_modelo)
    datos = BASELINE.cargar_muestra()
    assert len(datos) == 1352 and datos.intervencion_id.is_unique
    candidatos = configuraciones()
    archivos = [config.RUTA_L0 / "corpus.csv", config.RUTA_MUESTRAS / "gold_ciego_300.csv",
                config.RUTA_MUESTRAS / "piloto_300_tandas.csv", config.RUTA_MUESTRAS / "escalado_tandas.csv",
                config.RUTA_REPO / "requirements.txt", config.RUTA_REPO / "docs/codebook_v2.md",
                *[config.RUTA_REPO / "scripts" / f for f in
                  ["15_baseline_tfidf.py", "18_seleccionar_tfidf.py", "19_evaluar_tfidf_gold.py", "config.py", "utilidades.py", "05_validar_etiquetas.py"]],
                *sorted(config.RUTA_ETIQUETAS.glob("etiquetas_*.csv"))]
    protocolo = {
        "experimento": "tfidf_gold_v1", "fecha_inicio_utc": ahora(), "version_codebook": "v2",
        "n_train_ia": len(datos), "reuniones_train": datos.meeting_id.nunique(),
        "validacion": "5-fold GroupKFold por meeting_id; mismos folds para todos los candidatos",
        "criterio_seleccion": "mayor media no redondeada de macro-F1 de los 5 folds",
        "desempate": "menor ngram_max, mayor min_df, menor C",
        "candidatos": candidatos, "parametros_fijos_tfidf": BASELINE.PARAMS_TFIDF,
        "parametros_fijos_lr": BASELINE.PARAMS_LR, "etapas": "A relevancia; B postura sobre relevantes; mismos hiperparámetros en A/B",
        "entrada_modelo": ["texto"], "prohibido_usar_en_modelo": ["etiquetas humanas", "citas", "notas", "confianza", "fecha", "actor", "macro"],
        "test_primario": "306 decisiones humanas; macro-F1, accuracy, tasa de error, κ y métricas por clase",
        "test_secundario": ["siempre neutral", "sin textos idénticos a training", "por fase TPM", "con/sin señal de decisión", "flag de relevancia"],
        "ajuste_tras_test": "prohibido dentro de esta corrida; no seleccionar modelos con el test humano",
        "salvedad": "El mejor CV es una métrica de selección (optimista), no una evaluación independiente ni temporal prospectiva. El gold fue inspeccionado en la auditoría; no se usará para ajustar.",
        "sha256_insumos": {str(p.relative_to(config.RUTA_REPO)): sha256(p) for p in archivos},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__},
    }
    salida.mkdir(parents=True)
    escribir_json(salida / "protocolo.json", protocolo)
    resultados, detalle, asignacion = buscar_configuracion(datos, candidatos)
    resultados.to_csv(salida / "validacion_cv.csv", index=False)
    detalle.to_csv(salida / "validacion_folds.csv", index=False)
    asignacion.to_csv(salida / "asignacion_folds.csv", index=False)
    elegida = elegir_configuracion(resultados)
    tfidf, regresion = parametrizar(elegida)
    seleccion = {"fecha_seleccion_utc": ahora(), "candidato": int(elegida.candidato),
                 "parametros_tfidf": tfidf, "parametros_lr": regresion,
                 "macro_f1_cv_media": float(elegida.macro_f1_media),
                 "macro_f1_cv_oof_conjunto": float(elegida.macro_f1_oof_conjunto),
                 "sha256_protocolo": sha256(salida / "protocolo.json"),
                 "sha256_validacion": sha256(salida / "validacion_cv.csv")}
    escribir_json(salida / "seleccion.json", seleccion)
    # Solo una configuración final se reajusta; la humana todavía no se lee.
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        modelo = BASELINE.entrenar_modelo(datos, tfidf, regresion)
    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
    with ruta_modelo.open("xb") as archivo:
        joblib.dump(modelo, archivo, compress=3)
    test = cargar_textos_reservados(datos)
    predicciones = BASELINE.predecir_textos(modelo, test.texto)
    salida_pred = pd.concat([test.drop(columns="texto"), predicciones], axis=1)
    assert len(salida_pred) == len(test) and salida_pred.intervencion_id.is_unique
    salida_pred.to_csv(salida / "predicciones_gold.csv", index=False)
    escribir_json(salida / "predicciones_manifest.json", {
        "fecha_prediccion_utc": ahora(), "n_train": len(datos), "n_predicciones": len(test),
        "sha256_predicciones": sha256(salida / "predicciones_gold.csv"),
        "sha256_seleccion": sha256(salida / "seleccion.json"),
        "sha256_modelo": sha256(ruta_modelo), "modelo_local_no_versionado": str(ruta_modelo),
        "respuestas_humanas_leidas": False,
        "textos_repetidos_training": int(test.texto_repetido_training.sum()),
        "reuniones_gold": test.meeting_id.nunique(),
        "reuniones_gold_en_training": test.loc[test.reunion_en_training, "meeting_id"].nunique(),
        "probabilidades": "Etapa B tras máscara dura A; no calibradas. A=0 implica neutral=1.",
    })
    print(f"Selección congelada: candidato {int(elegida.candidato)}. Predicciones: {salida / 'predicciones_gold.csv'}")
    print("No se abrió el Excel humano. Comparar ahora con script 19 en otro proceso.")
    return seleccion


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=RUTA_EXPERIMENTO)
    parser.add_argument("--modelo", type=Path, default=RUTA_MODELO)
    args = parser.parse_args(argv)
    ejecutar(args.salida, args.modelo)


if __name__ == "__main__":
    main()
