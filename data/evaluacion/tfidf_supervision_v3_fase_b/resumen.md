# Fase B — TF-IDF reentrenado con supervisión v3

Se conservaron los 1.352 IDs IA-base, 793 validaciones, cinco folds, purga, arquitectura y parámetros históricos. Solo cambió etiqueta/relevancia de supervisión a v3. El ancla v2 se reprodujo exactamente antes del ajuste v3.

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A congelada→v3 | 0.919294 | 0.762620 | 0.662393 | 0.663972 | 64 | 15 | 15 | 34 |
| B entrenada v3→v3 | 0.928121 | 0.767917 | 0.668367 | 0.661574 | 57 | 13 | 16 | 28 |

Esta sigue siendo evaluación de desarrollo reutilizada, no una prueba independiente. No se añadieron las 89 IA nuevas, pre-2000 ni sintéticos.
