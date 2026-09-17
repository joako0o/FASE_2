# Reestimación única C versus W+C con 300 humanas v3

Las 300 referencias entraron solo al train permitido, con exclusión por reunión y texto. Esta apertura histórica no es evaluación independiente.

| Condición | Macro-F1 | F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C+89 (ancla) | 0.772956 | 0.676339 | 0.571429 | 0.562500 | 0.781250 | 0.966191 | 57 | 12 | 15 | 30 |
| C+89+300 | 0.780340 | 0.686543 | 0.596491 | 0.531250 | 0.776596 | 0.967934 | 54 | 11 | 19 | 24 |
| W+C+89+300 | 0.811673 | 0.732728 | 0.678571 | 0.593750 | 0.786885 | 0.969562 | 49 | 8 | 21 | 20 |

**C vs W+C:** retener_c.
**Frente al ancla:** retener_ancla_c89.
**Modelo de desarrollo resultante:** `ancla_c_89`.
