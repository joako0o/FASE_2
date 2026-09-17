# Cierre v3 de las dos rondas prioritarias

**Fecha:** 17-09-2026  
**Alcance:** 77/77 filas de `etiquetas_r13_tanda09.csv` y `etiquetas_r14_tanda10.csv`.  
**Regla:** `codebook_v3.md`, dirección monetaria respaldada; no postura relativa al menú o fase.

## Resultado frente a la referencia v2 vigente

| Resultado | Casos |
|---|---:|
| Compatibles | 65 |
| Cambio de etiqueta | **11** |
| Cambio solo de relevancia | **1** |
| Pendientes | 0 |
| Total | **77** |

Cambios de etiqueta:

| Transición | Casos |
|---|---:|
| D → N | 5 |
| D → H | 2 |
| H → N | 2 |
| H → D | 1 |
| N → D | 1 |

Además, `RPM-2008-03-13:1739:1` conserva N pero cambia `es_relevante` de 0 a 1: discute la comunicación de una consideración que el actor declara parte integral de su decisión monetaria. La dirección no puede heredarse de la intervención anterior, pero la unidad no es una formalidad vacía.

## Dos falsos N examinados

La revisión exhaustiva de las 48 N encontró dos unidades con orientación D respecto de la anotación IA original. Una de ellas ya estaba corregida en la referencia v2 vigente:

- `RPM-2007-04-12:1214:1`: **N → D** en v3, confianza media. El actor hace propio el juicio previo de que podría requerirse mayor impulso y cuestiona que haya fundamento adicional para mantener.
- `RPM-2008-12-11:2238:1`: la IA original decía N, pero la referencia v2 vigente ya dice D. V3 conserva D: el staff afirma que la discusión es sobre magnitud y momento del ciclo de relajamiento, no sobre su conveniencia en el escenario más probable.

Asimismo, `RPM-2006-11-16:976:1` era D en la IA original, pero ya era N en la referencia v2 vigente; v3 conserva N. Por eso el cierre compara siempre contra **v2 vigente**, sin volver a contar como nuevas las correcciones previamente aceptadas.

## Distribución del lote

| Versión | H | D | N |
|---|---:|---:|---:|
| V2 vigente | 18 | 11 | 48 |
| V3 | 17 | 6 | 54 |

La caída de D refleja principalmente pausas, eliminación de un sesgo al alza o mantenciones sin dirección que antes se interpretaban relativamente. No se utiliza esta distribución para ajustar cuotas ni mejorar una métrica.

## Evidencia y límites

Cada fila está en `data/auditoria/revision_rondas_prioritarias_v3/revision_77.csv` con etiqueta/relevancia IA original, v2 vigente y v3; cita, fundamento, confianza, archivo y hash del texto. Las 77 citas —o vacíos permitidos en formalidades irrelevantes— y los 77 hashes fueron verificados contra L0.

Las etiquetas fueron visibles y la revisión fue realizada por el agente, no por un segundo anotador ciego. El cierre corrige la capa v3 y preserva los archivos IA y referencias v2. No permite extrapolar una tasa de cambios a las otras rondas.

## Estado

Estas dos rondas quedan cerradas para v3: **77 revisadas, cero pendientes**. La migración total pasa de 29 a 77 revisadas y quedan 1.670 de 1.747 IDs. No se entrenó ni se modificaron resultados históricos.
