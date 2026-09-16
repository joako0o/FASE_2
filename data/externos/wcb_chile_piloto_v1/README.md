# WCB Chile: muestra externa y traducción de desarrollo v1

## Atribución y licencia de estos datos

Fuente: Agam Shah, Siddhant Sukhani, Huzaifa Pardawala y colaboradores (2025), *Words That Unite The World: A Unified Framework for Deciphering Central Bank Communications Globally*.

- Dataset público: https://huggingface.co/datasets/gtfintechlab/central_bank_of_chile
- Revisión HF observada en API el 2026-09-16: `c1ead3f6011bbc358d3ef94b598238b78b7b45fa`.
- Repositorio: https://github.com/gtfintechlab/WorldCentralBanks
- Commit GitHub consultado: `70a90d3c004a8fdb6d74df9e88455a42c0654022`.
- Artículo: https://arxiv.org/abs/2505.17048
- **CC BY-NC-SA 4.0**, tanto los datos derivados de esta carpeta como su traducción. Texto legal en [LICENSE.txt](LICENSE.txt); resumen: https://creativecommons.org/licenses/by-nc-sa/4.0/ . No comercial; atribución y condiciones de compartir adaptaciones aplicables. No se pretende relicenciar el corpus original de FASE_2 ni todo su código con esta licencia. No se guardan modelos ajustados con estos datos.

## Qué contiene

`muestra.tsv`: las primeras **100 filas (0–99)** del **train** de la configuración **5768**. Selección determinista de conveniencia, no muestreo representativo nuevo ni selección por etiqueta. No ampliar después de ver métricas. Son 28 H / 30 D / 41 N / 1 irrelevant; se conservan todas las etiquetas originales. Se omite únicamente `irrelevant` del entrenamiento B, que tiene tres clases. A no se entrena con datos externos.

Endpoint de procedencia:

https://datasets-server.huggingface.co/rows?dataset=gtfintechlab%2Fcentral_bank_of_chile&config=5768&split=train&offset=0&length=100

La respuesta se consultó completa (cinco chunks de la herramienta de páginas; `partial=false`, 700 filas totales, ninguna celda de estas filas truncada). La extracción a TSV de `row_idx`, `__index_level_0__` renombrado `source_id`, `year`, `stance_label` y `sentences` renombrado `texto_en` fue realizada por el agente desde esa respuesta. **No es una descarga binaria del Parquet**. La salida local queda hasheada; permanece un riesgo de transcripción y la consulta al endpoint no está fijada por revisión, aunque el SHA de la ficha se registró en la misma sesión. No se afirma que un hash local verifique por sí solo equivalencia con el archivo remoto completo.

`texto_es` es una **traducción del agente IA en esta sesión**, no español oficial recuperado, ni traducción humana independiente. Se tradujeron las 100 frases completas, incluidas las ambiguas y fragmentarias, sin añadir recomendaciones ausentes ni corregir etiquetas. El traductor pudo ver las etiquetas, por lo que no fue ciego. Se conservó el orden de cifras y los decimales escritos en el original. MPR se traduce como TPM, governor como presidente y los nombres de encuestas se adaptan al español. No resolver pronombres trayendo contexto externo. En la fila 97 se conserva la ambigüedad de `mp`, sin inventar una tasa concreta.

Validaciones automáticas: 100 filas/IDs únicos y ordenados, no textos vacíos, etiquetas permitidas, ausencia de duplicados exactos normalizados dentro de la muestra, mismas secuencias de números/signos y porcentajes entre idiomas, y comparación de solape textual contra las 1.352 intervenciones IA. Estas validaciones **no certifican fidelidad semántica** ni calidad de las etiquetas.

## Particiones, idioma y límites

La ficha publica 700 train / 150 val / 150 test, y tres configuraciones por semilla. Solo se adquirieron estas 100 filas del train 5768. **No se auditaron exhaustivamente los solapes de las tres configuraciones ni se descargó/inspeccionó val o test.** No sumar semillas como ejemplos independientes. Ningún split externo se emplea para evaluar nuestro resultado.

El esquema publicado ofrece año e índice de fila, no enlace directo a una frase española. Los metadatos GitHub consultados señalan documentos de minutas en inglés; no se construyó alineación con los originales españoles. La traducción permite un piloto, no sustituye esa alineación. No se afirma que no existan versiones oficiales en español.

Criterios de postura distintos de nuestro codebook: por ejemplo, fila 66 (`source_id=217`) describe recesión en Argentina y tiene D; fila 32 (`434`) describe un alza de la Fed y tiene H; fila 1 (`921`) describe consumo débil y tiene D. Bajo R2/R3 no bastarían por sí solas para inferir postura sobre la TPM chilena. Es una incompatibilidad de tarea, no prueba de etiquetas globalmente invertidas. Se preservaron para probar transferencia **sin armonización**, nunca se incorporaron al directorio de anotaciones canónicas.

Revisión de traducción: lectura del agente de las 100 frases al traducir y control numérico automático. Sin adjudicación humana ni medición de exactitud de traducción. Resultados del piloto: [informe](../../../docs/EVALUACION_WCB_PILOTO_V1.md).
