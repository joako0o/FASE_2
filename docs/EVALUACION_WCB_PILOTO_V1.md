# Piloto: añadir datos de WCB Chile al TF-IDF

**Mejor media observada: B0_base.** El entrenamiento con la traducción española cambia la media de macro-F1 en **-0.0544** respecto de la referencia.

**Alcance: 100 frases externas seleccionadas, 99 utilizadas en B; no las 700 ni las 1.000 completas.** Se mantienen etiquetas WCB, sin armonizar con nuestro codebook. Traducción del agente IA, no español oficial ni revisión humana.

## Diseño y procedencia

[Protocolo congelado](PROTOCOLO_WCB_PILOTO_V1.md). [Datos, atribución, traducción y límites](../data/externos/wcb_chile_piloto_v1/README.md).
- Primeras 100 filas de train 5768, fuente pública con revisión HF registrada. 28 H / 30 D / 41 N / 1 irrelevant. El único irrelevant se conserva en el archivo, pero no se utiliza para B. No se añade nada a A.
- Mismos cinco folds IA: 793 intervenciones evaluadas y 559 adicionales solo en train. A unigramas fija compartida; B n-gramas 1–4, C=2/min_df=3. Vocabulario, IDF y regresión ajustados exclusivamente con el train de cada variante.
- E1 incorpora los 99 textos ingleses como control. E2 incorpora los mismos ejemplos traducidos. Igual peso individual y etiquetas. Balanced se recalcula, por lo que cambia también el peso de las clases: el control inglés no es un efecto lingüístico puro.
- No se descargó ni inspeccionó val/test externo. No se contaron las tres semillas como ejemplos distintos; sus solapes completos no se auditaron. No se abrió/predijo el gold humano.

## Resultados sobre las mismas 793 intervenciones IA

| Variante | Macro-F1 medio | DE | Delta base | Mejora folds | Macro-F1 conjunto | Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| B0_base | 0.7803 | 0.0640 | +0.0000 | 0/5 | 0.7810 | 0.9218 |
| E1_ingles | 0.7285 | 0.0503 | -0.0518 | 0/5 | 0.7362 | 0.9130 |
| E2_espanol | 0.7259 | 0.0865 | -0.0544 | 1/5 | 0.7306 | 0.9067 |

| Variante | F1 H | F1 D | Recall H | Recall D | Errores | H↔D | N→dirección | Dirección→N | Corregidos | Nuevos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0_base | 0.7397 | 0.6372 | 0.7826 | 0.7347 | 62 | 17 | 34 | 11 | 0 | 0 |
| E1_ingles | 0.7260 | 0.5200 | 0.7681 | 0.5306 | 69 | 19 | 30 | 20 | 4 | 11 |
| E2_espanol | 0.6887 | 0.5437 | 0.7536 | 0.5714 | 74 | 20 | 36 | 18 | 4 | 16 |

## Lectura y decisión

E2 **no cumple** el criterio práctico prefijado para avanzar a confirmación. No adoptar esta importación ni ampliar tamaño/pesos después de ver el resultado.
El criterio exige ≥0,01 de mejora media, al menos tres folds mejores y pérdidas de recall H/D ≤0,02. No son pruebas de significación. La métrica principal se fijó antes de ajustar; no sustituirla por otra más favorable.
**No equivale a descartar el dataset completo.** Solo se prueba esta muestra, traducción, combinación, peso y versión de etiquetas. Un resultado favorable también seguiría limitado por la evaluación IA reutilizada y por la traducción.

## Compatibilidad y calidad

- Diferencia de unidad: frases recientes de minutas frente a intervenciones completas históricas. Los fragmentos pueden depender de antecedentes ausentes.
- Diferencia de criterio: WCB asigna D a una frase de recesión argentina (source_id 217) y H a una subida de la Fed (434), mientras nuestro R3 requiere vínculo con política doméstica. También hay diagnósticos de consumo etiquetados D sin recomendación explícita. No se corrigieron etiquetas ni se eligieron solo los ejemplos convenientes.
- El esquema publicado no incluye enlace directo por fila al español oficial. No se realizó alineación con originales. La traducción fue realizada por el agente que pudo ver las etiquetas; no es una revisión independiente y puede introducir sesgos.
- Se verificó que cifras/signos y cantidad de porcentajes se conservaran; no hay duplicados exactos normalizados dentro de la muestra ni contra las 1.352 IA. Esto no certifica traducción ni excluye duplicados semánticos.
- Captura local de columnas desde la respuesta de API, no copia binaria Parquet verificada independientemente. La respuesta no quedó fijada por revisión; se registra el SHA observado de la ficha y el hash de la muestra congelada. Persisten riesgos de transcripción.
- Licencia de los datos externos y su traducción: CC BY-NC-SA 4.0, atribuida en su carpeta. No se mezclaron con anotaciones canónicas ni se guardaron modelos derivados.

## Controles y límites de evaluación

- B0 reproduce exactamente las 793 predicciones históricas de (1,4); A da idénticas predicciones entre variantes. No se sustituye el modelo unigramas guardado del examen humano.
- Persisten 34 textos IA repetidos con su train, aunque reuniones disjuntas. La comparación es desarrollo adaptativo, no test independiente; los folds comparten training y externos.
- Usar texto de 2018–2024 para evaluar 2005–2015 es un experimento retrospectivo; no una demostración de pronóstico histórico sin información futura.
- No se reajustó con todas las 1.352 ni se puntuó el corpus completo. La repetición y los tests se registran después en `reproducibilidad.json`; no prueban la exactitud de la traducción.

## Archivos y repetición

`data/evaluacion/wcb_chile_piloto_v1/`: protocolo previo, auditoría de la muestra, asignaciones, 2.379 predicciones, 15 resultados por fold, comparación, matrices, tiempos y manifiesto. Las tablas contienen soporte por clase, vocabulario, cobertura de ocurrencias de rasgos (no comprensión semántica) y pesos de clases.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/25_evaluar_wcb_piloto.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/25_evaluar_wcb_piloto.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
```
