# CODEBOOK v3 — Dirección monetaria respaldada

**Proyecto D&H · Actas del Banco Central de Chile**  
**Aprobado por el investigador: 17-09-2026.** Sustituye v2 para nuevas anotaciones y para la revisión v3. V2, sus referencias y métricas se conservan como versión histórica.

## 1. Variable principal

> **Clasificar la dirección monetaria doméstica que una unidad textual completa adopta, recomienda o respalda para Chile: endurecimiento (H), expansión (D) o ausencia de dirección respaldada (N).**

La etiqueta no mide sentimiento económico, nivel absoluto de la tasa, sorpresa frente al mercado, distancia respecto de otra alternativa, posición frente a la mayoría ni resultado macroeconómico posterior.

Para el corpus 2005–2015 y el Plan B centrado en tasas, el objeto principal es la TPM o la tasa que el texto vincule expresamente con la conducción monetaria. Otros instrumentos históricos requieren función monetaria documentada y una extensión versionada; no se clasifican por el nombre del instrumento o por verbos aislados.

La unidad vigente del corpus 2005–2015 es la intervención completa. En corpus históricos con varios asuntos se preservan texto original, offsets, actor y reunión; una nueva segmentación debe versionarse.

## 2. Clases

### H — hawkish

La unidad adopta, recomienda o respalda:

- subir la tasa o retirar impulso monetario;
- un sesgo futuro al alza;
- sostener una restricción monetaria explícita;
- rechazar sustantivamente mayor relajamiento porque defiende evitar estímulo excesivo.

No basta ser más conservador que otra persona u opción.

### D — dovish

La unidad adopta, recomienda o respalda:

- bajar la tasa o ampliar el impulso monetario;
- un sesgo futuro a la baja;
- sostener una orientación expansiva explícita;
- rechazar sustantivamente mayor endurecimiento porque defiende preservar el estímulo.

No basta postergar un alza por razones tácticas u operativas.

### N — neutral

La unidad está dentro del objetivo y es evaluable, pero no revela dirección respaldada. Incluye:

- diagnóstico macroeconómico sin conexión con una orientación de política;
- opciones o escenarios sin preferencia;
- pregunta sin respuesta o expectativa ajena;
- relato histórico no adoptado en el pronunciamiento actual;
- mantención sin sesgo identificable;
- argumentos balanceados sin resolución direccional.

N no significa irrelevante.

## 3. Relevancia y estado de evaluación

`es_relevante=1` corresponde a contenido monetario o contexto sustantivo evaluable, incluso si la postura es N. `es_relevante=0` se reserva para formalidad, logística o contenido fuera del objetivo sin orientación ni contexto monetario doméstico.

La falta de información indispensable, el texto dañado o una unidad que mezcla asuntos/direcciones sin resolución se registra como `pendiente`, no como N de alta confianza ni como irrelevante forzado. Un pendiente queda fuera del entrenamiento supervisado hasta resolverse.

Toda fila relevante requiere una cita literal continua de hasta 300 caracteres; normalizar espacios no autoriza introducir elipsis o reparar OCR. La cita documenta la decisión tras leer la unidad completa, no reemplaza el texto de entrada.

## 4. Prioridad de decisión

1. **Identificar sujeto y acto.** Clasificar lo que hace propio el actor o la unidad institucional, no opiniones de terceros.
2. **Resolver objeto y función antes del signo.** Bajar una multa no es bajar la TPM; reducir estímulo es H aunque el verbo sea “reducir”.
3. **La acción monetaria actual explícita prima.** Subir 25 en vez de 50 sigue siendo H; bajar 50 en vez de 70 sigue siendo D.
4. **Mantener no tiene signo automático.** Mantener con sesgo al alza puede ser H; con sesgo a la baja, D; sin dirección, N.
5. **La orientación futura propia cuenta.** Esperar para subir luego puede ser H; esperar para bajar luego puede ser D. Una posibilidad incidental o trayectoria ajena no basta.
6. **Rechazar una acción no se invierte mecánicamente.** Debe existir defensa sustantiva de la restricción o del estímulo; esperar por información o por operación es N si no hay dirección propia.
7. **Una condición no elimina automáticamente la postura.** Si el actor respalda la respuesta bajo una condición identificada, conservar dirección y condición. Enumerar escenarios alternativos sin elegir es N.
8. **El diagnóstico no asigna H/D por sí solo.** Inflación, actividad, empleo, cobre o tipo de cambio requieren conexión textual con la orientación respaldada.
9. **No añadir contexto invisible.** No heredar automáticamente menú, tasa, sesgo o motivos desde otra intervención. El contexto externo necesario debe incorporarse y registrarse de forma uniforme.
10. **Ante direcciones contrapuestas**, usar la resolución explícita. Si no existe y la unidad no puede segmentarse justificadamente, registrar pendiente.

## 5. Acción, sesgo y comparación relativa

Guardar por separado cuando estén disponibles:

- `accion_actual`: subir, mantener, bajar u otra acción identificada;
- `sesgo_futuro`: alza, neutral, baja, mixto o no identificado;
- `nivel_descrito`: expansivo, neutral o restrictivo, solo si el texto lo afirma;
- `comparacion_relativa`: frente al menú, mayoría, mercado o trayectoria previa.

`comparacion_relativa` nunca determina por sí sola H/D/N. Una “baja hawkish” periodística sigue siendo D en la etiqueta principal si la acción actual elegida es bajar; su mensaje futuro restrictivo queda en `sesgo_futuro`.

## 6. Casos mínimos de calibración

| Situación | Etiqueta principal |
|---|---|
| Vota subir 25 pb aunque otra opción era subir 50 | H |
| Vota bajar 50 pb aunque otra opción era bajar 70 | D |
| Mantiene y respalda continuar alzas graduales | H |
| Mantiene y prepara una reducción futura que considera justificada | D |
| Mantiene para esperar información, sin dirección propia | N |
| Retira un sesgo al alza y comunica mantención, sin sesgo a la baja | N |
| Describe inflación alta sin recomendar respuesta | N |
| Presenta subir/mantener/bajar sin preferencia | N |
| Acuerdo institucional de alza o baja | H o D según la acción |
| Formalidad de apertura/cierre | N, `es_relevante=0` |

## 7. Migración desde v2

La revisión v3 comprende:

- las 19 rondas IA originales: 1.352 IDs;
- las cuatro tandas IA nuevas: 89 IDs;
- las 306 respuestas humanas v2.

Son 1.747 IDs distintos. La revisión debe buscar tanto H/D relativas como N que omitan una dirección respaldada. Las etiquetas originales permanecen inmutables; cualquier cambio se registra por ID con etiqueta anterior, etiqueta v3, cita, fundamento, confianza, estado y hash del texto.

Las respuestas humanas dejan de ser una evaluación ciega para v3 desde la autorización de abrirlas. Se conserva su carácter histórico como gold v2, pero una referencia v3 derivada de su revisión no debe presentarse como test independiente intacto.

No se reentrena hasta cerrar la revisión definida para la comparación. Al evaluar, se separa el efecto de cambiar referencias del efecto de cambiar supervisión.

## 8. Versionado

| Versión | Estado | Definición |
|---|---|---|
| v2 | Histórica, congelada | Inclinación contractiva/expansiva; convivió con énfasis dominante y convenciones relativas heredadas. |
| v3 | Aprobada 17-09-2026 | Dirección monetaria doméstica respaldada; excluye clasificación automática por menú, mayoría, fase o diagnóstico. |

Fuentes de la decisión: `CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md`, `DEFINICION_POSTURA_MONETARIA_PROPUESTA_V1.md`, `AUDITORIA_COMPATIBILIDAD_CRITERIOS_V1.md` y `REVISION_DIRECCION_RESPALDADA_V1.md`.
