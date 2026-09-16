# FASE_2

Proyecto D&H: score **hawkish/dovish por intervención** en las Actas de las Reuniones de Política Monetaria del Banco Central de Chile (2005–2015).

- Datos: `consolidado_D&H.xlsx` — 9.725 intervenciones, 132 reuniones, 55 actores
- Plan metodológico + roadmap + cómo retomar: [`PLAN.md`](PLAN.md) (sección 9.1 handoff)
- Reglas de trabajo: [`docs/REGLAS.md`](docs/REGLAS.md)
- Estado y continuidad entre sesiones: [`docs/AVANCE.md`](docs/AVANCE.md)
- Codebook de etiquetado vigente (v2, congelado): [`docs/codebook_v2.md`](docs/codebook_v2.md)

## Estado (2026-09-15)

- **Training set IA cerrado**: 1.352 etiquetas en `data/etiquetas/` (validadas por `scripts/05`).
- **Baseline TF-IDF** dos etapas corrido (macroF1 0,35): `scripts/15_baseline_tfidf.py`.
- **Validación agregada**: serie stance por reunión vs ΔTPM, spearman 0,66: `scripts/16_validacion_serie_stance.py`.
- **Siguiente hito**: gold humano ciego 306 (`data/muestras/gold_ciego_300.csv`) → κ → fine-tune BETO.

## Setup

```bash
python3 -m venv ~/venvs/fase2
~/venvs/fase2/bin/pip install -r requirements.txt
~/venvs/fase2/bin/python scripts/05_validar_etiquetas.py data/etiquetas/etiquetas_escalado_r16.csv  # sanity
```

Flujo de trabajo: rondas con PRs desde `arena/01a0a3a0-fase-2`.
