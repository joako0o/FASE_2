# 10_muestra_enriquecida.py
# =============================================================================
# Muestra enriquecida de stance para el training set (decisión 10 del PLAN)
#
# CONTEXTO
# Diagnóstico del desbalance del training set cerrado (sesión 8f AVANCE): de
# las 1.025 etiquetas ia_ronda, 88% son neutrales (incluye 213 con
# es_relevante=0, logística procedural filtrable) y solo 122 (12%) son
# hawkish+dovish (69/53), insuficiente para un fine-tune estable de las clases
# minoritarias. La distribución es en parte genuina (las actas RPM son
# mayoritariamente descriptivas), pero el n de minoritarias es un riesgo
# concreto: el modelo tendería a sub-predecir H/D, que es donde vive la señal
# para la serie mensual s_i.
#
# MITIGACIÓN (decisión 10, tanto como la opción elegida por el investigador)
# Parte 1 (este script): ~250 intervenciones adicionales etiquetadas en chat
# (tandas 9+, mismas reglas del codebook v2), muestreadas CON ENRIQUECIMIENTO
# de los tramos donde vive el stance:
#   - pool A: votos/posiciones del Consejo (config.CARGOS_CONSEJO) con señal
#     de decisión (config.PATRON_DECISION);
#   - pool B: minuta de opciones del staff (config.CARGOS_OPCIONES) con señal.
# Parte 2 (Fase 7/8): modelo en dos etapas — etapa A filtra stance
# (procedural / descriptivo / con-stance) usando es_relevante y las etiquetas
# actuales; etapa B clasifica H/D/N solo sobre lo filtrado.
#
# REGLAS
# - Exclusión dura: todo lo ya etiquetado en data/etiquetas/ y TODO el gold
#   ciego (data/muestras/gold_ciego_300.csv), que es test puro.
# - Estratificación por fase (config.FASES_TPM sin 2005_alzas: 2005 ya tiene
#   alta densidad H/D en el training set, 17,8%, la mayor de todas).
# - Troceo en tandas por presupuesto de palabras (config), numeración
#   continuando en 9 (las tandas 5 a 8 son las del estrato por fases).
#
# SOBRE EL SESGO DE SELECCIÓN (documentado, no oculto): este bloque NO sigue
# la distribución poblacional — a propósito. La evaluación honesta del modelo
# se hace contra el gold 306 (diseño propio, instrumentado en 09) y las
# métricas se reportan por clase y por sub-estrato del gold.
#
# SALIDA: data/muestras/estrato_enriquecido.csv + _resumen.csv
# =============================================================================

import glob

import pandas as pd
from utilidades import exigir_salidas_nuevas, asignar_tandas

import config as C

SEMILLA = C.SEED_MAESTRA + 2
CUOTA_FASE = 28            # 9 fases * 28 = 252 intervenciones
MAX_POOL_A = 20            # tope Consejo por fase (equilibrio A/B ~ 70/30)
TANDA_INICIAL = 9

FASES = [f for f in C.FASES_TPM if f[0] != "2005_alzas"]


def main() -> None:
    # Fuentes/muestras congeladas: no regenerar sobre selecciones existentes.
    exigir_salidas_nuevas(C.RUTA_MUESTRAS / "estrato_enriquecido.csv", C.RUTA_MUESTRAS / "estrato_enriquecido_resumen.csv")
    uni = pd.read_csv(C.RUTA_MUESTRAS / "escalado_tandas.csv", parse_dates=["fecha"])

    # exclusiones duras: etiquetadas (cualquier ronda) + gold ciego (test puro)
    ya = set()
    for f in glob.glob(str(C.RUTA_ETIQUETAS / "etiquetas_*.csv")):
        ya |= set(pd.read_csv(f, usecols=["intervencion_id"]).intervencion_id)
    gold = pd.read_csv(C.RUTA_MUESTRAS / "gold_ciego_300.csv",
                       usecols=["intervencion_id"])
    ya |= set(gold.intervencion_id)
    libre = uni[~uni.intervencion_id.isin(ya)].copy()

    senal = libre.texto.str.contains(C.PATRON_DECISION, case=False)
    libre["pool"] = "fuera"
    libre.loc[senal & libre.cargo.isin(C.CARGOS_OPCIONES), "pool"] = "B_opciones"
    libre.loc[senal & libre.cargo.isin(C.CARGOS_CONSEJO), "pool"] = "A_consejo"

    partes = []
    for nombre, ini, fin in FASES:
        cand = libre[(libre.fecha >= ini) & (libre.fecha <= fin)]
        pool_a = cand[cand.pool == "A_consejo"]
        pool_b = cand[cand.pool == "B_opciones"]
        a = pool_a.sample(n=min(MAX_POOL_A, len(pool_a)), random_state=SEMILLA)
        b = pool_b.sample(n=min(CUOTA_FASE - len(a), len(pool_b)),
                          random_state=SEMILLA)
        falta = CUOTA_FASE - len(a) - len(b)
        assert falta == 0, f"fase {nombre}: {len(a)}+{len(b)} < {CUOTA_FASE}"
        sel = pd.concat([a, b]).assign(fase=nombre)
        partes.append(sel)
        print(f"  {nombre}: A={len(a)} B={len(b)} total={len(sel)} "
              f"(disponibles A={len(pool_a)}, B={len(pool_b)})")
    muestra = pd.concat(partes)
    assert muestra.intervencion_id.is_unique
    assert not muestra.intervencion_id.isin(ya).any()

    # orden aleatorio dentro de fase (shuffle global con seed + 1); troceo
    orden_fase = {f[0]: i for i, f in enumerate(FASES)}
    muestra = (muestra.sample(frac=1, random_state=SEMILLA + 1)
                      .assign(orden_f=lambda d: d.fase.map(orden_fase))
                      .sort_values("orden_f", kind="stable"))
    muestra["tanda"] = asignar_tandas(muestra.largo_palabras, C.PRESUPUESTO_PALABRAS_TANDA, TANDA_INICIAL)
    tanda = int(muestra.tanda.max())

    out = muestra.drop(columns=["orden_f"])
    out.to_csv(C.RUTA_MUESTRAS / "estrato_enriquecido.csv", index=False)
    resumen = (out.groupby(["tanda", "fase"], as_index=False)
                  .agg(intervenciones=("intervencion_id", "count"),
                       palabras=("largo_palabras", "sum"),
                       desde=("fecha", "min"), hasta=("fecha", "max")))
    resumen.to_csv(C.RUTA_MUESTRAS / "estrato_enriquecido_resumen.csv",
                   index=False)
    print(f"\nestrato_enriquecido: {len(out)} intervenciones / "
          f"{out.largo_palabras.sum():,} palabras en tandas "
          f"{TANDA_INICIAL}-{tanda}")
    print(resumen.to_string(index=False))


if __name__ == "__main__":
    main()
