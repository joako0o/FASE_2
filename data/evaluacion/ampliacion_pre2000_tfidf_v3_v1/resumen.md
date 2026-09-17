# Ampliación real con pre-2000

Comparación de desarrollo reutilizada; no es evaluación independiente.

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C | 0.928121 | 0.772956 | 0.676339 | 0.661682 | 0.571429 | 57 | 12 | 15 | 30 |
| C + 250 pre-2000 | 0.925599 | 0.772918 | 0.677033 | 0.670915 | 0.596491 | 59 | 12 | 16 | 31 |

| Fold | F1-HD C | F1-HD C+pre-2000 | Delta |
|---:|---:|---:|---:|
| 1 | 0.482540 | 0.477941 | -0.004599 |
| 2 | 0.761905 | 0.805405 | +0.043501 |
| 3 | 0.745349 | 0.695035 | -0.050313 |
| 4 | 0.809091 | 0.866667 | +0.057576 |
| 5 | 0.509524 | 0.509524 | +0.000000 |

**Decisión: rechazar la dosis completa pre-2000.** Mejora la media por fold y F1 D, pero solo mejora 2/5 folds, aumenta los errores de 57 a 59, reduce F1 H y deteriora levemente accuracy. No se incorpora al candidato congelado.
