"""Bootstrap pareado agrupado por reunión para la evaluación ciega (300).

Recalcula las métricas puntuales de C+89 y W+C+600 a partir de
`data/predicciones_evaluacion_ciega.csv`, las contrasta contra
`data/resultados_evaluacion_ciega.json` y emite la distribución bootstrap
de la DIFERENCIA (Δ) entre ambos modelos, remuesteando reuniones completas
con reemplazo, según el protocolo de `docs/METODOLOGIA_Y_BENCHMARK.md` §6
(10.000 remuestras, semilla 20260917, percentiles 2,5 / 50 / 97,5 y
proporción de remuestras con diferencia positiva).

Esto es reanálisis de modelos ya decididos: no selecciona variantes nuevas
y no reabre la evaluación ciega.

Uso:
    python scripts/bootstrap_ciega_pareado.py
    python scripts/bootstrap_ciega_pareado.py --remuestras 10000 --salida out.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict

CLASES = ("hawkish", "dovish", "neutral")
GOLD = "data/evaluacion_ciega_gold.csv"
PRED = "data/predicciones_evaluacion_ciega.csv"
REF = "data/resultados_evaluacion_ciega.json"
SEMILLA = 20260917


def cargar():
    gold = {}
    with open(GOLD, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            gold[r["intervencion_id"]] = r
    filas = []
    with open(PRED, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["incluir_evaluacion"] != "true":
                continue
            g = gold[r["intervencion_id"]]
            assert g["etiqueta_v3"] == r["etiqueta_v3"], "gold inconsistente entre archivos"
            filas.append(
                {
                    "id": r["intervencion_id"],
                    "meeting": r["meeting_id"],
                    "y": r["etiqueta_v3"],
                    "c89": r["pred_c_89"],
                    "wc600": r["pred_wc_600"],
                }
            )
    return filas


def metricas(filas, col):
    """Accuracy, F1 por clase, macro-F1, F1-HD y recall por clase."""
    n = len(filas)
    aciertos = sum(f[col] == f["y"] for f in filas)
    out = {"accuracy": aciertos / n, "n": n}
    f1s, recalls = {}, {}
    for c in CLASES:
        vp = sum(f["y"] == c and f[col] == c for f in filas)
        fp = sum(f["y"] != c and f[col] == c for f in filas)
        fn = sum(f["y"] == c and f[col] != c for f in filas)
        prec = vp / (vp + fp) if vp + fp else math.nan
        rec = vp / (vp + fn) if vp + fn else math.nan
        f1s[c] = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        recalls[c] = rec if vp + fn else math.nan
    out["f1"] = f1s
    out["recall"] = recalls
    out["macro_f1"] = sum(f1s.values()) / 3
    out["f1_hd"] = (f1s["hawkish"] + f1s["dovish"]) / 2
    return out


def intervalo_wilson(vp, n, z=1.959963985):
    if n == 0:
        return (math.nan, math.nan)
    p = vp / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    semi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (centro - semi, centro + semi)


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remuestras", type=int, default=10_000)
    ap.add_argument("--salida", default=None)
    args = ap.parse_args()

    filas = cargar()
    reuniones = sorted({f["meeting"] for f in filas})
    por_reunion = defaultdict(list)
    for f in filas:
        por_reunion[f["meeting"]].append(f)

    punto = {"c89": metricas(filas, "c89"), "wc600": metricas(filas, "wc600")}

    # Contraste contra los números almacenados
    ref = json.load(open(REF, encoding="utf-8"))
    for modelo, clave in (("c89", "c_89"), ("wc600", "wc_600")):
        for m in ("accuracy", "macro_f1", "f1_hd"):
            assert abs(punto[modelo][m] - ref["modelos"][clave][m]) < 1e-12, (
                f"{modelo}.{m} no reproduce el JSON almacenado"
            )
        for c in CLASES:
            assert abs(punto[modelo]["f1"][c] - ref["modelos"][clave]["por_clase"][c]["f1"]) < 1e-12
    print(f"Sanity check: métricas puntuales reproducen resultados_evaluacion_ciega.json (n={len(filas)}, "
          f"{len(reuniones)} reuniones).\n")

    print("Distribución gold:", dict(Counter(f["y"] for f in filas)))
    print("Predicho C+89  :", dict(Counter(f["c89"] for f in filas)))
    print("Predicho W+C+600:", dict(Counter(f["wc600"] for f in filas)))
    con_d = sum(1 for m in reuniones if any(f["y"] == "dovish" for f in por_reunion[m]))
    print(f"Reuniones con ≥1 dovish en gold: {con_d}/{len(reuniones)}")

    r_d = sum(1 for f in filas if f["y"] == "dovish" and f["wc600"] == "dovish")
    n_d = punto["wc600"]["f1"] and sum(1 for f in filas if f["y"] == "dovish")
    lo, hi = intervalo_wilson(r_d, n_d)
    print(f"\nRecall_D W+C+600 = {r_d}/{n_d}; IC95% Wilson = [{lo:.3f}, {hi:.3f}] "
          f"(semi-amplitud ≈ {(hi - lo) / 2:.3f})")

    # Bootstrap pareado agrupado por reunión
    rng = random.Random(SEMILLA)
    deltas = defaultdict(list)
    claves = (
        "accuracy",
        "macro_f1",
        "f1_hd",
        "f1_hawkish",
        "f1_dovish",
        "f1_neutral",
        "recall_dovish",
    )
    for _ in range(args.remuestras):
        muestra = [por_reunion[m] for m in rng.choices(reuniones, k=len(reuniones))]
        plana = [f for grp in muestra for f in grp]
        a = metricas(plana, "c89")
        b = metricas(plana, "wc600")
        deltas["accuracy"].append(b["accuracy"] - a["accuracy"])
        deltas["macro_f1"].append(b["macro_f1"] - a["macro_f1"])
        deltas["f1_hd"].append(b["f1_hd"] - a["f1_hd"])
        for c in CLASES:
            deltas[f"f1_{c}"].append(b["f1"][c] - a["f1"][c])
        deltas["recall_dovish"].append(b["recall"]["dovish"] - a["recall"]["dovish"])

    def pct(xs, q):
        xs = sorted(xs)
        i = (len(xs) - 1) * q / 100
        lo_i, hi_i = math.floor(i), math.ceil(i)
        return xs[lo_i] + (xs[hi_i] - xs[lo_i]) * (i - lo_i)

    pto = {
        "accuracy": punto["wc600"]["accuracy"] - punto["c89"]["accuracy"],
        "macro_f1": punto["wc600"]["macro_f1"] - punto["c89"]["macro_f1"],
        "f1_hd": punto["wc600"]["f1_hd"] - punto["c89"]["f1_hd"],
        "f1_hawkish": punto["wc600"]["f1"]["hawkish"] - punto["c89"]["f1"]["hawkish"],
        "f1_dovish": punto["wc600"]["f1"]["dovish"] - punto["c89"]["f1"]["dovish"],
        "f1_neutral": punto["wc600"]["f1"]["neutral"] - punto["c89"]["f1"]["neutral"],
        "recall_dovish": punto["wc600"]["recall"]["dovish"] - punto["c89"]["recall"]["dovish"],
    }

    print(f"\nΔ = W+C+600 − C+89 (bootstrap pareado, {args.remuestras} remuestras de "
          f"{len(reuniones)} reuniones, semilla {SEMILLA})")
    encabezado = f"{'métrica':14s} {'Δ punto':>9s} {'IC2,5%':>8s} {'IC50%':>8s} {'IC97,5%':>8s} {'P(Δ>0)':>8s}"
    print(encabezado)
    resumen = {}
    for k in claves:
        xs = deltas[k]
        q025, q50, q975 = pct(xs, 2.5), pct(xs, 50), pct(xs, 97.5)
        p_pos = sum(1 for v in xs if v > 0) / len(xs)
        signo_ic = "significativo" if q025 > 0 or q975 < 0 else "IC contiene 0"
        print(f"{k:14s} {pto[k]:9.4f} {q025:8.4f} {q50:8.4f} {q975:8.4f} {p_pos:8.4f}  {signo_ic}")
        resumen[k] = {
            "punto": pto[k],
            "ic95": [q025, q975],
            "mediana": q50,
            "p_mayor_que_cero": p_pos,
            "ic_contiene_cero": not (q025 > 0 or q975 < 0),
        }

    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": "bootstrap_ciega_pareado_v1",
                    "remuestras": args.remuestras,
                    "semilla": SEMILLA,
                    "n": len(filas),
                    "reuniones": len(reuniones),
                    "gold": dict(Counter(f["y"] for f in filas)),
                    "deltas": resumen,
                },
                f,
                ensure_ascii=False,
                indent=1,
            )
        print(f"\nEscrito: {args.salida}")


if __name__ == "__main__":
    principal()
