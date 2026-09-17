# Benchmark esencial de modelos y defensa de TF-IDF

## Propósito

Este documento forma parte del núcleo que debe conservarse cuando se ordene y reduzca el proyecto. Su finalidad es demostrar que TF-IDF no fue elegido por comodidad: se comparó bajo controles comunes con caracteres, BETO, jerarquías, adaptación de dominio, NB-SVM, datos adicionales y ensambles.

El registro exacto y legible por máquina está en `data/evaluacion/benchmark_esencial_v3_v1/registro.json`; la tabla exportable está en `tabla_modelos.csv`. Cada resultado referencia su artefacto y checksum.

## Protocolo común v3

- 793 casos de desarrollo histórico.
- Cinco outer folds agrupados por `meeting_id`.
- Una reunión nunca aparece simultáneamente en train y validación.
- Purga adicional de textos normalizados duplicados.
- Selección de hiperparámetros, cuando correspondió, mediante `GroupKFold(3)` dentro del outer train.
- Métricas centrales: macro-F1, F1-HD, F1 D, recall D, F1 H, F1 N, inversiones, omisiones y falsas direcciones.
- Los 793 casos son desarrollo abierto y no evaluación final independiente.

## Parámetros TF-IDF congelados

### Arquitectura

Dos etapas:

1. **A, relevancia:** relevante frente a irrelevante;
2. **B, orientación:** H/D/N entre los casos relevantes.

Si A predice irrelevante, la salida final es neutral. Ambas etapas usan regresión logística.

### Regresión logística

| Parámetro | Valor |
|---|---:|
| `class_weight` | `balanced` |
| `C` | 2,0 |
| `max_iter` | 2.000 |
| `random_state` | 20260915 |

### TF-IDF de palabras

| Parámetro | Etapa A | Etapa B |
|---|---:|---:|
| `ngram_range` | (1,1) | (1,4) |
| `min_df` | 3 | 3 |
| `max_df` | 0,9 | 0,9 |
| `sublinear_tf` | sí | sí |
| `strip_accents` | unicode | unicode |
| `lowercase` | sí | sí |

### Componente de caracteres W+C

| Parámetro | Valor |
|---|---:|
| Analizador | `char_wb` |
| `ngram_range` | (3,5) |
| `min_df` | 3 |
| `max_df` | 0,98 |
| `sublinear_tf` | sí |
| `max_features` | 120.000 |
| Pesos por outer fold 1–5 | 1,0; 0,5; 1,0; 1,0; 1,0 |

## Resultados v3 comparables

| Modelo | Macro-F1 | F1-HD | F1 H | F1 D | F1 N | Errores | H↔D | H/D→N | Decisión de su ronda |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| C+89 | 0,772956 | 0,676339 | 0,781250 | 0,571429 | 0,966191 | 57 | 12 | 15 | ancla formal |
| W+C inicial | 0,789804 | 0,701974 | 0,778947 | 0,625000 | 0,965465 | 56 | 10 | 16 | rechazado por multicriterio |
| C + pre-2000 | 0,772918 | 0,677033 | 0,757576 | 0,596491 | 0,964688 | 59 | 12 | 16 | rechazado |
| Jerarquía W+C | 0,763360 | 0,663194 | 0,770833 | 0,555556 | 0,963691 | 62 | 14 | 12 | rechazado |
| TF-IDF adaptado con L0 | 0,780393 | 0,687831 | 0,772487 | 0,603175 | 0,965517 | 57 | 11 | 17 | rechazado |
| NB-SVM | 0,779276 | 0,684492 | 0,780749 | 0,588235 | 0,968843 | 52 | 10 | 22 | rechazado |
| Ensamble calibrado | 0,770451 | 0,674028 | 0,763441 | 0,584615 | 0,963296 | 60 | 11 | 19 | rechazado |
| C+600 | 0,786694 | 0,697513 | 0,782123 | 0,612903 | 0,965056 | 55 | 8 | 23 | no adoptado |
| **W+C+600** | **0,825003** | **0,752701** | **0,784091** | **0,721311** | **0,969607** | **48** | **7** | 22 | mejor numérico/challenger |

## Comparación controlada histórica con BETO

Esta comparación pertenece al benchmark legado v2 y no debe mezclarse numéricamente con la tabla v3, pero sí demuestra una comparación directa bajo el mismo conjunto y folds de esa ronda.

| Modelo | Accuracy | Macro-F1 | F1-HD | F1 D | Errores | H↔D | H/D→N |
|---|---:|---:|---:|---:|---:|---:|---:|
| TF-IDF legado | 0,935687 | 0,819928 | 0,743528 | 0,697248 | 51 | 15 | 12 |
| BETO | 0,916772 | 0,743412 | 0,630660 | 0,509804 | 66 | 25 | 14 |

BETO perdió en macro-F1, F1-HD, F1 D, errores e inversiones. Esto no prueba que todo transformer sea inferior; prueba que **ese BETO, con ese protocolo y esos datos**, no justificó reemplazar TF-IDF.

MrBERT-es queda registrado como experimento pendiente. Su resultado deberá añadirse sin borrar el resultado negativo de BETO ni cambiar retrospectivamente los criterios.

## Por qué se sostiene TF-IDF/W+C

1. **Evidencia empírica:** fue mejor que BETO en la comparación controlada y más estable que las extensiones evaluadas.
2. **Eficiencia de datos:** el corpus etiquetado es pequeño para ajustar encoders sin alta varianza.
3. **Adecuación lingüística:** n-gramas de palabras capturan frases monetarias; caracteres 3–5 absorben flexión, OCR, tildes y variantes ortográficas.
4. **Trazabilidad:** coeficientes, vocabulario y contribuciones pueden auditarse.
5. **Reproducibilidad:** se entrena en CPU con semillas, versiones y hashes, sin depender de pesos remotos cambiantes.
6. **Costo:** permite nested CV agrupada y repetición de controles con recursos modestos.
7. **Desempeño:** W+C+600 alcanza macro-F1 0,825 y F1-HD 0,753 en desarrollo.

## Límites de la defensa

- El mejor resultado v3 aún no es una evaluación ciega final.
- W+C+600 aumentó omisiones frente al ancla formal C+89 y por eso no lo reemplazó bajo la regla congelada.
- La procedencia humana, asistida o automática de cada tanda debe declararse.
- La conclusión final debe incorporar MrBERT-es y las 300 evaluaciones ciegas sin reescribir el historial.

## Elementos que no deben eliminarse al condensar

1. este documento y el registro JSON;
2. codebook v3 y sus reglas de adjudicación;
3. asignación de folds y protocolo de purga;
4. parámetros exactos de C y W+C;
5. predicciones OOF del ancla, BETO y W+C+600;
6. tablas de métricas, matrices de confusión y decisiones negativas;
7. manifiestos y checksums;
8. notebook y resultado de MrBERT-es;
9. instrumento, cuarentena y resultado de la evaluación ciega.
