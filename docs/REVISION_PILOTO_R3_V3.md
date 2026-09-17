# Revisión v3 — piloto r3

**Fecha:** 17-09-2026  
**Archivo:** `data/etiquetas/etiquetas_piloto_r3.csv`  
**Alcance:** 85/85 intervenciones, incluidas H, D, N y relevancia.

## Resultado frente a v2 vigente

| Resultado | Casos |
|---|---:|
| Compatibles | **85** |
| Cambios de etiqueta | 0 |
| Cambios de relevancia | 0 |
| Pendientes | 0 |

La distribución permanece en 8 D y 77 N, de las cuales 29 tienen relevancia0.

## Controles semánticos

Las ocho D contienen recortes elegidos, mayor estímulo respaldado, inicio o continuación explícita de un ciclo de reducción, o apoyo de la política a la recuperación. El caso `5699:3`, aunque usa “ajustes” en su frase central, pertenece a un comunicado institucional que vincula esos ajustes con desaceleración, inflación subyacente baja y la trayectoria de flexibilización; se conserva D leyendo la unidad completa, no por la palabra aislada.

Se revisaron las 77 N. Permanecen N las mantenciones sin sesgo, opciones sin preferencia, trayectorias o expectativas ajenas, exposiciones técnicas, diagnósticos y preguntas. No se convirtió en H/D una descripción de políticas expansivas extranjeras ni una expectativa de recorte del mercado.

Los 29 N/relevancia0 son encabezados, formalidades, ofrecimientos de palabra, saludos o fragmentos sin contenido autónomo evaluable. No se detectó un cambio de relevancia.

## Evidencia y límites

La revisión completa está en `data/auditoria/revision_etiquetas_piloto_r3_v3/revision.csv`, con v2/v3, cita, fundamento, confianza y hash. Se cotejaron 85 IDs, citas/vacíos permitidos y hashes contra L0. Las etiquetas eran visibles y la revisión fue realizada por el agente, no por un segundo anotador ciego.

El lote queda cerrado con cero pendientes. El avance acumulado es **360/1.747** y quedan **1.387 IDs**. No se entrenó ni se sobrescribió v2.
