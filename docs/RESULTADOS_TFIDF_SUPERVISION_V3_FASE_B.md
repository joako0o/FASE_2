# Resultados de fase B: TF-IDF con supervisión v3

## Diseño ejecutado

Se reentrenó desde cero el TF-IDF histórico dentro de cada fold, sustituyendo únicamente etiqueta y relevancia por la referencia v3. Se conservaron:

- los mismos 1.352 IDs IA-base;
- los mismos 793 IDs de validación y cinco folds por reunión;
- la misma purga de textos normalizados repetidos;
- TF-IDF A de unigramas y TF-IDF B de n-gramas 1–4;
- regresión logística balanceada, `C=2`, `max_iter=2000`, semilla 20260915;
- la regla final: A irrelevante produce neutral; A relevante usa la predicción B.

No se añadieron las 89 IA nuevas, el set pre-2000 ni datos sintéticos. No hubo búsqueda de hiperparámetros ni refit global. Antes de entrenar v3, la reconstrucción con supervisión v2 reprodujo exactamente `pred_a`, `pred_b` y predicción final en los 793 IDs históricos.

## Resultado agregado

| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores | H↔D | H/D→N | N→H/D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fase A: congelada→v3 | 0,919294 | 0,762620 | 0,662393 | 0,663972 | 64 | 15 | 15 | 34 |
| Fase B: entrenada v3→v3 | 0,928121 | 0,767917 | 0,668367 | 0,661574 | 57 | 13 | 16 | 28 |
| Delta B−A | +0,008827 | +0,005297 | +0,005974 | **−0,002398** | −7 | −2 | +1 | −6 |

El reentrenamiento modificó 40 predicciones finales: corrigió 19 errores y creó 12, para una mejora neta de siete aciertos.

## Resultado por clase

| Clase | Precisión A | Precisión B | Recall A | Recall B | F1 A | F1 B |
|---|---:|---:|---:|---:|---:|---:|
| Hawkish | 0,8025 | 0,6944 | 0,7386 | 0,8523 | 0,7692 | 0,7653 |
| Dovish | 0,4310 | 0,6667 | 0,7813 | 0,5000 | 0,5556 | 0,5714 |
| Neutral | 0,9771 | 0,9758 | 0,9495 | 0,9584 | 0,9631 | 0,9670 |

La matriz B, filas reales y columnas predichas H/D/N, es `[[75, 2, 11], [11, 16, 5], [22, 6, 645]]`.

La precisión D mejora porque el modelo emite muchas menos predicciones D, pero su recall cae de 78,13% a 50,00%. Las inversiones totales bajan de 15 a 13, aunque cambian de composición: ahora hay 2 H→D y 11 D→H. Por tanto, el problema direccional no está resuelto; se desplazó principalmente hacia la omisión de D como H.

## Estabilidad entre folds

| Fold | n | F1-HD A | F1-HD B | Delta | Errores A | Errores B |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 158 | 0,607143 | 0,507353 | −0,099790 | 14 | 12 |
| 2 | 159 | 0,798319 | 0,750000 | −0,048319 | 7 | 7 |
| 3 | 159 | 0,660088 | 0,702899 | +0,042811 | 16 | 14 |
| 4 | 159 | 0,652778 | 0,866667 | +0,213889 | 14 | 8 |
| 5 | 158 | 0,601533 | 0,480952 | −0,120580 | 13 | 16 |

Solo dos folds mejoran en F1-HD. La mejora agregada está fuertemente influida por el fold 4, mientras los folds 1 y 5 empeoran de manera importante. Por eso la media de F1-HD por fold baja levemente pese a mejorar el F1-HD calculado sobre las 793 filas juntas.

## Decisión

**No adoptar todavía la fase B como modelo definitivo.** El resultado confirma que supervisar con v3 mejora siete aciertos, reduce falsas señales direccionales y eleva la precisión D, pero presenta alta inestabilidad entre folds y pierde la mitad de los D reales. No corresponde ajustar parámetros después de observar este resultado dentro de la fase B fijada.

El próximo paso del plan debe ser un diagnóstico de los 57 errores B y de los 40 cambios de predicción. Ese diagnóstico permitirá definir la auditoría de la futura base sintética sin fabricar ejemplos para casos de validación individuales. Cuando la base sintética esté disponible, se evaluará como aumento separado mediante la curva de dosis acordada y siempre contra validación real.

## Artefactos

Los resultados reproducibles están en `data/evaluacion/tfidf_supervision_v3_fase_b/`:

- `predicciones.csv`: comparación por ID entre A congelada y B reentrenada;
- `comparacion_casos.csv`: las 40 predicciones finales que cambiaron;
- `errores_fase_b.csv`: los 57 errores B clasificados por tipo;
- `metricas.json`: métricas agregadas, por clase y fold;
- `ejecucion_folds.json`: tamaños, purgas, clases, vocabularios e iteraciones;
- `protocolo.json`, `verificacion.json` y `manifest.json`: parámetros, ancla e integridad;
- `resumen.md`: síntesis de resultados.

Ejecución en una ruta nueva:

```bash
python scripts/40_gestionar_proyecto.py entrenar-tfidf-v3 --salida /ruta/nueva
```

La evaluación continúa siendo desarrollo reutilizado y no una prueba independiente.
