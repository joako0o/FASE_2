# Datos del proyecto

Este directorio contiene las fuentes canónicas, conjuntos de entrenamiento y referencias de evaluación.

- `corpus_bcch_2005_2015.csv`: Fuente canónica única del texto completo de las 9.725 intervenciones del Banco Central de Chile (2005–2015).
- `entrenamiento_wc600.csv`: Conjunto de entrenamiento final (1.596 intervenciones etiquetadas y purgadas con 5 particiones/miembros).
- `evaluacion_ciega_gold.csv`: Referencia humana ciega (300 intervenciones de reuniones no vistas en entrenamiento).
- `predicciones_evaluacion_ciega.csv`: Predicciones de evaluación ciega obtenidas por el modelo adjudicado.
- `resultados_evaluacion_ciega.json`: Métricas de evaluación ciega oficial (Macro-F1 0,7463).
- `benchmark_modelos.csv` y `benchmark_modelos.json`: Comparativa de los 14 modelos evaluados.
- `analisis_factorial.json`: Descomposición de aporte de datos adicionales (+600) vs componentes de n-gramas.
- `actores_metadata.csv`: Metadatos estandarizados de los 55 actores registrados en las actas.
- `revision_votos_actores.csv`: Auditoría de decisiones de voto asistidas textualmente.
- `manifest.json`: Sumas de comprobación SHA-256 de los activos analíticos esenciales.
