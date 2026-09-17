# Protocolo previo: cuatro representaciones de postura, v1

Autorización: usuario, 2026-09-16 («vamos con tu recomendación»). Este documento y el código se registran por hash **antes del primer ajuste sobre el corpus**. No modificar la representación tras observar resultados; una corrección posterior requeriría declarar si invalida la corrida y crear otra versión.

## Objetivo y límites

Comparación de desarrollo contra IA, no confirmación humana. Mismos cinco folds históricos: 793 intervenciones validadas, 559 adicionales solo en train; 34 textos de validación repetidos con train. Se mantienen reuniones separadas, no se eliminan copias retrospectivamente. Sin acceso semántico al gold humano, sin refit final con 1.352, sin scoring completo, sin modelos persistidos ni cambio del codebook.

## Cuatro variantes, sin rejilla adicional

- **B0_base:** TF-IDF de texto completo, n-gramas 1–4, tokenización original.
- **B1_numeros:** misma vista completa, con tokenizador numérico descrito abajo.
- **B2_contexto:** B0 + bloque TF-IDF de fragmentos candidatos de decisión/contexto.
- **B3_ambos:** B1 + el mismo bloque contextual con tokenizador numérico.

A se ajusta una sola vez por fold con su configuración unigramas original y se comparte entre las cuatro B. B se ajusta solo con train relevante. En todos los bloques: min_df=3, max_df=0,9, sublinear_tf=True, normalización L2; vocabulario e IDF exclusivos de train. Regresión logística C=2, balanced, max_iter=2000 y semilla heredada. Peso fijo 1 por bloque; concatenación sin renormalización global. Añadir un bloque cambia la norma total y la geometría de regularización: no atribuir toda diferencia a comprensión lingüística. Sin calibración, stacking ni umbrales aprendidos.

## Representación numérica

Conservar tokens léxicos de al menos dos caracteres como el baseline. Cada secuencia de dígitos con cero o un separador decimal se representa como un token `numero_...`, incluyendo dígitos aislados; coma y punto decimales se canonizan, ceros finales redundantes se eliminan sin redondear. `%` se conserva como `unidad_porcentaje`. Signos +/− delante de números se representan cuando están precedidos por inicio, espacio o paréntesis; no interpretar guiones de fechas como signo negativo.

No se infiere instrumento, aritmética, sentido de la acción ni nivel neutral de TPM. Los números con un separador y tres dígitos posteriores son ambiguos respecto a miles: se registran como diagnóstico, no se resuelven con información externa. Fracciones, miles compuestos y otros formatos no están resueltos; se conserva el original. Esta ablación prueba reparación léxica, **no comprensión numérica completa**. No se eliminan cifras ni nombres.

## Vista contextual mínima y verificable

Segmentación por salto de línea o puntuación final `. ! ?` seguida de espacio; no se divide por coma, punto y coma o conectores adversativos, ni dentro de decimales. Abreviaturas pueden inducir divisiones; ventana vecina reduce pero no elimina ese límite.

Una frase es candidata si contiene TPM, tasa(s) de política, política monetaria, sesgo, raíz de estímulo, opción/opciones, voto/votar, proponer/propongo, recomendar o normalización. Los patrones exactos quedan en el módulo versionado. Se conserva la frase y una vecina anterior/posterior dentro de la misma intervención. Ventanas solapadas o adyacentes se fusionan. Se guardan posiciones exactas y subcadenas verificadas; no truncar por longitud ni completar desde otra intervención.

En el bloque contextual se generan n-gramas por ventana, sin cruzar huecos entre ventanas. Un analyzer invocable implementa explícitamente los n-gramas 1–4, pues sklearn no los genera automáticamente en ese modo. Si no hay candidato, el bloque contextual es cero y permanece el texto completo. Si todo el train carece de vocabulario contextual, se usa un bloque de cero columnas y se registra.

No se invierten etiquetas por negación ni se eliminan pasado, condiciones, menciones extranjeras o alternativas. **Esta primera versión selecciona contexto, no extrae de forma fiable emisor, objeto, respaldo ni alcance de negación.** El clasificador aprende sobre las vistas, sin un diccionario direccional. No implementa aún el extractor semántico completo de la investigación.

## Evaluación y criterio prefijado

Principal: macro-F1 H/D/N de salida A+B, media de cinco folds. Informar además DE, métricas por clase, matrices, H↔D, N→dirección, dirección→N, cambios acertados y errores nuevos frente a B0, cobertura/longitud de extracción y vocabularios. B0 debe reproducir exactamente las predicciones del candidato (1,4) anterior; A debe ser idéntica entre variantes.

Mayor media sin redondear identifica el **mejor observado**, con empate exacto por orden B0, B1, B2, B3. No hay adopción automática. Para recomendar avanzar a confirmación, una variante debe satisfacer simultáneamente: aumento medio ≥0,01 respecto de B0; mejora en al menos 3/5 folds; pérdidas de recall conjunto H y D no mayores a 0,02; tasa de aciertos de pruebas sintéticas de clase no inferior a B0 en más de 0,05. Son tolerancias prácticas prefijadas, no significación estadística. Si ninguna cumple, mantener B0 como referencia y reportarlo, sin buscar nuevas combinaciones en esta ronda.

La batería sintética se fija en código antes del entrenamiento: opciones explícitas, negación, menú, condicional, contrafactual, objeto, atribución, formato decimal, nombre y recomendación final. Expectativas didácticas del agente según v2, no nuevas etiquetas del corpus ni revisión humana. Medir por separado acierto de clase e invariancia; un par igualmente equivocado puede ser invariante. Se predice cada caso con cada modelo de fold, sin usarlos para entrenar o retocar la variante. Los folds no son repeticiones independientes. Pasar esta batería no prueba generalización.

## Trazabilidad y reproducción

Protocolo JSON previo con hashes de entradas, particiones, código y este documento. Salidas nuevas, nunca sobrescritura de resultados congelados. Registrar tiempos en archivo separado de CSV deterministas. Repetición en una carpeta temporal para comparar predicciones, métricas, asignaciones y vistas; comprobar hashes de fuentes/modelo y ejecutar tests excluyendo expresamente el antiguo test que reabre referencias humanas.
