"""
03_muestra_piloto.py — Genera la muestra piloto estratificada (n=300) y la submuestra test-retest.

Que hace:
    1. Carga la capa L0 y asigna a cada intervencion un grupo de actor
       (consejo_votante, ministro_hacienda, staff_tecnico, consejo_entidad).
    2. Excluye del universo los registros con texto dañado (flag_texto_danado).
    3. Estratifica por año x grupo de actor: minimo por estrato + asignacion
       proporcional (metodo de residuos mayores) hasta llegar exactamente a 300.
    4. Muestrea con semilla maestra derivada por estrato (reproducible).
    5. Selecciona dentro del piloto la submuestra test-retest de 30, que se
       re-etiquetara en cada ronda para medir estabilidad.
    6. Valida con asserts y escribe los CSV.

Por que asi:
    - Estratificar por año evita que la muestra se concentre en pocos periodos
      (el lenguaje monetario cambia en el tiempo).
    - El grupo de actor evita sobrerrepresentar al staff tecnico (que habla mucho
      y es mayormente neutral) y garantiza votantes en la muestra.
    - Se excluye texto dañado porque no es evaluable (codebook v2, R8).

Ejecucion:  python scripts/03_muestra_piloto.py   (despues del script 01)
Entrada:    data/L0/corpus.csv
Salida:     data/muestras/piloto_300.csv, data/muestras/test_retest_30.csv,
            data/muestras/piloto_300_estratos.csv
"""

import pandas as pd

from config import MIN_POR_ESTRATO, N_PILOTO, N_TEST_RETEST, RUTA_L0, RUTA_MUESTRAS, SEED_MAESTRA

# Cargos con derecho a voto en la decision de TPM (consejeros, VP y Presidente).
CARGOS_VOTANTES = {
    "Presidente del Banco Central",
    "Vicepresidente del Banco Central",
    "Consejero",
}

COLUMNAS_SALIDA = [
    "intervencion_id", "meeting_id", "fecha", "anio", "actor", "cargo",
    "grupo_actor", "topico", "keywords", "largo_palabras",
    "flag_cotejo", "detalle_cotejo", "texto",
]


def grupo_de_actor(cargo: str) -> str:
    """Asigna el grupo estratificador segun el cargo (ver docstring del script)."""
    if cargo == "Consejo":
        return "consejo_entidad"
    if cargo == "Ministro de Hacienda":
        return "ministro_hacienda"
    if cargo in CARGOS_VOTANTES:
        return "consejo_votante"
    return "staff_tecnico"


def asignar_cupos(conteos: pd.Series, n_total: int, minimo: int) -> pd.Series:
    """Reparte n_total entre estratos: minimo garantizado + resto proporcional.

    Metodo: base = min(minimo, tamano_del_estrato); el resto se reparte en
    proporcion al tamano y el residuo entero se asigna por decimales mayores.
    Si algun estrato queda topeado por su tamano, el sobrante se redistribuye
    iterativamente hasta completar n_total exacto.
    """
    cupos = conteos.clip(upper=minimo).astype(int)
    restante = n_total - cupos.sum()
    while restante > 0:
        capacidad = (conteos - cupos).clip(lower=0)
        if capacidad.sum() == 0:
            raise ValueError("no hay capacidad suficiente para completar la muestra")
        extra = (capacidad / capacidad.sum() * restante).astype(int)
        if extra.sum() == 0:
            # el redondeo no asigno nada: forzar 1 unidad al estrato con mayor capacidad
            extra = extra * 0
            extra.loc[capacidad.idxmax()] = 1
        extra = extra.clip(upper=capacidad)
        cupos = cupos + extra
        restante = n_total - cupos.sum()
    return cupos


def main() -> None:
    RUTA_MUESTRAS.mkdir(parents=True, exist_ok=True)

    # ---- 1. Carga L0 y asignacion de grupo de actor ----
    df = pd.read_csv(RUTA_L0 / "corpus.csv", parse_dates=["fecha"])
    df["grupo_actor"] = df["cargo"].map(grupo_de_actor)

    # ---- 2. Universo del piloto: se excluye texto dañado (codebook v2, R8) ----
    pool = df[~df["flag_texto_danado"]].copy()
    print(f"universo piloto: {len(pool)} (excluidos {len(df) - len(pool)} con texto dañado)")

    # ---- 3. Estratos año x grupo y cupos exactos que suman N_PILOTO ----
    conteos = pool.groupby(["anio", "grupo_actor"]).size()
    cupos = asignar_cupos(conteos, N_PILOTO, MIN_POR_ESTRATO)
    assert int(cupos.sum()) == N_PILOTO

    # ---- 4. Muestreo estratificado con semilla determinista por estrato ----
    fragmentos = []
    for i, ((anio, grupo), n) in enumerate(sorted(cupos.items())):
        estrato = pool[(pool["anio"] == anio) & (pool["grupo_actor"] == grupo)]
        fragmentos.append(estrato.sample(n=int(n), random_state=SEED_MAESTRA + i))
    piloto = pd.concat(fragmentos).sort_values(["anio", "meeting_id", "orden_habla"])

    # ---- 5. Submuestra test-retest (fija, dentro del piloto) ----
    test_retest = piloto.sample(n=N_TEST_RETEST, random_state=SEED_MAESTRA + 1)

    # ---- 6. Validaciones (fail-fast, REGLAS seccion 4) ----
    assert len(piloto) == N_PILOTO
    assert piloto["intervencion_id"].is_unique
    assert piloto["anio"].nunique() == 11, "debe cubrir los 11 años"
    assert not piloto["flag_texto_danado"].any()
    assert set(test_retest["intervencion_id"]) <= set(piloto["intervencion_id"])

    # ---- 7. Escritura ----
    piloto[COLUMNAS_SALIDA].to_csv(
        RUTA_MUESTRAS / "piloto_300.csv", index=False, encoding="utf-8"
    )
    test_retest[["intervencion_id"]].to_csv(
        RUTA_MUESTRAS / "test_retest_30.csv", index=False, encoding="utf-8"
    )
    resumen = cupos.rename("n_muestra").reset_index()
    resumen.to_csv(RUTA_MUESTRAS / "piloto_300_estratos.csv", index=False, encoding="utf-8")

    # ---- 8. Resumen en consola ----
    print(f"piloto_300.csv: {len(piloto)} filas | años {piloto['anio'].min()}-{piloto['anio'].max()}")
    print(piloto.groupby("grupo_actor")["intervencion_id"].count().to_string())
    print(f"test_retest_30.csv: {len(test_retest)} ids")


if __name__ == "__main__":
    main()
