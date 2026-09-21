"""Curvas de aprendizaje agrupadas por reunión para la arquitectura lineal W+C.

Pregunta: ¿cuánta anotación necesita la tarea H/D/N? Para cada tamaño
presupuestado N (en intervenciones), muestrea reuniones completas del pool de
desarrollo (sin tocar la evaluación ciega), ajusta la arquitectura de dos
etapas con los parámetros congelados del modelo formal y evalúa sobre un
conjunto fijo de reuniones de prueba.

Diseño anti-artefactos (lo que un referee ataca primero):

- el conjunto de evaluación se fija UNA vez y no cambia entre puntos de la curva;
- las reuniones se muestreo completas (nunca filas sueltas);
- el muestreo se ESTRATIFICA por presencia de dovish: en cada muestra entran
  reuniones con dovish en proporción a su peso de filas en el pool, para que
  la clase D no desaparezca en los N pequeños (en la ciega solo 12/33
  reuniones contienen dovish; el mismo desbalance existe aquí);
- cada punto agrega múltiples repeticiones con distintas muestras.

Uso:
    python scripts/curvas_aprendizaje.py --repeticiones 15
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
SALIDA = ROOT / "resultados/robustez_supervisada/curvas_aprendizaje.json"
SEMILLA = 20260915
ORDEN = ("hawkish", "dovish", "neutral")
PARRILLA_N = (200, 400, 800, 1200, 1596)

WORD_A = {"strip_accents": "unicode", "lowercase": True, "ngram_range": (1, 1), "min_df": 3, "max_df": 0.9, "sublinear_tf": True}
WORD_B = {**WORD_A, "ngram_range": (1, 4)}
CHAR = {"analyzer": "char_wb", "ngram_range": (3, 5), "min_df": 3, "max_df": 0.98, "sublinear_tf": True, "strip_accents": "unicode", "lowercase": True, "max_features": 120000}
LR = {"class_weight": "balanced", "C": 2.0, "max_iter": 2000, "random_state": SEMILLA}


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
        f1[c] = 0.0 if (np.isnan(prec) or np.isnan(rec) or prec + rec == 0) else 2 * prec * rec / (prec + rec)
        recalls[c] = rec
    return {
        "accuracy": float(np.mean(y_true == y_pred)),
        "macro_f1": float(np.mean([f1[c] for c in ORDEN])),
        "f1_hd": float((f1["hawkish"] + f1["dovish"]) / 2),
        "f1_d": f1["dovish"],
        "f1_h": f1["hawkish"],
        "recall_d": recalls["dovish"],
    }


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeticiones", type=int, default=15)
    args = ap.parse_args()

    data = pd.read_csv(TRAIN, dtype=str, keep_default_na=False)
    data["con_d"] = data.etiqueta_v3.eq("dovish")
    por_reunion = {m: g for m, g in data.groupby("meeting_id")}
    info = {m: {"filas": len(g), "con_d": bool(g.con_d.any())} for m, g in por_reunion.items()}
    reuniones = sorted(info)

    # --- Conjunto de evaluación fijo (~20 % de filas, estratificado por presencia de D) ---
    rng = np.random.default_rng(SEMILLA)
    con_d = [m for m in reuniones if info[m]["con_d"]]
    sin_d = [m for m in reuniones if not info[m]["con_d"]]
    rng.shuffle(con_d)
    n_eval_d = max(3, int(round(0.2 * len(con_d))))
    eval_d, pool_d = set(con_d[:n_eval_d]), set(con_d[n_eval_d:])
    filas_objetivo = int(round(0.2 * len(data)))
    eval_nd, pool_nd = [], []
    orden_nd = list(sin_d)
    rng.shuffle(orden_nd)
    acumulado = sum(info[m]["filas"] for m in eval_d)
    for m in orden_nd:
        if acumulado >= filas_objetivo:
            pool_nd.append(m)
        else:
            eval_nd.append(m)
            acumulado += info[m]["filas"]
    eval_meetings = sorted(eval_d | set(eval_nd))
    eval_idx = data.meeting_id.isin(eval_meetings)
    eval_set = data[eval_idx]
    pool_d = sorted(pool_d)
    pool_nd = sorted(pool_nd)
    y_eval = eval_set.etiqueta_v3.to_numpy()

    fraccion_d_pool = sum(info[m]["filas"] for m in pool_d) / (len(data) - len(eval_set))
    print(f"Evaluación fija: {len(eval_meetings)} reuniones, {len(eval_set)} filas "
          f"({int(eval_set.etiqueta_v3.eq('dovish').sum())} D). "
          f"Pool: {len(pool_d)} reuniones con D / {len(pool_nd)} sin D; fracción D del pool = {fraccion_d_pool:.3f}")

    resultados = {}
    for n_objetivo in PARRILLA_N:
        n_objetivo = min(n_objetivo, len(data) - len(eval_set))
        por_repeticion = []
        for r in range(args.repeticiones):
            rng_rep = np.random.default_rng(SEMILLA + 1000 * n_objetivo + r)
            # estratificación: reuniones con D aportan fraccion_d_pool de las filas
            filas_d_objetivo = int(round(n_objetivo * fraccion_d_pool))
            orden_d = list(pool_d)
            orden_nd = list(pool_nd)
            rng_rep.shuffle(orden_d)
            rng_rep.shuffle(orden_nd)
            muestra, filas_d, filas_nd = [], 0, 0
            i_d = i_nd = 0
            while (filas_d < filas_d_objetivo and i_d < len(orden_d)) or (filas_nd < n_objetivo - filas_d_objetivo and i_nd < len(orden_nd)):
                if filas_d < filas_d_objetivo and i_d < len(orden_d):
                    m = orden_d[i_d]
                    i_d += 1
                    muestra.append(m)
                    filas_d += info[m]["filas"]
                if filas_nd < n_objetivo - filas_d_objetivo and i_nd < len(orden_nd):
                    m = orden_nd[i_nd]
                    i_nd += 1
                    muestra.append(m)
                    filas_nd += info[m]["filas"]
            train_set = pd.concat([por_reunion[m] for m in muestra])
            t0 = time.time()
            va, ma, vb, mb = ajustar(train_set)
            pred = etiqueta_final(va, ma, vb, mb, eval_set.texto)
            m_aux = metricas(y_eval, pred)
            m_aux["n_entrenamiento"] = len(train_set)
            m_aux["d_entrenamiento"] = int(train_set.etiqueta_v3.eq("dovish").sum())
            m_aux["segundos"] = round(time.time() - t0, 1)
            por_repeticion.append(m_aux)
        xs = {k: np.array([f[k] for f in por_repeticion], dtype=float) for k in ("macro_f1", "f1_hd", "f1_d", "f1_h", "recall_d", "accuracy")}
        resumen = {
            k: {
                "media": float(np.nanmean(v)),
                "desv": float(np.nanstd(v, ddof=1)),
                "p25": float(np.nanpercentile(v, 25)),
                "p975": float(np.nanpercentile(v, 97.5)),
                "nan": int(np.isnan(v).sum()),
            }
            for k, v in xs.items()
        }
        resultados[str(n_objetivo)] = {
            "n_real_medio": float(np.mean([f["n_entrenamiento"] for f in por_repeticion])),
            "d_entrenamiento_medio": float(np.mean([f["d_entrenamiento"] for f in por_repeticion])),
            "resumen": resumen,
            "por_repeticion": por_repeticion,
        }
        rr = resumen
        print(f"N≈{n_objetivo:4d} (real {resultados[str(n_objetivo)]['n_real_medio']:.0f}, "
              f"D tren {resultados[str(n_objetivo)]['d_entrenamiento_medio']:.0f}): "
              f"macro {rr['macro_f1']['media']:.4f}±{rr['macro_f1']['desv']:.4f} | "
              f"F1-HD {rr['f1_hd']['media']:.4f}±{rr['f1_hd']['desv']:.4f} | "
              f"F1-D {rr['f1_d']['media']:.4f} (NaN folds: {rr['f1_d']['nan']}) | "
              f"recall-D {rr['recall_d']['media']:.4f}")

    salida = {
        "version": "curvas_aprendizaje_v1",
        "arquitectura": "W+C dos etapas, un miembro, parámetros congelados del modelo formal",
        "evaluacion_fija": {
            "reuniones": len(eval_meetings),
            "filas": len(eval_set),
            "distribucion": dict(Counter(y_eval)),
            "semilla": SEMILLA,
        },
        "estratificacion": {
            "fraccion_d_pool": fraccion_d_pool,
            "nota": "muestreo de reuniones completas estratificado por presencia de dovish; evita que la clase D desaparezca en N pequeños",
        },
        "repeticiones": args.repeticiones,
        "curvas": resultados,
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nEscrito: {SALIDA}")


if __name__ == "__main__":
    principal()
