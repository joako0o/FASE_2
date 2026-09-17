# Resultados de fase C: ampliación TF-IDF v3 con 89 IA reales

## Diseño

Se comparó la fase B contra el mismo entrenamiento ampliado con las 89 intervenciones IA nuevas auditadas bajo v3: H30/D34/N25, todas relevantes. Se mantuvieron arquitectura, parámetros, folds y los mismos 793 IDs reales de validación.

Para cada fold se excluyeron las intervenciones nuevas pertenecientes a reuniones de validación o con texto normalizado repetido. No hubo copias textuales; por coincidencia de reunión entraron 79, 79, 79, 72 y 76 ejemplos nuevos en los folds 1–5. La fase B fue reentrenada y reproducida exactamente antes de comparar.

No se utilizaron datos sintéticos ni pre-2000.

## Resultado agregado

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B base v3 | 0,928121 | 0,767917 | 0,668367 | 0,661574 | 57 | 13 | 16 | 28 |
| C base+89 | 0,928121 | 0,772956 | 0,676339 | 0,661682 | 57 | 12 | 15 | 30 |
| Delta C−B | 0 | +0,005039 | +0,007972 | +0,000107 | 0 | −1 | −1 | +2 |

Cambian 11 predicciones finales: cuatro errores se corrigen y cuatro aciertos se pierden. No cambia la exactitud ni el total de errores. El F1-HD agregado mejora ligeramente, pero su media por fold queda prácticamente igual.

## Resultado por clase

| Clase | Precisión B | Precisión C | Recall B | Recall C | F1 B | F1 C |
|---|---:|---:|---:|---:|---:|---:|
| Hawkish | 0,6944 | 0,7212 | 0,8523 | 0,8523 | 0,7653 | 0,7813 |
| Dovish | 0,6667 | 0,5806 | 0,5000 | 0,5625 | 0,5714 | 0,5714 |
| Neutral | 0,9758 | 0,9772 | 0,9584 | 0,9554 | 0,9670 | 0,9662 |

Los 34 D nuevos elevan el recall D de 50,00% a 56,25%, pero reducen su precisión de 66,67% a 58,06%; el F1 D queda exactamente igual. La mejora de F1-HD procede principalmente de hawkish.

## Estabilidad por fold

| Fold | F1-HD B | F1-HD C | Delta |
|---:|---:|---:|---:|
| 1 | 0,5074 | 0,4825 | −0,0249 |
| 2 | 0,7500 | 0,7619 | +0,0119 |
| 3 | 0,7029 | 0,7453 | +0,0424 |
| 4 | 0,8667 | 0,8091 | −0,0576 |
| 5 | 0,4810 | 0,5095 | +0,0286 |

Mejoran tres folds y empeoran dos. El promedio prácticamente nulo confirma que el efecto es pequeño e inestable.

## Decisión

Las 89 IA reales muestran una **señal favorable pequeña**, particularmente en recall D, inversiones y F1-HD agregado, pero no evidencia suficiente para declarar una mejora robusta: no reducen errores, no mejoran F1 D y no elevan materialmente la media por fold.

Se conserva fase C como tratamiento candidato, sin reemplazar todavía la fase B. La futura base sintética debe evaluarse contra ambos puntos de referencia y mediante una curva de dosis; no debe añadirse automáticamente sobre C sin reportar también B+sintético por separado.

## Artefactos

`data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/` contiene predicciones por ID, 11 cambios, 57 errores, inclusión/purga de los 89 por fold, métricas, ejecución, protocolo, verificación, resumen y manifiesto.
