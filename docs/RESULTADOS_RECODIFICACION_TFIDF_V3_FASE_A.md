# Resultados de la fase A: recodificación v2/v3 de predicciones TF-IDF congeladas

## Objetivo y alcance

Esta es la fase A fijada en `PROTOCOLO_COMPARACION_V3.md`. Se seleccionaron exactamente las 793 filas únicas con `supervision=seis_mas_trece` de `data/evaluacion/referencias_corregidas_v2/predicciones_validacion.csv`. Se preservaron ID, fold y predicción final. La única variable de la comparación es la referencia usada para puntuar: etiqueta corregida v2 frente a etiqueta canónica v3.

No hubo entrenamiento, ajuste de hiperparámetros, reselección de modelos ni modificación de predicciones. Tampoco es una nueva evaluación ciega: reutiliza el conjunto histórico de desarrollo después de la revisión de sus referencias.

## Verificación del ancla v2

Antes de calcular v3, el evaluador reprodujo exactamente los cuatro resultados publicados para v2:

| Métrica | Resultado reproducido |
|---|---:|
| Accuracy | 0.935687263556116 |
| Macro-F1 | 0.8199279654489144 |
| F1-HD | 0.7435283118097353 |
| Media de F1-HD por fold | 0.7470596639017691 |

También reprodujo los 51 errores y la matriz histórica en orden real/predicho H, D, N: `[[62, 6, 8], [9, 38, 4], [10, 14, 642]]`.

## Resultado al cambiar solamente la referencia

| Referencia | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores |
|---|---:|---:|---:|---:|---:|
| v2 | 0.935687 | 0.819928 | 0.743528 | 0.747060 | 51 |
| v3 | 0.919294 | 0.762620 | 0.662393 | 0.663972 | 64 |
| Delta v3 − v2 | -0.016393 | -0.057308 | -0.081135 | -0.083088 | +13 |

La matriz v3, con el mismo orden, es `[[65, 11, 12], [4, 25, 3], [12, 22, 639]]`.

| Fold | n | F1-HD v2 | F1-HD v3 | Delta | Errores v2 | Errores v3 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 158 | 0.778571 | 0.607143 | -0.171429 | 8 | 14 |
| 2 | 159 | 0.799242 | 0.798319 | -0.000923 | 7 | 7 |
| 3 | 159 | 0.738739 | 0.660088 | -0.078651 | 12 | 16 |
| 4 | 159 | 0.686603 | 0.652778 | -0.033825 | 13 | 14 |
| 5 | 158 | 0.732143 | 0.601533 | -0.130610 | 11 | 13 |

## Cambios de referencia y efecto mecánico

En los 793 IDs hay 28 cambios de etiqueta y un cambio de relevancia:

- dovish → neutral: 12;
- dovish → hawkish: 8;
- neutral → hawkish: 6;
- hawkish → dovish: 1;
- hawkish → neutral: 1.

De los 28 cambios de etiqueta, 19 convierten un acierto v2 en error v3, seis convierten un error v2 en acierto v3 y tres no alteran el estado de acierto. El saldo neto es de 13 aciertos menos, exactamente el cambio de 51 a 64 errores.

El único cambio de relevancia favorece la predicción binaria congelada (`pred_a=1`): sus aciertos pasan de 767/793 (0.967213) con v2 a 768/793 (0.968474) con v3. Este resultado binario se mantiene separado de las métricas H/D/N.

## Interpretación correcta

La caída no demuestra que un modelo reentrenado con v3 sea peor. En esta fase no existe ese modelo: las predicciones son idénticas a las históricas. El resultado cuantifica cuánto cambia la puntuación cuando el criterio oficial de referencia cambia de v2 a v3. La mayor reducción en F1-HD indica que las predicciones congeladas estaban más alineadas con la antigua codificación direccional, particularmente con usos de `dovish` recodificados bajo el criterio de dirección respaldada.

La pregunta de aprendizaje —qué ocurre al supervisar el mismo TF-IDF con v3— corresponde a la fase B y debe mantenerse separada. La incorporación de las 89 IA nuevas corresponde a la fase C. Los 257 registros pre-2000 siguen excluidos.

## Reproducibilidad

Ejecutar desde la raíz en una ruta nueva:

```bash
python scripts/40_gestionar_proyecto.py evaluar-recodificacion-v3 --salida /ruta/nueva
```

La implementación usa solo la biblioteca estándar, rechaza sobreescrituras y registra hashes de fuentes y salidas. Los artefactos canónicos están en `data/evaluacion/recodificacion_tfidf_v3_fase_a/`:

- `predicciones_referencias_v2_v3.csv`: alineación por ID y efecto individual;
- `cambios_referencia.csv`: los casos cuya etiqueta o relevancia cambió;
- `errores_v3.csv`: los 64 errores con tipo operativo, prioridad, cita y fundamento v3;
- `desagregacion_errores.json`: errores por clase, confusión y reunión;
- `metricas.json`: resultados globales y por fold;
- `protocolo.json`: operación, limitación y hashes de las entradas;
- `verificacion.json`: reproducción del ancla histórica;
- `resumen.md`: síntesis legible;
- `manifest.json`: hashes de integridad de las salidas.
