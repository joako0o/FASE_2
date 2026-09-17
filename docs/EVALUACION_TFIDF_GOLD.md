# Prueba TF-IDF contra las 306 decisiones humanas

## Qué se hizo

1. Se compararon 12 configuraciones con validación cruzada de 5 particiones por reunión, usando solo las 1.352 etiquetas IA.
2. Se eligió la mayor media de macro-F1 de validación, sin consultar las respuestas humanas.
3. Se congeló la configuración, se reajustó con las 1.352 y se guardaron las 306 predicciones a partir de texto únicamente.
4. En un proceso posterior se abrió el Excel humano para comparar. No hubo ajustes después del test.

## Configuración elegida

- Candidato **6**: n-gramas [1, 1], min_df=3, C=2.0.
- Dos etapas TF-IDF + regresión logística con class_weight=balanced; sin variables de actor, fecha, macro o citas.
- Macro-F1 promedio en validación IA: **0.7264**. Es una métrica de selección, no una estimación independiente de generalización.

## Resultado del examen humano

**Coincidió en 260 de 306 intervenciones (85.0%). No coincidió en 46.**

| Métrica | Modelo seleccionado | Siempre neutral |
|---|---:|---:|
| Accuracy | 0.8497 | 0.7353 |
| Tasa de error | 0.1503 | 0.2647 |
| Macro-F1 | **0.6775** | 0.2825 |
| Kappa de Cohen | 0.6458 | 0.0000 |

| Clase humana | Casos | Precisión | Recall | F1 |
|---|---:|---:|---:|---:|
| hawkish | 49 | 0.6750 | 0.5510 | 0.6067 |
| dovish | 32 | 0.4146 | 0.5312 | 0.4658 |
| neutral | 225 | 0.9600 | 0.9600 | 0.9600 |

### Matriz de confusión

Filas: tu etiqueta. Columnas: predicción del modelo.

| Humano / Modelo | hawkish | dovish | neutral |
|---|---:|---:|---:|
| hawkish | 27 | 19 | 3 |
| dovish | 9 | 17 | 6 |
| neutral | 4 | 5 | 216 |

## Sensibilidad y límites

- Sin los textos idénticos a training: n=294, accuracy=0.8503, macro-F1=0.6859, κ=0.6512.
- Las 115 reuniones del gold también aparecen en training. Es un test por intervención, no por reuniones futuras.
- El muestreo gold enriquece vocabulario de decisión; no representa sin ponderación la prevalencia del corpus. Métricas por fase/señal en el JSON.
- Referencia humana: decisión inicial con revisión posterior de IA, sin cambios de etiquetas según autodeclaración. No es un protocolo completamente ciego.
- Estado documental: 86 incidencias de citas pendientes; las clases están completas y son utilizables para esta evaluación. No se forzó una importación gold ni se cambiaron etiquetas.
- El κ calculado es modelo TF-IDF vs decisiones humanas; no IA conversacional vs humano.
- Estos 306 ya se examinaron. No usarlos para ajustar y luego presentar una nueva cifra como test intacto.

## Archivos y reproducción

- `data/evaluacion/tfidf_gold_v1/validacion_cv.csv`: los 12 candidatos.
- `validacion_folds.csv` y `asignacion_folds.csv` en esa carpeta: resultados y particiones IA.
- `protocolo.json` y `seleccion.json`: búsqueda y elección congeladas antes de la comparación humana.
- `predicciones_gold.csv`: predicciones sin respuestas humanas; manifiesto con hash y fecha.
- `comparacion_gold.csv`: las 306 comparaciones, aciertos/errores, fase y textos repetidos.
- `metricas_gold.json`: resultados completos y trazabilidad.
- Modelo local en `modelos/tfidf_gold_v1.joblib` (ignorado por Git; se reconstruye con script 18).

Para repetir, usar rutas de salida NUEVAS; los scripts no sobrescriben el examen registrado.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/venvs/fase2/bin/python scripts/18_seleccionar_tfidf.py --salida /tmp/tfidf_reproduccion --modelo /tmp/tfidf_reproduccion.joblib
~/venvs/fase2/bin/python scripts/19_evaluar_tfidf_gold.py --experimento /tmp/tfidf_reproduccion --informe /tmp/tfidf_reproduccion.md
```
