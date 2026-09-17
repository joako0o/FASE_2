# Reestimación C versus W+C con 600 humanas v3

Apertura histórica de desarrollo; no evaluación independiente.

| Condición | Macro-F1 | F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C+89 | 0.772956 | 0.676339 | 0.571429 | 0.562500 | 0.781250 | 0.966191 | 57 | 12 | 15 | 30 |
| C+89+300 | 0.780340 | 0.686543 | 0.596491 | 0.531250 | 0.776596 | 0.967934 | 54 | 11 | 19 | 24 |
| C+89+600 | 0.786694 | 0.697513 | 0.612903 | 0.593750 | 0.782123 | 0.965056 | 55 | 8 | 23 | 24 |
| W+C+89+600 | 0.825003 | 0.752701 | 0.721311 | 0.687500 | 0.784091 | 0.969607 | 48 | 7 | 22 | 19 |

**C vs W+C:** aceptar_wc.
**Frente al ancla:** retener_ancla_c89.
**Modelo resultante:** `ancla_c_89`.
