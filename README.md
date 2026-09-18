# Clasificación de postura monetaria del Banco Central de Chile

Proyecto final y condensado para clasificar intervenciones de actas BCCh de **2005–2015** como `hawkish`, `dovish` o `neutral`.

## Resultado final

El modelo formal es **W+C+600**: TF-IDF de palabras y caracteres, regresión logística en dos etapas y voto de cinco miembros agrupados. En la evaluación ciega agrupada obtuvo:

| Accuracy | Macro-F1 | F1-HD | F1 H | F1 D | Recall D | Errores |
|---:|---:|---:|---:|---:|---:|---:|
| 0,8562 | 0,7463 | 0,6632 | 0,7111 | 0,6154 | 0,7619 | 43/299 |

Superó de forma robusta al modelo anterior C+89. El análisis factorial mostró que la mayor parte de la mejora proviene de las 600 anotaciones adicionales; el aporte incremental de caracteres frente a C+600 es pequeño e incierto. Esta distinción está preservada en la documentación.

## Estructura

```text
├── README.md
├── requirements.txt
├── data/
│   ├── corpus_bcch_2005_2015.csv       Corpus que se quiere clasificar
│   ├── entrenamiento_wc600.csv         Entrenamiento final, ya purgado
│   ├── evaluacion_ciega_gold.csv       Referencia humana final
│   ├── predicciones_evaluacion_ciega.csv
│   ├── resultados_evaluacion_ciega.json
│   ├── analisis_factorial.json
│   └── benchmark_modelos.{csv,json}
├── docs/
│   ├── CODEBOOK_ETIQUETADO.md
│   ├── METODOLOGIA_MODELO.md
│   ├── RESULTADOS_Y_ROBUSTEZ.md
│   ├── BENCHMARK_MODELOS.md
│   └── PROTOCOLO_*.md
├── scripts/modelo_final.py
└── tests/test_proyecto_esencial.py
```

## Uso

Python 3.11 recomendado:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/modelo_final.py verificar
.venv/bin/python scripts/modelo_final.py predecir data/corpus_bcch_2005_2015.csv predicciones_corpus.csv
```

En Windows, usar `.venv\Scripts\python.exe`. El comando de predicción entrena los cinco miembros con parámetros congelados y crea un CSV nuevo; nunca sobrescribe una salida existente.

## Clasificación completa disponible

El modelo ya fue ejecutado sobre las 9.725 intervenciones. El resultado está en `resultados/clasificacion_wc600_9725.csv`, con las cinco predicciones individuales, el voto final, el rol de cada fila y una señal de acuerdo entre miembros. `resultados/resumen_clasificacion.json` contiene distribuciones y conteos por año.

## Lectura recomendada

1. [`docs/METODOLOGIA_MODELO.md`](docs/METODOLOGIA_MODELO.md)
2. [`docs/RESULTADOS_Y_ROBUSTEZ.md`](docs/RESULTADOS_Y_ROBUSTEZ.md)
3. [`docs/BENCHMARK_MODELOS.md`](docs/BENCHMARK_MODELOS.md)
4. [`docs/CODEBOOK_ETIQUETADO.md`](docs/CODEBOOK_ETIQUETADO.md)

## Límites

La evaluación ciega es una muestra enriquecida como desafío y no estima prevalencia natural. Sus reuniones fueron excluidas del ajuste prospectivo, pero habían aparecido durante el desarrollo histórico. Una anotación no decidible fue excluida, dejando 299 casos evaluables. No se debe reutilizar este conjunto para seleccionar nuevas variantes.

El historial Git conserva todas las auditorías, experimentos y scripts eliminados durante la condensación. El último estado previo a ella es el commit `7aa63cc`.
