# Búsqueda del límite de n-gramas: 1–6

**Mejor límite observado: (1,4)**, con macro-F1 medio **0.7803**. Es el mejor entre seis límites con esta configuración, no un óptimo universal.

## Diseño

- Misma reserva IA de 793 intervenciones / 80 reuniones. Cinco folds: 1.193–1.194 para train y 158–159 para validación. Las 559 intervenciones del grupo de descubrimiento anterior siempre entran solo en train.
- A (relevancia) fija en unigramas; solo cambia B (postura): (1,1), (1,2), (1,3), (1,4), (1,5), (1,6). Sin diccionario.
- min_df=3, max_df=0,9, C=2, balanced, sublinear_tf y normalización/tokenizador estándar del baseline. No se cambian otros parámetros ni se amplía la búsqueda tras ver resultados.
- Vocabularios, IDF y clasificadores se ajustan exclusivamente dentro del train de cada fold. A se comparte entre las seis variantes.
- Selección por mayor macro-F1 medio sin redondear; empate exacto: menor longitud. El OOF conjunto no decide el ganador.

## Resultados

DE es desviación estándar muestral entre los cinco folds; no es un intervalo de confianza. F1 H/D y recall corresponden al OOF conjunto.

| Límite | Macro-F1 medio | DE folds | Macro-F1 conjunto | F1 H | F1 D | Vocabulario B medio |
|---|---:|---:|---:|---:|---:|---:|
| (1,1) | 0.7500 | 0.0897 | 0.7497 | 0.6974 | 0.5872 | 4,297 |
| (1,2) | 0.7617 | 0.0531 | 0.7624 | 0.7162 | 0.6071 | 17,284 |
| (1,3) | 0.7673 | 0.0646 | 0.7678 | 0.7200 | 0.6182 | 29,488 |
| (1,4) | 0.7803 | 0.0640 | 0.7810 | 0.7397 | 0.6372 | 36,702 |
| (1,5) | 0.7730 | 0.0491 | 0.7769 | 0.7347 | 0.6306 | 40,608 |
| (1,6) | 0.7753 | 0.0467 | 0.7791 | 0.7347 | 0.6364 | 42,846 |

| Límite | Precisión H | Recall H | Precisión D | Recall D |
|---|---:|---:|---:|---:|
| (1,1) | 0.6386 | 0.7681 | 0.5333 | 0.6531 |
| (1,2) | 0.6709 | 0.7681 | 0.5397 | 0.6939 |
| (1,3) | 0.6667 | 0.7826 | 0.5574 | 0.6939 |
| (1,4) | 0.7013 | 0.7826 | 0.5625 | 0.7347 |
| (1,5) | 0.6923 | 0.7826 | 0.5645 | 0.7143 |
| (1,6) | 0.6923 | 0.7826 | 0.5738 | 0.7143 |

## Estabilidad y lectura del resultado

- Ganador frente a (1,1): diferencia media +0.0303; mejora en 4/5 folds y empeora en 1/5.
- Ganador frente a (1,4): diferencia media +0.0000; mejora en 0/5 folds y empeora en 0/5.
- Diferencia con el segundo, (1,6): +0.0050. No demuestra superioridad estadística con cinco folds.
- Más n-gramas no garantizan mejor resultado: aumentan el vocabulario y cambian los pesos TF-IDF. El tamaño mostrado es el del train relevante de B, no un vocabulario aprendido de validación.

## Límites y qué queda decidido

- Referencia IA: 69 hawkish / 49 dovish / 675 neutral. La accuracy y F1 neutral también quedan en el CSV, junto a todos los soportes.
- 34/793 textos de validación son idénticos a alguno de su train tras normalizar espacios, aun con reuniones disjuntas. No se modifica la partición después de evaluar.
- La reserva y los resultados de longitudes 1 y 4 ya eran conocidos; también se había seleccionado el baseline sobre las 1.352 IA. Esta búsqueda es desarrollo/selección interna adaptativa, no un test independiente. La puntuación máxima puede ser optimista.
- No se abrieron ni predijeron las 306 respuestas humanas. Tampoco se usó el catálogo descriptivo completo ni el diccionario para construir características.
- Se deja (1,4) como candidato seleccionado de esta búsqueda. No se reajustó un modelo con las 1.352, no se puntuó el corpus y no se reemplazó TF-IDF v1. La confirmación independiente requiere otra evaluación y control de textos repetidos.

## Artefactos y reproducción

En `data/evaluacion/longitud_ngramas_v1/`: protocolo guardado antes de entrenar, asignación de folds, predicciones IA, resultados por fold, comparación, selección y manifiesto de hashes. Los límites 1 y 4 reproducen las predicciones del experimento anterior.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/22_seleccionar_longitud_ngramas.py \
  --salida /ruta/nueva/evaluacion --informe /ruta/nueva/informe.md
```

Las rutas deben ser nuevas; no se sobrescriben resultados. La selección se limita a seis alternativas incluso si gana el extremo (1,6).
