# Ronda lineal — palabras + caracteres

Pesos de caracteres elegidos solo mediante CV interna agrupada por reunión. Evaluación de desarrollo abierta, no test final.

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 0.928121 | 0.772956 | 0.676339 | 0.661682 | 0.571429 | 0.562500 | 0.781250 | 0.966191 | 57 | 12 | 15 | 30 |
| Palabra+carácter | 0.929382 | 0.789804 | 0.701974 | 0.696007 | 0.625000 | 0.625000 | 0.778947 | 0.965465 | 56 | 10 | 16 | 30 |

| Fold | F1-HD C | F1-HD palabra+carácter | Delta | Peso char interno |
|---:|---:|---:|---:|---:|
| 1 | 0.482540 | 0.588889 | +0.106349 | 1.0 |
| 2 | 0.761905 | 0.761905 | +0.000000 | 0.5 |
| 3 | 0.745349 | 0.745349 | +0.000000 | 1.0 |
| 4 | 0.809091 | 0.780952 | -0.028139 | 1.0 |
| 5 | 0.509524 | 0.602941 | +0.093417 | 1.0 |

**Decisión multicriterio: RECHAZAR.** Controles: `{"media_f1_hd_mejora": true, "al_menos_3_folds": false, "f1_d_no_baja": true, "recall_d_no_baja": true, "inversiones_no_aumentan": true, "omisiones_no_aumentan": false, "macro_f1_no_baja": true, "f1_n_no_baja": false}`.
