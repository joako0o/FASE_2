"""
06_tandas_escalado.py — Genera las tandas de la Fase 5 (escalado al corpus completo).

Que hace:
    1. Toma la capa L0, excluye los 51 registros con texto dañado (R8) y las 300
       intervenciones del piloto (ya etiquetadas o reservadas a validacion).
    2. Ordena el universo restante cronologicamente y lo empaqueta en tandas de
       PRESUPUESTO_PALABRAS_TANDA palabras (misma regla operativa que el piloto,
       acordada con el investigador en sesion 4).
    3. Escribe data/muestras/escalado_tandas.csv (universo con columna tanda) y
       data/muestras/escalado_tandas_resumen.csv (controles por tanda).

Por que asi: Fase 5 escala el etiquetado IA al universo completo en rondas de
chat. Las tandas por presupuesto de palabras hacen el trabajo por turno
predecible, y el orden cronologico preserva la continuidad del analisis.

Ejecucion:  python scripts/06_tandas_escalado.py
"""

import pandas as pd
from utilidades import exigir_salidas_nuevas, asignar_tandas

from config import (
    PRESUPUESTO_PALABRAS_TANDA,
    RUTA_L0,
    RUTA_MUESTRAS,
)


def construir_universo() -> pd.DataFrame:
    """Corpus etiquetable: L0 integro menos piloto y menos texto danado."""
    corpus = pd.read_csv(RUTA_L0 / "corpus.csv")
    sano = corpus[~corpus["flag_texto_danado"]].copy()
    piloto = pd.read_csv(RUTA_MUESTRAS / "piloto_300.csv")
    universo = sano[~sano["intervencion_id"].isin(piloto["intervencion_id"])].copy()
    universo = universo.sort_values(["fecha", "intervencion_id"]).reset_index(drop=True)

    # Controles estructurales del universo
    assert len(corpus) == 9725, "L0 debe tener 9.725 filas"
    assert len(piloto) == 300, "piloto debe tener 300 filas"
    assert len(universo) == len(sano) - 300, "universo = sano - piloto"
    assert not universo["intervencion_id"].duplicated().any(), "IDs duplicados en universo"
    return universo


def empaquetar_universo(universo: pd.DataFrame) -> pd.DataFrame:
    """Empaqueta cronologicamente en tandas de PRESUPUESTO_PALABRAS_TANDA palabras."""
    universo = universo.copy()
    universo["tanda"] = asignar_tandas(universo.largo_palabras, PRESUPUESTO_PALABRAS_TANDA)
    resumen = (
        universo.groupby("tanda")
        .agg(n_intervenciones=("intervencion_id", "count"),
             n_palabras=("largo_palabras", "sum"),
             fecha_min=("fecha", "min"),
             fecha_max=("fecha", "max"))
        .reset_index()
    )
    # Cada tanda excedida solo puede contener un texto indivisible.
    excedidas = resumen[resumen.n_palabras > PRESUPUESTO_PALABRAS_TANDA]
    assert excedidas.n_intervenciones.eq(1).all(), "tanda múltiple excede presupuesto"
    return universo, resumen


def main() -> None:
    # Fuentes/muestras congeladas: no regenerar sobre selecciones existentes.
    exigir_salidas_nuevas(RUTA_MUESTRAS / "escalado_tandas.csv", RUTA_MUESTRAS / "escalado_tandas_resumen.csv")
    universo = construir_universo()
    universo, resumen = empaquetar_universo(universo)
    universo.to_csv(RUTA_MUESTRAS / "escalado_tandas.csv", index=False)
    resumen.to_csv(RUTA_MUESTRAS / "escalado_tandas_resumen.csv", index=False)
    print(f"universo escalado: {len(universo)} intervenciones, "
          f"{universo['largo_palabras'].sum():,} palabras, {resumen['tanda'].max()} tandas")
    print(resumen.head(12).to_string())


if __name__ == "__main__":
    main()
