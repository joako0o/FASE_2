# Ensamble calibrado C + W+C

Selección íntegra en 559 filas fold=0; una sola política se abrió externamente.

Peso W+C elegido: `1.0`. Política ganadora: `blend_50`.

| Política interna | Controles (de 8) | Media F1-HD | Recall D | F1 D |
|---|---:|---:|---:|---:|
| blend_50 | 5 | 0.525954 | 0.181818 | 0.266667 |
| blend_50_d115 | 2 | 0.505319 | 0.181818 | 0.242424 |
| blend_75wc_d115 | 2 | 0.502114 | 0.181818 | 0.242424 |
| blend_75wc_d115_margin05 | 2 | 0.508693 | 0.181818 | 0.242424 |
| blend_50_maxsent_d115 | 3 | 0.512621 | 0.181818 | 0.258065 |

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 0.928121 | 0.772956 | 0.676339 | 0.661682 | 0.571429 | 0.562500 | 0.781250 | 0.966191 | 57 | 12 | 15 | 30 |
| blend_50 | 0.924338 | 0.770451 | 0.674028 | 0.662059 | 0.584615 | 0.593750 | 0.763441 | 0.963296 | 60 | 11 | 19 | 30 |

**Decisión: RECHAZAR.** `{"media_f1_hd_mejora": true, "mayoria_folds": false, "f1_d_no_baja": true, "recall_d_no_baja": true, "inversiones_no_aumentan": true, "omisiones_no_aumentan": false, "macro_f1_no_baja": false, "f1_n_no_baja": false}`
