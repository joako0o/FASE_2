# Ronda jerárquica direccional

Tres etapas: relevancia, presencia de dirección y signo H/D. Se reutiliza sin cambios la representación y el peso seleccionados internamente en la ronda anterior.

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 0.928121 | 0.772956 | 0.676339 | 0.661682 | 0.571429 | 0.562500 | 0.781250 | 0.966191 | 57 | 12 | 15 | 30 |
| Multiclase W+C | 0.929382 | 0.789804 | 0.701974 | 0.696007 | 0.625000 | 0.625000 | 0.778947 | 0.965465 | 56 | 10 | 16 | 30 |
| Jerarquía | 0.921816 | 0.763360 | 0.663194 | 0.651548 | 0.555556 | 0.625000 | 0.770833 | 0.963691 | 62 | 14 | 12 | 36 |

| Fold | F1-HD C | F1-HD jerarquía | Delta |
|---:|---:|---:|---:|
| 1 | 0.482540 | 0.553247 | +0.070707 |
| 2 | 0.761905 | 0.750000 | -0.011905 |
| 3 | 0.745349 | 0.738095 | -0.007254 |
| 4 | 0.809091 | 0.719697 | -0.089394 |
| 5 | 0.509524 | 0.496703 | -0.012821 |

**Decisión multicriterio vs C: RECHAZAR.** `{"media_f1_hd_mejora": false, "al_menos_3_folds": false, "f1_d_no_baja": false, "recall_d_no_baja": true, "inversiones_no_aumentan": false, "omisiones_no_aumentan": true, "macro_f1_no_baja": false, "f1_n_no_baja": false}`
