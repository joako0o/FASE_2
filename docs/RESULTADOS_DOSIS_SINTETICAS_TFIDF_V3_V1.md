# Resultados de la curva de dosis sintética TF-IDF v3

## Diseño fijado antes de ejecutar

Se conservaron 801 textos normalizados únicos de las 1.018 filas. Las dosis anidadas se fijaron en 250, 500, 750 y 801, con balance aproximado H/D/N, alternancia de los dos lotes y cobertura progresiva de familias provisionales `lote + tema`.

Los sintéticos se incorporaron **solo al clasificador H/D/N (etapa B)**. No se usaron para la puerta de relevancia porque todos tienen relevancia positiva y el diagnóstico previo mostró que ninguno de los 57 errores del control provenía de esa puerta. La única variable predictora sintética fue `texto`; tema, cita y justificación quedaron fuera.

Se evaluaron por separado:

- base B + cada dosis;
- base C (+89 IA reales) + cada dosis.

La validación permaneció formada exclusivamente por los mismos 793 textos reales. No se incorporó pre-2000, no hubo búsqueda de hiperparámetros y no se guardó un modelo global.

## Preparación de dosis

| Dosis | H | D | N | Lote 1–517 | Lote 518–1.018 | Familias cubiertas |
|---:|---:|---:|---:|---:|---:|---:|
| 250 | 83 | 84 | 83 | 126 | 124 | 211 |
| 500 | 167 | 167 | 166 | 251 | 249 | 336 |
| 750 | 254 | 254 | 242 | 393 | 357 | 465 |
| 801 | 274 | 285 | 242 | 444 | 357 | 501 |

## Resultados

| Base | Dosis | Accuracy | F1-HD | Media folds F1-HD | Precisión D | Recall D | Errores | H↔D | N→H/D | H/D→N |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B | 0 | 0,928121 | 0,668367 | 0,661574 | 0,6667 | 0,5000 | 57 | 13 | 28 | 16 |
| B | 250 | 0,930643 | 0,647113 | 0,632444 | 0,8571 | 0,3750 | 55 | 10 | 20 | 25 |
| B | 500 | 0,929382 | 0,613142 | 0,591047 | 0,8333 | 0,3125 | 56 | 10 | 17 | 29 |
| B | 750 | 0,930643 | 0,600649 | 0,585835 | 0,9000 | 0,2813 | 55 | 9 | 12 | 34 |
| B | 801 | 0,930643 | 0,600649 | 0,585835 | 0,9000 | 0,2813 | 55 | 9 | 12 | 34 |
| C | 0 | 0,928121 | 0,676339 | 0,661682 | 0,5806 | 0,5625 | 57 | 12 | 30 | 15 |
| C | 250 | 0,925599 | 0,640980 | 0,626167 | 0,6364 | 0,4375 | 59 | 11 | 24 | 24 |
| C | 500 | 0,931904 | 0,662465 | 0,653831 | 0,8667 | 0,4063 | 54 | 9 | 18 | 27 |
| C | 750 | 0,934426 | 0,670249 | 0,660242 | 0,9286 | 0,4063 | 52 | 8 | 14 | 30 |
| C | 801 | 0,934426 | 0,670249 | 0,660242 | 0,9286 | 0,4063 | 52 | 8 | 14 | 30 |

## Interpretación

Los sintéticos reducen falsas señales direccionales e inversiones H/D, y elevan marcadamente la precisión D. Sin embargo, lo logran haciendo al clasificador mucho más conservador:

- con B+801, el recall D cae de 50,00% a 28,13%;
- con C+750/801, cae de 56,25% a 40,63%;
- las omisiones H/D→N aumentan de 16 a 34 sobre B y de 15 a 30 sobre C;
- todas las dosis reducen la media de F1-HD frente a su control;
- ninguna dosis satisface los criterios fijados antes del ensayo.

C+750/801 reduce los errores totales de 57 a 52 y las inversiones de 12 a 8, pero no constituye una mejora direccional equilibrada: pierde señales H/D reales y su media de F1-HD queda ligeramente bajo C. Elegirla por accuracy favorecería indebidamente la clase neutral.

Los resultados idénticos entre 750 y 801 indican que las últimas 51 filas no alteran ninguna predicción real, no que aporten evidencia adicional de generalización.

## Decisión

**No adoptar ninguna dosis sintética en su forma actual.** Se conservan los resultados completos, pero `modelo_adoptado=false`.

El experimento sí es informativo: demuestra una brecha de estilo entre las señales explícitas del sintético y las formulaciones reales. Para una nueva versión sintética conviene priorizar:

1. D reales difíciles expresados de manera indirecta, no solo “acordó reducir/recortar”;
2. H/D que usan normalización, trayectoria, oposición a alternativas y comparaciones relativas;
3. neutrales relevantes que mencionan alzas o bajas ajenas sin respaldarlas;
4. menor repetición de cláusulas resolutivas y mayor variación ortográfica realista;
5. metadatos de plantilla, prompt, generador y semilla;
6. eventual peso sintético menor, pero solo en un protocolo nuevo fijado antes de observar sus resultados.

No corresponde probar pesos o nuevas dosis de manera oportunista sobre los mismos 793 casos. Primero debe corregirse el diseño de generación y fijarse un segundo protocolo.

## Artefactos

- Preparación: `data/preparacion/dosis_sinteticas_post2020_v1/`.
- Evaluación: `data/evaluacion/dosis_sinteticas_tfidf_v3_v1/`.
- Predicciones de las diez condiciones, métricas globales/por clase/por fold, criterios, ejecuciones, protocolos, verificaciones y manifiestos quedan versionados.
