# Revisión v3 — escalado r6

**Fecha:** 17-09-2026
**Archivo:** `data/etiquetas/etiquetas_escalado_r6.csv`
**Alcance:** 93/93 intervenciones, incluidas H, D, N y relevancia.

## Resultado frente a v2 vigente

| Resultado | Casos |
|---|---:|
| Compatibles | **88** |
| Cambios de etiqueta | **5** |
| Cambios de relevancia | 0 |
| Pendientes | 0 |

Transiciones: 4 N→H y 1 D→N. La distribución pasa de 5 H/1 D/87 N a 9 H/0 D/84 N.

## Correcciones

- `RPM-2005-03-10:179:1`, N→H: concuerda con las recomendaciones de normalización pausada; postergar el alza por táctica no elimina esa trayectoria propia.
- `RPM-2005-03-10:186:1`, N→H: respalda una reducción futura gradual del impulso, aunque rechaza convertirla en un precompromiso mecánico.
- `RPM-2005-03-10:193:1`, N→H: respalda señalizar el camino hacia una tasa neutral que describe por encima de la actual.
- `RPM-2005-03-10:196:1`, N→H: mantiene como estrategia una reducción gradual y pausada del pronunciado estímulo, aun si se hace una pausa inmediata.
- `RPM-2005-03-10:185:1`, D→N: cuestiona la certeza de los supuestos que justificarían alzas y pide revisar datos mes a mes, pero no adopta expansión ni trayectoria a la baja.

Se conservaron H los casos `:190:1`, `:192:1`, `:198:1` y `:200:1`, cuyas unidades completas respaldan retirar estímulo o proseguir una trayectoria restrictiva. Se mantuvieron N `:183:1`, `:194:1`, `:197:1` y `:199:1`: una pausa actual o el rechazo de un alza inmediata no bastan sin una dirección independiente adoptada. `:178:1` permanece H porque el diagnóstico hace propia la estrategia de normalización, aunque exponga mantener o subir como opciones del mes.

## Evidencia y límites

La revisión por ID está en `data/auditoria/revision_etiquetas_escalado_r6_v3/revision.csv`; las cinco decisiones que cambian v2 están declaradas en `decisiones.json`. Se verificaron IDs, citas literales tras normalizar espacios y hashes contra L0. Las etiquetas eran visibles y la revisión fue realizada por el agente, no por un segundo anotador ciego. El lote queda cerrado, sin entrenamiento ni sobrescritura de originales.
