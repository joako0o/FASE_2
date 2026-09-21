"""Verifica que `clasificacion_wc600_9725.csv` y `tabla_maestra.csv` provienen
del mismo run del modelo y que sus totales H/D difieren EXCLUSIVAMENTE por la
regla de procedencia documentada en `docs/METODOLOGIA_Y_BENCHMARK.md` §7:

1. la tabla maestra usa, por fila, la mejor evidencia disponible:
   etiqueta validada (1.596) y gold ciega (299) donde existen, y la
   predicción de W+C+600 en las 7.829 restantes;
2. `clasificacion_wc600_9725.csv` conserva la predicción del modelo en las
   9.725 filas, sin sustituciones;
3. la etiqueta dura del modelo es el voto mayoritario de los cinco miembros
   con desempate fijo H, D, N (no el argmax de las probabilidades promedio).

El script falla (exit 1) si alguna igualdad no se cumple. Uso:
    python scripts/verificar_procedencia.py
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASIF = ROOT / "resultados/clasificacion_wc600_9725.csv"
MAESTRA = ROOT / "resultados/analisis_descriptivo/tabla_maestra.csv"
ORDEN = ("hawkish", "dovish", "neutral")
HUMANAS = {"etiqueta_validada_entrenamiento", "gold_evaluacion_ciega"}


def leer(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def voto_mayoritario(cinco):
    c = Counter(cinco)
    m = max(c.values())
    return next(e for e in ORDEN if c[e] == m)


def principal():
    cla = leer(CLASIF)
    tm = leer(MAESTRA)
    print(f"filas: clasificacion={len(cla)}, tabla_maestra={len(tm)}")
    ok = True

    def chequear(cond, mensaje):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + mensaje)
        ok = ok and cond

    # 1) mismos identificadores, sin filas de más ni de menos
    ids_cla = [r["intervencion_id"] for r in cla]
    chequear(len(cla) == len(tm) and set(ids_cla) == {r["intervencion_id"] for r in tm},
             "ambos archivos cubren exactamente las mismas 9.725 intervenciones")

    pred = {r["intervencion_id"]: r["prediccion_v3"] for r in cla}

    # 2) en filas de procedencia modelo, maestra == predicción, fila por fila
    dif_modelo = sum(1 for r in tm if r["procedencia_etiqueta"] == "prediccion_wc600"
                     and r["etiqueta_analisis"] != pred[r["intervencion_id"]])
    chequear(dif_modelo == 0, "en las 7.829 filas de procedencia 'prediccion_wc600', "
                              "maestra y clasificacion coinciden fila por fila")

    # 3) los totales difieren EXACTAMENTE por las 1.895 filas con etiqueta humana
    #    (dirección de los netos: maestra − clasificacion)
    netos = {e: 0 for e in ORDEN}
    filas_humanas = 0
    for r in tm:
        if r["procedencia_etiqueta"] in HUMANAS:
            filas_humanas += 1
            e, p = r["etiqueta_analisis"], pred[r["intervencion_id"]]
            if e != p:
                netos[e] += 1
                netos[p] -= 1
    # la fila no decidible tiene predicción en clasificacion pero no aporta a las
    # clases H/D/N de la maestra: su predicción se descuenta
    no_dec = [r for r in tm if r["procedencia_etiqueta"] == "gold_no_decidible"]
    if len(no_dec) == 1:
        netos[pred[no_dec[0]["intervencion_id"]]] -= 1
    tot_cla = Counter(pred.values())
    tot_tm = Counter(r["etiqueta_analisis"] for r in tm)
    for e in ORDEN:
        esperado = tot_tm[e] - tot_cla[e]
        chequear(netos[e] == esperado,
                 f"{e}: cambio neto por filas humanas {netos[e]:+d} == "
                 f"total maestra {tot_tm[e]} − total clasificacion {tot_cla[e]}")
    print(f"       ({filas_humanas} filas con etiqueta humana: 1.596 validadas + 299 gold ciega)")

    # 4) la etiqueta del modelo es voto mayoritario con desempate fijo
    mism_voto = sum(1 for r in cla
                    if voto_mayoritario([r[f"pred_miembro_{i}"] for i in range(1, 6)]) == r["prediccion_v3"])
    chequear(mism_voto == len(cla),
             f"prediccion_v3 == voto mayoritario de los 5 miembros en {mism_voto}/{len(cla)} filas")

    # 5) el 9.724 conocido: la única fila no decidible
    no_dec = [r for r in tm if r["procedencia_etiqueta"] == "gold_no_decidible"]
    chequear(len(no_dec) == 1 and no_dec[0]["etiqueta_analisis"] == "no_puedo_decidir",
             "la fila 'no_puedo_decidir' explica las series de 9.724 casos decidibles")

    print("\nCONCLUSIÓN: " + ("los dos archivos son el mismo run; los totales difieren "
                             "exactamente por la regla de procedencia (§7)." if ok else
                             "NO se confirmó la reconciliación: revisar los FAIL de arriba."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(principal())
