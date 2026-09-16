# 10_muestra_tanda9_stance.py
# =============================================================================
# Tanda 9 enriquecida en stance (decisión 10 del PLAN)
#
# CONTEXTO
# El training set estratificado por fases (tandas 1-8, 1.025 etiquetas) quedó
# 85% neutral / 15% H+D (n=122), fiel a la composición real de las actas pero
# insuficiente para un fine-tune estable de las clases minoritarias. Esta
# muestra añade ~250 intervenciones nuevas, sobre-representando los roles y
# textos donde concentra la posición de política monetaria.
#
# DISEÑO
# - Universo: escalado_tandas.csv menos (a) TODA intervención ya etiquetada en
#   data/etiquetas/ y menos (b) el gold ciego de 306 (decisión 9): el gold es
#   test puro y la tanda 9 es entrenamiento, no pueden intersectar.
# - Sub-estratos de enriquecimiento (cuotas CUOTAS):
#   * autoridad_señal: consejeros/presidencia/vicepresidencia/ministerio o
#     comunicados del Consejo CON vocabulario de decisión (máxima densidad H/D);
#   * staff_señal: resto del personal CON vocabulario de decisión (opciones y
#     reseñas de votación del staff);
#   * resto_sin_señal: intervenciones descriptivas sin vocabulario de decisión
#     (mantiene diversidad de ejemplos neutrales y evita que el modelo aprenda
#     que "vocabulario de decisión == clase minoritaria").
#   El patrón de decisión es el mismo regex documentado de
#   09_muestra_gold_ciego.py (centralizado en config.py).
# - Tandas: orden aleatorio por sub-estrato y troceo por presupuesto de
#   palabras (config.PRESUPUESTO_PALABRAS_TANDA) continuando la numeración: la
#   numeración de tandas 1-4 cronológicas y 5-8 estratificadas ya está cerrada;
#   esta muestra continúa en la tanda 9.
#
# PARÁMETROS: constantes de este archivo + config.PRESUPUESTO_PALABRAS_TANDA.
# SALIDA: data/muestras/estrato_tanda9.csv + estrato_tanda9_resumen.csv
# =============================================================================

import glob
import re

import pandas as pd
from utilidades import exigir_salidas_nuevas, asignar_tandas

import config as C

SEMILLA = C.SEED_MAESTRA + 2
TANDA_INICIAL = 9
CUOTAS = {"autoridad_señal": 150, "staff_señal": 62, "resto_sin_señal": 38}
PATRON_DECISION = re.compile(C.PATRON_DECISION, re.IGNORECASE)
MASCARA_AUTORIDAD = re.compile(r"Consejero|Presidente|Vicepresidente")

# mismas fases que 08_muestra_estrato_fases.py + tramo inicial 2005
FASES = C.FASES_TPM


def main() -> None:
    # Fuentes/muestras congeladas: no regenerar sobre selecciones existentes.
    exigir_salidas_nuevas(C.RUTA_MUESTRAS / "estrato_tanda9.csv", C.RUTA_MUESTRAS / "estrato_tanda9_resumen.csv")
    uni = pd.read_csv(C.RUTA_MUESTRAS / "escalado_tandas.csv", parse_dates=["fecha"])

    ya = pd.concat([pd.read_csv(f, usecols=["intervencion_id"])
                    for f in glob.glob(str(C.RUTA_ETIQUETAS / "etiquetas_*.csv"))])
    gold = pd.read_csv(C.RUTA_MUESTRAS / "gold_ciego_300.csv",
                       usecols=["intervencion_id"])
    excluidos = set(ya.intervencion_id) | set(gold.intervencion_id)
    libre = uni[~uni.intervencion_id.isin(excluidos)].copy()
    assert len(libre) == len(uni) - len(excluidos & set(uni.intervencion_id))

    libre["senal_decision"] = libre.texto.str.contains(PATRON_DECISION)
    es_consejo = libre.cargo.str.contains(MASCARA_AUTORIDAD, na=False) | \
        libre.actor.str.contains("Consejo del Banco Central|Ministro", na=False)
    libre["subestrato"] = "resto_sin_señal"
    libre.loc[libre.senal_decision & ~es_consejo, "subestrato"] = "staff_señal"
    libre.loc[libre.senal_decision & es_consejo, "subestrato"] = "autoridad_señal"

    partes = []
    for nombre, cuota in CUOTAS.items():
        cand = libre[libre.subestrato == nombre]
        assert len(cand) >= cuota, f"{nombre}: solo {len(cand)} candidatos"
        partes.append(cand.sample(n=cuota, random_state=SEMILLA))
        print(f"  {nombre}: muestra {cuota}/{len(cand)}")
    muestra = pd.concat(partes)
    assert muestra.intervencion_id.is_unique, "duplicados en la muestra"

    # fase por fecha (para cobertura y documentación)
    def fase_de(fecha):
        for nombre, ini, fin in FASES:
            if ini <= str(fecha.date()) <= fin:
                return nombre
        return "fuera_fase"
    muestra["fase"] = muestra.fecha.map(fase_de)
    cobertura = muestra.groupby("fase").size()
    # 2005 ya está densamente cubierto por el piloto y las tandas 1-4; se exige
    # cobertura mínima solo en las fases 2006 en adelante
    control = cobertura.reindex([f[0] for f in FASES if f[0] != "2005_alzas"], fill_value=0)
    assert (control >= 10).all(), f"fases con menos de 10 ítems: {cobertura}"

    muestra = muestra.sample(frac=1, random_state=SEMILLA + 1).reset_index(drop=True)
    muestra["tanda"] = asignar_tandas(muestra.largo_palabras, C.PRESUPUESTO_PALABRAS_TANDA, TANDA_INICIAL)
    tanda = int(muestra.tanda.max())

    muestra.to_csv(C.RUTA_MUESTRAS / "estrato_tanda9.csv", index=False)
    resumen = (muestra.groupby(["tanda", "subestrato"], as_index=False)
                      .agg(intervenciones=("intervencion_id", "count"),
                           palabras=("largo_palabras", "sum"),
                           desde=("fecha", "min"), hasta=("fecha", "max")))
    resumen.to_csv(C.RUTA_MUESTRAS / "estrato_tanda9_resumen.csv", index=False)
    print(f"\nestrato_tanda9: {len(muestra)} intervenciones / "
          f"{muestra.largo_palabras.sum():,} palabras "
          f"en tandas {TANDA_INICIAL}-{tanda}")
    print(resumen.to_string(index=False))
    print("\npor fase:")
    print(cobertura.to_string())


if __name__ == "__main__":
    main()
