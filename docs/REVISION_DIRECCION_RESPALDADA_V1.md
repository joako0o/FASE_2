# Revisión dirigida de H/D bajo el criterio de dirección respaldada

> **Superada por el cierre de 77 filas:** consultar `REVISION_RONDAS_PRIORITARIAS_V3.md`. Esta primera pantalla comparó las 29 H/D con la etiqueta IA de sus archivos de origen. El cierre posterior compara correctamente con la referencia v2 vigente —que ya había corregido 976:1 y 2238:1— e incorpora las 48 N.

**Fecha:** 17-09-2026  
**Estado:** auditoría de compatibilidad; no adopta un codebook, no modifica etiquetas y no entrena modelos.

## Pregunta

¿Las etiquetas de las dos rondas prioritarias son compatibles con el criterio propuesto en `CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md`, que define H/D por la dirección monetaria que la unidad adopta o respalda y no por su posición relativa frente al menú o la fase?

## Alcance real

Las rondas `etiquetas_r13_tanda09.csv` y `etiquetas_r14_tanda10.csv` contienen 77 filas: 18 H, 11 D, 38 N relevantes y 10 N no relevantes. Esta revisión adjudica las **29 etiquetas H/D** contra sus intervenciones completas en L0. Las etiquetas eran visibles: no es doble anotación ciega ni revisión humana independiente.

Las 48 etiquetas N no se adjudicaron exhaustivamente para buscar falsos N. Por tanto, el resultado demuestra incompatibilidad dentro de H/D, pero todavía no mide todos los cambios posibles de las 77 filas.

## Resultado

| Resultado | Casos |
|---|---:|
| Etiqueta H/D compatible con el criterio propuesto | 18 |
| Cambio propuesto | **11** |
| Total H/D revisado | **29** |

Transiciones propuestas:

| De → a | Casos |
|---|---:|
| D → N | 6 |
| D → H | 2 |
| H → N | 2 |
| H → D | 1 |

De los 11 cambios, siete se consideran de confianza alta y cuatro de confianza media. La concentración es asimétrica: cambiarían 8 de las 11 D revisadas y 3 de las 18 H. **Eso no es una tasa de error extrapolable**, porque estas dos rondas fueron priorizadas precisamente por conservar convenciones relativas documentadas.

## Cambios propuestos por ID

| ID | v2 | Propuesta | Confianza | Razón abreviada |
|---|---|---|---|---|
| RPM-2005-12-13:525:1 | D | H | media | Pausa hoy, pero respalda conservar la política gradual de alzas; no corresponde D por comparación con una sexta alza inmediata. |
| RPM-2006-05-11:672:1 | D | H | media | Evita acelerar la normalización, pero hace propio un escenario de aumentos posteriores. |
| RPM-2006-06-15:737:1 | D | N | alta | Mantiene por asimetría del costo de error, sin respaldar expansión ni sesgo futuro a la baja. |
| RPM-2006-09-07:867:1 | D | N | alta | El staff justifica mantener y declara que los riesgos no dan un sesgo claro. |
| RPM-2006-10-12:936:1 | D | N | alta | Cambia de sesgo al alza a escenario de mantención; retirar H no equivale a respaldar D. |
| RPM-2006-11-16:976:1 | D | N | alta | Descarta subir y bajar hoy; el signo futuro se declara incierto. |
| RPM-2006-11-16:984:1 | D | N | alta | Mantiene y propone maniobra futura en cualquier dirección. |
| RPM-2007-01-11:1054:1 | H | D | media | Posterga el recorte, pero considera justificada y prepara una reducción futura; esperar para bajar luego no es H relativo. |
| RPM-2007-02-08:1102:1 | H | N | alta | Mantiene y pide explícitamente un comunicado neutral, sin curso futuro. |
| RPM-2007-04-12:1218:1 | H | N | media | Mantiene para acumular antecedentes; la preocupación inflacionaria no se conecta con una orientación restrictiva propia explícita. |
| RPM-2008-05-08:1848:1 | D | N | alta | Mantiene y declara riesgos balanceados y sesgo neutral. |

El detalle auditable —cita, fundamento, nota original, archivo y hash del texto— está en `data/auditoria/revision_direccion_respaldada_v1/revision_29_hd.csv`.

## Casos que sí permanecen compatibles

Se conservan 15 H y 3 D. Los H contienen alzas elegidas/recomendadas, acuerdos de alza o un sesgo de normalización respaldado. Preferir una subida de 25 frente a 50 pb no cambia H, y votar una subida contra una mantención mayoritaria tampoco. Los tres D compatibles respaldan mayor impulso, una baja o un ciclo futuro de reducciones; no dependen únicamente de ser “menos duros” que otra opción.

## Dictamen

**Sí: estamos mezclando criterios en una parte material de estas anotaciones.** Las etiquetas relativas no son plenamente compatibles con la definición direccional propuesta. Esto confirma un problema real, no solo una diferencia de redacción.

Pero el dictamen no autoriza afirmar que todas las 1.352 IA o las 306 humanas estén mal:

- la muestra priorizada no es representativa;
- faltan revisar los N para detectar dirección omitida;
- faltan buscar las mismas familias en las otras 17 rondas;
- no se abrieron ni reevaluaron respuestas humanas;
- el criterio usado sigue siendo una propuesta y no un codebook v3 aprobado.

## Siguiente decisión recomendada

1. Aprobar o rechazar explícitamente la definición direccional como nueva versión del codebook.
2. Si se aprueba, terminar las 48 N de estas rondas y extender la auditoría por familias a las otras rondas y a las 89 incorporaciones nuevas.
3. Guardar toda recodificación en una capa nueva, preservando v2.
4. Evaluar por separado el cambio de referencia y el reentrenamiento; no presentar una mejora causada por nuevas etiquetas como mejora del clasificador.

No se modificaron `data/etiquetas`, referencias v2, folds, resultados, modelos ni el gold humano.
