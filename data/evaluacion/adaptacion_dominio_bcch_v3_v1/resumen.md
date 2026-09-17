# Adaptación no supervisada al dominio BCCh

Vocabulario e IDF se ajustan con textos L0 sin etiquetas y excluyendo íntegramente las reuniones de validación externa.

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 0.928121 | 0.772956 | 0.676339 | 0.661682 | 0.571429 | 0.562500 | 0.781250 | 0.966191 | 57 | 12 | 15 | 30 |
| W+C | 0.929382 | 0.789804 | 0.701974 | 0.696007 | 0.625000 | 0.625000 | 0.778947 | 0.965465 | 56 | 10 | 16 | 30 |
| Adaptado L0 | 0.928121 | 0.780393 | 0.687831 | 0.687729 | 0.603175 | 0.593750 | 0.772487 | 0.965517 | 57 | 11 | 17 | 29 |

| Fold | F1-HD C | F1-HD adaptado | Delta |
|---:|---:|---:|---:|
| 1 | 0.482540 | 0.553247 | +0.070707 |
| 2 | 0.761905 | 0.816667 | +0.054762 |
| 3 | 0.745349 | 0.702153 | -0.043196 |
| 4 | 0.809091 | 0.763636 | -0.045455 |
| 5 | 0.509524 | 0.602941 | +0.093417 |

**Decisión multicriterio: RECHAZAR.** `{"media_f1_hd_mejora": true, "al_menos_3_folds": true, "f1_d_no_baja": true, "recall_d_no_baja": true, "inversiones_no_aumentan": true, "omisiones_no_aumentan": false, "macro_f1_no_baja": true, "f1_n_no_baja": false}`
