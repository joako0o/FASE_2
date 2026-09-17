# -*- coding: utf-8 -*-
"""
07_macro_desde_excel.py — Materializa la capa L2 macro desde consolidado_macro.xlsx.

Contexto
--------
El usuario descargo localmente las series macro (mindicador.cl y fuentes BCCh)
y las entrego consolidadas en el libro ``consolidado_macro.xlsx`` (raiz del
repo). Este script es el punto unico de ingreso de ese libro a la capa L2:

- ``data/L2/macro_por_reunion.csv``: una fila por reunion RPM del corpus,
  con TPM, TPM_post, dTPM, policy_decision y ultimos datos macro conocidos
  a la fecha de la reunion. Es el insumo de la validacion del score vs dTPM.
- ``data/L2/macro_mensual.csv``: panel mensual (2000-2025) con promedios y
  cierres de TPM, IPC, IMACEC, desempleo, dolar y cobre.

Salvedades conocidas (documentadas en PEN - pendientes_manifest.csv):
- La serie desempleo de mindicador.cl parte en 2010-03 (limite del API).
- eee_inflacion_1a, ipec, sit_pais_1a, pib, exportaciones e importaciones
  quedan pendientes (fuentes sin descarga automatica: BDE/Adimark/Aduanas).
"""
import pandas as pd
from utilidades import exigir_salidas_nuevas

from config import RUTA_EXCEL_MACRO, RUTA_L0, RUTA_L2

# ---------------------------------------------------------------------------
# Seccion 1 - Parametros del proceso (todo el resto del script es mecanico)
# ---------------------------------------------------------------------------

COLUMNAS_REUNION = [
    "fecha", "meeting_id", "TPM", "TPM_post", "dTPM", "policy_decision",
    "ipc_ultimo", "imacec_ultimo", "desempleo_ultimo",
    "dolar_reunion", "cobre_reunion",
]
COLUMNAS_MENSUAL = [
    "fecha_mes", "tpm_prom", "tpm_cierre", "ipc", "imacec",
    "tasa_desempleo", "dolar_prom", "dolar_cierre",
    "libra_cobre_prom", "libra_cobre_cierre",
]
DECISIONES_VALIDAS = {"sube", "mantiene", "baja"}
MES_MIN_CORPUS = "2005-01-01"
MES_MAX_CORPUS = "2015-12-01"

# ---------------------------------------------------------------------------
# Seccion 2 - Macro_por_Reunion: corte al universo del corpus y validaciones
# ---------------------------------------------------------------------------


def construir_macro_por_reunion(meetings_corpus: set[str]) -> pd.DataFrame:
    """Filtra la hoja Macro_por_Reunion a las reuniones del corpus L0."""
    df = pd.read_excel(RUTA_EXCEL_MACRO, sheet_name="Macro_por_Reunion")
    df = df[df["meeting_id"].isin(meetings_corpus)].copy()
    # Una fila por reunion, sin duplicados y cobertura total del corpus.
    assert not df["meeting_id"].duplicated().any(), "meeting_id duplicado"
    assert set(df["meeting_id"]) == meetings_corpus, "reuniones faltantes"
    # Variables criticas de la validacion del score sin faltantes.
    assert df["TPM"].notna().all(), "TPM faltante"
    assert df["dTPM"].notna().all(), "dTPM faltante"
    assert set(df["policy_decision"].unique()) <= DECISIONES_VALIDAS
    # dTPM coherente con la decision declarada: signo compatible.
    for decision, signo in [("sube", 1), ("mantiene", 0), ("baja", -1)]:
        valores = df.loc[df.policy_decision.eq(decision), "dTPM"]
        assert ((valores > 0) if signo == 1 else (valores < 0) if signo == -1 else (valores == 0)).all()
    assert df.TPM_post.notna().all(), "TPM_post faltante"
    assert (df.TPM_post - df.TPM - df.dTPM).abs().lt(1e-8).all(), "dTPM != TPM_post - TPM"
    fechas = pd.to_datetime(df.fecha).dt.strftime("%Y-%m-%d")
    assert ("RPM-" + fechas).equals(df.meeting_id), "fecha e ID de reunión inconsistentes"
    return df[COLUMNAS_REUNION].sort_values("fecha").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Seccion 3 - Panel mensual: orden, unicidad y cobertura del periodo corpus
# ---------------------------------------------------------------------------


def construir_macro_mensual() -> pd.DataFrame:
    """Lee el panel mensual y verifica cobertura del periodo del corpus."""
    df = pd.read_excel(RUTA_EXCEL_MACRO, sheet_name="Panel_Macro_Mensual")
    df["fecha_mes"] = pd.to_datetime(df["fecha_mes"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values("fecha_mes").reset_index(drop=True)
    assert not df["fecha_mes"].duplicated().any(), "mes duplicado"
    meses = set(df["fecha_mes"])
    esperados = set(pd.date_range(MES_MIN_CORPUS, MES_MAX_CORPUS, freq="MS")
                    .strftime("%Y-%m-%d"))
    assert esperados <= meses, f"meses del corpus sin panel: {esperados - meses}"
    # TPM e IPC deben existir en todo el periodo del corpus.
    tramo = df[df["fecha_mes"].isin(esperados)]
    assert tramo["tpm_prom"].notna().all(), "tpm_prom faltante en corpus"
    assert tramo["ipc"].notna().all(), "ipc faltante en corpus"
    return df[COLUMNAS_MENSUAL]


# ---------------------------------------------------------------------------
# Seccion 4 - Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Fuentes/muestras congeladas: no regenerar sobre selecciones existentes.
    exigir_salidas_nuevas(RUTA_L2 / "macro_por_reunion.csv", RUTA_L2 / "macro_mensual.csv")
    corpus = pd.read_csv(RUTA_L0 / "corpus.csv")
    meetings_corpus = set(corpus["meeting_id"].unique())

    reunion = construir_macro_por_reunion(meetings_corpus)
    mensual = construir_macro_mensual()
    RUTA_L2.mkdir(parents=True, exist_ok=True)
    reunion.to_csv(RUTA_L2 / "macro_por_reunion.csv", index=False)
    decisiones = reunion["policy_decision"].value_counts().to_dict()
    print(f"macro_por_reunion.csv: {len(reunion)} reuniones | {decisiones}")

    mensual.to_csv(RUTA_L2 / "macro_mensual.csv", index=False)
    print(f"macro_mensual.csv: {len(mensual)} meses "
          f"({mensual['fecha_mes'].min()} -> {mensual['fecha_mes'].max()})")


if __name__ == "__main__":
    main()
