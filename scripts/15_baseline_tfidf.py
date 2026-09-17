# ------------------------------------------------------------------------
# 15_baseline_tfidf.py -- Baseline TF-IDF + regresion logistica (Fase 6a)
# ------------------------------------------------------------------------
# Proposito: piso de comparacion previo a BETO.
# Corrección 2026-09-16: se ensamblan las salidas OOF por índice de test,
# no por concatenación de folds. El antiguo macroF1 0,3511 era inválido;
# la evaluación corregida da ~0,7173 contra etiquetas IA (no contra gold).
# GroupKFold separa reuniones, no simula predicción temporal prospectiva.
#
# Arquitectura de dos etapas (decision 10):
#   A) es_relevante binario (0/1) sobre todo el texto.
#   B) stance 3 clases (hawkish/dovish/neutral) sobre es_relevante == 1.
# Etiqueta final: A==0 -> neutral; si no, argmax de B.
# score = P(hawkish) - P(dovish) tras aplicar la mascara de A.
#
# Evaluacion: 5 folds GroupKFold por meeting_id (evita fuga entre
# intervenciones de la misma reunion). class_weight="balanced" por el
# desbalance 8,6/6,6/84,8 del training set.
#
# Salidas:
#   data/L2/baseline_tfidf_oof.csv    predicciones out-of-fold por intervencion
#   data/L2/baseline_tfidf_metrics.json  metricas macro y por clase
# Uso:  ~/venvs/fase2/bin/python scripts/15_baseline_tfidf.py
# ------------------------------------------------------------------------

import json
from datetime import datetime, timezone
import numpy as np
import sklearn
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold
from utilidades import sha256, cargar_entrenamiento

CLASES = ["hawkish", "dovish", "neutral"]
PARAMS_TFIDF = dict(strip_accents="unicode", lowercase=True,
                    ngram_range=(1, 2), min_df=3, max_df=0.9, sublinear_tf=True)
PARAMS_LR = dict(class_weight="balanced", max_iter=2000,
                 random_state=config.SEED_MAESTRA)
N_FOLDS = 5


def cargar_muestra():
    """Training set IA (1.352) unido a los textos del universo L0."""
    etq = cargar_entrenamiento()
    etq["es_relevante"] = etq.es_relevante.astype(str)

    # Fuente única de texto: L0. Se conserva el orden histórico de entrenamiento
    # (piloto, luego escalado) para comparar la corrección con el artefacto previo.
    ids = pd.concat([pd.read_csv(config.RUTA_MUESTRAS / nombre,
                                usecols=["intervencion_id"], dtype=str)
                     for nombre in ["piloto_300_tandas.csv", "escalado_tandas.csv"]])
    assert ids.intervencion_id.is_unique
    corpus = pd.read_csv(config.RUTA_L0 / "corpus.csv", dtype=str, keep_default_na=False)
    assert corpus.intervencion_id.is_unique
    d = ids.merge(etq[["intervencion_id", "etiqueta", "es_relevante", "confianza"]],
                  on="intervencion_id", how="inner", validate="one_to_one")
    d = d.merge(corpus[["intervencion_id", "texto", "fecha", "meeting_id", "actor", "cargo"]],
                on="intervencion_id", how="left", validate="one_to_one")
    assert len(d) == len(etq), "etiquetas sin ID en el marco de entrenamiento"
    assert d.texto.notna().all() and d.texto.str.strip().ne("").all()
    assert set(d.etiqueta) == set(CLASES)
    assert set(d.es_relevante) <= {"0", "1"}
    gold = pd.read_csv(config.RUTA_MUESTRAS / "gold_ciego_300.csv", usecols=["intervencion_id"])
    assert not d.intervencion_id.isin(gold.intervencion_id).any(), "gold en entrenamiento"
    return d.reset_index(drop=True)


# ---- 2. Modelo de dos etapas compartido por CV y prueba humana ----
def entrenar_modelo(datos, parametros_tfidf=None, parametros_lr=None):
    """Ajusta vocabularios y clasificadores SOLO con los ejemplos de entrenamiento."""
    parametros_tfidf = PARAMS_TFIDF if parametros_tfidf is None else parametros_tfidf
    parametros_lr = PARAMS_LR if parametros_lr is None else parametros_lr
    textos = datos["texto"].tolist()
    relevancia = datos.es_relevante.astype(str).eq("1").astype(int)
    assert len(datos) and set(relevancia) == {0, 1}
    vector_a = TfidfVectorizer(**parametros_tfidf)
    clasificador_a = LogisticRegression(**parametros_lr).fit(
        vector_a.fit_transform(textos), relevancia)
    relevantes = relevancia.eq(1).to_numpy()
    assert set(datos.loc[relevantes, "etiqueta"]) == set(CLASES)
    vector_b = TfidfVectorizer(**parametros_tfidf)
    clasificador_b = LogisticRegression(**parametros_lr).fit(
        vector_b.fit_transform([t for t, r in zip(textos, relevantes) if r]),
        datos.loc[relevantes, "etiqueta"])
    return {"vector_a": vector_a, "clasificador_a": clasificador_a,
            "vector_b": vector_b, "clasificador_b": clasificador_b}


def predecir_textos(modelo, textos):
    """Solo recibe textos, nunca etiquetas, citas, notas o relevancia humana.

    Probabilidades B condicionadas a la máscara dura de A: si A=0 se fuerza
    neutral=1 y score=0. No son probabilidades calibradas ni marginalización A×B.
    """
    textos = list(textos)
    assert textos and all(isinstance(t, str) and t.strip() for t in textos)
    relevancia = modelo["clasificador_a"].predict(modelo["vector_a"].transform(textos))
    clasificador_b = modelo["clasificador_b"]
    probabilidades_b = clasificador_b.predict_proba(modelo["vector_b"].transform(textos))
    posiciones = {c: i for i, c in enumerate(clasificador_b.classes_)}
    etiquetas = clasificador_b.classes_[probabilidades_b.argmax(axis=1)]
    probabilidades = probabilidades_b[:, [posiciones[c] for c in CLASES]].copy()
    probabilidades[relevancia == 0] = [0.0, 0.0, 1.0]
    etiquetas = np.where(relevancia == 0, "neutral", etiquetas)
    assert np.isfinite(probabilidades).all()
    assert np.allclose(probabilidades.sum(axis=1), 1)
    salida = pd.DataFrame(probabilidades, columns=[f"prob_{c}" for c in CLASES])
    salida["pred"] = etiquetas
    salida["es_relevante_pred"] = relevancia
    salida["score_pred"] = salida.prob_hawkish - salida.prob_dovish
    return salida


# ---- 3. Evaluación OOF con escritura por posición original ----
def evaluar_oof(d, parametros_tfidf=None, parametros_lr=None):
    """Cada intervención recibe exactamente una predicción fuera de entrenamiento."""
    X_text = d["texto"].tolist()
    y_stance = d["etiqueta"]
    grupos = d["meeting_id"]

    gkf = GroupKFold(n_splits=N_FOLDS)
    oof_pred = np.empty(len(d), dtype=object)
    oof_score = np.full(len(d), np.nan)
    oof_fold = np.zeros(len(d), dtype=int)
    visitas = np.zeros(len(d), dtype=int)

    for k, (tr, te) in enumerate(gkf.split(X_text, y_stance, grupos), 1):
        assert not set(grupos.iloc[tr]) & set(grupos.iloc[te]), "fuga entre reuniones"
        modelo = entrenar_modelo(d.iloc[tr], parametros_tfidf, parametros_lr)
        predicciones = predecir_textos(modelo, d.iloc[te].texto)
        oof_pred[te] = predicciones.pred.to_numpy()
        oof_score[te] = predicciones.score_pred.to_numpy()
        oof_fold[te] = k
        visitas[te] += 1

    assert (visitas == 1).all(), "cada ID debe tener exactamente una predicción OOF"
    assert np.isfinite(oof_score).all()
    assert set(oof_pred) <= set(CLASES)
    d = d.copy()

    d["pred"] = oof_pred
    d["score_pred"] = [f"{s:.4f}" for s in oof_score]
    d["fold"] = oof_fold

    assert d.groupby("meeting_id")["fold"].nunique().eq(1).all()
    return d


# ---- 4. Métricas y linaje de la corrida ----
def calcular_metricas(d):
    y_stance, oof_pred = d["etiqueta"], d["pred"]
    acc = accuracy_score(y_stance, oof_pred)
    f1m = f1_score(y_stance, oof_pred, labels=CLASES, average="macro", zero_division=0)
    f1c = dict(zip(CLASES, f1_score(y_stance, oof_pred, labels=CLASES,
                                    average=None, zero_division=0)))
    # Piso: clasificador que siempre predice "neutral"
    f1_piso = f1_score(y_stance, ["neutral"] * len(y_stance), labels=CLASES,
                       average="macro", zero_division=0)
    cm = confusion_matrix(y_stance, oof_pred, labels=CLASES)

    metricas = dict(
        n=len(d), accuracy=round(acc, 4), macro_f1=round(f1m, 4),
        f1_por_clase={c: round(v, 4) for c, v in f1c.items()},
        macro_f1_piso_neutral=round(f1_piso, 4),
        matriz_confusion=dict(
            filas_reales=CLASES, columnas_pred=CLASES, valores=cm.tolist()),
        modelo_a="tfidf(1,2)+logreg balanced | es_relevante",
        modelo_b="tfidf(1,2)+logreg balanced | hawkish/dovish/neutral",
        folds=N_FOLDS, agrupacion="meeting_id (fecha)",
        semilla=config.SEED_MAESTRA,
        version_evaluacion="oof_por_indice_v2",
        referencia="etiquetas IA; no gold humano",
        limitacion="GroupKFold por reunión, no evaluación temporal prospectiva",
    )

    return metricas


def main():
    d = evaluar_oof(cargar_muestra())
    metricas = calcular_metricas(d)
    metricas["fecha_ejecucion_utc"] = datetime.now(timezone.utc).isoformat()
    metricas["version_codebook"] = "v2"
    metricas["versiones"] = {"pandas": pd.__version__, "numpy": np.__version__,
                             "scikit_learn": sklearn.__version__}
    insumos = [config.RUTA_L0 / "corpus.csv", config.RUTA_REPO / "docs/codebook_v2.md",
               config.RUTA_REPO / "requirements.txt", Path(__file__),
               config.RUTA_REPO / "scripts/config.py",
               config.RUTA_MUESTRAS / "gold_ciego_300.csv",
               config.RUTA_MUESTRAS / "piloto_300_tandas.csv",
               config.RUTA_MUESTRAS / "escalado_tandas.csv",
               *sorted(config.RUTA_ETIQUETAS.glob("etiquetas_*.csv"))]
    metricas["sha256_insumos"] = {str(f.relative_to(config.RUTA_REPO)): sha256(f) for f in insumos}
    config.RUTA_L2.mkdir(parents=True, exist_ok=True)
    ruta_oof = config.RUTA_L2 / "baseline_tfidf_oof.csv"
    d[["intervencion_id", "fecha", "actor", "etiqueta", "es_relevante",
       "pred", "score_pred", "fold"]].to_csv(ruta_oof, index=False)
    metricas["sha256_oof"] = sha256(ruta_oof)
    (config.RUTA_L2 / "baseline_tfidf_metrics.json").write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"n={len(d)} reuniones={d.meeting_id.nunique()}")
    print(f"accuracy={metricas['accuracy']:.4f} | macroF1={metricas['macro_f1']:.4f}")
    print("F1 por clase:", metricas["f1_por_clase"])


if __name__ == "__main__":
    main()
