# Metodología del modelo final

## Objetivo y unidad

Se clasifica cada intervención de las actas del Banco Central de Chile de 2005–2015 según la dirección monetaria doméstica respaldada: hawkish, dovish o neutral. La definición completa está en `CODEBOOK_ETIQUETADO.md`.

## Arquitectura W+C+600

El sistema usa dos etapas:

1. **A — relevancia:** contenido monetario/contextual evaluable frente a irrelevante;
2. **B — postura:** hawkish, dovish o neutral entre casos relevantes.

Si A predice irrelevante, la salida final es neutral. Cada etapa combina TF-IDF de palabras y caracteres y usa regresión logística.

### Parámetros exactos

| Componente | Parámetros |
|---|---|
| Palabras A | n-gramas 1–1; `min_df=3`; `max_df=0.9`; `sublinear_tf=True`; minúsculas; acentos Unicode |
| Palabras B | n-gramas 1–4; resto igual a A |
| Caracteres | `char_wb`; n-gramas 3–5; `min_df=3`; `max_df=0.98`; `sublinear_tf=True`; `max_features=120000` |
| Regresión logística | `class_weight=balanced`; `C=2.0`; `max_iter=2000`; semilla 20260915 |
| Peso de caracteres | miembros 1–5: `1.0, 0.5, 1.0, 1.0, 1.0` |
| Agregación | voto mayoritario; desempate fijo H, D, N |

## Entrenamiento final

`data/entrenamiento_wc600.csv` contiene 1.596 intervenciones únicas ya excluidas de las 33 reuniones de evaluación y purgadas contra sus textos. La columna `miembros` determina exactamente qué filas recibe cada uno de los cinco modelos:

| Miembro | Filas |
|---:|---:|
| 1 | 1.494 |
| 2 | 1.450 |
| 3 | 1.453 |
| 4 | 1.473 |
| 5 | 1.466 |

Los orígenes únicos disponibles son 1.092 referencias base v3, 67 de la ampliación IA89 y 437 de las dos tandas adicionales tras la cuarentena. Las referencias adicionales fueron asistidas por IA y validadas por personas.

## Prevención de contaminación

- folds agrupados por reunión;
- ninguna reunión ciega entra al entrenamiento final;
- purga de texto normalizado entre entrenamiento y evaluación;
- las citas, fundamentos, confianza, estratos y metadatos de adjudicación no son predictores;
- el test ciego quedó cerrado tras una apertura y no puede usarse para ajustar nuevas variantes.

## Por qué se retuvo TF-IDF

- mejor desempeño controlado que BETO y MrBERT-es en desarrollo;
- mejora confirmada frente a C+89 en evaluación agrupada;
- eficiencia con pocos datos direccionales;
- trazabilidad de vocabulario y coeficientes;
- ejecución reproducible en CPU;
- menor costo y dependencia externa que un encoder remoto.

Esto no demuestra que todos los transformers sean inferiores. El benchmark completo y sus decisiones negativas están en `BENCHMARK_MODELOS.md` y `data/benchmark_modelos.json`.
