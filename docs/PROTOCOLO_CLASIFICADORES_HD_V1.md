# Comparación de clasificadores H/D v1 — protocolo previo

## 1. Autorización, objetivo y límite de ejecución

2026-09-16: el usuario autoriza pruebas y exige mantener todo limpio, tras expresar preocupación por el bajo reconocimiento humano de H y D. Esta es una ronda nueva, no una modificación de las anteriores.

**Objetivo:** comparar alternativas ejecutables con énfasis en H/D, penalizando también las falsas alarmas direccionales sobre neutrales. No afirmar que resultados contra IA prueben mejora contra personas.

**BETO no ejecutable en esta sesión:** sin GPU detectada, dos CPU lógicas, aproximadamente 3,8 GiB de RAM, ningún checkpoint local. La petición Python al `config.json` de `https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased/resolve/main/config.json` falló con `URLError: TLS/SSL connection has been closed (EOF)`. PyPI sí respondió. El README oficial https://github.com/dccuchile/beto remite a Hugging Face; no se obtuvo ningún peso. No se instalarán bibliotecas grandes sin poder adquirir el modelo. Esto es un bloqueo de infraestructura, **no un resultado negativo de BETO**. Su repositorio declara intención CC BY 4.0 con reservas sobre licencias de las fuentes de preentrenamiento.

Se informó al usuario antes de ajustar: se compararán SVM, palabras/caracteres y clasificación jerárquica. **Ninguno de estos métodos es un transformer contextual**. No se importan FinancES, otros datos financieros ni más traducciones WCB en esta ronda.

## 2. Datos, control de copias y separación

Reutilizar las mismas 1.352 IA y los cinco folds por reunión de scripts 21–22: 793 intervenciones de validación y 559 inicialmente solo de entrenamiento. Sin abrir ni predecir las 306 respuestas humanas; tampoco leer su Excel para diagnósticos. Sin reajuste final ni scoring del corpus completo.

Para cada fold, construir una versión **purgada** de train: retirar toda fila cuyo texto coincida con alguno de validación después de normalizar espacios, minúsculas y acentos. No utilizar etiquetas de validación para decidir exclusiones; no borrar filas de L0 ni anotaciones. Conservar todas las 793 filas de validación, incluso sus repeticiones internas. Algunos de los 559 fijos pueden salir de train por esta regla. Verificar reuniones y claves textuales disjuntas; registrar cada exclusión por ID/fold/hash de texto y los tamaños antes/después.

No usar este control como prueba de ausencia de equivalencias semánticas, plantillas o contaminación previa de selección. Continúa siendo desarrollo adaptativo conocido, con folds que comparten entrenamiento y posibles repeticiones dentro de train/validación. No hay nuevo test independiente.

## 3. Variantes cerradas antes de medir

| Código | Train | Modelo B | Representación B |
|---|---|---|---|
| H0_historica | Original | Regresión logística histórica | Palabras 1–4 |
| B0_limpia | Purgado | Misma regresión logística | Palabras 1–4 |
| B1_svm | Purgado | LinearSVC | Palabras 1–4 |
| B2_lr_mixta | Purgado | Regresión logística | Palabras 1–4 + caracteres 3–5 |
| B3_svm_mixta | Purgado | LinearSVC | Palabras 1–4 + caracteres 3–5 |
| B4_jerarquica | Purgado | LR neutral/direccional y luego LR H/D | Palabras 1–4 |

**H0 es únicamente ancla histórica**, no candidata a selección. Debe reproducir las 793 predicciones previas de (1,4). No comparar el 0,7803 histórico como si fuera la referencia limpia: calcular B0 nuevamente con la misma purga que todas las alternativas.

A (relevancia): unigramas/logística históricos; ajuste solo sobre train. A se comparte entre los cinco modelos limpios; H0 tiene su propia A con train original. B solo usa filas IA relevantes. A=0 sigue dando neutral final.

Palabras: parámetros históricos, ngram_range=(1,4), min_df=3, max_df=0,9, unicode/lowercase, sublinear_tf y L2. Sin reabrir búsqueda de longitud. Caracteres: `char_wb`, ngram_range=(3,5), los mismos min_df/max_df, sublinear_tf, unicode/lowercase, L2 y máximo 50.000 características (límite de recursos prefijado, no optimizado). En mixtas, concatenar ambos bloques de igual peso y aplicar L2 global; si ambos son no vacíos, equivale a escalar cada bloque por 1/√2. Vocabulario/IDF solo en train relevante, no en validación o ejemplos sintéticos. Caracteres pueden compartir raíces y variantes ortográficas, **no interpretan automáticamente negación, números ni causalidad**.

Logística: C=2, balanced, max_iter=2000 y semilla histórica 20260915. SVM: C=1, balanced, squared_hinge, penalización L2, dual=auto, max_iter=10000, tol=0,0001, random_state=20260915. Distintos C no son una búsqueda optimizada ni prueba exhaustiva de cada familia.

Jerárquica: puerta LR binaria entrenada con todas las relevantes para neutral vs H/D; segunda LR entrenada solo con H/D del train. Ambas C=2/balanced. Vocabulario e IDF compartidos aprendidos con todo train relevante. Usar `predict` sin ajustar umbrales: puerta neutral produce N, puerta direccional activa H/D. No determinar la puerta con la verdad de validación ni usar el modelo jerárquico solo en los casos que ya sabemos direccionales.

Sin calibración, combinadores aprendidos, cambios de etiquetas, ponderación externa ni modelos guardados. Una advertencia de convergencia detiene la ejecución; no silenciarla para declarar éxito.

## 4. Métrica principal y controles

**Principal nueva, prefijada por la preocupación H/D del usuario:** promedio entre folds de **(F1_H + F1_D)/2**, calculando precisión/recall sobre **todas** las intervenciones, de modo que predecir H/D sobre un neutral cuente como falso positivo. No es accuracy de un problema binario aislado ni probabilidad/confianza de cada predicción.

Secundarias: macro-F1 H/D/N medio y conjunto, DE entre folds, accuracy, precisión/recall/F1/soporte por clase, matrices, errores H↔D, N→dirección y dirección→N, errores corregidos/nuevos frente a B0 limpia. Acierto sobre H/D verdaderos: número de H/D correctamente identificados dividido por su soporte; una salida neutral en esos casos cuenta como error. Informar también media de recall H y D, para no ocultar desequilibrio.

Dos referencias ingenuas, aprendidas solo de train purgado: clase mayoritaria de tres clases y clase mayoritaria entre H/D. Ambas predicen de manera constante **sobre las 793 filas**, sin oráculo que conozca la verdad ni puerta A. La segunda suele fallar masivamente sobre neutrales, pero permite ver cuánto del acierto H/D viene solo del desbalance. No son candidatas. Una moneda H/D tiene 50% de acierto esperado sobre H/D verdaderos; no afirmar significación por superar 50%.

Batería conductual: los mismos 14 casos inventados ya usados y congelados en `representaciones_contextuales.py`, aplicada a los seis modelos de cada fold. 420 predicciones, no 420 ejemplos independientes. Es una batería **conocida**, no test nuevo. No ajustar métodos por sus respuestas. Reportar exactitud y los cuatro pares de invariancia, sin equiparar invariancia con corrección.

## 5. Regla de cierre

Ordenar candidatas por media F1 H/D, desempate exacto por orden B0/B1/B2/B3/B4. Elegir mayor media solo identifica el mejor observado. Para recomendar confirmación separada, la alternativa debe cumplir **todas**:

- Mejorar a B0 limpia por al menos 0,02 de media F1 H/D.
- Mejorar F1 H/D en al menos 3 de 5 folds.
- No perder más de 0,005 de media macro-F1 H/D/N.
- No perder más de 0,02 de recall conjunto en H ni en D.
- No perder más de 0,05 de exactitud en la batería conductual conocida.

Umbrales prácticos, no pruebas estadísticas. No sustituir la métrica tras resultados ni elegir una variante por un solo indicador favorable. No aumentar C, longitudes, pesos o variantes después de medir. Si ninguna cumple, cerrar sin adopción. Si alguna cumple, sigue pendiente confirmación independiente; no reemplazar automáticamente el modelo guardado.

## 6. Limpieza y reproducción

Un evaluador nuevo (`26_comparar_clasificadores_hd.py`), un archivo de pruebas, este protocolo y un informe generado. Preparación separada: hashes de código, tests, fuentes y asignaciones/exclusiones antes de `fit`. Ejecución exclusiva en carpeta nueva; verificar hashes al final. Solo conservar artefactos usados en auditoría/reproducción; no checkpoints, duplicados de datasets ni scripts vacíos de BETO.

Repetir en temporal y eliminarlo; comparar CSV, métricas e informe. Registrar tiempos por separado. Ejecutar tests omitiendo expresamente el antiguo que reabre referencias humanas. Verificar hashes de 177 archivos previos, además de los protegidos históricos y el modelo. No modificar experimentos cerrados para compartir código nuevo: se reutilizan utilidades versionadas compatibles y se mantienen intactos los hashes anteriores.
