# Resultados — análisis secundario del test ciego v3

## Estatuto

Análisis explicativo postapertura, fijado antes de generar C+600 y W+C+89. No es una nueva confirmación independiente, no hubo búsqueda de hiperparámetros y el test no puede reutilizarse para seleccionar nuevas variantes.

## Factorial congelado 2×2 (n=299)

| Modelo | Accuracy | Macro-F1 | F1-HD | Errores | H↔D | H/D→N |
|---|---:|---:|---:|---:|---:|---:|
| C+89 | 0,775920 | 0,629934 | 0,513709 | 67 | 7 | 14 |
| W+C+89 | 0,779264 | 0,630112 | 0,513661 | 66 | 6 | 15 |
| C+600 | 0,846154 | 0,735642 | 0,651135 | 46 | 3 | **13** |
| W+C+600 | **0,856187** | **0,746259** | **0,663248** | **43** | **3** | 14 |

## Atribución

La mayor parte de la mejora proviene de los datos adicionales:

- +600 sobre C: +0,0702 accuracy, +0,1057 macro-F1 y +0,1374 F1-HD;
- +600 sobre W+C: +0,0769 accuracy, +0,1161 macro-F1 y +0,1496 F1-HD;
- caracteres con +89: +0,0033 accuracy, +0,0002 macro-F1 y −0,00005 F1-HD;
- caracteres con +600: +0,0100 accuracy, +0,0106 macro-F1 y +0,0121 F1-HD.

Por tanto, el test confirma con fuerza el valor de las 600 anotaciones, pero la contribución incremental de caracteres es pequeña.

## Incertidumbre agrupada por reunión

Bootstrap de 10.000 remuestras de las 33 reuniones:

| Comparación | Métrica | P2,5 | Mediana | P97,5 | P(Δ>0) |
|---|---|---:|---:|---:|---:|
| W+C+600 − C+89 | Accuracy | 0,0443 | 0,0796 | 0,1158 | 1,0000 |
|  | Macro-F1 | 0,0523 | 0,1165 | 0,1933 | 1,0000 |
|  | F1-HD | 0,0604 | 0,1497 | 0,2583 | 0,9997 |
| W+C+600 − C+600 | Accuracy | −0,0065 | 0,0100 | 0,0283 | 0,8339 |
|  | Macro-F1 | −0,0263 | 0,0115 | 0,0561 | 0,7203 |
|  | F1-HD | −0,0408 | 0,0134 | 0,0784 | 0,6794 |

W+C+600 supera a C+89 de forma robusta: gana en aciertos en 17 reuniones, empata en 14 y pierde en 2. Frente a C+600, gana en 5, empata en 26 y pierde en 2; los intervalos incluyen cero.

## Errores y robustez de W+C+600

Sus 43 errores se reparten en 26 falsas direcciones N→H/D, 14 omisiones H/D→N y 3 inversiones H↔D. Por estrato, la accuracy es 0,972 en aleatorio contextual, 0,780 en candidato dovish, 0,831 en candidato hawkish y 0,759 en neutral difícil. Los 12 casos con desacuerdo entre miembros alcanzan 0,583 frente a 0,868 en los 287 casos unánimes, por lo que el desacuerdo es una señal útil de revisión, no un umbral ajustado.

## Conclusión metodológica

La comparación primaria W+C+600 contra C+89 fue justa para escoger entre dos sistemas completos congelados y su ventaja es robusta. No fue una ablación justa de la representación. La comparación factorial muestra que **+600 explica casi toda la mejora**. W+C+600 tiene tres errores menos que C+600, pero una omisión más, y su ventaja incremental no es concluyente al agrupar por reunión.

En consecuencia, se conserva la decisión primaria registrada de W+C+600 frente al antiguo incumbente C+89, pero no debe afirmarse que los caracteres sean inequívocamente superiores a palabras con los mismos datos. C+600 queda como alternativa parsimoniosa y de menor omisión para una futura validación independiente. Este test queda cerrado y no se usará para nuevas selecciones.
