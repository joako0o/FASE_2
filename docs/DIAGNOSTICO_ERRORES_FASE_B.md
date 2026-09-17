# Diagnóstico dirigido de los 57 errores de fase B

## Localización del fallo

Los 57 errores finales tienen `pred_a_v3=1` y los 57 casos son relevantes bajo v3. Por tanto, en esta validación **ningún error final proviene de la puerta de relevancia A**. Todos se originan en la clasificación H/D/N de la etapa B.

| Referencia → predicción | Casos |
|---|---:|
| H→D | 2 |
| H→N | 11 |
| D→H | 11 |
| D→N | 5 |
| N→H | 22 |
| N→D | 6 |

Esto descarta como próximo objetivo inmediato modificar el umbral o entrenamiento de relevancia. El cuello de botella es separar dirección respaldada de neutral y, particularmente, distinguir D de H.

## Distribución por fold

| Fold | Errores | Composición principal |
|---:|---:|---|
| 1 | 12 | 5 H→N, 3 N→D, 2 D→H |
| 2 | 7 | 4 N→H, 2 D→H |
| 3 | 14 | 6 N→H, 4 D→H |
| 4 | 8 | 5 N→H, sin inversiones H/D |
| 5 | 16 | 6 N→H, 3 D→H, 2 H→D |

Los problemas no están confinados a un solo fold. El fold 5 combina el mayor número de errores con cinco inversiones H/D; el fold 3 contiene cuatro D→H. La mejora agregada de fase B no resuelve esta heterogeneidad.

## Implicación para nuevas bases

Los datos adicionales deben ayudar a la etapa B, no limitarse a aportar ejemplos fáciles de relevancia. Son especialmente valiosos:

- dovish respaldados con lenguaje de normalización, trayectoria futura o comparación de alternativas que pueda confundirse con H;
- neutrales relevantes con vocabulario de alzas/bajas pero sin respaldo propio;
- pares contrastivos que mantengan tema y estilo pero cambien quién respalda la dirección;
- ejemplos agrupados por escenario para impedir que paráfrasis hermanas contaminen validación.

No deben generarse imitaciones directas de los 57 textos de validación. El diagnóstico define familias generales, no objetivos individuales para optimizar el examen conocido.
