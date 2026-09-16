# Protocolo previo: enriquecimiento con WCB Chile, piloto v1

Autorizado el 2026-09-16 («si puedes probarla bien»). Alcance comunicado: piloto de 100 frases train externas; no evaluación de las 700/1.000 completas. Documento, traducción y código congelados por hash antes del ajuste al corpus. No modificar traducciones/etiquetas/selección tras ver resultados.

## Pregunta

¿Añadir un pequeño conjunto de ejemplos WCB Chile con sus etiquetas originales mejora el TF-IDF (1,4) sobre nuestra validación IA? Comparación de desarrollo, no evaluación humana independiente ni predicción temporal prospectiva: incorpora texto 2018–2024 para analizar actas 2005–2015.

## Datos externos y tratamiento

100 primeras filas del train 5768 (índices 0–99), identificadas por su índice fuente. Muestra determinista de conveniencia, no diseñada por clase, y sin ampliación adaptativa. Se consultó la respuesta completa de la API por herramientas web y se capturaron las columnas necesarias; no afirmar descarga binaria independiente. Fuente/revisión/licencia y límites en [atribución](../data/externos/wcb_chile_piloto_v1/README.md).

Traducción al español del agente IA, no oficial ni ciega a etiquetas. Mantener pronombres, condiciones, tiempo y números, sin añadir un vínculo a Chile ausente. Conservar etiquetas WCB, incluidas las incompatibles con nuestro R2/R3, sin convertirlas en anotaciones v2. Es una prueba de transferencia sin armonización. El único `irrelevant` se excluye de B, dejando 99 ejemplos (28 H/30 D/41 N). No usar ninguno en A ni añadir columnas de temporalidad o certeza como rasgos. Nada se escribe en `data/etiquetas` ni en L0.

No usar ni inspeccionar val/test externos o las 306 referencias humanas. No auditar las otras semillas como si eso diera nuevas muestras. Verificar unicidad y números de las 100 filas; si se detectan duplicados exactos normalizados dentro de la muestra o respecto de los textos IA, detener antes de ajustar. Este control no demuestra ausencia de duplicados semánticos o de plantillas parecidas. La fuente externa no expone meeting_id por fila en estas columnas; no se inventa.

## Tres variantes, mismo problema y evaluación

1. **B0_base:** referencia texto completo TF-IDF n-gramas 1–4.
2. **E1_ingles:** referencia + 99 frases originales inglesas, control de importación sin resolver idioma.
3. **E2_espanol:** referencia + las mismas 99 frases traducidas al español.

A única por fold: unigramas, solo training IA. B: solo IA relevante, más los 99 externos cuando corresponde. Vocabulario/IDF aprendido con el train de cada variante, incluyendo externos; jamás con la validación. C=2, min_df=3, max_df=0,9, sublinear_tf=True, L2, class_weight=balanced, max_iter=2000 y semilla histórica. Peso individual externo=1, sin optimizar peso ni tamaño. Recalcular balanced con las clases de cada train: altera pesos también en E1, así que su resultado no es un control lingüístico puro. No contextualizador/híbrido v1, nuevo tokenizador, transformer ni más longitudes.

Cinco folds ya utilizados: 793 IA evaluadas y 559 siempre adicionales en train; mismo orden y reuniones. Las 34 repeticiones históricas permanecen documentadas. Mismos 99 externos adicionales en los cinco train, nunca en validación. B0 debe reproducir exactamente las predicciones anteriores de (1,4). A debe dar la misma salida en las tres variantes.

## Métricas y regla de cierre

Principal: media del macro-F1 H/D/N de salida A+B por fold. Secundarias: DE entre folds, macro-F1 conjunto, accuracy, precisión/recall/F1/soportes de cada clase, matrices, tipos de error y errores corregidos/nuevos frente a B0; tamaños de vocabulario, porcentajes de tokens/rasgos de validación presentes en vocabulario y pesos de clases. Estos diagnósticos no seleccionan otro método a posteriori.

Mayor media identifica mejor observado; empate exacto por orden B0, E1, E2. Para recomendar una confirmación adicional de la ampliación española: E2 debe superar B0 por ≥0,01 de media, mejorar ≥3/5 folds y no perder más de 0,02 de recall conjunto en H ni D. Umbrales prácticos, no significación. E1 es un control, no una alternativa a adoptar por ganar esta comparación. No adoptar ni hacer refit automáticamente en ningún caso.

Si E2 no mejora, la conclusión se limita a este piloto/tamaño/traducción/etiquetas/peso; no descarta WCB completo, otras traducciones o etiquetas armonizadas. No traducir más ni filtrar etiquetas después del resultado para perseguir mejora.

## Trazabilidad

Preparación separada con protocolo JSON, auditoría de externos y asignación por reunión; comprobar hashes antes y después del ajuste. Versiones de Python/librerías y fuentes congeladas. Guardar predicciones por ID/fold/variante, métricas, vocabularios y cobertura, y reporte; tiempos separados de las tablas deterministas. No persistir clasificadores ni cambiar el modelo anterior.

Repetir en temporal y comparar CSV/métricas/informe; ejecutar suite con omisión explícita de la prueba antigua que reabre respuestas humanas. Verificar fuentes históricas y modelo por hash. La repetición reproduce esta traducción guardada, **no valida independientemente su calidad semántica o la transcripción desde la API**.
