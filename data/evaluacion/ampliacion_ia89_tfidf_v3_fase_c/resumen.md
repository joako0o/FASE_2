# Fase C — ampliación TF-IDF v3 con 89 IA reales

La fase B se reprodujo exactamente. Las 89 IA nuevas entraron solo al train permitido después de purga por reunión/texto; la validación sigue siendo la misma colección real de 793 IDs.

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B base v3 | 0.928121 | 0.767917 | 0.668367 | 0.661574 | 57 | 13 | 16 | 28 |
| C base+89 | 0.928121 | 0.772956 | 0.676339 | 0.661682 | 57 | 12 | 15 | 30 |

No es una evaluación independiente. No se usaron datos sintéticos ni pre-2000.
