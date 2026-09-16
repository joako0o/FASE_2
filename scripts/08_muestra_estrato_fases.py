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
import config as C

SEMILLA = 20260915
CUOTA_FASE = 42            # intervenciones por fase (9 fases * 42 = 378)
TANDA_INICIAL = 5          # la tanda 4 cierra el bloque cronológico 2005

# Fases del ciclo de política monetaria, derivadas de data/L2/macro_por_reunion.csv
# (transiciones policy_decision; el límite es la fecha de la reunión RPM).
# (nombre, inicio, fin, descripción)
FASES = [
    ("2006_alza_fin",       "2005-07-13", "2006-12-31", "alzas finales del ciclo hasta 5,25%"),
    ("2007_mixto",          "2007-01-01", "2007-12-31", "baja de enero y cuatro alzas en el semestre 2"),
    ("2008_crisis_alza",    "2008-01-01", "2008-12-31", "alzas hasta 7,75% en pleno shock inflacionario"),
    ("2009_bajas",          "2009-01-01", "2009-12-31", "siete bajas agresivas hasta piso 0,5%"),
    ("2010_alza_emergencia","2010-01-01", "2010-12-31", "salida de la tasa de emergencia hasta 3,0%"),
    ("2011_alza",           "2011-01-01", "2011-12-31", "alzas hasta 5,0% y pausa en el semestre 2"),
    ("2012_13_mantiene",    "2012-01-01", "2013-09-30", "mantención prolongada (salvo baja ene-2012)"),
    ("2013_14_bajas",       "2013-10-01", "2014-12-31", "ciclo de bajas hasta 3,0%"),
    ("2015_quiebre",        "2015-01-01", "2015-12-31", "mantención 9 meses y primeras alzas del nuevo ciclo"),
]

CARGA_DANADA = {"flag_texto_danado", "flag_cotejo"}

def main():
    uni = pd.read_csv(C.RUTA_MUESTRAS / "escalado_tandas.csv", parse_dates=["fecha"])
    uni = uni[uni.tanda >= TANDA_INICIAL].copy()

    # exclusiones: tandas 1-4 ya en curso, pinte etiquetado en cualquier ronda
    ya = pd.concat([pd.read_csv(f, usecols=["intervencion_id"]) for f in glob.glob(str(C.RUTA_ETIQUETAS / "*.csv"))])
    uni = uni[~uni.intervencion_id.isin(ya.intervencion_id)]
    assert not uni.flag_texto_danado.astype(bool).any(), "el universo de escalado no admite texto dañado"

    partes = []
    for nombre, ini, fin, _ in FASES:
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
    tandas, tanda, acum = [], TANDA_INICIAL, 0
    for palabras in muestra.largo_palabras:
        if acum + palabras > C.PRESUPUESTO_PALABRAS_TANDA and acum > 0:
            tanda, acum = tanda + 1, 0
        tandas.append(tanda)
        acum += palabras
    muestra["tanda"] = tandas

    out = muestra.drop(columns=["orden_f"])
    out.to_csv(C.RUTA_MUESTRAS / "estrato_fases.csv", index=False)
    resumen = (out.groupby(["tanda", "fase"], as_index=False)
                  .agg(intervenciones=("intervencion_id", "count"),
                       palabras=("largo_palabras", "sum"),
                       desde=("fecha", "min"), hasta=("fecha", "max")))
    resumen.to_csv(C.RUTA_MUESTRAS / "estrato_fases_resumen.csv", index=False)

    etiquetadas_ya = len(ya) + 52   # 52 = tanda 4 cronológica (pendiente de etiquetar)
    total_proy = etiquetadas_ya + len(out)
    print(f"\nestrato_fases: {len(out)} intervenciones / {out.largo_palabras.sum():,} palabras "
          f"en tandas {TANDA_INICIAL}-{tanda}")
    print(f"proyección training set: {total_proy:,} intervenciones (meta ~1.000)")
    print(resumen.to_string(index=False))

if __name__ == "__main__":
    main()
