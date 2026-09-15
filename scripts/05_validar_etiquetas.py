"""
05_validar_etiquetas.py — Valida un archivo de etiquetas del proyecto D&H.

Que hace:
    1. Verifica la estructura: columnas exactas del formato largo (PLAN.md §4.2).
    2. Verifica dominios: etiqueta en {hawkish, dovish, neutral}; confianza en
       {alta, media, baja}; es_relevante en {0, 1}; metodo en el set conocido.
    3. Verifica coherencia estadistica: probabilidades en [0,1], suma ~= 1, y
       score == prob_hawkish - prob_dovish.
    4. Verifica reglas del codebook: la etiqueta debe ser el argmax de las
       probabilidades; si es_relevante=0 la nota es obligatoria (codebook §2.4);
       si es_relevante=1 la frase_justificante es obligatoria (R10).
    5. Verifica cobertura: los IDs existen en la capa L0 y no hay duplicados.

Por que asi: toda corrida de etiquetado debe pasar este control antes de ser
usable (REGLAS.md seccion 4: un fallo detiene la pipeline, no pasa en silencio).
Es parametrico, sirve para todas las rondas y metodos.

Ejecucion:  python scripts/05_validar_etiquetas.py data/etiquetas/etiquetas_piloto_r1.csv
"""

import sys

import pandas as pd

from config import RUTA_L0

COLUMNAS = [
    "intervencion_id", "metodo", "etiqueta",
    "prob_hawkish", "prob_dovish", "prob_neutral", "score",
    "frase_justificante", "confianza", "es_relevante", "nota",
    "ronda", "version_codebook", "fecha", "etiquetador",
]
ETIQUETAS = {"hawkish", "dovish", "neutral"}
CONFIANZAS = {"alta", "media", "baja"}
METODOS = {"ia_ronda", "humano_gold", "tfidf", "embeddings", "beto_ft", "llm_zeroshot"}
TOLERANCIA_SUMA_PROB = 1e-6


def validar(df: pd.DataFrame) -> dict:
    """Bateria de controles; levanta AssertionError con detalle al primer fallo."""
    assert list(df.columns) == COLUMNAS, f"columnas distintas del formato: {list(df.columns)}"
    assert df["intervencion_id"].is_unique, "intervencion_id duplicado en la corrida"

    # Columnas estructurales no nulas (detecta filas mal formadas con menos
    # campos de los esperados, que pandas rellena silenciosamente con NaN).
    for col in ["intervencion_id", "metodo", "ronda", "version_codebook", "fecha", "etiquetador", "confianza", "es_relevante"]:
        assert df[col].notna().all(), f"nulos en columna estructural: {col}"

    # Dominios de valores controlados
    assert set(df["etiqueta"]) <= ETIQUETAS, f"etiquetas fuera de dominio: {set(df['etiqueta']) - ETIQUETAS}"
    assert set(df["confianza"]) <= CONFIANZAS, "confianza fuera de dominio"
    assert set(df["es_relevante"]) <= {0, 1}, "es_relevante debe ser 0 o 1"
    assert set(df["metodo"]) <= METODOS, "metodo fuera de dominio"

    # Coherencia de probabilidades y score
    probs = df[["prob_hawkish", "prob_dovish", "prob_neutral"]]
    assert ((probs >= 0) & (probs <= 1)).all().all(), "probabilidad fuera de [0,1]"
    assert (probs.sum(axis=1) - 1).abs().max() < TOLERANCIA_SUMA_PROB, "probabilidades no suman 1"
    assert (df["score"] - (df["prob_hawkish"] - df["prob_dovish"])).abs().max() < 1e-6, (
        "score != prob_hawkish - prob_dovish"
    )
    argmax = probs.idxmax(axis=1).str.replace("prob_", "", regex=False)
    assert (argmax == df["etiqueta"]).all(), (
        f"etiqueta != argmax de probabilidades en: {df.loc[argmax != df['etiqueta'], 'intervencion_id'].tolist()}"
    )

    # Reglas del codebook v2
    sin_nota = (df["es_relevante"] == 0) & df["nota"].isna()
    assert not sin_nota.any(), "nota obligatoria cuando es_relevante=0 (codebook §2.4)"
    sin_frase = (df["es_relevante"] == 1) & df["frase_justificante"].isna()
    assert not sin_frase.any(), "frase_justificante obligatoria cuando es_relevante=1 (R10)"

    # Cobertura contra L0
    corpus = pd.read_csv(RUTA_L0 / "corpus.csv", usecols=["intervencion_id"])
    faltantes = set(df["intervencion_id"]) - set(corpus["intervencion_id"])
    assert not faltantes, f"IDs no presentes en L0: {list(faltantes)[:5]}"

    return {
        "filas": len(df),
        "distribucion": df["etiqueta"].value_counts().to_dict(),
        "irrelevantes": int((df["es_relevante"] == 0).sum()),
        "confianza": df["confianza"].value_counts().to_dict(),
    }


def main() -> None:
    assert len(sys.argv) == 2, "uso: python 05_validar_etiquetas.py <archivo_csv>"
    df = pd.read_csv(sys.argv[1])
    resumen = validar(df)
    print(f"VALIDACION OK: {sys.argv[1]}")
    print(resumen)


if __name__ == "__main__":
    main()
