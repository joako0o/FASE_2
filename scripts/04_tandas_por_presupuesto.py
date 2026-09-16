"""
04_tandas_por_presupuesto.py — Asigna cada intervencion del piloto a una tanda por presupuesto de palabras.

Que hace:
    1. Lee la muestra piloto (ordenada cronologicamente por el script 03).
    2. Recorre las filas acumulando palabras; al superar el presupuesto de la
       tanda (config.PRESUPUESTO_PALABRAS_TANDA) abre la siguiente tanda.
    3. Escribe la asignacion (columna tanda) y un resumen por tanda.

Por que asi:
    - Acordado con el investigador: el limite operativo por turno de etiquetado
      es de PALABRAS de lectura, no de numero de intervenciones (hay textos de
      34 y de miles de palabras; medir por intervenciones distorsiona la carga).
    - Determinista: mismo piloto + mismo presupuesto -> misma asignacion.
    - Excepcion documentada: si un unico texto excede el presupuesto, forma una
      tanda propia (se marca excede_presupuesto=True) en vez de partirse.

Ejecucion:  python scripts/04_tandas_por_presupuesto.py   (despues del script 03)
Entrada:    data/muestras/piloto_300.csv
Salida:     data/muestras/piloto_300_tandas.csv, data/muestras/tandas_resumen.csv
"""

import pandas as pd

from config import PRESUPUESTO_PALABRAS_TANDA, RUTA_MUESTRAS


def asignar_tandas(df: pd.DataFrame, presupuesto: int) -> pd.Series:
    """Asignacion greedy secuencial de tandas por acumulacion de palabras."""
    tandas = []
    tanda, acumulado = 1, 0
    for palabras in df["largo_palabras"]:
        if acumulado > 0 and acumulado + palabras > presupuesto:
            tanda, acumulado = tanda + 1, 0
        acumulado += palabras
        tandas.append(tanda)
    return pd.Series(tandas, index=df.index, name="tanda")


def main() -> None:
    # ---- 1. Carga y asignacion determinista de tandas ----
    df = pd.read_csv(RUTA_MUESTRAS / "piloto_300.csv")
    df["tanda"] = asignar_tandas(df, PRESUPUESTO_PALABRAS_TANDA)

    # ---- 2. Resumen por tanda (insumo para planificar los turnos) ----
    resumen = (
        df.groupby("tanda")
        .agg(
            intervenciones=("intervencion_id", "count"),
            palabras=("largo_palabras", "sum"),
            anio_min=("anio", "min"),
            anio_max=("anio", "max"),
            excede_presupuesto=("largo_palabras", lambda s: bool((s > PRESUPUESTO_PALABRAS_TANDA).any())),
        )
        .reset_index()
    )

    # ---- 3. Validaciones basicas ----
    assert len(df) == 300
    assert df["intervencion_id"].is_unique
    assert resumen["tanda"].is_unique
    sobrias = resumen[~resumen["excede_presupuesto"]]["palabras"]
    assert (sobrias <= PRESUPUESTO_PALABRAS_TANDA).all(), "tanda sobria excede el presupuesto"

    # ---- 4. Escritura y reporte ----
    df.to_csv(RUTA_MUESTRAS / "piloto_300_tandas.csv", index=False, encoding="utf-8")
    resumen.to_csv(RUTA_MUESTRAS / "tandas_resumen.csv", index=False, encoding="utf-8")
    print(resumen.to_string(index=False))
    print(f"\npresupuesto por tanda: {PRESUPUESTO_PALABRAS_TANDA} palabras | tandas totales: {resumen['tanda'].max()}")


if __name__ == "__main__":
    main()
