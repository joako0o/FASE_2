# ¿Son compatibles las anotaciones anteriores con el criterio afinado?

**17-09-2026. Auditoría de documentos, estructura de las 1.352 IA y lectura de 12 casos. Sin reclasificación ni acceso a las 306 respuestas humanas.**

## Respuesta directa

**No hay base para declarar que las anotaciones originales estén mal en bloque. Pero sí hay evidencia concreta de convenciones usadas en el entrenamiento IA que no son equivalentes al criterio que ahora proponemos.** Por tanto, no basta con cambiar la redacción de la guía y seguir mezclando etiquetas como si no hubiera cambiado nada.

La conclusión afecta primero a la **compatibilidad de una parte de las etiquetas IA**, no demuestra que las 306 decisiones del investigador sean incorrectas. No se leyeron esas respuestas ni se estimó qué fracción cambiaría. Sus originales y decisiones aceptadas se conservan.

El agente debió distinguir antes entre aclarar una regla ya existente y sustituir una convención de etiquetado. El trabajo anterior no se invalida retrospectivamente por cambiar el objetivo; debe quedar asociado a su criterio y versión.

## 1. La separación N/relevancia ya existía y se utilizó

El codebook v2 establece diagnóstico descriptivo y opciones sin preferencia como N, y separa la relevancia como variable ortogonal. La documentación conservada del instrumento humano también dice que un diagnóstico puede ser N/relevante=1 y que la cita se exige en todos los relevantes.

El recuento de los 19 CSV originales es:

| Etiqueta | Relevancia | Original IA | Vista v2 con correcciones aceptadas |
|---|---:|---:|---:|
| H | 1 | 116 | 125 |
| D | 1 | 89 | 89 |
| N | 1 | **878** | **869** |
| N | 0 | **269** | **269** |
| **Total** | | **1.352** | **1.352** |

Por tanto, **el error de convertir los N monetarios en irrelevantes que vimos en el plan B no describe automáticamente nuestra base original**. Esta tabla comprueba la separación estructural, no la corrección semántica individual de cada etiqueta.

Las diferencias entre columnas corresponden a los 16 cambios efectivos ya aceptados y registrados. No son cambios hechos por esta auditoría.

## 2. La convención relativa sí está documentada en el entrenamiento IA

`docs/CONVENCIONES_ETIQUETADO.md` conserva literalmente reglas de generadores retirados y decisiones de sesiones previas. Incluye:

- “Voto/pausa explicita dentro de un ciclo de alzas con opcion de alza viva = dovish (contra la corriente de fase)”.
- “Vota mantener” cuando el menú era reducir o mantener y había sesgo previo a la baja = “hawkish relativo”.
- También conserva mantención con ajustes/alzas pendientes como H y advierte que esas convenciones podían requerir contexto externo a la intervención.

Eso es distinto de **no asignar D solo por pausar dentro de una trayectoria de alzas**, o de exigir que la dirección esté respaldada en el texto propio, sin inferirla por el menú de otro actor o por la fase.

El v2 formal también permite “énfasis dominante” en riesgos como base para H/D. El criterio propuesto enfatiza la conexión con una orientación respaldada. **Esta diferencia puede requerir recodificación**, no simplemente una corrección ortográfica del manual.

## 3. Cuatro rastros explícitos en las notas originales

Se examinó el campo nota de las 1.352 IA con un tamiz declarado: `pausa tras|vota pausa|mantener contra recorte`. Aparecieron cuatro casos, leídos completos:

| ID | Etiqueta original y v2 | Nota original / cuestión de compatibilidad |
|---|---|---|
| RPM-2005-12-13:525:1 | D | “pausa tras 5 alzas…”. El texto también afirma que no debe variarse la política de aumento gradual de tasas |
| RPM-2006-05-11:672:1 | D | “vota pausa: dos alzas consecutivas alterarían…”. Conviven pausa táctica y escenario de alzas futuras |
| RPM-2007-02-08:1102:1 | H | “vota mantener contra recorte…; comunicado neutral similar a enero”. La unidad mantiene y pide lenguaje neutral |
| RPM-2007-04-12:1218:1 | H | “vota mantener contra recorte…”. Predominan riesgos inflacionarios y se decide esperar mayores antecedentes |

Estos casos **requieren revisar el criterio aplicado**, pero no se les adjudica una etiqueta nueva en esta auditoría. En unos, el conflicto con la nueva formulación es más directo; en otros importa decidir si el rechazo sustantivo de relajamiento o el énfasis inflacionario bastan para H. No convertir cuatro coincidencias de una búsqueda en “cuatro errores confirmados”.

Los cuatro están en `etiquetas_r13_tanda09.csv` (41 filas) y `etiquetas_r14_tanda10.csv` (36 filas). **Esas 77 filas son un punto de partida razonable para revisión, no 77 etiquetas declaradas malas ni el límite máximo del problema.** Las convenciones históricas se describían como heredadas de sesiones anteriores.

## 4. Controles fuera del tamiz: no revisar solo casos sospechosos

Se seleccionaron ocho controles por hash determinista: dos H/1, dos D/1, dos N/1 y dos N/0. Se excluyeron los cuatro focos, IDs/textos normalizados del marco humano y casos cuya referencia v2 difiriera de la original. No se eligieron por errores del modelo. Las etiquetas eran visibles: esto no es doble anotación independiente ni muestra representativa para estimar una tasa global de error.

| ID | Etiqueta conservada | Resultado de esta inspección |
|---|---|---|
| RPM-2011-02-17:3810:1 | H/1 | Compatible: voto explícito de alza25pb |
| RPM-2005-01-11:57:1 | H/1 | Compatible: acuerdo institucional de alza25pb; las formalidades anexas no anulan la decisión |
| RPM-2005-06-09:292:1 | D/1 | Frontera: pausa táctica dentro de una estrategia de normalización; está fuera de los dos archivos prioritarios |
| RPM-2009-04-09:2498:1 | D/1 | Compatible: voto de baja50pb y previsión de otras bajas; menor magnitud no cambia el signo |
| RPM-2007-09-13:1449:2 | N/1 | Frontera de evaluabilidad: “la cifra resultante es menor y no mayor”, sin identificar el objeto en la unidad |
| RPM-2005-03-10:186:1 | N/1 | Frontera: discusión comunicacional que también considera adecuado anunciar una reducción gradual del impulso |
| RPM-2005-04-07:206:4 | N/0 | Compatible: invitación procedimental a formular comentarios |
| RPM-2005-12-13:516:8 | N/0 | Compatible: cierre de un tema sin contenido sustantivo en esa unidad |

**Cinco controles se ven compatibles; dos requieren aclarar el criterio y uno la evaluabilidad.** Esto no es una accuracy ni una proporción extrapolable. Incluyendo los cuatro focos, se leyeron **12 textos completos, 27.887 caracteres / 4.591 palabras**.

El caso292:1 muestra por qué no bastaría con revisar únicamente los77 registros de r13/r14. Su nota está vacía, como ocurre en930anotaciones originales. Una nota vacía en relevante no infringía el esquema original: las notas eran opcionales allí y se exigía cita. Sí limita que una búsqueda de notas revele todos los criterios utilizados.

## 5. Qué sigue siendo igual y qué puede cambiar

| Aspecto | Situación |
|---|---|
| Texto completo; decisión explícita de alza/recorte | Ya previsto en v2; no exige invalidar todos los votos claros |
| Diagnóstico ≠ postura; N relevante | Ya previsto; el recuento muestra que N/relevancia se separó |
| Recomendación del staff y anuncio institucional | Ya previstos; no requieren un voto formal para tener dirección |
| Magnitud menor de alza/recorte no cambia su signo | Compatible con las convenciones históricas documentadas |
| Pausa/no bajar según el menú o fase | Convención histórica documentada; puede cambiar al exigir respaldo propio y no ranking relativo |
| Énfasis macro vs conexión con política respaldada | Frontera real entre formulaciones; requiere acuerdo uniforme |
| Información insuficiente y texto dañado | V2 admite N conservador y, en ciertos casos, relevancia0; la propuesta separa pendientes, por lo que cambiaría el esquema |
| Relato histórico frente a postura actual | Hay que fijar qué variable se mide; R7 y convenciones de relato no se deben interpretar retrospectivamente a conveniencia |
| Instrumentos/unidades del plan B histórico | Nuevo alcance propuesto; no se traslada automáticamente a etiquetas2005–2015 |

## 6. Qué podemos decir sobre las 306 humanas

Se revisó **documentación**, no el libro de respuestas, sus etiquetas o sus citas. La documentación conservada remite al codebook v2 y distingue N relevante. Eso no acredita qué interpretación siguió el investigador en cada caso ni permite deducir su compatibilidad individual con la propuesta posterior.

- No hay un dictamen de “tus300 están mal”.
- Tampoco hay garantía de compatibilidad total con una nueva definición.
- Las decisiones humanas originales no se borran ni se sobrescriben.
- Si se adoptara una nueva referencia, debe identificarse como tal y no convertirse en un test independiente reutilizable por cambiar su nombre.
- No se pide volver a anotar todo desde cero. Primero se debe cerrar el criterio y medir el alcance de cualquier revisión autorizada, separando claramente las fuentes IA y humana.

## 7. Recomendación

**Sí debemos revisar la compatibilidad de una parte del entrenamiento IA antes de continuar sumando ejemplos o mezclar el plan B. No debemos descartar las1.352 ni invalidar las306humanas.**

Orden recomendado:

1. Acordar la frontera entre dirección respaldada y clasificación relativa/por énfasis. No seguir utilizando ambos criterios bajo una única etiqueta de versión sin señalarlo.
2. Auditar las77filas prioritarias y extender la búsqueda a casos de la misma familia en las demás rondas; incluir controles. Las89anotaciones nuevas también requieren la misma coherencia si se adopta otro criterio.
3. Registrar por ID referencia anterior, evidencia y propuesta en una capa nueva, sin cambiar originales o adjudicaciones silenciosamente. **Esta auditoría no contiene etiquetas nuevas.**
4. Si se aprueba una referencia nueva, evaluar separadamente el efecto de recodificar la referencia y el de entrenar un modelo sobre datos revisados. No convertir una mejora de score por cambio de etiquetas en mejora del modelo.

Los errores de representación del TF-IDF ya diagnosticados siguen siendo reales; este hallazgo de convenciones no demuestra que sean la única causa del deterioro +59 ni que el ampliado sea mejor. Sus métricas originales quedan intactas.

## Reproducción y límites

`python scripts/40_gestionar_proyecto.py auditar-compatibilidad --salida RUTA_NUEVA`

Reproduce conteos, tamiz y selección de controles y coteja la lectura registrada contra L0. No genera juicios semánticos automáticamente. No sobrescribe una auditoría existente, etiqueta ejemplos o entrena. Módulo de biblioteca estándar, sin acceso al archivo de respuestas humanas.

Evidencia: `data/auditoria/compatibilidad_criterios_v1/`, con lectura, conteos, casos inspeccionados, protocolo, manifiesto y verificación. Las fuentes y su alcance de lectura están ligadas por hashes. Los resultados son una auditoría inicial de compatibilidad, **no revisión semántica exhaustiva de1.352intervenciones**.
