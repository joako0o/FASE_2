# Diagnóstico del deterioro TF-IDF +59: protocolo

El investigador solicita revisar los errores nuevos y pensar por qué falla. Se leen las 16 intervenciones con predicción cambiada: nueve errores nuevos, tres corregidos y cuatro que siguen errados. Se conservan las referencias y resultados previos, sin nuevos modelos candidatos ni selección posterior de ejemplos para mejorar una métrica.

## Evidencia cuantitativa

1. Verificar hashes y reconstruir exactamente control/ampliado del ensayo `ampliacion_tfidf_59_v1`. Mismos hiperparámetros/cohortes/purgas. Reproducir A/B/final sobre los 793 casos de cada condición antes de interpretar coeficientes.
2. Para cada cambio, definir el margen como score de la clase predicha por el ampliado menos score de la clase predicha por el control. Debe ser negativo en el control y positivo en el ampliado.
3. Alinear los términos activos del texto entre ambos vocabularios; los términos ausentes se representan con x=0 y peso=0. Separar intercepto y cada contribución x*w.
4. Descomposición simétrica exacta: `delta(x*w) = media(x)*delta(w) + media(w)*delta(x)`. Verificar cierres numéricos. La división de la interacción es una convención algebraica: no identifica una intervención causal de IDF frente a coeficientes, y los términos nuevos se reparten entre ambos componentes bajo esa convención.
5. Guardar contribuciones completas, no solo las favorables a una interpretación. N-gramas solapados son características del modelo, no piezas independientes de significado.
6. Recuperar tres vecinos entre los **nuevos ejemplos del train permitido de ese fold**, usando coseno en el TF-IDF ampliado. No consultar candidatos vetados por reunión. Son similitudes léxicas, no prueba de influencia causal o errores de anotación de esos ejemplos.
7. Registrar vocabularios y pesos balanced implícitos en cada train. No cambiar pesos, vocabulario, umbrales o features para medir una variante nueva.

## Lectura cualitativa

Leer la intervención íntegra, conservar una cita literal de la resolución y distinguir diagnóstico económico, alternativas, preguntas, intención respaldada y trayectoria futura. Señalar fronteras de criterio entre referencias si existen, sin adjudicar nuevas etiquetas ni recomputar scores con ellas. Una predicción que ahora concuerda con v2 no demuestra comprensión correcta; revisar también las correcciones.

Interpretación permitida: explicar matemáticamente qué desplaza el margen y proponer hipótesis de selección/representación/consistencia. No afirmar causas de generalización, culpar un ejemplo solo por ser vecino, ajustar etiquetas para recuperar F1 o declarar que llegar a 300 resolverá el problema.

Se exportan márgenes, aportes por término, vecinos permitidos, reajustes y un informe de lectura. No se persisten pesos ni modelos. La ejecución recrea los mismos ajustes ya evaluados, no entrena otra variante ni hace refit global.
