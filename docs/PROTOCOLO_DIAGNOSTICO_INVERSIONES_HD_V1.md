# Diagnóstico dirigido de inversiones H/D — protocolo previo

## Alcance autorizado

El usuario aceptó diagnosticar las 10 inversiones con referencias más claras y usar ese diagnóstico para preparar la comparación con un modelo contextual. No se adjudican etiquetas nuevas, no se optimizan n-gramas/umbrales, no se abre el examen de 306 ni se declara ejecutado BETO.

Selección exhaustiva desde las predicciones `seis_mas_trece` del experimento 36, frente a `etiqueta_corregida_v2`: 15 inversiones H↔D. Separar los cinco casos cuyo estado histórico de revisión es `ambigua`. Los diez restantes son nueve referencias respaldadas por el agente y una corrección N→D posteriormente aceptada (De Ramón, agosto de 2015). «Más claras» no significa verdad independiente o ausencia de matices; Marfán, marzo de 2008, requiere interpretar un paquete condicionado y un sesgo alcista.

Relectura completa de 40.937 caracteres, sin truncar las diez fuentes. Citas y lectura manual congeladas en `data/auditoria/inversiones_hd_v1/lecturas_agente.json` antes de obtener coeficientes o probar citas aisladas. Las opiniones son posteriores a conocer referencia/predicción.

## Reconstrucción e interpretación

Reconstruir los cinco folds de la supervisión `seis_mas_trece` con las mismas funciones/particiones/parámetros de 36/26. Validar las 793 predicciones A, B y finales, no solo las diez seleccionadas. No refit global ni persistencia de pesos. Un aviso de falta de convergencia detiene el ensayo.

Para cada uno de los diez casos, descomponer el margen lineal de B entre la clase predicha y la referencia corregida:

`margen = intercepto_pred − intercepto_ref + Σ TFIDF_j × (coef_pred,j − coef_ref,j)`.

Guardar todos los aportes activos, sus pesos, valor TF-IDF y frecuencias documentales en el train relevante por clase. Mostrar seis términos principales de cada signo y el residuo de los no mostrados. Verificar la igualdad contra decision_function con tolerancia 1e-9. La puerta A debe valer 1; conservar también scores de las tres clases para no ocultar N.

Las contribuciones explican algebraicamente la decisión del clasificador lineal. No identifican por sí solas el significado de una palabra, causalidad lingüística o qué ocurriría al borrarla: borrar cambia n-gramas y normalización L2. No sumar apariciones individuales como si fueran features independientes ni confundir coeficiente con aporte TF-IDF local.

## Sonda de evidencia aislada

Sin reajustar nada, introducir en B **solo la primera cita literal preseleccionada** de cada caso. Guardar la predicción y margen, sin puerta A. No unir citas ni escoger la mejor después de predecir. Contrastar cuánto aporta el texto completo frente a la evidencia corta.

Esto es una sonda post-predicción con selección manual informada por la referencia: **no es un extractor, una nueva validación, una mejora de modelo ni evidencia de que eliminar contexto siempre ayuda**. Si B falla también en la cita, la longitud no basta para explicar el error. Si acierta, no demuestra que un sistema pueda encontrar automáticamente esa cita.

## Salidas y controles

Script 37 con preparación previa, salidas exclusivas y replay temporal. Exportar selección, cinco excluidos, casos con textos completos y opiniones anteriores, todas las contribuciones, predicciones reconstruidas, resumen e informe; hashes de insumos/salidas. Los errores globales de 36 quedan congelados: 15 inversiones, 12 direccionales→N, 24 N→direccionales.

Pruebas de selección sin omitir/duplicar, separación de ambiguos, literalidad de citas, evidencia no truncada, descomposición exacta y residuo, coincidencia de 793 predicciones, sonda primera-cita y control de archivos/hashes. Reutilizar pruebas 31–36 sin ejecutar la suite histórica de 306. La reproducción demuestra consistencia del diagnóstico, no adjudicación independiente.

## Comparación contextual posterior: diseño, no ejecución

Conservar referencia v2, particiones purgadas y puerta A. Comparar B contextual con B TF-IDF, sin citas manuales como entradas o ventanas elegidas con las etiquetas. BETO debe cubrir toda la intervención, incluyendo su conclusión, mediante segmentos de hasta 512 tokens con solapamiento de 64 y agregación por intervención. El diseño de tres épocas, AdamW 2e-5 y pérdida por intervención de 31 sigue siendo punto de partida; no hay runner probado con pesos reales y el acceso a HF sigue bloqueado según 36.

Reportar matriz completa, H→D y D→H por separado, conteos y tasas sobre soportes fijos de H y D, H/D→N y N→H/D. No dividir solo por los casos predichos direccionales: un modelo que esconda toda duda en N no debe parecer mejor. Mantener F1 H/D como principal y macro-F1/recall H/D como guardas. Umbrales de desarrollo ya previstos: +0,02 F1 H/D medio y mejora en ≥3/5 folds, sin pérdida macro >0,005 ni recall H o D >0,02. Además, exigir reducción de inversiones sin aumentar H/D→N y mostrar ambos sentidos; estos requisitos se fijan antes de ejecutar el nuevo candidato.

Los diez casos y sus fenómenos son una batería conocida de diagnóstico, no un test nuevo ni diez ejemplos adicionales para entrenar. Ni cumplir los umbrales de desarrollo ni acertar sus citas demuestra generalización; para esa afirmación hará falta confirmación realmente nueva. No cambiar la arquitectura o las etiquetas repetidamente hasta acertarlos todos.
