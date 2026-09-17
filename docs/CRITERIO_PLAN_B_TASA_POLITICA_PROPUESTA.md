# Plan B centrado en tasa de política: criterio propuesto y segunda calibración

**17-09-2026. Propuesta para acuerdo, no aplicación al corpus ni cambio del codebook v2.** El investigador pide decidir el criterio antes de continuar y presenta 15 ejemplos de 1995–1999 extraídos por otro agente. La revisión se limita a los textos pegados, sin actas originales o anexos verificados.

## Criterio recomendado

**Orientación monetaria doméstica respaldada en la unidad textual completa**, no sentimiento económico, ranking entre consejeros, nivel absoluto de la tasa o mera aparición de “TPM”.

Para esta fase del plan B, filtrar decisiones, recomendaciones, sesgos y discusión sobre **la tasa que cumple la función de instrumento de política en Chile**, aunque se denomine tasa de instancia, tasa objetivo o corresponda a facilidades/interbancario que el propio texto vincula expresamente a la conducción monetaria. No recoger cualquier préstamo, tasa de mercado, sanción o tasa extranjera como una decisión del Banco Central.

Este alcance deliberadamente más acotado no niega que encajes o crédito dirigido puedan haber sido instrumentos monetarios históricos. Esos otros instrumentos quedan en una colección separada para una eventual ampliación de objetivo. Véase el borrador general `DEFINICION_POSTURA_MONETARIA_PROPUESTA_V1.md`, también sin aprobar/aplicar.

## Reglas mínimas para enviar al agente del plan B

1. **Primero relevancia, después dirección.** Una discusión sustantiva de política monetaria puede ser neutral y relevante (`N`, `es_relevante=1`). Las opciones sin preferencia, análisis de transmisión y expectativas del mercado no son formalidades solo por carecer de voto. Reservar `es_relevante=0` para unidades realmente ajenas al objetivo o puramente administrativas.
2. **H:** alza/retirada de estímulo elegida, recomendada o respaldada; sesgo futuro al alza; o rechazo sustantivo de mayor relajamiento por defender evitar estímulo excesivo. No basta ser más conservador que otra persona.
3. **D:** baja/mayor estímulo elegida, recomendada o respaldada; sesgo futuro a la baja; o defensa sustantiva de sostener una orientación expansiva. No basta postergar un alza por una razón táctica u operativa.
4. **N relevante:** descripción o relato sin nueva adhesión, opciones sin elección, pregunta sin respuesta o mantención sin dirección respaldada. Si la unidad no permite identificar el instrumento/signo por falta de información o mezcla, marcar pendiente en lugar de asignar N de alta confianza.
5. **La dirección actual explícita prima.** Bajar 50 en vez de 70 pb sigue siendo D; subir 25 en vez de 50 sigue siendo H. Una baja actual con sesgo neutral posterior sigue siendo D. Registrar magnitud y sesgo futuro aparte; no mezclar cambio de tasa con comparación relativa al menú.
6. **Mantener requiere leer el contexto.** Mantener con sesgo al alza puede ser H; con sesgo a la baja, D; sin dirección, N. Negarse a un cambio no invierte mecánicamente la etiqueta: distinguir defensa sustantiva de una orientación de una espera operativa o temporal.
7. **Historia y expectativas ajenas no equivalen a postura actual.** Conservar como información auxiliar la dirección del episodio relatado, si interesa, pero no usarla como etiqueta del pronunciamiento actual sin respaldo explícito. No convertir todas las recapitulaciones de bajas en D.
8. **No reparar texto automáticamente para etiquetar/entrenar.** Usar `texto_original`, cita literal ≤300 caracteres y procedencia. `texto_corregido` puede conservarse como sugerencia auxiliar con diff y cotejo de fuente, no sustituir el original sin validación. No completar faltantes, tasas, beneficiarios o signos por intuición.

Son reglas de sesgo comunicado, **no una clasificación mecánica del cambio numérico**: por ello una oposición razonada a más estímulo puede ser H aun manteniendo la tasa. Si se eligiera en cambio una tarea estricta de subir/mantener/bajar, toda mantención sería cero y esa sería otra variable. Se recomienda no mezclar ambos criterios dentro de la misma columna.

## Segunda calibración por ID (orientativa, no anotaciones importadas)

| ID | Lectura recomendada bajo el criterio | Relevancia | Corrección/precaución |
|---|---|---|---|
| 21716 | D, alta | 1 | Decisión explícita de relajar y reducir 5,2→5 anual sobre UF. No es una tasa nominal en pesos; conservar tipo de tasa. La cita suministrada tiene 291 caracteres y cumple el límite de 300; no necesita recorte |
| 21910 | N como pronunciamiento actual de relato, con D histórico auxiliar | 1 | Relata decisiones de 1994 y evolución posterior; no formula una nueva preferencia para septiembre1995. D alta correspondería a clasificar el episodio relatado, una tarea distinta |
| 22078 | H, alta | 1 | Declara consolidar/profundizar restricción y objetivo interbancario. Separar el acuerdo posterior sobre canasta de monedas y cierre de sesión |
| 27863 | H, alta | 1 | Propuesta de subir 7→8,5 anual sobre UF. Registrar que es propuesta, no resolución final |
| 27867 | H, alta | 1 | Decisión explícita de elevar el objetivo 150pb. Pertenece al mismo evento que27863: agrupar por acta/reunión, no dividir entre train/validación |
| 29595 | Pendiente de segmentación/dirección | 1 para el contenido sustantivo | No es solo apertura: anuncia cambios de tasa, banda y encaje. La parte ceremonial es separable. No deducir el signo de la tasa al “acercarse al mercado” ni resolver por intuición la inconsistencia encaje cambiario/bancario |
| 30704 | D para el acuerdo de reducción | 1 | Tanto70 como50pb son bajas. Serrano no sería H solo por preferir50. Separar intervenciones si la unidad es por actor; evitar atribuir toda la discusión a una persona |
| 31369 | N, alta, como opciones sin preferencia resuelta | **1, no0** | Discute directamente la tasa de política: la ausencia de elección no lo vuelve irrelevante |
| 31429 | D, alta | 1 | Comunicado explícito de reducción 50pb. Aislar el comunicado si se usa unidad institucional y no mezclarlo con discusión de otros actores; conservar el final incompleto como tal |
| 31986 | H, media defendible | 1 | Por rechazo explícito a nuevo estímulo considerado excesivo, no por votar contra la mayoría. `accion_actual=mantener`, `sesgo=oposicion_relajamiento`. No llamar alza a esa decisión |
| 32169 | N, alta | **1, no0** | Describe mercados/tasa de instancia y transmisión; no hace propia la trayectoria de los precios de mercado |
| 32179 | D, alta | 1 | Respalda la reducción actual. No contemplar nuevas rebajas no revierte la dirección del recorte. Cita más corta y literal |
| 32531 | N, alta | **1, no0** | Análisis de mercados internos/externos y agregados para la discusión monetaria, sin recomendación propia. No convertir el alza esperada de la Fed en H chilena |
| 33553 | N, media provisional; no D alta | 1 | Defiere la revisión por el cambio de milenio y reconoce una corrección futura imprecisa. No inferir D solo por mantener frente a un alza hipotética; si el contexto aclarara una trayectoria de subida respaldada habría que revisarlo, no asumirlo |
| 33554 | N, alta | 1 | Acuerdo de mantención sin sesgo expresado en esta unidad. No heredar motivos/dirección de33553 |

Las reservas de31986/33553 requieren que se cierre explícitamente la regla sobre oposición sustantiva frente a espera operativa. No son aprobaciones humanas ni una nueva referencia usada en métricas; no se cuentan para300.

## Otros problemas de formato y unidad

- No usar `es_relevante` como sinónimo de `etiqueta != neutral`: eliminaría los N relevantes que el modelo debe aprender a distinguir de H/D.
- Un párrafo que empieza con asistentes puede contener después contenido sustantivo, como29595. No decidir por el comienzo.
- En30704 aparecen varios hablantes; en22078 se incorpora otro acuerdo. Definir si se estudia cada intervención o la decisión institucional de un asunto antes de generar filas.
- Mantener una ID de acta/reunión común para todos sus fragmentos y controlar casi copias. Propuesta y resolución del mismo evento no son dos eventos independientes.
- El texto corregido no siempre cambia solo tildes: en30704 se sustituye “gasto agregado a la actividad” por “gasto agregado y la actividad”. Puede ser una corrección razonable, pero necesita cotejo; no se valida por parecer más fluida.
- Separar magnitud de tasa, indexación UF, periodicidad y tipo de instrumento. No comparar un nivel real/UF con otro nominal para inferir postura.

## Estado y siguiente paso

La extracción nueva está mejor alineada con una tarea centrada en tasa de política que la mezcla de ayudas/multas/regulación anterior. Aun así, **no está aprobada para incorporarla al plan A**. Primero acordar estas reglas y calibrar con ejemplos completos, preservando sus fuentes. El codebook v2, la validación y los datos/modelos existentes permanecen intactos. El investigador pidió detener la continuación hasta aclarar este criterio; no se lanzó ningún entrenamiento ni nueva anotación del plan A en esta consulta.


## Tercera salida de calibración: mejoras y pendientes

El investigador presentó una salida revisada sin `texto_corregido`: corrige N relevantes a relevancia1 (incluidos31369/32169/32531),21910a relatoN, evita tratar la baja de50frente70comoH, y reduce confianza de33553. Son avances de coherencia con la propuesta, no validación independiente ni importación al corpus.

Pendientes antes de aceptar esa salida como anotaciones listas:

- **29595:** relevancia1 está mejor, pero Nalta no se justifica por ausencia de voto. El texto propone/anticipa medidas y dice que parece oportuno adoptarlas hoy. Las recomendaciones también cuentan. Separar apertura y asuntos sustantivos; si la dirección no se puede identificar, dejar pendiente y fuera del entrenamiento, no neutralidad segura. No resolver por intuición la diferencia encaje cambiario/bancario.
- **31986:** Hmedia es defendible por oposición a estímulo que considera excesivo, pero la nota sigue usando una regla de H relativo al menú. Retirar esa justificación automática. La cita contiene `[...]`, que no es una subcadena literal del original: usar un fragmento continuo, como el voto final, o campos separados si se diseñan varias citas.
- **N relevantes:**21910/31369/32169/32531 aparecen sin cita. La regla de evidencia literal también se aplica a N con relevancia1: una cita puede documentar que se describen mercados, se relata historia o se presentan opciones, y la nota explica la ausencia de orientación tras leer el conjunto.
- **33553:** no afirmar simultáneamente que hay un sesgo al alza declarado e inequívoco y que no hay dirección. Expresar la ambigüedad: referencia a una corrección eventual y postergación operativa sin trayectoria suficientemente especificada. Si realmente se verificara una subida futura respaldada, mantener hoy no la neutralizaría. Nmedia sigue siendo provisional, no una regla de “postergar siempre=N”.
- **27863:** es una propuesta del Gerente, suficiente para una lectura H; no afirmar por ello que el Consejo ya la adoptó.
- **21716:** se verificó el largo de la cita pegada: **291 caracteres**, válido. La sugerencia previa de acortarla no era necesaria y queda corregida aquí.
- Persisten asuntos/unidades mezclados en22078/30704/31429. Preservar actor/tipo de acto y relación con el acta. No completar finales truncados.

No se añadieron datos, modificaron etiquetas históricas ni se entrenó un modelo con esta salida.

## ¿Esto invalida las anotaciones originales IA y humanas?

**No hay base para afirmar que todas estén mal, ni se ha comprobado que todas sean compatibles con los afinamientos.** La pregunta se refiere a las1.352anotaciones IA originales y a las306humanas, no solo a la ampliación89. No se ha hecho una revisión completa de esas colecciones bajo otra definición; no se conoce la cantidad que cambiaría y no se han reabierto las306respuestas.

Hay que distinguir:

1. **Aplicación inconsistente de reglas ya vigentes**, como confundir N relevante con irrelevante: puede requerir corrección de casos concretos.
2. **Cambio de variable o de definición**, como clasificar orientación de un episodio relatado frente a postura respaldada en el pronunciamiento: una etiqueta puede ser válida para la primera tarea y no para la segunda. No se declara un error del anotador por cambiar después el objetivo.
3. **Error del modelo**, que no implica error de referencia: los atajos léxicos ya diagnosticados son un problema distinto.

El agente debió distinguir mejor estas situaciones al explicar la necesidad de revisión. Los originales humanos se conservan como referencia histórica, no se anulan ni se sobrescriben. Cualquier auditoría/migración requiere alcance y reglas fijadas, preservación de decisiones y separación del efecto de recodificar referencias frente a reentrenar. Esta consulta no autoriza una reclasificación masiva ni abrir el examen humano antiguo.
