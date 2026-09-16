# ------------------------------------------------------------------------
# 16_validacion_serie_stance.py -- Validacion agregada de etiquetas IA
# ------------------------------------------------------------------------
# Proposito: antes de contar con el gold, validar que las convenciones del
# etiquetado IA son coherentes a nivel REUNION: el score medio por reunion
# s = mean(PH-PD) sobre intervenciones relevantes debe alinearse con dTPM
# (decision del Consejo) y con policy_decision (sube/baja/mantiene).
# No es una prueba formal de calidad (eso sera el kappa chat-vs-humano del
# gold), pero detecta violaciones groseras de la semantica del codebook v2.
#
# Definiciones (config.py): mapeo de decision a clase esperada
#   sube -> hawkish | baja -> dovish | mantiene -> neutral
# Class dominante de reunion = argmax(mean P_h, mean P_d, mean P_n).
#
# Salidas:
#   data/L2/serie_stance_reunion.csv   s por reunion + concordancia
#   data/L2/validacion_serie_stance.json  correlaciones y precision direccional
# Uso:  ~/venvs/fase2/bin/python scripts/16_validacion_serie_stance.py
# ------------------------------------------------------------------------

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
import pandas as pd
import numpy as np
from utilidades import cargar_entrenamiento
from scipy.stats import pearsonr, spearmanr

MAPA_CLASE = {"sube": "hawkish", "baja": "dovish", "mantiene": "neutral"}
# Umbral de la regla descriptiva |s| > th -> direccional. Seleccionado sobre
# estas mismas 131 reuniones para maximizar precision direccional (sesgo
# optimista declarado en el JSON); sirve como referencia, no como inferencia.
UMBRALES_S = [0.00, 0.05, 0.10]


def main():
    # Etiquetas IA relevantes
    etq = cargar_entrenamiento()
    etq["es_relevante"] = etq.es_relevante.astype(str)
    etq["meeting_id"] = etq["intervencion_id"].str.extract(r"(RPM-\d{4}-\d{2}-\d{2})")
    for c in ["prob_hawkish", "prob_dovish", "prob_neutral", "score"]:
        etq[c] = etq[c].astype(float)
    rel = etq[etq["es_relevante"] == "1"].copy()
    assert not rel.empty

    # Serie por reunion
    g = rel.groupby("meeting_id", sort=True)
    s = g.agg(n_int=("intervencion_id", "size"),
              fecha=("meeting_id", lambda x: x.iloc[0].replace("RPM-", "")),
              pH=("prob_hawkish", "mean"),
              pD=("prob_dovish", "mean"),
              pN=("prob_neutral", "mean"),
              s_score=("score", "mean")).reset_index()
    s["clase_dominante"] = s[["pH", "pD", "pN"]].idxmax(axis=1).map(
        {"pH": "hawkish", "pD": "dovish", "pN": "neutral"})

    # Union con decision TPM
    macro = pd.read_csv(config.RUTA_L2 / "macro_por_reunion.csv",
                        dtype=str, keep_default_na=False)
    macro["dTPM"] = macro["dTPM"].astype(float)
    assert macro.meeting_id.is_unique, "macro con reuniones duplicadas"
    assert set(macro.policy_decision) <= set(MAPA_CLASE)
    assert np.isfinite(macro.dTPM).all()
    d = s.merge(macro[["meeting_id", "dTPM", "policy_decision"]], on="meeting_id",
                how="left", validate="one_to_one", indicator=True)
    assert d["_merge"].eq("both").all(), "reuniones con etiquetas sin macro"
    d = d.drop(columns="_merge")

    # Concordancia direccional (clase dominante vs decision)
    d["concuerda"] = d["clase_dominante"] == d["policy_decision"].map(MAPA_CLASE)
    prec = float(d["concuerda"].mean())

    # Correlaciones s_score vs dTPM
    pr, pr_p = pearsonr(d["s_score"], d["dTPM"])
    sr, sr_p = spearmanr(d["s_score"], d["dTPM"])

    # Regla de umbrales: |s| > th predice la direccion de la decision
    regla_ok = {}
    for th in UMBRALES_S:
        pred_dec = d["s_score"].apply(
            lambda v: "sube" if v > th else ("baja" if v < -th else "mantiene"))
        regla_ok[f"th_{th:.2f}"] = round(float((pred_dec == d["policy_decision"]).mean()), 4)

    # Desglose por decision
    desglose = {}
    for dec, sub in d.groupby("policy_decision"):
        desglose[dec] = dict(
            n=int(len(sub)),
            media_s=round(float(sub["s_score"].mean()), 4),
            concordancia=round(float(sub["concuerda"].mean()), 4))

    # Reuniones con peor discordancia: decision fuerte y s con signo contrario
    discord = d[((d["dTPM"] >= 0.25) & (d["s_score"] < 0)) |
                ((d["dTPM"] <= -0.25) & (d["s_score"] > 0))]
    d_out = d[["meeting_id", "fecha", "n_int", "pH", "pD", "pN", "s_score",
               "dTPM", "policy_decision", "clase_dominante", "concuerda"]].round(4)
    d_out.to_csv(config.RUTA_L2 / "serie_stance_reunion.csv", index=False)

    resumen = dict(
        n_reuniones=int(len(d)),
        reuniones_con_etiquetas_ia=int(len(d)),
        precision_direccional=round(prec, 4),
        pearson_s_vs_dTPM=round(float(pr), 4), pearson_p=round(float(pr_p), 6),
        spearman_s_vs_dTPM=round(float(sr), 4), spearman_p=round(float(sr_p), 6),
        por_decision=desglose,
        regla_direccion=regla_ok,
        sesgo_umbral="el umbral que maximiza se eligio sobre la misma muestra "
                     "(uso descriptivo, no inferencial)",
        n_discordancias_fuertes=int(len(discord)),
        discordancias=discord[["meeting_id", "s_score", "dTPM",
                               "clase_dominante", "policy_decision",
                               "n_int"]].to_dict("records"),
        nota="Validacion preliminar a nivel reunion del etiquetado IA; "
             "la prueba formal sera el kappa vs gold humano (decision 9).")
    with open(config.RUTA_L2 / "validacion_serie_stance.json", "w",
              encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)

    print(f"reuniones: {len(d)} | precision direccional: {prec:.3f}")
    print(f"pearson(s, dTPM) = {pr:.3f} (p={pr_p:.2e})")
    print(f"spearman         = {sr:.3f} (p={sr_p:.2e})")
    for dec, v in desglose.items():
        print(f"  {dec:9s} n={v['n']:3d} media_s={v['media_s']:+.3f} concord={v['concordancia']:.3f}")
    print("regla |s|>th:", regla_ok)
    if len(discord):
        print(f"discordancias fuertes: {len(discord)}")
        print(discord[["meeting_id", "s_score", "dTPM",
                       "clase_dominante", "policy_decision"]].to_string(index=False))


if __name__ == "__main__":
    main()
