# ------------------------------------------------------------------------
# 15_baseline_tfidf.py -- Baseline TF-IDF + regresion logistica (Fase 6a)
# ------------------------------------------------------------------------
# Proposito: piso de comparacion previo a BETO.
# Nota metodologica (2026-09-15, tras diagnostico): el piso honesto de
# bag-of-words es macroF1 ~0,35 en la muestra completa. El paso B1
# (direccional H/D vs neutral) apenas supera azar (F1_dir ~0,20): las
# convenciones del codebook v2 (ej. "mantener en menu {mantener,bajar}" =
# hawkish relativo; pausa en ciclo de normalizacion = dovish) requieren
# contexto de reunion que un vectorizador por terminos no ve. Este limite
# es el argumento operativo del fine-tune de BETO (decision 10 dos etapas).
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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupKFold

CLASES = ["hawkish", "dovish", "neutral"]
PARAMS_TFIDF = dict(strip_accents="unicode", lowercase=True,
                    ngram_range=(1, 2), min_df=3, max_df=0.9, sublinear_tf=True)
PARAMS_LR = dict(class_weight="balanced", max_iter=2000,
                 random_state=config.SEED_MAESTRA)
N_FOLDS = 5


def cargar_muestra():
    """Training set IA (1.352) unido a los textos del universo L0."""
    archivos = sorted(config.RUTA_ETIQUETAS.glob("etiquetas_*.csv"))
    etq = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False)
                     for f in archivos], ignore_index=True)
    etq = etq[etq.metodo == "ia_ronda"].copy()
    assert etq["intervencion_id"].value_counts().max() == 1

    texts = []
    for ruta in [config.RUTA_MUESTRAS / "piloto_300_tandas.csv",
                 config.RUTA_MUESTRAS / "escalado_tandas.csv"]:
        df = pd.read_csv(ruta, dtype=str, keep_default_na=False)
        texts.append(df[["intervencion_id", "texto", "fecha", "actor", "cargo"]])
    uni = pd.concat(texts).drop_duplicates("intervencion_id")

    d = uni.merge(etq[["intervencion_id", "etiqueta", "es_relevante", "confianza"]],
                  on="intervencion_id", how="inner")
    assert len(d) == len(etq), f"textos faltantes: {len(etq) - len(d)}"
    d["meeting_id"] = d["fecha"]  # agrupacion por reunion
    assert set(d.etiqueta) <= set(CLASES)
    return d.reset_index(drop=True)


def main():
    d = cargar_muestra()
    X_text = d["texto"].tolist()
    y_rel = (d["es_relevante"] == "1").astype(int)
    y_stance = d["etiqueta"]
    grupos = d["meeting_id"]

    gkf = GroupKFold(n_splits=N_FOLDS)
    oof_pred, oof_score, oof_fold = [], [], []

    for k, (tr, te) in enumerate(gkf.split(X_text, y_stance, grupos), 1):
        X_tr_tr = [X_text[i] for i in tr]
        X_te = [X_text[i] for i in te]

        # Etapa A: relevancia
        vec_a = TfidfVectorizer(**PARAMS_TFIDF)
        Xa_tr = vec_a.fit_transform(X_tr_tr)
        Xa_te = vec_a.transform(X_te)
        clf_a = LogisticRegression(**PARAMS_LR).fit(Xa_tr, y_rel.iloc[tr])
        pred_rel = clf_a.predict(Xa_te)

        # Etapa B: stance (solo relevantes del train)
        vec_b = TfidfVectorizer(**PARAMS_TFIDF)
        mask_rel_tr = y_rel.iloc[tr].values == 1
        Xb_tr = vec_b.fit_transform([t for t, m in zip(X_tr_tr, mask_rel_tr) if m])
        clf_b = LogisticRegression(**PARAMS_LR).fit(Xb_tr, y_stance.iloc[tr][mask_rel_tr])
        Xb_te = vec_b.transform(X_te)
        proba_b = clf_b.predict_proba(Xb_te)
        idx = {c: i for i, c in enumerate(clf_b.classes_)}
        score_b = proba_b[:, idx["hawkish"]] - proba_b[:, idx["dovish"]]
        pred_b = clf_b.classes_[proba_b.argmax(axis=1)]

        # Composicion: no relevante -> neutral, score 0
        pred_fin = [p if r == 1 else "neutral" for p, r in zip(pred_b, pred_rel)]
        score_fin = [s if r == 1 else 0.0 for s, r in zip(score_b, pred_rel)]
        oof_pred.extend(pred_fin)
        oof_score.extend(score_fin)
        oof_fold.extend([k] * len(te))

    d["pred"] = oof_pred
    d["score_pred"] = [f"{s:.4f}" for s in oof_score]
    d["fold"] = oof_fold

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
    )

    config.RUTA_L2.mkdir(exist_ok=True)
    d[["intervencion_id", "fecha", "actor", "etiqueta", "es_relevante",
       "pred", "score_pred", "fold"]].to_csv(
        config.RUTA_L2 / "baseline_tfidf_oof.csv", index=False)
    with open(config.RUTA_L2 / "baseline_tfidf_metrics.json", "w", encoding="utf-8") as fh:
        json.dump(metricas, fh, ensure_ascii=False, indent=2)

    print(f"n={len(d)} meetings={grupos.nunique()}")
    print(f"accuracy={acc:.4f} | macroF1={f1m:.4f} (piso neutral={f1_piso:.4f})")
    for c in CLASES:
        n_real = int((y_stance == c).sum())
        n_ok = int(((pd.Series(oof_pred) == c) & (y_stance == c)).sum())
        print(f"  {c:8s} F1={f1c[c]:.4f} | acierta {n_ok}/{n_real}")
    print("matriz confusion (filas=real):")
    for c, fila in zip(CLASES, cm):
        print(f"  {c:8s} {fila.tolist()}")


if __name__ == "__main__":
    main()
