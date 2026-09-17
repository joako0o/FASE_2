# Qué es y qué no es postura monetaria: propuesta operacional

**17-09-2026 · Estado: propuesta para acuerdo, no sustitución del codebook v2 vigente.**

El investigador solicita definir el concepto y contrastarlo con otros trabajos, especialmente para un posible corpus de actas anteriores a 2000. Esta propuesta fija una recomendación explícita, sus fundamentos y las decisiones que habría que aprobar antes de aplicarla. **No se reclasifica ningún dato ni se modifica el entrenamiento/validación actual.**

## 1. Definición recomendada

> **Medir el sesgo monetario doméstico que una unidad textual completa adopta, recomienda o respalda para Chile: hacia el endurecimiento (H), hacia la expansión (D), o sin inclinación direccional respaldada (N), utilizando los instrumentos pertinentes al régimen de la época.**

Medimos una orientación expresada, **no un efecto macroeconómico realizado**, el beneficio a un destinatario, el sentimiento positivo/negativo del texto o una sorpresa de mercado. No exigimos demostrar que la decisión efectivamente movió inflación/crédito. Sí exigimos evidencia de qué decisión u orientación se respalda y de que pertenece a la función monetaria del instrumento.

“Endurecer” y “expandir” se refieren a retirar/aportar impulso monetario o restringir/facilitar condiciones monetarias **en función de política**, no a cualquier uso de “subir”, “bajar”, “ayuda” o “control”.

**Importante:** H/D aquí son etiquetas operativas de sesgo textual. No son una medición universal de cuán restrictiva es una tasa respecto de una tasa natural no observada. Una tasa que baja puede seguir siendo alta; una que sube puede continuar en terreno expansivo.

## 2. Qué aporta la literatura y qué elegimos nosotros

### A. Postura no es sentimiento financiero

Shah, Paturi y Chava, *Trillion Dollar Words* (ACL 2023), distinguen hawkish/dovish de sentimiento positivo/negativo. En §3 definen D como indicación de relajamiento futuro, H como endurecimiento futuro y N como mezcla, no cambio o ausencia de relación directa con la postura. Pero su guía del apéndice C también etiqueta estados macroeconómicos —como inflación creciente— por sí mismos. **No copiamos esa parte:** queremos orientación respaldada, no convertir mecánicamente el diagnóstico macro en postura. Es una elección de constructo del proyecto, no consenso universal demostrado por el paper. [1](https://aclanthology.org/2023.acl-long.368.pdf)

WCB (2025) separa postura, temporalidad e incertidumbre y añade irrelevancia para material no informativo. Esto respalda separar dimensiones: una afirmación futura puede ser incierta y aun revelar una orientación; una oración sobre un banco central puede no ser una postura. Sus etiquetas de frases en inglés no se trasladan automáticamente a nuestras unidades históricas en español. [1](https://arxiv.org/abs/2505.17048)

Ornithologist (Jones, 2025) usa temas y árboles de decisión para guiar la clasificación. Tomamos la idea de preguntas estructuradas y explicaciones comprobables, no sus árboles australianos ni la promesa de que una respuesta formalmente válida sea semánticamente correcta. Su distinción entre evaluación temática y de postura también impide confundir un buen recuperador con un buen clasificador H/D. [1](https://arxiv.org/abs/2505.09083)

### B. La política monetaria no se limita a la TPM moderna

Alexander, Baliño y Enoch, *The Adoption of Indirect Instruments of Monetary Policy* (FMI, 1995), incluyen controles de tasas, techos de crédito por banco y crédito dirigido entre instrumentos directos, además de encajes, mercado abierto y redescuentos entre los indirectos. Por tanto, **ser regulatorio, sectorial o aplicado por banco no basta para excluir un instrumento histórico**. [2](https://www.elibrary.imf.org/display/book/9781557754899/ch002.xml)

Lindgren (FMI, 1991) distingue función de gestión monetaria/macroeconómica de asignación selectiva de crédito, aun reconociendo efectos monetarios de esta última; también explica que la asistencia de última instancia puede requerir compensación con otros instrumentos. La taxonomía y las preferencias normativas de ese autor no constituyen un veredicto sobre cada operación chilena de 1977. Usamos la distinción funcional, no la regla “crédito sectorial nunca es monetario”. [4](https://www.elibrary.imf.org/display/book/9781557751850/ch022.xml)

**Matiz respecto de la nota de calibración anterior:** lo correcto es “el alivio financiero no demuestra por sí solo D monetaria”, no “toda ayuda/refinanciación queda fuera”. Hace falta identificar qué función cumplía y qué orientación se comunica.

### C. La misma herramienta puede cumplir fines diferentes

Borio (BIS, 2020) describe cómo operaciones de liquidez que tradicionalmente implementaban una postura o estabilizaban mercados pasaron también a utilizarse para impulsar demanda y definir la postura. Por eso no sirve clasificar por el nombre de la herramienta solamente. [4](https://www.bis.org/speeches/sp200930.htm)

Schnabel (ECB, 2023) expone la posibilidad de suministrar liquidez para estabilidad/transmisión sin renunciar al endurecimiento contra la inflación, bajo condiciones concretas; no afirma una separación incondicional. La implicación es **no sumar automáticamente toda ayuda como relajamiento** y distinguir su propósito. No se presume que esas condiciones existieran en Chile en 1977. [1](https://www.ecb.europa.eu/press/key/date/2023/html/ecb.sp230519~de2f790b1c.en.html)

Kuttner y Yetman, en BIS Papers 88, estudian herramientas de liquidez/esterilización cuyos efectos sobre el crédito pueden diferir incluso al condicionar por postura monetaria. Es otra razón para no equiparar “afecta crédito” con “cambió la postura”. Se consultó el extracto indexado del capítulo y la página del volumen, no se reprodujeron sus estimaciones. [5](https://www.bis.org/publ/bppdf/bispap88c_rh.pdf)

**Síntesis:** no existe un diccionario universal “instrumento → H/D”. La clasificación requiere función, objeto, alcance y acto discursivo. La literatura orienta estas decisiones; no reemplaza un codebook específico y su validación.

## 3. Tres ejes que no deben confundirse

### 3.1 Función: ¿de qué trata la unidad?

Registrar uno o varios ámbitos, identificando cuál es principal:

- **Decisión/orientación monetaria doméstica.**
- **Contexto para la discusión monetaria:** actividad, inflación, mercados y escenario internacional, sin que eso determine H/D.
- **Implementación de una postura ya fijada:** operaciones para ejecutar objetivos existentes, sin asumir un cambio de sesgo.
- **Liquidez o estabilidad financiera focalizada.**
- **Crédito dirigido/desarrollo o financiación fiscal.**
- **Regulación prudencial, cambiaria o de capitales.**
- **Deuda/pagos/financiación internacional.**
- **Administración:** personal, contabilidad, multas individuales, formalidades.

Las categorías no deciden por sí solas la relevancia: una operación de crédito dirigido o encaje puede tener una función monetaria documentada, y una compra de activos puede ser implementación, estabilización o expansión. Registrar funciones mixtas cuando existan.

### 3.2 Estado de evaluación: ¿podemos asignar una etiqueta?

| Estado propuesto | Significado | Tratamiento |
|---|---|---|
| **Dentro del objetivo, evaluable** | Unidad legible y coherente; el contenido permite evaluar si hay orientación respaldada | H/D/N, relevancia 1 |
| **Fuera del objetivo** | Solo otra función, sin orientación ni contexto de la discusión monetaria doméstica | No una observación N para B; relevancia 0 en una exportación compatible |
| **Información insuficiente** | Instrumento, norma base, autor, alcance o fragmento indispensables faltantes | Etiqueta pendiente y relevancia no forzada; excluir de entrenamiento supervisado |
| **Mixto por segmentación o medidas incompatibles** | La fila mezcla asuntos o direcciones cuyo sentido conjunto no queda resuelto | Separar por asunto si procede; si no, pendiente, sin forzar H/D/N |

**No confundir:** un texto completo que discute riesgos sin postura puede ser N con confianza alta. Un fragmento que cambia “5%” por “10%” sin identificar qué cambia tiene información insuficiente, no neutralidad demostrada.

Para compatibilidad técnica, el formato actual puede guardar `neutral` junto a relevancia 0 para un fuera-de-alcance; esa etiqueta es un marcador de exportación y **no debe entrar al entrenamiento B como neutral sustantivo**. Los pendientes no se convertirían en ceros de A ni neutrales de B. Esto necesita un adaptador/esquema nuevo si se aprueba; no pasar estos estados al runner v2 existente.

### 3.3 Orientación: H, D o N

| Clase | Definición recomendada |
|---|---|
| **H** | Adopta, recomienda o respalda una acción de endurecimiento monetario doméstico, un sesgo futuro en esa dirección o un compromiso de sostener una restricción monetaria explícita |
| **D** | Adopta, recomienda o respalda una acción de expansión monetaria doméstica, un sesgo futuro en esa dirección o un compromiso de sostener un estímulo monetario explícito |
| **N** | Dentro del objetivo y evaluable, no revela inclinación direccional respaldada: diagnóstico, opciones sin preferencia, pregunta sin respuesta, historia no adoptada, o mantención sin sesgo/orientación identificable |

Describir que la política vigente “es expansiva” o “es restrictiva” **no basta**: hay que distinguir esa descripción de respaldar que se sostenga así. No llamar N a todo mantenimiento, ni D a toda preocupación por crecimiento.

## 4. Prioridad de reglas para una etiqueta única

Esta prioridad es una **convención del proyecto**, coherente con la decisión explícita que ya se venía priorizando; no es una definición única impuesta por los papers.

1. **Identificar sujeto y acto.** Se clasifica lo que respalda el actor/unidad, no la opinión de terceros. Un acuerdo institucional actual sí cuenta; una pregunta sobre adherir no es la adhesión; una cita de una decisión pasada no es por sí sola una recomendación actual.
2. **Resolver función monetaria y objeto antes del signo.** Bajar una tasa de multa no es bajar la tasa de política. Reducir estímulo es restrictivo, aunque el verbo sea “reducir”.
3. **Si hay una acción monetaria actual explícitamente elegida y de dirección inequívoca, prima su signo.** Alza = H; recorte = D para una tasa de política. Subir 25 en vez de 50 sigue siendo H; bajar 25 en vez de 50 sigue siendo D. No se mide sorpresa respecto del mercado o de una alternativa más agresiva.
4. **Mantener no resuelve la etiqueta:** usar el sesgo o trayectoria respaldados. Mantener con sesgo al alza = H; con sesgo a la baja = D; sin dirección y con neutralidad explícita = N. La descripción del nivel de la tasa no reemplaza un sesgo.
5. **Sin cambio actual, la orientación futura propia cuenta.** Proponer o anticipar como escenario propio alzas/recortes, o comprometerse a sostener restricción/estímulo, puede dar H/D. Debe distinguirse de una encuesta ajena, una hipótesis incidental o una mera posibilidad sin preferencia.
6. **Una condición no elimina automáticamente la postura.** Si el actor respalda una respuesta monetaria bajo una condición identificada, registrar dirección y condición. Si solo enumera escenarios alternativos sin hacer propio uno, N. “No descarto” no es una etiqueta automática: decidir si existe una orientación respaldada en el resto de la unidad.
7. **Rechazar una acción no se invierte mecánicamente.** Rechazar una baja puede ser H si defiende sostener restricción; rechazar una subida puede ser D si defiende sostener estímulo. Pero esperar para subir luego sigue pudiendo ser H, esperar para bajar luego D y esperar sin orientación N.
8. **Si dos acciones monetarias admisibles tienen signos contrapuestos**, buscar la resolución global explícita. Si el texto no permite establecerla, no sumar por cantidad de menciones ni promediar montos de instrumentos distintos: registrar mixto/pendiente. Una operación puramente de liquidez para estabilidad no se trata como segunda dirección monetaria sin justificar antes su función.
9. **El diagnóstico por sí solo no asigna H/D.** Inflación alta, desempleo, crecimiento, cobre o devaluación no son una regla de Taylor automática del anotador. Se requiere conexión textual con orientación de política respaldada.
10. **No añadir contexto invisible.** Si para entender un cambio hace falta una norma previa, solo usarla si se incorpora y registra de forma consistente como parte de la entrada del nuevo diseño. En caso contrario, pendiente. Nunca usar la evolución posterior de inflación/tasas para decidir qué “quería decir” el texto.

### Acción, nivel y mensaje pueden diferir

Para evitar contradicciones, guardar por separado `accion_actual`, `sesgo_futuro` y, si está explícito, `nivel_descrito`. Una reducción actual con advertencia restrictiva futura se registra en ambas dimensiones; por la convención anterior, la etiqueta principal sigue la reducción, D. No equivale al uso periodístico de “hawkish cut”, que puede comparar el mensaje con expectativas o un camino alternativo. El nivel final puede seguir siendo restrictivo sin volver H el recorte.

## 5. Qué instrumentos entran y cuándo

| Instrumento/operación | Cuándo puede dar H/D | Qué no basta |
|---|---|---|
| Tasa de política, referencia o redescuento con función monetaria | Dirección de ajuste o sesgo respaldado, con naturaleza de la tasa identificada | Cualquier tasa de préstamo/multa; comparar mensual con anual o real con nominal |
| Encaje/requerimientos de reservas | Cambio de exigencia utilizado para control monetario y sentido identificable respecto del régimen previo | “Ayuda de encaje”, modificación contable, cambio de remuneración/base sin analizar su función |
| Techos/cuotas de crédito | Cambio de restricción dentro de un marco de control monetario documentado | El mero establecimiento de un límite sin saber si antes era mayor/menor o si es vinculante |
| Crédito dirigido/refinanciamiento | Su papel monetario en el régimen está identificado y la decisión respalda ampliar/restringir el impulso mediante él | Que sea un préstamo, refinanciación o apoyo sectorial; tampoco se excluye solo por ser sectorial |
| Compras/ventas de activos, liquidez y balance | Se comunican como instrumentos para ampliar/retirar impulso monetario o sostener ese sesgo | Tamaño bruto del balance, ayuda temporal, refinanciación de vencimientos o ejecución mecánica de una postura |
| Intervención/divisas/esterilización | Existe vínculo monetario explícito y orientación neta interpretable en la unidad/contexto declarado | Comprar divisas = D o vender = H sin considerar función/compensación; apreciar/depreciar moneda como sinónimo de H/D |
| Asistencia de emergencia/rescate | El texto permite identificar además una orientación monetaria, separada de la función de estabilización | Ayuda a una institución = D; no se presume esterilización ni ausencia de ella |
| Multas, deuda particular, capitalizaciones, personal | Solo entran si hay una función monetaria adicional documentada y separable | Reducir sanción, favorecer deudor, prorrogar deuda extranjera o ratificar una operación por sí solos |

Esta tabla evita dos extremos: **todo crédito es D** y **solo la TPM moderna puede expresar postura**. La misma herramienta puede aparecer dentro o fuera según su función. No clasificar normativamente si una política “debería” corresponder a un banco central: describir la función efectivamente documentada.

## 6. Aplicación provisional a los ejemplos históricos del investigador

No son adjudicaciones definitivas; se muestran las preguntas que el nuevo esquema exige.

| Ejemplos | Resultado del filtro conceptual propuesto |
|---|---|
| Multas 78 y alivios individuales 89 | Identificar tasa de sanción/alivio regulatorio. No D monetaria por el verbo bajar. Fuera de H/D si no hay función monetaria adicional |
| Bolivia 4480/4481 | Financiación/deuda internacional, no una dirección monetaria chilena demostrada. No llamarlo D por ser ayuda |
| Créditos/ayudas 26, 57, 23, 41, 58 | Separar asuntos y determinar si son caja/estabilidad/desarrollo o uso de un instrumento monetario histórico. No excluirlos automáticamente ni asignar D alta sin ese puente |
| 42 | Separar ratificación, regla de plazos y excepción crediticia. La excepción no es “más control” sin más; sin regla base identificable, dirección pendiente |
| 8713 y 69 | Regulación cambiaria/posición de cambios. El efecto sobre reservas se discute y el signo monetario no se deduce solo de control o flexibilización |
| 18566 | Aislar el cambio 5%→10% e identificar el parámetro. No rellenar por intuición ni clasificar toda la fila como rutina N alta |
| 12 frente a 45/23/41 | Aplicar el mismo criterio funcional a ratificaciones y decisiones nuevas; la forma administrativa no decide la postura |
| Personal/multas/contabilidad sin función monetaria | Fuera de alcance; no N sustantivo de B |

Que una unidad contenga “encaje”, “Banco Central” o una gran suma no sustituye el análisis. No se consultaron aún los originales/anexos de esas actas ni se definió su mapa histórico de instrumentos; cuando esto sea necesario, la respuesta honesta es pendiente.

## 7. Unidad, evidencia y registro mínimo

**Corpus actual:** intervención íntegra del actor, sin modificar sus límites para arreglar errores. **Corpus histórico propuesto:** una unidad coherente de asunto/acuerdo con discusión y resolución, preservando texto bruto, offsets y relación con el acta. Si cambia la unidad de observación, declararlo y no comparar sus conteos o métricas como si fueran idénticos.

Registrar al menos:

- ID original, fuente, fecha, régimen/contexto documentado, límites de la unidad y sujeto de la postura.
- Ámbito/función y nombre del instrumento; clase de tasa, moneda/indexación/periodicidad cuando importe.
- Acto discursivo: decisión, adhesión, recomendación, escenario propio, relato, expectativa ajena, pregunta u operación administrativa.
- Acción actual, sesgo futuro y condición, cuando estén expresados; referencia del cambio si es necesaria.
- Estado de evaluación y H/D/N solo cuando procede; confianza de anotación y motivo de reserva/exclusión.
- Cita literal ≤300 caracteres que identifique no solo la palabra direccional sino, cuando sea necesario, su objeto y respaldo; fuente adicional declarada si existe.
- Procedencia IA/humana/asistida. No confundir incertidumbre del mensaje con confianza del anotador.

La cita no reemplaza el texto completo al entrenar. Campos faltantes no se rellenan inventando nombres, tasas, reglas previas o efectos de esterilización.

## 8. Qué cambiaría frente al v2, y cómo evitar una revisión oportunista

Esta propuesta conserva muchas decisiones ya aceptadas —texto completo, objeto, respaldo, futuro, no heredar tasas de otras intervenciones—, pero **no es una modificación compatible sin revisión**:

1. La frase de v2 sobre “énfasis dominante” en inflación/actividad puede entrar en tensión con diagnóstico ≠ postura. Aquí se exige conexión con orientación respaldada, no mero predominio de un riesgo en palabras.
2. V2 utiliza N como salida conservadora de ciertas dudas. Aquí se separa falta de información/segmentación de neutralidad sustantiva; cambiaría el esquema de anotación y potencialmente A.
3. El ámbito instrumental se amplía de TPM a instrumentos históricos con función documentada.
4. La unidad histórica por asunto/acuerdo no es automáticamente la misma intervención individual.
5. La prioridad de acción actual sobre mensaje futuro se declara para que una sola etiqueta no mezcle cambio de tasa, nivel y sorpresa de mercado.

**Para adoptar:** acordar estas decisiones, versionar un codebook nuevo para el alcance definido y realizar una calibración pequeña que cubra las familias de casos. Revisar por reglas fijadas, no seleccionar solo los errores del modelo. Conservar las referencias antiguas y sus scores; cualquier nueva referencia se evalúa y reporta por separado, sin presentar su efecto como ganancia del clasificador. No meter casos de validación en su propio train.

No se aprueba ahora reetiquetado masivo, importación histórica, generación sintética, otro entrenamiento o cambio del contador 300/300. El objetivo inmediato es acordar qué variable queremos medir.

## 9. Registro de fuentes y alcance real de lectura

Búsqueda dirigida, no revisión sistemática ni reproducción de experimentos. No se descargaron modelos/datasets ni se contrató acceso.

| Fuente | Secciones efectivamente consultadas | Uso y límite |
|---|---|---|
| Shah, Paturi, Chava, ACL 2023 [1](https://aclanthology.org/2023.acl-long.368.pdf) | PDF chunks 0,1,6,7; introducción, §3 y apéndice C | Diferencia de sentimiento/postura, guía y sus límites; no adoptar automáticamente estados macro como etiquetas |
| WCB, arXiv 2505.17048 [1](https://arxiv.org/abs/2505.17048) | Abstract y HTML v1 §2/selección de bancos (chunk1) | Separación postura/temporalidad/incertidumbre; no todos los apéndices ni corpus importado |
| Jones, Ornithologist 2025 [1](https://arxiv.org/abs/2505.09083) | Abstract y HTML v1 chunk2, generador/validación | Taxonomía y decisiones estructuradas; no garantía de verdad por gramática |
| Alexander, Baliño, Enoch, FMI1995 [2](https://www.elibrary.imf.org/display/book/9781557754899/ch002.xml) | Chunks0–1, modos de operación y tablas de instrumentos | Reconocer instrumentos directos e indirectos; no clasificar toda operación individual por el nombre del instrumento |
| Lindgren, FMI1991 [4](https://www.elibrary.imf.org/display/book/9781557751850/ch022.xml) | Chunks0–2: objetivos, definición, diseño, redescuento/última instancia | Función monetaria frente a asignación de crédito, posibilidad de compensación; separar sus recomendaciones normativas de hechos históricos |
| Borio, BIS2020 [4](https://www.bis.org/speeches/sp200930.htm) | Página institucional, chunk0, recorrido y lecciones | Funciones cambiantes del balance/liquidez; no causa demostrada de cada operación chilena |
| Schnabel, ECB2023 [1](https://www.ecb.europa.eu/press/key/date/2023/html/ecb.sp230519~de2f790b1c.en.html) | Chunks0 y4: separación y condiciones | Estabilidad y postura pueden requerir instrumentos distintos; separación no universal ni evidencia de Chile1977 |
| Kuttner y Yetman, BIS Papers88 [5](https://www.bis.org/publ/bppdf/bispap88c_rh.pdf) | Extracto indexado del capítulo; la URL de fetch redirigió a la página del volumen de2016 | Efectos de liquidez y postura no idénticos; no lectura íntegra del volumen ni validación de estimaciones |
| FMI, Central Bank Transparency Code [1](https://www.imf.org/external/datamapper/CBT/browse/) | Extractos indexados de §3.1 | Marco operativo, instrumentos y objetivos; no es un codebook H/D |

Otras búsquedas de Apel/Blix Grimaldi devolvieron referencias secundarias o acceso no íntegro; no se atribuyen aquí reglas específicas a su paper. Los estudios del FMI/BCCh ya reseñados en `CALIBRACION_PLAN_B_ACTAS_HISTORICAS.md` aportan contexto de cambio de régimen, no un mapeo automático de las actas del investigador.
