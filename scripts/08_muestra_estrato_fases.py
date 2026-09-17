# 08_muestra_estrato_fases.py
# =============================================================================
# Muestra estratificada del training set por fase de política monetaria (2006-2015)
#
# CONTEXTO
# Decisión 8 del PLAN (2026-09-15): el etiquetado en chat construye un training
# set de ~1.000 intervenciones para el fine-tune de BETO; el modelo etiqueta el
# resto del corpus en la Fase 8. El bloque cronológico (tandas 1 a 4 del
# escalado: ene-2005 a jul-2005) ya cubre la fase de alzas 2,25 -> 4,50% TPM.
# Este script muestrea el resto del universo de escalado (2005-07 en adelante)
# de forma estratificada por fase del ciclo de política monetaria, tal que el
# modelo vea ejemplos de todos los regímenes observados 2005-2015
# (alzas 2006, mixto 2007, crisis-alza 2008, bajas 2009, alzas 2010-11,
# mantención 2012-13, bajas 2013-14 y quiebre 2015).
#
# MÉTODO
# - Universo: escalado_tandas.csv (corpus L0 sano menos piloto), excluyendo las
#   tandas 1 a 4 (ya etiquetadas o reservadas al cierre cronológico de 2005) y
#   cualquier intervención ya etiquetada en data/etiquetas/.
# - Estratos: fases delimitadas por las transiciones reales de policy_decision
#   en data/L2/macro_por_reunion.csv (ver FASES abajo).
# - Asignación: cuota fija por fase (CUOTA_FASE), muestreo aleatorio sin
#   reemplazo dentro de cada fase (seed SEMILLA). Si la fase tiene menos
#   intervenciones que la cuota, se toma completa (assert informativo).
# - Tandas: la muestra se ordena por (fase, aleatorio) y se trocea por
#   presupuesto de palabras (PRESUPUESTO_PALABRAS_TANDA de config.py)
#   continuando la numeración de tandas en 5.
#
# PARÁMETROS: solo contantes de este archivo + config.PRESUPUESTO_PALABRAS_TANDA.
# SALIDA: data/muestras/estrato_fases.csv + data/muestras/estrato_fases_resumen.csv
# =============================================================================

import glob
import pandas as pd
from utilidades import exigir_salidas_nuevas, asignar_tandas
import config as C

SEMILLA = C.SEED_MAESTRA
CUOTA_FASE = 42            # intervenciones por fase (9 fases * 42 = 378)
TANDA_INICIAL = 5          # la tanda 4 cierra el bloque cronológico 2005

# Fases del ciclo de política monetaria, derivadas de data/L2/macro_por_reunion.csv
# (transiciones policy_decision; el límite es la fecha de la reunión RPM).
# (nombre, inicio, fin), centralizado en config.
FASES = [f for f in C.FASES_TPM if f[0] != "2005_alzas"]


def main():
    # Fuentes/muestras congeladas: no regenerar sobre selecciones existentes.
    exigir_salidas_nuevas(C.RUTA_MUESTRAS / "estrato_fases.csv", C.RUTA_MUESTRAS / "estrato_fases_resumen.csv")
    uni = pd.read_csv(C.RUTA_MUESTRAS / "escalado_tandas.csv", parse_dates=["fecha"])
    uni = uni[uni.tanda >= TANDA_INICIAL].copy()

    # exclusiones: tandas 1-4 ya en curso, pinte etiquetado en cualquier ronda
    ya = pd.concat([pd.read_csv(f, usecols=["intervencion_id"]) for f in glob.glob(str(C.RUTA_ETIQUETAS / "*.csv"))])
    uni = uni[~uni.intervencion_id.isin(ya.intervencion_id)]
    assert not uni.flag_texto_danado.astype(bool).any(), "el universo de escalado no admite texto dañado"

    partes = []
    for nombre, ini, fin in FASES:
        cand = uni[(uni.fecha >= ini) & (uni.fecha <= fin)]
        n = min(CUOTA_FASE, len(cand))
        sel = cand.sample(n=n, random_state=SEMILLA).assign(fase=nombre)
        partes.append(sel)
        print(f"  {nombre}: muestra {n}/{len(cand)} intervenciones")
    muestra = pd.concat(partes)
    assert muestra.intervencion_id.is_unique, "duplicados en la muestra estratificada"

    # ordenando: fase (según lista) y azar dentro de fase; troceo por palabras
    orden_fase = {f[0]: i for i, f in enumerate(FASES)}
    muestra = (muestra.sample(frac=1, random_state=SEMILLA + 1)
                      .assign(orden_f=lambda d: d.fase.map(orden_fase))
                      .sort_values("orden_f", kind="stable"))
    muestra["tanda"] = asignar_tandas(muestra.largo_palabras, C.PRESUPUESTO_PALABRAS_TANDA, TANDA_INICIAL)
    tanda = int(muestra.tanda.max())

    out = muestra.drop(columns=["orden_f"])
    out.to_csv(C.RUTA_MUESTRAS / "estrato_fases.csv", index=False)
    resumen = (out.groupby(["tanda", "fase"], as_index=False)
                  .agg(intervenciones=("intervencion_id", "count"),
                       palabras=("largo_palabras", "sum"),
                       desde=("fecha", "min"), hasta=("fecha", "max")))
    resumen.to_csv(C.RUTA_MUESTRAS / "estrato_fases_resumen.csv", index=False)

    print(f"\nestrato_fases: {len(out)} intervenciones / {out.largo_palabras.sum():,} palabras "
          f"en tandas {TANDA_INICIAL}-{tanda}")
    print(resumen.to_string(index=False))

if __name__ == "__main__":
    main()
