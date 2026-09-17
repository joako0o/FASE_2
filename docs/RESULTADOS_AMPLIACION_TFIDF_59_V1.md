# TF-IDF con 59 ejemplos nuevos: comparación controlada

**17-09-2026. Resultado: cambia, pero empeora en la validación de desarrollo. No se sustituye el control.**

## Resumen

Se entrenó aquí, en CPU, el TF-IDF original y su versión ampliada con los **59 H/D nuevos de alta confianza** disponibles: 29 H y 30 D. Se mantuvieron referencias v2, cinco folds purgados, filtro A y parámetros. Tras excluir por reunión/texto de validación, cada B recibió **53/51/52/50/53** ejemplos adicionales.

| Métrica | Control | Con ampliación | Cambio |
|---|---:|---:|---:|
| **F1 H/D media de cinco folds** | **0,747060** | **0,713526** | **−0,033533** |
| Macro-F1 media de cinco folds | 0,822250 | 0,798866 | −0,023383 |
| Errores / 793 | 51 | 57 | +6 |
| **Inversiones H↔D** | **15** | **17** | **+2** |
| H→D | 6 | 7 | +1 |
| D→H | 9 | 10 | +1 |
| H/D→N | 12 | 12 | Igual |
| N→H/D | 24 | 28 | +4 |
| Recall H | 62/76 = 81,58% | 61/76 = 80,26% | −1 acierto |
| Recall D | 38/51 = 74,51% | 37/51 = 72,55% | −1 acierto |
| Precisión D | 65,52% | 58,73% | −6,79 puntos porcentuales |

La F1 H/D de la matriz conjunta, distinta de la media por fold, pasa de **0,743528 a 0,715587**. La métrica principal del protocolo sigue siendo la media por fold, no la accuracy ni la F1 agrupada.

## Estabilidad por fold

| Fold | Control: F1 H/D | Ampliado: F1 H/D | Diferencia | Nuevos permitidos H / D |
|---|---:|---:|---:|---:|
| 1 | 0,778571 | 0,681159 | −0,097412 | 27 / 26 |
| 2 | 0,799242 | 0,752688 | −0,046554 | 22 / 29 |
| 3 | 0,738739 | 0,762548 | +0,023810 | 26 / 26 |
| 4 | 0,686603 | 0,658378 | −0,028224 | 23 / 27 |
| 5 | 0,732143 | 0,712857 | −0,019286 | 26 / 27 |

**Mejora solo 1/5 folds; empeora en cuatro.** No se escogió retrospectivamente el fold favorable ni otra combinación de ejemplos.

## Matrices completas

Filas = referencia H, D, N. Columnas = predicción H, D, N.

| Referencia | Control H | D | N | Ampliado H | D | N |
|---|---:|---:|---:|---:|---:|---:|
| H | 62 | 6 | 8 | 61 | 7 | 8 |
| D | 9 | 38 | 4 | 10 | 37 | 4 |
| N | 10 | 14 | 642 | 9 | 19 | 638 |

El deterioro no consiste en mandar más casos direccionales a N en conjunto. Aparecen más confusiones de dirección y más **neutrales predichos D (14→19)**. No se puede interpretar como mejora por el mero hecho de que haya aumentado el número de etiquetas direccionales de entrenamiento.

## Cambios pareados

Cambian **16 de 793** predicciones finales:

- **3 errores se corrigen:** dos H/D antes enviados a N y un N antes predicho D.
- **9 aciertos se pierden:** cinco N pasan a dirección, tres direccionales se invierten y un H pasa a N.
- Cuatro casos cambian de un error a otro: tres N pasan de H a D y una inversión D→H pasa a N.

El saldo es **seis errores adicionales**. Los 16 IDs, referencias, predicciones y folds están en `comparacion_casos.csv`; no se cambiaron etiquetas por conocer estos resultados.

Los cinco ambiguos conocidos permanecen dentro de la evaluación principal. En el suplemento que los retira simétricamente, las inversiones también suben **10→12** y los errores **46→52**. No se presenta el suplemento como un nuevo test ni como justificación para excluirlos.

## Qué se controló

1. Cohorte exacta de las cuatro tandas previas, no las colas G pendientes. Reservas medias, N, dudas y E009 repetido excluidos. Los textos son completos, no solo sus citas.
2. **El control reprodujo exactamente sus 793 predicciones A, B y finales**, además de las referencias. No se comparó contra una baseline reconstruida de forma diferente.
3. A se ajustó solo en el train original y se compartió entre ambas condiciones. Los nuevos ejemplos no cambiaron su entrenamiento ni sus decisiones.
4. B mantuvo n-gramas 1–4, min_df=3, max_df=0,9, sublinear_tf y regresión logística C=2, balanced, semilla 20260915. **Vocabulario, IDF y ponderaciones balanced se aprendieron dentro del train de cada condición**. Su cambio es una consecuencia de añadir documentos, no una búsqueda nueva de hiperparámetros.
5. Se respetaron las exclusiones ya registradas de reunión/texto por fold. Los train relevantes B pasan de 946/959/962/959/958 a 999/1010/1014/1009/1011. La validación nunca se usó para ajustar vocabulario o IDF.
6. Protocolo y hashes registrados antes del fit. Se hizo **una sola comparación de cohorte**, no una selección de tamaño, umbral o combinación después de ver los resultados.
7. **Dos corridas completas** con 15 ajustes cada una: cinco A originales, cinco B originales y cinco B ampliados. Predicciones, tabla pareada, inclusión por fold y métricas se reprodujeron byte a byte. Protocolo/ejecución coinciden salvo fecha y tiempos.
8. Una cuenta aritmética sin las funciones de métricas de sklearn confirmó las matrices y medias F1. **111 pruebas de software aprobadas, 0 omitidas**. La primera pasada de suite encontró una dependencia de preparación ausente; se instaló la lista fijada y se repitió la suite completa, sin saltar la prueba.

Se restauró el entorno CPU y se regeneró exactamente la entrada `f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`. No se descargaron pesos BETO ni se entrenó el encoder. No se guardaron modelos de esta comparación ni se reemplazaron artefactos anteriores.

## Interpretación y siguiente decisión

**Estos 59 ejemplos, con esta configuración, no aportan una mejora observada.** No cumplen las guardas de F1 H/D, número de folds favorables, macro-F1 ni reducción de inversiones. Las guardas de recall H/D y no aumentar H/D→N sí pasan, pero no bastan para aprobar el conjunto.

Esto **no demuestra que ampliar datos siempre empeore** ni que llegar a 300 sea inútil. El ensayo combina el efecto del contenido/variedad de los ejemplos, sus etiquetas de IA y la readaptación normal de la representación y los pesos del clasificador. No identifica causalmente cuál de esos componentes explica el deterioro.

Mi recomendación es **conservar el control original y revisar consistencia/representatividad del enriquecimiento antes de continuar acumulando por número**. La meta 300/300 sigue registrada, pero no debe convertirse en una cuota que obligue a añadir texto repetitivo o interpretaciones dudosas. No cambiar referencias o retirar filas porque perjudican el score. Cualquier diagnóstico o prueba adicional debe declararse aparte, sin selección retrospectiva oculta.

Las 793 validaciones se han usado en desarrollo y revisión asistida. Ni esta pérdida ni una futura ganancia constituyen una estimación independiente de generalización. Tampoco se justifica un refit global o scoring de todo el corpus.

## Archivos y reproducción

Resultados: `data/evaluacion/ampliacion_tfidf_59_v1/`.

- `protocolo.json`: diseño, cohortes, parámetros, versiones y hashes previos al entrenamiento.
- `inclusion_nuevos_por_fold.csv`: las 59 decisiones de inclusión/exclusión por cada fold.
- `predicciones.csv`: 793 predicciones de cada condición.
- `comparacion_casos.csv`: alineación pareada de los 793 casos.
- `metricas.json`: todos los indicadores, criterios y suplemento.
- `ejecucion.json`: tamaños de train/vocabulario, iteraciones y tiempos.
- `manifest.json`, `verificacion.json`: integridad, replay y pruebas.

Protocolo legible: [PROTOCOLO_AMPLIACION_TFIDF_59_V1](PROTOCOLO_AMPLIACION_TFIDF_59_V1.md).

Para reproducir en una ruta nueva, con el entorno de preparación instalado:

```bash
python scripts/40_gestionar_proyecto.py evaluar-ampliacion-tfidf --salida entregas/repeticion_tfidf_59
```

El gestor delega en un módulo reutilizable; no hay que ejecutar los scripts numerados uno a uno. Se conserva la obligación de limpieza extrema final. La cohorte de este ensayo se mantiene fijada a las cuatro tandas aquí evaluadas, aunque posteriormente existan nuevas anotaciones.
