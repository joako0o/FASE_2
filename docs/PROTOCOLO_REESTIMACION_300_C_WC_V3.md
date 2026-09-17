# Prerregistro — reestimación única C versus W+C con 300 anotaciones v3

**Fijado:** 17-09-2026, después del cierre semántico humano y antes de ejecutar o consultar resultados de esta reestimación.

## Pregunta y alcance

Medir una sola vez si las 300 anotaciones humanas cerradas mejoran el candidato **C** y si, con exactamente el mismo train permitido, la representación **W+C** supera a C. Esta es una evaluación de desarrollo sobre los 793 casos históricos ya consultados; no es una prueba independiente ni confirma la aspiración oficial.

No se usan sintéticos, pre-2000, racionales, citas, confianza, estratos ni predicciones como atributos.

## Datos y exclusiones congeladas

En cada uno de los cinco outer folds históricos:

1. la validación continúa siendo exclusivamente el fold histórico correspondiente;
2. el train base contiene los demás folds y `fold_validacion=0`;
3. se incorporan las 89 referencias IA v3 ya aceptadas;
4. se incorporan las 300 referencias humanas cerradas v3;
5. tanto las 89 como las 300 se excluyen si su `meeting_id` aparece en la validación o si su texto normalizado coincide con un texto de validación;
6. también se purgan del train base las copias textuales de validación.

Las 300 filas nunca ingresan a la validación. Se registrará por fila y fold la causa de inclusión o exclusión.

## Modelos congelados

- **C+300:** la puerta de relevancia y el clasificador H/D/N TF-IDF de palabras del candidato C, sin cambiar parámetros.
- **W+C+300:** la misma arquitectura de dos etapas, sustituyendo cada representación por la unión de TF-IDF de palabras y `char_wb` 3–5.

No habrá búsqueda nueva. Para W+C se congelan los pesos de caracteres elegidos previamente por CV interna, antes de disponer de las etiquetas de estas 300 filas:

| Outer fold | Peso char |
|---:|---:|
| 1 | 1,0 |
| 2 | 0,5 |
| 3 | 1,0 |
| 4 | 1,0 |
| 5 | 1,0 |

Se reproducirá primero el ancla C+89 en cada fold. C+300 y W+C+300 usan idénticas filas de entrenamiento dentro de cada fold.

## Métricas y decisiones

Se reportan accuracy, macro-F1, F1-HD, F1/precision/recall por clase, media de F1-HD entre folds, errores, inversiones H↔D, omisiones H/D→N y falsos N→H/D.

W+C+300 reemplaza a C+300 únicamente si satisface simultáneamente los ocho controles ya congelados:

1. mejora la media de F1-HD de folds;
2. mejora F1-HD en al menos tres folds;
3. F1 D no baja;
4. recall D no baja;
5. inversiones H↔D no aumentan;
6. omisiones H/D→N no aumentan;
7. macro-F1 no baja;
8. F1 N no baja.

Si falla alguno, la representación seleccionada es C+300. Después, la representación seleccionada solo reemplaza el ancla C+89 si satisface los mismos ocho controles frente a esa ancla. No se cambiarán reglas, pesos ni etiquetas después de observar el resultado.

## Límites

Este resultado solo decide si conservar una variante para desarrollo prospectivo. El objetivo oficial exige otra fuente o período real, ciego y agrupado por reunión. Las 300 anotaciones son train de desarrollo y no un test final intacto.
