"""
01_excel_a_capa_l0.py — Convierte el Excel consolidado en la capa L0 (corpus inmutable).

Que hace:
    1. Lee la hoja de transcripciones del Excel original (fuente unica de verdad).
    2. Construye identificadores: meeting_id (reunion) y orden de habla dentro de ella.
    3. Normaliza nombres de columnas a snake_case y genera variables derivadas.
    4. Produce un EDA reproducible (conteos por año, topico y actor).
    5. Valida el resultado con asserts (forma, unicidad, nulos).
    6. Escribe data/L0/corpus.csv + tablas EDA.

Por que asi: la capa L0 nunca se vuelve a editar (REGLAS.md, seccion 5). Todo lo
demas del proyecto se construye sobre este CSV, no sobre el Excel.

Ejecucion:  python scripts/01_excel_a_capa_l0.py
Entrada:    consolidado_D&H.xlsx (raiz del repo)
Salida:     data/L0/corpus.csv, data/L0/eda_*.csv
"""

import re

import pandas as pd
from utilidades import exigir_salidas_nuevas

from config import (
    HOJA_TRANSCRIPCION,
    N_INTERVENCIONES_ESPERADAS,
    N_REUNIONES_ESPERADAS,
    RUTA_EXCEL,
    RUTA_L0,
)

# Patron del identificador de intervencion: RPM-AAAA-MM-DD:N:M
#   - el prefijo RPM-AAAA-MM-DD identifica la reunion (meeting_id)
#   - N es el orden de habla dentro de la sesion (base de la metrica de convergencia)
#   - M es un subindice de registro
PATRON_ID = re.compile(r"^(RPM-\d{4}-\d{2}-\d{2}):(\d+):(\d+)$")

# Renombre de columnas del Excel a snake_case estable para todo el proyecto.
RENOMBRE_COLUMNAS = {
    "Fecha": "fecha",
    "ID": "id_original",
    "ID_Intervencion": "intervencion_id",
    "Actor": "actor",
    "Cargo": "cargo",
    "Tópico": "topico",
    "Keywords": "keywords",
    "Texto": "texto",
    "Cotejar_PDF": "detalle_cotejo",
}


def construir_identificadores(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae meeting_id, orden de habla y subindice desde intervencion_id.

    Marca regex_ok=False en cualquier fila que no calce el patron, para que
    la validacion la detecte en vez de propagar un NaN silencioso.
    """
    partes = df["intervencion_id"].str.extract(PATRON_ID)
    df = df.copy()
    df["meeting_id"] = partes[0]
    df["orden_habla"] = pd.to_numeric(partes[1], errors="coerce").astype("Int64")
    df["subindice"] = pd.to_numeric(partes[2], errors="coerce").astype("Int64")
    df["regex_ok"] = partes[0].notna() & partes[1].notna()
    return df


def agregar_derivados(df: pd.DataFrame) -> pd.DataFrame:
    """Genera variables derivadas de bajo riesgo (ninguna altera el texto).

    - anio: para estratificacion temporal.
    - largo_palabras / largo_caracteres: para analisis y ponderadores.
    - flag_cotejo: la intervencion tiene alguna marca de calidad registrada.
    - flag_texto_danado: submarca critica; esos registros se excluyen del piloto.
    """
    df = df.copy()
    df["anio"] = df["fecha"].dt.year
    df["largo_caracteres"] = df["texto"].str.len()
    df["largo_palabras"] = df["texto"].str.split().str.len()
    df["flag_cotejo"] = df["detalle_cotejo"].notna()
    df["flag_texto_danado"] = df["detalle_cotejo"].str.contains(
        "TEXTO_DANADO", na=False
    )
    return df


def generar_eda(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Tablas EDA simples y deterministas (mismos datos -> mismas tablas)."""
    return {
        "eda_intervenciones_por_anio": (
            df.groupby("anio").agg(
                intervenciones=("intervencion_id", "count"),
                reuniones=("meeting_id", "nunique"),
            ).reset_index()
        ),
        "eda_intervenciones_por_topico": (
            df["topico"].value_counts().rename_axis("topico")
            .reset_index(name="intervenciones")
        ),
        "eda_top_actores": (
            df["actor"].value_counts().head(15).rename_axis("actor")
            .reset_index(name="intervenciones")
        ),
    }


def validar(df: pd.DataFrame) -> None:
    """Controles minimos de integridad. Un fallo detiene la pipeline (REGLAS 4)."""
    assert len(df) == N_INTERVENCIONES_ESPERADAS, (
        f"filas={len(df)}, esperadas={N_INTERVENCIONES_ESPERADAS}"
    )
    assert df["intervencion_id"].is_unique, "intervencion_id duplicado"
    assert df["regex_ok"].all(), (
        f"IDs fuera de patron: {df.loc[~df['regex_ok'], 'intervencion_id'].head(5).tolist()}"
    )
    assert df["meeting_id"].nunique() == N_REUNIONES_ESPERADAS, (
        f"reuniones={df['meeting_id'].nunique()}, esperadas={N_REUNIONES_ESPERADAS}"
    )
    for col in ["intervencion_id", "fecha", "actor", "cargo", "topico", "texto"]:
        assert df[col].notna().all(), f"nulos en columna clave: {col}"


def main() -> None:
    # Fuentes/muestras congeladas: no regenerar sobre selecciones existentes.
    exigir_salidas_nuevas(RUTA_L0 / "corpus.csv", RUTA_L0 / "eda_intervenciones_por_anio.csv", RUTA_L0 / "eda_intervenciones_por_topico.csv", RUTA_L0 / "eda_top_actores.csv")
    # ---- 1. Carga del consolidado original (solo lectura, nunca se modifica) ----
    RUTA_L0.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(RUTA_EXCEL, sheet_name=HOJA_TRANSCRIPCION)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df = df.rename(columns=RENOMBRE_COLUMNAS)

    # ---- 2. Identificadores y variables derivadas ----
    df = construir_identificadores(df)
    df = agregar_derivados(df)

    # ---- 3. Validacion antes de persistir (fail-fast) ----
    validar(df)

    # ---- 4. Escritura de L0 y EDA (index=False: los IDs ya son la clave) ----
    ruta_corpus = RUTA_L0 / "corpus.csv"
    df.to_csv(ruta_corpus, index=False, encoding="utf-8")
    for nombre, tabla in generar_eda(df).items():
        tabla.to_csv(RUTA_L0 / f"{nombre}.csv", index=False, encoding="utf-8")

    # ---- 5. Resumen en consola (trazabilidad de la corrida) ----
    print(f"L0 escrito en {ruta_corpus}")
    print(f"filas={len(df)} | reuniones={df['meeting_id'].nunique()} | actores={df['actor'].nunique()}")
    print(f"texto danado (excluido del piloto): {int(df['flag_texto_danado'].sum())}")
    print("EDA: eda_intervenciones_por_anio, eda_intervenciones_por_topico, eda_top_actores")


if __name__ == "__main__":
    main()
