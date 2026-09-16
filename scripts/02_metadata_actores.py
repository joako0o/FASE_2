"""Metadata de actores: derivación L0 y curado histórico con fuentes.

La macro se importa exclusivamente con script 07. Este script no descarga
APIs ni reescribe el manifiesto macro. No sobreescribe metadata existente.
"""

# ---- 1. Fuentes y curado existente (sin cambios sustantivos) ----
import pandas as pd
from config import RUTA_L0, RUTA_L2
from utilidades import exigir_salidas_nuevas

METADATA_CURADA = {
    "José De Gregorio Rebeco": {
        "mandato_inicio": "2001-06-21",
        "mandato_fin": "2011-12-07",
        "presidente_inicio": "2007-12-07",
        "presidente_fin": "2011-12-07",
        "vicepresidente_inicio": "2003-12-18",
        "vicepresidente_fin": "2007-12-13",
        "fuente": "es.wikipedia.org/wiki/José_De_Gregorio",
        "verificado": True,
    },
    "Manuel Marfán Lewis": {
        "mandato_inicio": "2003-12-18",
        "mandato_fin": "2013-12-17",
        "presidente_inicio": "",
        "presidente_fin": "",
        "vicepresidente_inicio": "2010-01-07",
        "vicepresidente_fin": "2013-12-17",
        "fuente": "en.wikipedia.org/wiki/Manuel_Marfán",
        "verificado": True,
    },
    "Jorge Desormeaux Jiménez": {
        "mandato_inicio": "1999-12-07",
        "mandato_fin": "2009-12-04",
        "presidente_inicio": "",
        "presidente_fin": "",
        "vicepresidente_inicio": "2007-12-13",
        "vicepresidente_fin": "2009-12-04",
        "fuente": "en.wikipedia.org/wiki/Jorge_Desormeaux",
        "verificado": True,
    },
    "Vittorio Corbo Lioi": {
        "mandato_inicio": "",
        "mandato_fin": "",
        "presidente_inicio": "2003-01-01",
        "presidente_fin": "2007-12-07",
        "vicepresidente_inicio": "",
        "vicepresidente_fin": "",
        "fuente": "es.wikipedia.org/wiki/José_De_Gregorio (sucesion); Boletin Mensual BCCh sept-2007",
        "verificado": False,
    },
}


# ---- 2. Derivación desde el corpus ----
def construir_metadata_actores() -> pd.DataFrame:
    """Metadata por actor: derivada del corpus + capa curada y verificada.

    Los campos derivados (primera/ultima sesion observada, cargos, volumen)
    son cota temporal objetiva; la capa curada solo incluye datos con fuente.
    """
    corpus = pd.read_csv(RUTA_L0 / "corpus.csv", parse_dates=["fecha"])
    base = (
        corpus.groupby("actor")
        .agg(
            n_intervenciones=("intervencion_id", "count"),
            primera_sesion=("fecha", "min"),
            ultima_sesion=("fecha", "max"),
            cargos_observados=("cargo", lambda s: "; ".join(sorted(s.unique()))),
        )
        .reset_index()
    )
    columnas_curadas = [
        "mandato_inicio", "mandato_fin",
        "presidente_inicio", "presidente_fin",
        "vicepresidente_inicio", "vicepresidente_fin",
        "fuente", "verificado",
    ]
    for col in columnas_curadas:
        base[col] = base["actor"].map(
            lambda a, c=col: METADATA_CURADA.get(a, {}).get(c, False if c == "verificado" else "")
        )
    base["nominado_por"] = ""       # pendiente: fase posterior con fuente oficial
    base["background"] = ""         # pendiente: academia / publico / privado
    base["educacion"] = ""          # pendiente
    return base.sort_values("n_intervenciones", ascending=False).reset_index(drop=True)

# ---- 3. Materialización protegida ----
def main():
    ruta = RUTA_L2 / "actores_metadata.csv"
    exigir_salidas_nuevas(ruta)
    actores = construir_metadata_actores()
    assert actores.actor.is_unique and len(actores) == 55
    RUTA_L2.mkdir(parents=True, exist_ok=True)
    actores.to_csv(ruta, index=False)
    print(f"Metadata: {len(actores)} actores; {int(actores.verificado.sum())} con curado histórico.")


if __name__ == "__main__":
    main()
