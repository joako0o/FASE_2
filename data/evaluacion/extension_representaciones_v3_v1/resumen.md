# Extensión de representaciones v3

Selección exclusiva mediante CV agrupada en las 559 filas `fold=0`; solo el ganador se evaluó externamente.

| Método interno | Media F1-HD | Recall D | Macro-F1 |
|---|---:|---:|---:|
| token_monetario | 0.518334 | 0.181818 | 0.652216 |
| nbsvm | 0.533438 | 0.181818 | 0.666659 |
| lsa128 | 0.494491 | 0.363636 | 0.634375 |
| suavizado_oraciones | 0.452587 | 0.090909 | 0.631497 |

**Ganador interno fijado: `nbsvm`.**

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 0.928121 | 0.772956 | 0.676339 | 0.661682 | 0.571429 | 0.562500 | 0.781250 | 0.966191 | 57 | 12 | 15 | 30 |
| nbsvm | 0.934426 | 0.779276 | 0.684492 | 0.670885 | 0.588235 | 0.468750 | 0.780749 | 0.968843 | 52 | 10 | 22 | 20 |

**Decisión multicriterio: RECHAZAR.** `{"media_f1_hd_mejora": true, "al_menos_3_folds": false, "f1_d_no_baja": true, "recall_d_no_baja": false, "inversiones_no_aumentan": true, "omisiones_no_aumentan": false, "macro_f1_no_baja": true, "f1_n_no_baja": true}`
