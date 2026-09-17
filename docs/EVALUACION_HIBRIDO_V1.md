# Evaluación del híbrido contextual v1

**Mejor media observada: B0_base.** Variantes que cumplen el criterio práctico para avanzar a confirmación: **ninguna**.

Comparación de desarrollo contra IA, no rendimiento humano ni confirmación independiente. No se reemplazó el modelo guardado.

## Diseño congelado

[Protocolo previo](PROTOCOLO_HIBRIDO_V1.md) y [fundamento externo](INVESTIGACION_HIBRIDO.md). Cuatro variantes, cinco folds históricos; 793 validaciones y 559 adicionales en train. A fija compartida; B se ajusta solo en train relevante. N-gramas 1–4, min_df=3, C=2. Sin diccionario direccional, calibración ni búsqueda adicional.

**Alcance real:** la vista numérica conserva decimales/dígitos/unidad, pero no resuelve instrumento ni aritmética. La vista contextual selecciona frases candidatas y vecinas; no es un extractor fiable de respaldo, negación, emisor o tiempo. Conserva la vista completa. Añadir un bloque L2 de peso 1 cambia la geometría además de la representación.

## Resultados

| Variante | Macro-F1 medio | DE folds | Delta base | Mejora folds | F1 H | F1 D | Recall H | Recall D |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0_base | 0.7803 | 0.0640 | +0.0000 | 0/5 | 0.7397 | 0.6372 | 0.7826 | 0.7347 |
| B1_numeros | 0.7793 | 0.0618 | -0.0010 | 2/5 | 0.7297 | 0.6422 | 0.7826 | 0.7143 |
| B2_contexto | 0.7764 | 0.0699 | -0.0039 | 3/5 | 0.7500 | 0.6261 | 0.7826 | 0.7347 |
| B3_ambos | 0.7764 | 0.0747 | -0.0039 | 3/5 | 0.7448 | 0.6379 | 0.7826 | 0.7551 |

## Errores frente a IA y cambios frente a B0

| Variante | Total | H↔D | N→dirección | Dirección→N | Corregidos | Nuevos |
|---|---:|---:|---:|---:|---:|---:|
| B0_base | 62 | 17 | 34 | 11 | 0 | 0 |
| B1_numeros | 61 | 18 | 32 | 11 | 2 | 1 |
| B2_contexto | 62 | 17 | 34 | 11 | 8 | 8 |
| B3_ambos | 63 | 16 | 36 | 11 | 9 | 10 |

## Pruebas conductuales

14 ejemplos inventados, fijados antes de ajustar, repetidos con cinco modelos de fold. No son 70 observaciones independientes ni etiquetas humanas. El acierto usa salida A+B; invariancia se calcula aparte, pues dos predicciones iguales pueden estar ambas equivocadas.

| Variante | Acierto de clase (70 ejecuciones) | Invariancia (20 pares×fold) |
|---|---:|---:|
| B0_base | 35.7% | 70.0% |
| B1_numeros | 35.7% | 70.0% |
| B2_contexto | 35.7% | 75.0% |
| B3_ambos | 35.7% | 80.0% |

Los CSV contienen resultados por caso/fenómeno y fold. No se retocaron los métodos para pasar estos ejemplos.

## Extracción y controles

- Intervenciones de validación con ventana contextual: 345/793; sin candidato: 448. Sin candidato el bloque es cero, no se fuerza neutral.
- Fracción de caracteres seleccionados en validación: 41.0%. No es precisión del extractor: las ventanas son candidatos, no evidencia adjudicada.
- Textos con formatos numéricos potencialmente ambiguos (un separador y tres dígitos): 8. No se resuelven automáticamente como miles.
- Posiciones de todas las ventanas verificadas contra el original; sin truncamiento. B0 reproduce exactamente las 793 predicciones de (1,4); A es idéntica en las cuatro variantes.
- Vocabularios/IDF aprendidos solo en train; no cambios de fuentes ni modelo previo. Tiempos de ejecución registrados aparte; no se guardan clasificadores.

## Decisión y límites

El criterio previo exige delta medio ≥0,01, mejora en ≥3 folds, caída de recall H/D ≤0,02 y caída de acierto conductual ≤0,05. Son tolerancias prácticas, no pruebas de significación. Mayor media por sí sola no autoriza adopción.
Ninguna variante cumple: mantener B0 como referencia. No ampliar esta búsqueda tras ver resultados. Un extractor más semántico o un transformer sería otra comparación que requiere autorización.
- Los 793 ya se usaron para selección y diagnóstico; los 17 errores H/D conocidos no son un test nuevo. Persisten 34 textos repetidos con train, aunque las reuniones estén separadas.
- A permanece fija: cambiar B no corrige relevancia. Pasado, condiciones y referencias extranjeras no se descartan automáticamente; tampoco se resuelven plenamente.
- Las 306 respuestas humanas no se examinaron ni predijeron. Sin refit final con 1.352 ni scoring completo. Una confirmación necesita otra evaluación y control prefijado de duplicados.

## Artefactos y reproducción

En `data/evaluacion/hibrido_contextual_v1/`: protocolo, asignación, predicciones, resultados por fold, comparación, errores, pruebas conductuales, invariancias, vistas/ventanas verificadas, métricas, tiempos y manifiesto. `reproducibilidad.json` registra los controles posteriores cuando se completa la repetición.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/24_evaluar_hibrido_contextual.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/24_evaluar_hibrido_contextual.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
```
