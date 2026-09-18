# Datos esenciales

| Archivo | Contenido | Uso |
|---|---|---|
| `corpus_bcch_2005_2015.csv` | 9.725 intervenciones, orden de habla, tópico y keywords humanos del período oficial | Entrada para clasificación, secuencia intrarreunión y análisis semántico |
| `entrenamiento_wc600.csv` | 1.596 referencias únicas y miembros permitidos | Entrenamiento exacto del modelo final |
| `actores_metadata.csv` | 55 actores, cargos y cobertura temporal histórica | Insumo incompleto; no usar campos biográficos sin verificación |
| `revision_votos_actores.csv` | Auditoría asistida de 46 votos inicialmente no resueltos, con criterio y nota | Complemento trazable de la base de votos; no equivale a validación humana |
| `evaluacion_ciega_gold.csv` | 300 decisiones validadas; 299 evaluables | Evidencia final, nunca entrenamiento |
| `predicciones_evaluacion_ciega.csv` | Predicciones congeladas de cuatro condiciones | Reproducción de comparaciones |
| `resultados_evaluacion_ciega.json` | Métricas primarias completas | Resultado oficial |
| `analisis_factorial.json` | Factorial, bootstrap y robustez | Interpretación secundaria |
| `benchmark_modelos.csv/json` | Registro de 14 condiciones y parámetros | Defensa de selección |
| `manifest.json` | Checksums SHA-256 | Integridad |

No agregar `evaluacion_ciega_gold.csv` al entrenamiento. La columna `incluir_evaluacion=false` identifica el único caso no decidible.
