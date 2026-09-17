# Revisión v3 — escalados r11 a r17

**Fecha:** 17-09-2026
**Archivos:** `data/etiquetas/etiquetas_escalado_r11.csv` a `etiquetas_escalado_r17.csv`
**Alcance:** 414/414 intervenciones, incluidas H, D, N y relevancia.

## Resultado frente a v2 vigente

| Lote | Revisadas | Compatibles | Cambios de etiqueta | Cambios de relevancia |
|---|---:|---:|---:|---:|
| r11 | 110 | 108 | 2 | 0 |
| r12 | 54 | 53 | 1 | 0 |
| r13 | 58 | 57 | 1 | 0 |
| r14 | 56 | 56 | 0 | 0 |
| r15 | 71 | 69 | 2 | 0 |
| r16 | 58 | 56 | 2 | 0 |
| r17 | 7 | 7 | 0 | 0 |
| **Total** | **414** | **406** | **8** | **0** |

Las transiciones son 6 D→N y 2 D→H. La distribución conjunta pasa de 35 H/35 D/344 N a 37 H/27 D/350 N.

## Correcciones

Se reclasificaron D→N seis mantenciones que no adoptan dirección futura: los dos casos de septiembre de 2011 (`4329:1`, `4333:1`), `6854:1`, `1566:1`, `4332:1` y `979:1`. Incluyen acuerdos de mantención desnudos, mantenciones con sesgo neutral y espera por información. Ninguno sostiene una orientación expansiva.

Los casos `RPM-2006-05-11:671:1` y `RPM-2006-03-16:621:1` pasan D→H: ambos hacen propia la normalización monetaria y prefieren una pausa por gradualidad o razones tácticas. Pausar dentro de una trayectoria de alzas respaldada no invierte su dirección.

Se conservaron D los recortes actuales, los sesgos explícitos a la baja, la mantención prolongada de estímulo y las defensas sustantivas de no endurecer. Se conservaron H las alzas, sesgos al alza, retiros de estímulo y rechazos sustantivos de relajar. Las mantenciones sin dirección y los menús sin preferencia permanecen N. Todos los N/relevancia0 fueron revisados y corresponden a formalidad, logística o unidades fuera del objetivo sin orientación monetaria.

## Cierre de la IA base

Con estos siete lotes quedan revisados los **1.352/1.352 IDs de las 19 rondas IA originales**. Permanecen por revisar las 89 anotaciones IA nuevas y las 306 humanas. Las respuestas humanas están autorizadas para revisión, pero cualquier referencia v3 resultante no será presentada como test ciego intacto.

La evidencia por ID está en `data/auditoria/revision_etiquetas_escalado_r11_v3/` a `revision_etiquetas_escalado_r17_v3/`, con decisiones, citas, fundamentos, confianza, procedencia y hashes. Las etiquetas eran visibles; no fue una segunda anotación ciega. No hubo entrenamiento ni sobrescritura de originales.
