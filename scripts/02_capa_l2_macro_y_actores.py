"""
02_capa_l2_macro_y_actores.py — Construye la capa L2: macro por reunion + metadata de actores.

Que hace:
    1. Descarga series macro desde mindicador.cl (TPM, IPC, IMACEC, tasa_desempleo)
       ano a ano y guarda los JSON crudos en data/L2/raw/ (fuente auditable).
    2. Procesa la TPM diaria disponible y la cruza con las 132 reuniones del corpus,
       derivando TPM del dia, TPM post-reunion, dTPM y policy_decision.
    3. Genera la metadata de actores: derivada del corpus + datos curados y
       verificados con fuente publica (nunca se inventan datos; los huecos quedan
       registrados).
    4. Escribe un manifiesto de pendientes (series o campos no obtenidos y por que).

Por que asi:
    - Descarga tolerante a fallos: en el entorno sandbox sin salida TLS el script
      no se cae; registra el pendiente y sigue. En una maquina con internet normal
      descarga todo sin intervencion. Tambien se pueden depositar manualmente los
      JSON en data/L2/raw/ con el mismo nombre de archivo y el script los procesa.
    - Regla TPM->decision documentada en la seccion correspondiente.

Ejecucion:  python scripts/02_capa_l2_macro_y_actores.py   (despues del script 01)
Entrada:    data/L0/corpus.csv + internet (o JSON crudos en data/L2/raw/)
Salida:     data/L2/tpm_diaria.csv (si hay raw TPM), data/L2/macro_por_reunion.csv,
            data/L2/actores_metadata.csv, data/L2/pendientes_manifest.csv
"""

import json
import time
import urllib.error
import urllib.request

import pandas as pd

from config import (
    ANIO_MAX,
    ANIO_MIN,
    INDICADORES_DESCARGA,
    RUTA_L0,
    RUTA_L2,
    RUTA_L2_RAW,
    TIMEOUT_HTTP_SEG,
    URL_MINDICADOR,
    USER_AGENT_HTTP,
)

# Series que el proyecto necesita pero que no estan en mindicador o requieren
# registro: quedan en el manifiesto con su fuente sugerida.
SERIES_PENDIENTES = [
    {
        "serie": "eee_inflacion_1a",
        "por_que": "Expectativas de inflacion a 1 ano (Encuesta de Expectativas Economicas)",
        "fuente_sugerida": "API BDE del BCCh (requiere registro gratuito): si3.bcentral.cl",
    },
    {
        "serie": "ipec",
        "por_que": "Indice de Percepcion de la Economia (confianza del consumidor, Adimark)",
        "fuente_sugerida": "Adimark / prensa economica (historico parcial, posible scraping)",
    },
    {
        "serie": "sit_pais_1a",
        "por_que": "Expectativa sobre la situacion del pais a 1 ano (componente de encuestas)",
        "fuente_sugerida": "Adimark / CEP segun definicion final de la variable",
    },
]

# Datos curados y verificados con fuentes publicas durante la sesion 3.
# Regla: solo se registra lo que tiene fuente; el resto queda vacio y
# verificado=False para completar en fases posteriores.
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


def descargar_series() -> list[dict]:
    """Descarga cada indicador por año; tolerante a fallos de red.

    Devuelve la lista de intentos fallidos para el manifiesto. Los JSON crudos
    se guardan con nombre estable {indicador}_{anio}.json para auditoria y
    reprocesamiento sin re-descarga.
    """
    fallos = []
    RUTA_L2_RAW.mkdir(parents=True, exist_ok=True)
    for indicador in INDICADORES_DESCARGA:
        for anio in range(ANIO_MIN, ANIO_MAX + 1):
            url = f"{URL_MINDICADOR}/{indicador}/{anio}"
            destino = RUTA_L2_RAW / f"{indicador}_{anio}.json"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT_HTTP})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT_HTTP_SEG) as resp:
                    destino.write_bytes(resp.read())
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                fallos.append({"descarga": url, "motivo": f"{type(exc).__name__}"})
            time.sleep(0.2)  # cortesia con la API publica
    return fallos


def cargar_serie_diaria(indicador: str) -> pd.DataFrame:
    """Lee todos los JSON crudos disponibles de un indicador y los aplana."""
    registros = []
    for ruta in sorted(RUTA_L2_RAW.glob(f"{indicador}_*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        registros.extend(datos.get("serie", []))
    df = pd.DataFrame(registros)
    if df.empty:
        return df
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.tz_localize(None)
    df = df[["fecha", "valor"]].drop_duplicates("fecha").sort_values("fecha")
    return df.reset_index(drop=True)


def construir_macro_por_reunion(tpm: pd.DataFrame) -> pd.DataFrame:
    """Cruza la TPM diaria con las fechas de reunion del corpus.

    Regla de decision (documentada y verificada con el caso 2015-12-17):
    la TPM publicada el DIA de la reunion es la vigente ANTES de la decision;
    la nueva TPM rige desde el dia habil siguiente. Por tanto:
        dTPM = TPM(primer dia posterior) - TPM(dia de la reunion)
        policy_decision = sube / baja / mantiene segun el signo de dTPM
    tpm_dia usa el ultimo valor disponible <= fecha de reunion (cubre feriados).
    """
    reuniones = (
        pd.read_csv(RUTA_L0 / "corpus.csv", parse_dates=["fecha"])["fecha"]
        .drop_duplicates().sort_values().reset_index(drop=True)
    )
    fe = tpm.set_index("fecha")["valor"]
    filas = []
    for fecha in reuniones:
        tpm_dia = fe.loc[:fecha].iloc[-1] if (fe.index <= fecha).any() else None
        posteriores = fe.loc[fe.index > fecha]
        tpm_post = posteriores.iloc[0] if len(posteriores) else None
        dtpm = None if (tpm_dia is None or tpm_post is None) else round(tpm_post - tpm_dia, 2)
        decision = (
            "sin_dato" if dtpm is None
            else "sube" if dtpm > 0
            else "baja" if dtpm < 0
            else "mantiene"
        )
        filas.append({
            "fecha": fecha,
            "meeting_id": f"RPM-{fecha:%Y-%m-%d}",
            "TPM": tpm_dia,
            "TPM_post": tpm_post,
            "dTPM": dtpm,
            "policy_decision": decision,
        })
    return pd.DataFrame(filas)


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


def main() -> None:
    # ---- 1. Descarga de series macro (tolerante a fallos de red) ----
    fallos = descargar_series()
    print(f"intentos de descarga fallidos: {len(fallos)}")

    # ---- 2. Procesamiento TPM: solo si hay JSON crudos presentes ----
    tpm = cargar_serie_diaria("tpm")
    if tpm.empty:
        print("sin datos TPM crudos en data/L2/raw/: se omite macro_por_reunion")
    else:
        tpm.to_csv(RUTA_L2 / "tpm_diaria.csv", index=False, encoding="utf-8")
        macro = construir_macro_por_reunion(tpm)
        macro.to_csv(RUTA_L2 / "macro_por_reunion.csv", index=False, encoding="utf-8")
        n_ok = int((macro["policy_decision"] != "sin_dato").sum())
        print(f"macro_por_reunion: {n_ok}/132 reuniones con decision derivada")

    # ---- 3. Metadata de actores (corpus + curada verificada) ----
    actores = construir_metadata_actores()
    actores.to_csv(RUTA_L2 / "actores_metadata.csv", index=False, encoding="utf-8")
    assert len(actores) == 55, f"actores={len(actores)}, esperados=55"
    print(f"actores_metadata: {len(actores)} actores | verificados curados: {int(actores['verificado'].sum())}")

    # ---- 4. Manifiesto de pendientes (ningun hueco queda invisible) ----
    pendientes = SERIES_PENDIENTES + [
        {"serie": f["descarga"], "por_que": "descarga fallida (sin salida TLS en sandbox)",
         "fuente_sugerida": "re-ejecutar este script con internet normal, o depositar el JSON en data/L2/raw/"}
        for f in fallos
    ]
    pendientes.append({
        "serie": "actores_metadata (campos curados restantes)",
        "por_que": "mandatos y background de actores no verificados aun (Vergara, Claro, Marshall, Vial, Naudon, Corbo parcial, ministros y staff)",
        "fuente_sugerida": "Memoria Anual y Boletin Mensual BCCh, Wikipedia, prensa; completar curado en METADATA_CURADA",
    })
    pd.DataFrame(pendientes).to_csv(
        RUTA_L2 / "pendientes_manifest.csv", index=False, encoding="utf-8"
    )
    print("pendientes_manifest actualizado")


if __name__ == "__main__":
    main()
