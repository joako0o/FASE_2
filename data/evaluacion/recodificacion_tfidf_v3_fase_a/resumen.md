# Fase A — recodificación de predicciones TF-IDF congeladas

Esta fase **no reentrena ni modifica predicciones**: evalúa las mismas 793 salidas `seis_mas_trece` contra las referencias v2 y v3. No es una prueba independiente.

| Referencia | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores |
|---|---:|---:|---:|---:|---:|
| v2 | 0.935687 | 0.819928 | 0.743528 | 0.747060 | 51 |
| v3 | 0.919294 | 0.762620 | 0.662393 | 0.663972 | 64 |

| Fold | n | F1-HD v2 | F1-HD v3 | Delta | Errores v2 | Errores v3 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 158 | 0.778571 | 0.607143 | -0.171429 | 8 | 14 |
| 2 | 159 | 0.799242 | 0.798319 | -0.000923 | 7 | 7 |
| 3 | 159 | 0.738739 | 0.660088 | -0.078651 | 12 | 16 |
| 4 | 159 | 0.686603 | 0.652778 | -0.033825 | 13 | 14 |
| 5 | 158 | 0.732143 | 0.601533 | -0.130610 | 11 | 13 |

Cambian 28 etiquetas y 1 marca de relevancia. En exactitud multiclase, 19 aciertos pasan a error y 6 errores pasan a acierto: saldo neto de 13 aciertos menos. La exactitud del clasificador de relevancia congelado pasa de 0.967213 a 0.968474. El delta describe exclusivamente el cambio de referencia; no degradación por entrenamiento.
