# Cierre de revisión humana v3

**Fecha:** 17-09-2026  
**Criterio:** [`codebook_v3.md`](codebook_v3.md), dirección monetaria doméstica respaldada.  
**Alcance:** las 306 respuestas de `gold_ciego_300_listo.xlsx`, revisadas con la etiqueta humana visible y contra la intervención completa de `data/L0/corpus.csv`.

## Resultado

| Control | Resultado |
|---|---:|
| IDs revisados / únicos | 306 / 306 |
| Compatibles sin cambio | 277 |
| Cambios de etiqueta | 28 |
| Cambios de relevancia | 1 |
| Pendientes | 0 |
| Etiquetas humanas v2 | H49 / D32 / N225 |
| Etiquetas humanas v3 | H39 / D27 / N240 |
| Relevancia humana v2 | 265 sí / 41 no |
| Relevancia humana v3 | 266 sí / 40 no |

Las transiciones de etiqueta fueron: H→N 12, D→N 7, D→H 3, H→D 2, N→D 3 y N→H 1. No se modificó el libro original, `comparacion_gold.csv`, L0, la referencia v2, los folds ni modelos. Tampoco se entrenó.

## Correcciones

- **H→D:** `RPM-2014-03-13:6107:1` (sesgo explícito a la baja); `RPM-2014-01-16:6000:1` (próximo movimiento y sesgo a la baja).
- **N→D:** `RPM-2008-12-11:2254:1` (el comunicado institucional anuncia relajamiento); `RPM-2009-08-13:2682:1` (respalda una baja marginal, prolongar la TPM mínima y mayor expansividad); `RPM-2009-12-15:2833:1` (defiende estímulo suficiente y mecanismos adicionales).
- **D→H:** `RPM-2009-12-15:2838:1` (normalización futura propia); `RPM-2005-12-13:523:1` (la mantención eleva la tasa real y avanza la normalización); `RPM-2006-01-12:570:1` (preserva una trayectoria futura de alzas).
- **N→H:** `RPM-2010-05-13:3120:2` (afirma que será necesario iniciar normalización gradual).
- **H→N:** `RPM-2006-06-15:732:1`, `RPM-2013-07-11:5699:2`, `RPM-2006-11-16:986:1`, `RPM-2012-04-17:4784:2`, `RPM-2013-12-12:5962:1`, `RPM-2013-09-12:5812:2`, `RPM-2015-01-15:6581:1`, `RPM-2015-01-15:6582:1`, `RPM-2007-10-11:1515:1`, `RPM-2012-06-14:4898:1`, `RPM-2011-07-14:4205:1` y `RPM-2013-07-11:5694:1`. Son mantenciones, pausas, acuerdos institucionales sin sesgo, eliminación de un sesgo alcista o diagnósticos sin dirección propia.
- **D→N:** `RPM-2007-06-14:1302:1`, `RPM-2012-08-16:5027:1`, `RPM-2015-05-14:6806:2`, `RPM-2010-03-18:3018:1`, `RPM-2013-04-11:5500:1`, `RPM-2012-10-18:5146:1` y `RPM-2007-04-12:1200:1`. Son mantenciones/esperas sin sesgo, balance de ambas direcciones o riesgo macroeconómico sin respuesta monetaria respaldada.
- **Relevancia 0→1, N sin cambio:** `RPM-2011-04-12:3955:1`; el análisis de swaps y compensación inflacionaria es contexto monetario sustantivo aunque no tenga dirección.

Las razones y citas literales individualizadas están en `data/auditoria/revision_humana_v3/revision.csv`. Las 306 decisiones —incluidos los compatibles— están explicitadas en `decisiones.json` para demostrar cobertura y no solo registrar errores.

## Procedimiento y controles

1. Se extrajo reproduciblemente la hoja OOXML mediante `scripts/extraer_gold_humano.py`, sin `openpyxl`. La extracción conserva 306 IDs y las 16 columnas del libro. Los textos de las 306 filas coinciden con L0 tras normalizar espacios; 293 coinciden también byte a byte y 13 difieren solo en espacios.
2. Se priorizaron las 81 etiquetas H/D, las 33 respuestas de confianza humana media y los N con lenguaje de voto, recomendación, sesgo, normalización, relajamiento o estímulo. También se revisaron los demás N y las 41 filas originalmente irrelevantes.
3. Toda fila relevante v3 tiene una cita continua literal de hasta 300 caracteres verificada contra L0: 266/266. Todos los registros tienen hash del texto y estado cerrado.
4. El protocolo incluye hashes del XLSX original, la extracción, L0, decisiones, referencias v2 y codebook. El manifiesto fija los archivos resultantes.
5. La migración quedó en **1.747/1.747 revisados y 0 pendientes**.

## Límite de evaluación

Esta capa es una **revisión humana visible asistida por el agente bajo v3**, no una segunda anotación independiente ni un test ciego. La referencia humana v2 se conserva para reproducir resultados históricos. Cualquier evaluación futura debe declarar que la capa humana v3 fue revisada después de abrir las respuestas y separar el efecto de recodificar referencias del efecto de cambiar la supervisión o el modelo.
