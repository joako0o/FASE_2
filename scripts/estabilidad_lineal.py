"""Estabilidad del modelo lineal (arquitectura W+C, un miembro) bajo validación agrupada.

Reentrena la arquitectura formal de dos etapas (A relevancia + B H/D/N, TF-IDF
de palabras y caracteres, regresión logística con los parámetros congelados de
`docs/METODOLOGIA_Y_BENCHMARK.md`) sobre el entrenamiento de 1.596 filas bajo
dos esquemas de validación agrupados por reunión:

1. GroupKFold(5) determinista;
2. GroupShuffleSplit(10 repeticiones, 20 % de reuniones en prueba).

Objetivo: cuantificar la varianza POR MUESTREO DE DATOS del modelo lineal.
`LogisticRegression(lbfgs)` es determinista dados los datos: la varianza
observada es la que un rival encoder debe superar por semilla antes de
comparar medias. No se toca la evaluación ciega.

Uso:
    python scripts/estabilidad_lineal.py
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import FeatureUnion

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
SALIDA = ROOT / "resultados/robustez_supervisada/estabilidad_lineal.json"
SEMILLA_BASE = 20260915
ORDEN = ("hawkish", "dovish", "neutral")

WORD_A = {"strip_accents": "unicode", "lowercase": True, "ngram_range": (1, 1), "min_df": 3, "max_df": 0.9, "sublinear_tf": True}
WORD_B = {**WORD_A, "ngram_range": (1, 4)}
CHAR = {"analyzer": "char_wb", "ngram_range": (3, 5), "min_df": 3, "max_df": 0.98, "sublinear_tf": True, "strip_accents": "unicode", "lowercase": True, "max_features": 120000}
LR = {"class_weight": "balanced", "C": 2.0, "max_iter": 2000, "random_state": SEMILLA_BASE}


def vectorizer(words, weight=1.0):
    return FeatureUnion([("word", TfidfVectorizer(**words)), ("char", TfidfVectorizer(**CHAR))], transformer_weights={"word": 1.0, "char": weight}, n_jobs=1)


def ajustar(train):
    va = vectorizer(WORD_A)
    ma = LogisticRegression(**LR).fit(va.fit_transform(train.texto), train.relevancia_v3.astype(int))
    relevantes = train.relevancia_v3.eq("1")
    vb = vectorizer(WORD_B)
    mb = LogisticRegression(**LR).fit(vb.fit_transform(train.loc[relevantes, "texto"]), train.loc[relevantes, "etiqueta_v3"])
    return va, ma, vb, mb


def etiqueta_final(va, ma, vb, mb, textos):
    relevancia = ma.predict(va.transform(textos)).astype(int)
    dura_b = mb.predict(vb.transform(textos))
    return np.where(relevancia == 0, "neutral", dura_b)


def metricas(y_true, y_pred):
    f1, recalls = {}, {}
    for c in ORDEN:
        vp = int(np.sum((y_true == c) & (y_pred == c)))
        fp = int(np.sum((y_true != c) & (y_pred == c)))
        fn = int(np.sum((y_true == c) & (y_pred != c)))
        prec = vp / (vp + fp) if vp + fp else np.nan
        rec = vp / (vp + fn) if vp + fn else np.nan
        f1[c] = 0.0 if prec + rec == 0 or np.isnan(prec) or np.isnan(rec) else 2 * prec * rec / (prec + rec)
        recalls[c] = rec
    return {
        "accuracy": float(np.mean(y_true == y_pred)),
        "macro_f1": float(np.mean([f1[c] for c in ORDEN])),
        "f1_hd": float((f1["hawkish"] + f1["dovish"]) / 2),
        "f1_h": f1["hawkish"],
        "f1_d": f1["dovish"],
        "f1_n": f1["neutral"],
        "recall_d": recalls["dovish"],
        "soporte": {c: int(np.sum(y_true == c)) for c in ORDEN},
    }


def resumir(filas):
    claves = ["accuracy", "macro_f1", "f1_hd", "f1_h", "f1_d", "f1_n", "recall_d"]
    out = {}
    for k in claves:
        xs = np.array([f[k] for f in filas], dtype=float)
        out[k] = {"media": float(np.mean(xs)), "desv": float(np.std(xs, ddof=1)), "min": float(np.min(xs)), "max": float(np.max(xs))}
    return out


def principal():
    data = pd.read_csv(TRAIN, dtype=str, keep_default_na=False)
    grupos = data.meeting_id.to_numpy()
    print(f"Entrenamiento: {len(data)} filas, {len(set(grupos))} reuniones; "
          f"etiquetas {dict(Counter(data.etiqueta_v3))}")

    esquemas = {}
    duraciones = []

    # 1) GroupKFold(5) determinista
    t0 = time.time()
    filas_kfold = []
    for i, (tr, te) in enumerate(GroupKFold(5).split(data, groups=grupos), 1):
        va, ma, vb, mb = ajustar(data.iloc[tr])
        pred = etiqueta_final(va, ma, vb, mb, data.texto.iloc[te])
        filas_kfold.append(metricas(data.etiqueta_v3.iloc[te].to_numpy(), pred))
        duraciones.append(time.time() - t0)
        print(f"  kfold {i}: macro={filas_kfold[-1]['macro_f1']:.4f} f1_hd={filas_kfold[-1]['f1_hd']:.4f} "
              f"f1_d={filas_kfold[-1]['f1_d']:.4f} ({time.time()-t0:.0f}s acum)")
    esquemas["groupkfold5"] = {"por_pliegue": filas_kfold, "resumen": resumir(filas_kfold)}

    # 2) GroupShuffleSplit 10 repeticiones
    filas_shuffle = []
    for i in range(10):
        tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEMILLA_BASE + i).split(data, groups=grupos))
        t0 = time.time()
        va, ma, vb, mb = ajustar(data.iloc[tr])
        pred = etiqueta_final(va, ma, vb, mb, data.texto.iloc[te])
        m = metricas(data.etiqueta_v3.iloc[te].to_numpy(), pred)
        m["repeticion"] = i + 1
        m["segundos_ajuste"] = round(time.time() - t0, 1)
        filas_shuffle.append(m)
        print(f"  shuffle {i+1:2d}: macro={m['macro_f1']:.4f} f1_hd={m['f1_hd']:.4f} f1_d={m['f1_d']:.4f} "
              f"(test {m['soporte']['dovish']} D, {m['segundos_ajuste']}s)")
    esquemas = {
        "groupkfold5": {"por_pliegue": filas_kfold, "resumen": resumir(filas_kfold)},
        "groupshufflesplit_x10": {"por_repeticion": filas_shuffle, "resumen": resumir(filas_shuffle)},
    }

    salida = {
        "version": "estabilidad_lineal_v1",
        "arquitectura": "W+C dos etapas, un miembro, peso char 1.0, parámetros congelados del modelo formal",
        "nota_determinismo": "LogisticRegression(lbfgs) es determinista dados los datos; la varianza registrada proviene del muestreo de reuniones, no de la inicialización.",
        "semilla_base": SEMILLA_BASE,
        "n_filas": len(data),
        "n_reuniones": int(len(set(grupos))),
        "esquemas": esquemas,
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nEscrito: {SALIDA}")
    for esquema in esquemas:
        r = esquemas[esquema]["resumen"]
        print(f"[{esquema}] macro-F1 {r['macro_f1']['media']:.4f}±{r['macro_f1']['desv']:.4f} | "
              f"F1-HD {r['f1_hd']['media']:.4f}±{r['f1_hd']['desv']:.4f} | "
              f"F1-D {r['f1_d']['media']:.4f}±{r['f1_d']['desv']:.4f}")


if __name__ == "__main__":
    principal()
