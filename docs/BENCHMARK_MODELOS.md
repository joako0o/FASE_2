# Benchmark esencial de modelos y defensa de TF-IDF

## Propósito

Este documento forma parte del núcleo que debe conservarse cuando se ordene y reduzca el proyecto. Su finalidad es demostrar que TF-IDF no fue elegido por comodidad: se comparó bajo controles comunes con caracteres, BETO, jerarquías, adaptación de dominio, NB-SVM, datos adicionales y ensambles.

El registro exacto y legible por máquina está en `data/benchmark_modelos.json`; la tabla exportable está en `data/benchmark_modelos.csv`. Cada resultado conserva su ruta y checksum históricos, recuperables en Git desde el commit pre-condensación `7aa63cc`.

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
| MrBERT-es+600 | 0,771109 | 0,671369 | 0,766467 | 0,576271 | 0,970588 | 52 | 12 | 27 | rechazado controlado |

### Comparación controlada con MrBERT-es

MrBERT-es se ejecutó en Colab sobre los mismos 793 casos, cinco outer folds agrupados, datos adicionales +600, purga y etiquetas v3. Usó la revisión inmutable `34a7cc86e0d0a2b77e802d07a189db1c0ef2e7d4`, clasificación directa H/D/N, longitud máxima 1.024, dos épocas, tasa `2e-5`, batch 2, acumulación 8, `weight_decay=0,01` y pesos de clase inversos a la raíz de la frecuencia calculados solo en cada outer train.

Frente a W+C+600, MrBERT-es obtuvo menor accuracy (0,934426 frente a 0,939470), macro-F1 (0,771109 frente a 0,825003), F1-HD (0,671369 frente a 0,752701), F1 D (0,576271 frente a 0,721311) y F1 H (0,766467 frente a 0,784091). También produjo más errores (52 frente a 48), inversiones (12 frente a 7) y omisiones (27 frente a 22). Solo F1 N fue marginalmente mayor (0,970588 frente a 0,969607). No justificó sustituir TF-IDF/W+C.

El resultado es evidencia negativa importante, no una demostración de que todos los transformers sean inferiores. Es desarrollo comparativo abierto y no evaluación final independiente.

## Comparación controlada histórica con BETO

Esta comparación pertenece al benchmark legado v2 y no debe mezclarse numéricamente con la tabla v3, pero sí demuestra una comparación directa bajo el mismo conjunto y folds de esa ronda.

| Modelo | Accuracy | Macro-F1 | F1-HD | F1 D | Errores | H↔D | H/D→N |
|---|---:|---:|---:|---:|---:|---:|---:|
| TF-IDF legado | 0,935687 | 0,819928 | 0,743528 | 0,697248 | 51 | 15 | 12 |
| BETO | 0,916772 | 0,743412 | 0,630660 | 0,509804 | 66 | 25 | 14 |

BETO perdió en macro-F1, F1-HD, F1 D, errores e inversiones. Esto no prueba que todo transformer sea inferior; prueba que **ese BETO, con ese protocolo y esos datos**, no justificó reemplazar TF-IDF.

MrBERT-es queda registrado como experimento ejecutado y no adoptado. Su resultado se añadió sin borrar el resultado negativo de BETO ni cambiar retrospectivamente los criterios.

## Por qué se sostiene TF-IDF/W+C

1. **Evidencia empírica:** fue mejor que BETO en la comparación controlada y más estable que las extensiones evaluadas.
2. **Eficiencia de datos:** el corpus etiquetado es pequeño para ajustar encoders sin alta varianza.
3. **Adecuación lingüística:** n-gramas de palabras capturan frases monetarias; caracteres 3–5 absorben flexión, OCR, tildes y variantes ortográficas.
4. **Trazabilidad:** coeficientes, vocabulario y contribuciones pueden auditarse.
5. **Reproducibilidad:** se entrena en CPU con semillas, versiones y hashes, sin depender de pesos remotos cambiantes.
6. **Costo:** permite nested CV agrupada y repetición de controles con recursos modestos.
7. **Desempeño:** W+C+600 alcanza macro-F1 0,825 y F1-HD 0,753 en desarrollo.

## Confirmación ciega agrupada

Tras validación humana fila por fila se evaluaron 299 casos decidibles de las 300 filas. C+89 obtuvo accuracy 0,775920, macro-F1 0,629934 y F1-HD 0,513709; W+C+600 obtuvo accuracy 0,856187, macro-F1 0,746259 y F1-HD 0,663248. W+C redujo errores 67→43 e inversiones 7→3, mantuvo omisiones en 14 y mejoró los ocho controles congelados. Por ello **W+C+600 pasa a ser el modelo formal adoptado frente a C+89**.

El análisis factorial secundario mostró que +600 explica casi toda la mejora. Con los mismos +600 datos, C obtuvo macro-F1 0,735642 y W+C 0,746259, pero el intervalo agrupado de la diferencia incluye cero y W+C produjo 14 omisiones frente a 13 de C. Por tanto, no debe afirmarse que caracteres sea inequívocamente superior a palabras a igualdad de datos; C+600 queda como alternativa parsimoniosa para una futura validación independiente.

## Límites de la defensa

- La evaluación ciega es challenge enriquecida y no estima prevalencia natural.
- Sus 33 reuniones fueron excluidas totalmente del ajuste prospectivo, pero tuvieron exposición durante el desarrollo histórico.
- La anotación fue asistida por IA con validación humana fila por fila; una unidad no decidible quedó fuera de métricas.
- W+C+600 había aumentado omisiones en desarrollo y no se adoptó entonces; la adopción ocurrió solo tras no aumentarlas y superar los ocho controles en la apertura ciega.
- La conclusión incorpora el resultado negativo de MrBERT-es sin generalizarlo a todos los transformers.

## Evidencia preservada en la versión condensada

1. este documento y `data/benchmark_modelos.json`, con parámetros, métricas y decisiones de 14 condiciones;
2. `CODEBOOK_ETIQUETADO.md` y los protocolos de evaluación;
3. entrenamiento final con asignación exacta a los cinco miembros y purga ya aplicada;
4. parámetros exactos de C y W+C en el registro y el único script de producción;
5. predicciones ciegas de C+89, W+C+89, C+600 y W+C+600;
6. métricas, matrices de confusión, bootstrap, errores y decisiones negativas;
7. manifiesto y checksums de todos los archivos esenciales;
8. parámetros y resultado de MrBERT-es y BETO dentro del benchmark;
9. gold humano cerrado y resultado de la evaluación ciega.

Los artefactos históricos de detalle que no usa el modelo activo —incluidos notebooks y predicciones OOF antiguas— permanecen recuperables en Git en el commit `7aa63cc`; no forman parte del árbol esencial.
