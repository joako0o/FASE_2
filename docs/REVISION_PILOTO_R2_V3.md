# Revisión v3 — piloto r2

**Fecha:** 17-09-2026  
**Archivo:** `data/etiquetas/etiquetas_piloto_r2.csv`  
**Alcance:** 88/88 intervenciones, incluidas H, D, N y relevancia.

## Resultado frente a v2 vigente

| Resultado | Casos |
|---|---:|
| Compatibles | 87 |
| Cambios de etiqueta | **1** |
| Cambios de relevancia | 0 |
| Pendientes | 0 |

### Cambio

`RPM-2011-08-18:4272:1`: **D → N**, confianza alta.

La unidad mantiene la TPM y propone quitar el sesgo restrictivo para recuperar flexibilidad ante escenarios futuros. No respalda una baja ni establece un sesgo expansivo. Bajo v3, retirar una señal H no produce automáticamente D: sin dirección propia posterior, corresponde N.

## Distribución

| Versión | H | D | N |
|---|---:|---:|---:|
| V2 vigente | 5 | 5 | 78 |
| V3 | 5 | 4 | 79 |

## Controles semánticos

Se conservaron como D las unidades que respaldan impulso adicional, mantener condiciones expansivas o un próximo movimiento a la baja. Se conservaron como H votos de alza y sesgos explícitos al alza. Las trayectorias de modelos, expectativas de terceros, diagnósticos, preguntas y mantenciones sin dirección permanecen N.

Los 24 casos N/relevancia0 son encabezados, formalidades, ofrecimientos de palabra o fragmentos sin contenido autónomo suficiente; no se detectó contenido monetario sustantivo que justificara elevar relevancia.

## Evidencia y límites

La revisión completa está en `data/auditoria/revision_etiquetas_piloto_r2_v3/revision.csv`, con v2/v3, cita, fundamento, confianza y hash. Se cotejaron 88 IDs, citas/vacíos permitidos y hashes contra L0. Las etiquetas eran visibles y la revisión fue realizada por el agente, no por un segundo anotador ciego.

El lote queda cerrado con cero pendientes. El avance acumulado es **275/1.747** y quedan **1.472 IDs**. No se entrenó ni se sobrescribió v2.
