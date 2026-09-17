# Antes del híbrido: investigación de métodos, trabajos y foros

**Proyecto D&H · Actas RPM de Chile, 2005–2015**  
**Fecha de consulta y cierre: 2026-09-16. Estado: investigación completada; experimentos propuestos, no ejecutados.**

## 1. Respuesta corta

**Sí hay antecedentes útiles, pero no respaldan agregar un diccionario que corrija automáticamente al modelo.** La recomendación de esta revisión es conservar el TF-IDF como referencia y estudiar una segunda representación que identifique **qué se propone, sobre qué instrumento, por quién, con qué respaldo y en qué contexto temporal**.

La literatura aporta tres advertencias especialmente relevantes:

1. **Una expresión no equivale a una postura.** Las reglas de coocurrencia y negación simple tienen antecedentes, pero pierden contexto. En *Trillion Dollar Words* los clasificadores contextualizados ajustados superan a las reglas en su evaluación; eso no demuestra todavía una mejora en nuestras actas. R01: [1](https://aclanthology.org/2023.acl-long.368.pdf).
2. **La unidad de lectura importa.** Dividir puede ayudar a separar argumentos, pero promediar frases puede diluir una recomendación o el disenso. *GPT Deciphering Fedspeak* contrasta lectura por frase, documento y hablante. R04: [1](https://aclanthology.org/2023.findings-emnlp.434.pdf).
3. **Un recurso internacional no es automáticamente compatible con Chile ni con nuestro codebook.** WCB separa postura, temporalidad e incertidumbre, pero selecciona documentos disponibles en inglés. Su guía chilena publicada en HTML v2 contiene inconsistencias que requieren aclaración antes de reutilizar sus anotaciones. R03: [1](https://arxiv.org/html/2505.17048v2).

**Decisión recomendada:** primero una comparación pequeña que separe el efecto de reparar números del efecto de añadir contexto. Un transformer en español o un LLM son candidatos posteriores, no ganadores por defecto. No propongo continuar la búsqueda de longitudes ni reemplazar el modelo vigente ahora.

### Qué se hizo y qué no

- Se buscaron trabajos de bancos centrales, métodos de extracción de opiniones/números, evaluación conductual y consultas técnicas de foros.
- Se leyeron las secciones metodológicas y resultados pertinentes de las fuentes principales; las partes efectivamente consultadas se registran en §9. **Es una revisión dirigida, no una revisión sistemática exhaustiva ni una reproducción de los artículos.**
- Se contrastaron consejos técnicos con documentación oficial. Una respuesta de foro no se considera prueba de mejora en clasificación monetaria.
- **No se entrenó, ajustó, calibró ni puntuó ningún modelo; no se importaron datasets externos, no se modificaron etiquetas ni el codebook y no se volvió a examinar el contenido de las 306 respuestas humanas.**
- Las cifras propias provienen del [diagnóstico ya cerrado](INFLUENCIAS_NGRAMAS.md), no de experimentos nuevos. Los ejemplos didácticos de este informe son inventados y no constituyen nuevas anotaciones del corpus.

## 2. Punto de partida: qué debemos resolver realmente

El diagnóstico anterior encontró 62 errores de postura contra IA entre 793 predicciones del candidato (1,4), incluidos 17 intercambios H↔D. Identificó problemas de números, negación, objeto de la acción, referencias internacionales, decisiones frente a opciones y asociaciones con nombres/fórmulas. Esos casos **ya son material de desarrollo**, no una futura prueba independiente. Véanse [informe](INFLUENCIAS_NGRAMAS.md) y [revisión trazable](../data/evaluacion/influencias_ngramas_v1/revision_17_confusiones_hd.csv).

La tarea sigue siendo la del [codebook v2](codebook_v2.md): postura respecto de la **TPM chilena**, por **intervención completa**, con relevancia separada. Esto condiciona la transferencia de cualquier artículo:

| Distinción | Consecuencia para nuestro proyecto |
|---|---|
| Sentimiento económico vs. postura monetaria | Una economía débil no basta para asignar D: R2 exige distinguir diagnóstico de inclinación de política. |
| Frase vs. intervención | Podemos extraer fragmentos internos, pero no convertir sin autorización la unidad final en frase o reunión. |
| Acción mencionada vs. preferida | Un menú, una cita o una opción rechazada no heredan automáticamente la dirección del verbo. |
| Tiempo vs. validez de la señal | R7 admite pasado y futuro; el tiempo se representa, **no se usa como filtro que descarte todo lo histórico**. |
| Condición vs. ausencia de postura | Una recomendación condicional puede revelar sesgo; no tratar todos los «si» como neutral. |
| Identidad vs. atribución | El apellido puede ser un atajo; saber quién propone y quién cita puede ser indispensable. |
| Neutral vs. abstención | Neutral es una clase sustantiva. «Revisar» sería un estado operativo, no una cuarta postura ni una nueva definición de neutral. |

Además, el codebook limita la herencia de una réplica a contenido presente en la misma intervención. Por eso, **traer intervenciones de otros hablantes como contexto no sería una simple mejora técnica**: requeriría resolver primero su compatibilidad con el criterio vigente.

## 3. Qué hacen los trabajos más cercanos

### 3.1 Trillion Dollar Words — Shah, Paturi y Chava, ACL 2023

**Diseño.** Trabaja con frases en inglés de minutas, conferencias de prensa y discursos de la Fed. El muestreo inicial contiene 2.379 frases, que pasan a 2.480 tras segmentación. Usa H/D/N, con neutral que incluye contenido mixto o no relacionado. Filtra con un diccionario temático antes de anotar y compara reglas, redes recurrentes, modelos preentrenados ajustados y GPT-3.5 sin ejemplos. R01, §§3–5: [1](https://aclanthology.org/2023.acl-long.368.pdf).

**Cómo aborda el problema.** Su baseline de reglas cruza grupos de sustantivos y verbos; ante determinadas negaciones invierte H↔D. Para separar tonos contrapuestos corta en conectores como *but*, *however* o *although*, con condiciones sobre los fragmentos. No es una resolución completa del alcance de negación ni de quién respalda cada opción. R01, §§3.1 y 4.1: [1](https://aclanthology.org/2023.acl-long.368.pdf).

**Resultado verificable.** En *Combined*, antes de dividir, la tabla 5 da **F1 ponderado** medio de tres semillas: reglas **0,4966**, RoBERTa-large ajustado **0,7171** y GPT-3.5 zero-shot **0,5872**. El diseño separa 80/20 train/test y vuelve a dividir el entrenamiento 80/20 para validación. Después de segmentar y reanotar, RoBERTa-large da **0,7113** en *Combined-S*: dividir no mejora universalmente. R01, §5 y tabla 5: [1](https://aclanthology.org/2023.acl-long.368.pdf).

**Qué tomar:** comparar aprendizaje contextual con una referencia sencilla; conservar cláusulas contrastivas; evaluar el tratamiento de negación.

**Qué no tomar:** copiar «negación = invertir clase» o trasladar automáticamente sus etiquetas de diagnóstico económico. La segmentación también cambia el conjunto anotado, por lo que no es una ablación limpia sobre nuestra misma unidad. Su F1 ponderado no es comparable con nuestro macro-F1; su filtro de entrada tampoco representa nuestra evaluación de relevancia.

### 3.2 Between hawks and doves — Tobback, Nardelli y Martens, ECB WP 2085, 2017

**Diseño.** Mide la percepción de la comunicación del BCE en noticias en inglés, no la postura individual de consejeros chilenos. Compara orientación semántica por palabras con TF-IDF + SVM lineal. En las reglas exige referencia al BCE y excluye determinadas palabras precedidas por negación; el ejemplo «no elevó tasas» no se trata como una subida. R02, §§3.1–3.2: [1](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2085.en.pdf).

**Resultado y advertencia.** La tabla 4 informa accuracy **92 %** para SVM frente a **65 %** para orientación semántica, en clasificación H/D de artículos. La prueba temporal de 85 artículos de 2014–2015 contiene **solo dovish**: su elevada accuracy no prueba discriminación temporal de las dos clases. El trabajo explica también cómo el léxico restringido pierde señales de compras de activos y muestra un ejemplo donde «rises» produce una lectura errónea frente al contexto de baja inflación prolongada. R02, §4 y tablas 4–5: [1](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2085.en.pdf).

**Qué tomar:** no abandonar el modelo lineal solo por ser sencillo; usar representaciones más completas puede ser valioso. La validación debe mostrar soportes por clase y cambios de vocabulario entre períodos.

**Qué no tomar:** interpretar un margen grande como certeza calibrada, ni usar el 92 % como objetivo para nuestro problema de tres clases. Que el SVM acierte un ejemplo contextual no demuestra que resuelva sistemáticamente negación o atribución.

### 3.3 Words That Unite The World — WCB, arXiv v2 / NeurIPS 2025

**Diseño.** Reúne 25 bancos para las tareas principales y conserva otro banco para estudios de transferencia. Usa **tres tareas distintas**: postura H/D/N/irrelevante, futuro/no futuro y certeza/incertidumbre. La selección exige documentos disponibles en **inglés**. Compara entrenamiento conjunto y por banco; describe una división de 700/150/150 y búsqueda de hiperparámetros para modelos ajustados. R03, §§2–4: [1](https://arxiv.org/html/2505.17048v2).

**Qué aporta:** separar postura de temporalidad y lenguaje incierto es una idea directamente útil. Evitar un filtro léxico rígido mediante una categoría de irrelevancia también ayuda a pensar la cobertura. En nuestro proyecto esto se traduciría en rasgos auxiliares y diagnóstico de A, **no** en cambiar las clases finales.

**Advertencia específica de Chile, verificada en la versión consultada.** El apartado chileno cubre 2018–2024 y declara acuerdo bruto entre anotadores de **55,5 % para postura**; no es κ ni accuracy del clasificador. La tabla 98 del HTML v2 coloca bajo la columna *Hawkish* expresiones que su propio contenido describe como *dovish*, y bajo *Dovish* expresiones descritas como *hawkish*. La fila de inflación menciona una «2% target», mientras el apartado de mandato del mismo documento indica 3 %. R03, apartado Chile y tabla 98: [1](https://arxiv.org/html/2505.17048v2#Ax69.T98).

La referencia oficial del BCCh consultada establece que la inflación proyectada a dos años debe ubicarse en **3 %**. R18: [2](https://www.bcentral.cl/en/content/-/detalle/ver-mas-preguntas-frecuentes-7-3).

**Alcance de la observación:** hay una inconsistencia interna en la guía publicada en HTML; **no se ha auditado el dataset ni demostrado que sus etiquetas estén globalmente invertidas**. Tampoco se verificó aquí esa tabla contra el PDF o con los autores. Antes de importar datos habría que aclarar la tabla y revisar correspondencia código–clase, idioma y compatibilidad con v2. No basta invertir todas las etiquetas.

Incluso si esa inconsistencia fuera solo editorial, subsiste otra diferencia: ejemplos de la guía infieren postura desde condiciones macroeconómicas que nuestro R2 no convertiría por sí solas en H/D. **La compatibilidad conceptual va antes del tamaño del dataset o del nombre del modelo.**

### 3.4 GPT Deciphering Fedspeak — Peskoff y colaboradores, Findings of EMNLP 2023

**Diseño.** Contrasta comunicados con transcripciones del FOMC y estudia disenso. Usa cinco posiciones entre dovish y hawkish. Compara medias de puntuaciones por frase, lectura del comunicado completo y lectura por hablante dentro de cada transcripción; describe 3.728 observaciones de frases de comunicados y 5.691 observaciones de hablantes. R04, §§2.3–2.4: [1](https://aclanthology.org/2023.findings-emnlp.434.pdf).

**Hallazgo útil.** Los autores muestran que el promedio de frases puede diluir el tono porque muchas frases son neutrales; además, el comunicado agregado puede ocultar desacuerdos de los participantes. No es equivalente puntuar el comunicado, cada frase y la posición de cada hablante. R04, §2.4 y figuras 3–4: [1](https://aclanthology.org/2023.findings-emnlp.434.pdf).

**Transferencia:** mantener la intervención completa como respaldo y no votar por mayoría de frases. Una recomendación final no debe perder frente a muchas frases descriptivas. Conservar emisor y distinción entre decisión institucional y preferencia individual.

**Límite:** el trabajo no valida nuestro híbrido ni proporciona una medición de mejora H/D sobre Chile. Tampoco autoriza ampliar la unidad del codebook a todas las intervenciones del mismo hablante.

### 3.5 CB-LMs — Gambacorta y colaboradores, BIS WP 1215, octubre de 2024

**Diseño.** Adapta encoders al dominio de bancos centrales con discursos y documentos; luego ajusta clasificadores. Una tarea usa 1.243 frases FOMC de 1997–2010, con muestreos 80/20 repetidos en 30 particiones seleccionadas para conservar la distribución de clases. R05, §5: [1](https://www.bis.org/publications/working-paper-1215-cb-lms-language-models-central-banking.pdf).

**Qué demuestra y qué matiza.** En esa tarea, los mejores RoBERTa adaptados alcanzan aproximadamente **84 % de accuracy media**, frente a aproximadamente **81 %** del modelo base; los BERT adaptados no muestran una mejora clara. El documento contiene redondeos distintos entre secciones, por lo que aquí se conserva la comparación aproximada del §5. No existe una ganancia garantizada por adaptar al dominio. R05, §§5–6: [1](https://www.bis.org/publications/working-paper-1215-cb-lms-language-models-central-banking.pdf).

En una segunda tarea usa **237 noticias resumidas**, de cinco frases y 67 palabras en promedio, y menos datos etiquetados. GPT-4 Turbo y Llama-3 70B alcanzan alrededor de 80–81 % de accuracy, frente a resultados inferiores de los CB-LMs. Los generativos puntúan todo el conjunto en zero-shot y los encoders se evalúan en particiones 80/20: los protocolos no son idénticos. R05, §7: [1](https://www.bis.org/publications/working-paper-1215-cb-lms-language-models-central-banking.pdf).

**Transferencia:** comparar modelos adaptados y generativos según tarea, recursos y longitud, sin afirmar «un LLM siempre gana». La segunda tarea cambia simultáneamente longitud, tipo de texto y disponibilidad de etiquetas: no aísla causalmente el efecto de contexto. Sus 67 palabras promedio tampoco representan necesariamente nuestras intervenciones más extensas.

## 4. Métodos complementarios: cómo representar y comprobar el contexto

### 4.1 Opinión estructurada: emisor, objeto y expresión

SemEval-2022 Task 10 formula la opinión como una estructura **(holder, target, expression, polarity)** y evalúa conjuntamente los elementos y sus relaciones. Incluye español, junto a otras cuatro lenguas. R06, §§1–4: [5](https://aclanthology.org/2022.semeval-1.180.pdf).

**Adaptación propuesta, no implementación:** conservar por cada señal monetaria:

- fragmento textual y posición exacta en la intervención;
- emisor de la opinión y entidad/instrumento al que se refiere;
- acción propuesta, mencionada, rechazada o contrafactual;
- condición y alcance de negación;
- tiempo del evento y orientación futura, sin descartar automáticamente ninguna;
- nivel de tasa, cambio y unidad cuando sean explícitos;
- estado «no determinado» cuando el texto no permita resolver un campo.

La estructura es una hipótesis inspirada en R06, **no el esquema original de SemEval ni una nueva obligación de etiquetado humano**. En la primera implementación eventual bastaría una vista de cláusulas candidatas con contexto y rasgos verificables. Resolver perfectamente todas las relaciones exigiría recursos y una evaluación de extracción propia; no se da por hecho que un parser o un LLM lo haga bien.

Ejemplo didáctico: en «rechazo reducir la TPM; prefiero mantenerla con sesgo al alza», guardar solo *reducir TPM* es peor que conservar la cláusula completa. Y en «reducir el estímulo», el objeto cambia la interpretación: no es lo mismo que reducir la TPM.

### 4.1.1 Negación en español: detectar la señal y su alcance por separado

*Detecting Negation Cues and Scopes in Spanish* (Jiménez-Zafra y colaboradores, LREC 2020) estudia exactamente esta separación. Sobre reseñas españolas SFU ReviewSP-NEG, entrena **dos clasificadores secuenciales CRF**: uno detecta marcadores de negación y el segundo usa esos marcadores predichos para identificar su alcance. Utiliza rasgos léxicos, gramaticales y de dependencias, y separa entrenamiento, desarrollo y test por reseñas. R20, §§1 y 3: [5](https://aclanthology.org/2020.lrec-1.853.pdf).

El trabajo muestra por qué no basta buscar «no» y mirar unas palabras a la derecha: existen marcadores discontinuos, usos que no niegan, alcances que se extienden antes y después del marcador y negaciones superpuestas. Su corpus también anota el evento afectado. R20, §§1 y 3.1: [5](https://aclanthology.org/2020.lrec-1.853.pdf).

**Qué tomar:** si incorporamos un módulo de negación, evaluar separadamente detección del marcador, alcance y efecto sobre la acción. Por ejemplo didáctico, «no es necesario bajar» y «no descarto bajar» no admiten la misma inversión automática. Guardar el marcador sin su complemento puede introducir una señal incorrecta.

**Qué no inferir:** un detector entrenado en reseñas no está validado en actas monetarias; resolver negación tampoco resuelve por sí solo preferencia, contrafactual o disenso. Añadir dependencias o un CRF no queda autorizado por esta revisión. Es un antecedente concreto para diseñar y evaluar el componente, no una mejora local ya demostrada.

### 4.2 Números: reconocer el token no basta

FinNum-2 estudia **a qué entidad se vincula cada número** en textos financieros. Presenta 10.340 instancias anotadas: su ejemplo inicial distingue un precio del petróleo de un precio de acción dentro del mismo texto. R07, §§1–3: [1](https://research.nii.ac.jp/ntcir/workshop/OnlineProceedings15/pdf/ntcir/01-NTCIR15-OV-FINNUM-ChenC.pdf).

**Transferencia conceptual:** asociar cada cifra con TPM, inflación, tasa extranjera, fecha o magnitud de un cambio. No importar su clasificador de tweets como solución de postura.

En nuestro diagnóstico, `5,25%` deja el token `25` y una tasa de `3%` pierde el dígito. La documentación oficial confirma que el patrón predeterminado de TF-IDF conserva tokens de dos o más caracteres y trata la puntuación como separador. R11: [1](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).

**Propuesta:** preservar la forma original, normalizar la representación numérica en una vista derivada y separar **nivel / cambio / unidad / instrumento** cuando haya evidencia suficiente. Por ejemplo, pasar de 5,25 % a 5 % equivale a −0,25 puntos porcentuales, o −25 puntos base; pero solo es una baja de TPM si ambas cifras se refieren a ese instrumento y a esa acción. La magnitud `25` sola no define dirección.

**No recomendado:** borrar todos los números o sustituirlos todos por el mismo marcador. Se perderían diferencias como mantener 5 %, bajar a 5 % y preferir 50 frente a 25 puntos base. Tampoco debemos agregar el nivel macroeconómico externo o la decisión efectiva posterior como si estuvieran expresados en la intervención.

### 4.3 Pruebas conductuales, no solo una métrica global

CheckList propone cruzar capacidades lingüísticas con pruebas de funcionalidad mínima, invariancia y cambios direccionales esperados; identifica fallos que pueden quedar ocultos en métricas agregadas. Sus demostraciones son de otras tareas NLP, no de nuestras actas. R08: [1](https://aclanthology.org/2020.acl-main.442/).

**Batería didáctica propuesta, todavía no construida ni ejecutada:**

| Fenómeno | Ejemplo inventado o transformación | Qué comprobar |
|---|---|---|
| Acción directa | «Propongo subir la TPM 25 puntos base» / «Propongo bajarla 25 puntos base» | Sensibilidad a dirección, no al número común. |
| Negación y apoyo | «Apoyo bajar la TPM» / «Rechazo bajar la TPM» | Identificar el cambio de respaldo; no invertir cualquier frase con «no». |
| Objeto | «Propongo reducir la TPM» / «Propongo reducir el estímulo monetario» | No confundir reducción de tasa con retiro de estímulo. |
| Opción sin preferencia | «Las opciones son subir o mantener; no expreso preferencia» | No convertir el menú en voto. |
| Condición prospectiva | «Si persiste la inflación, sería necesario subir la TPM» | Conservar el sesgo condicional según el codebook. |
| Contrafactual | Añadir un alza que el hablante habría apoyado bajo una condición que no ocurrió | Distinguir esa hipótesis de la opción que finalmente defiende; resolver con el texto completo. |
| Atribución | Añadir «La Fed elevó su tasa» a una recomendación chilena explícita | No trasladar mecánicamente la acción extranjera a la TPM. |
| Formato numérico | Cambiar `5,25 %` por `5.25%` sin alterar el valor | Invariancia al formato cuando la convención decimal es inequívoca. |
| Nivel y cambio | «Subir de 5 a 5,25 %» / «Bajar de 5,25 a 5 %» | Vincular extremos, orden y unidad. |
| Identidad | Sustituir un apellido por otro marcador conservando cargo, referencias y texto | Medir dependencia del nombre sin destruir atribución. |
| Recomendación final | Agregar diagnóstico neutral antes de una opción explícita | No diluir la recomendación ni truncarla. |

Las expectativas deben comprobarse con v2 antes de congelar los tests. No todos los cambios de país, tiempo o emisor son invariantes legítimos. Esta batería sería **de diagnóstico y desarrollo**, no una muestra representativa del corpus ni un test humano nuevo.

### 4.4 Abstención y confianza

La clasificación selectiva formaliza el intercambio entre **cobertura** y **error en lo aceptado**. El trabajo de Geifman y El-Yaniv usa imágenes; no demuestra garantías para nuestras etiquetas IA, reuniones dependientes o cambios históricos. R09: [1](https://arxiv.org/pdf/1705.08500).

La documentación de calibración explica por qué ajustar confianza con predicciones sobre el propio entrenamiento genera sesgo y exige datos separados o predicciones cruzadas. R12, §1.16.2–3: [1](https://scikit-learn.org/stable/modules/calibration.html).

**Aplicación propuesta:** marcar contradicciones o falta de evidencia para revisión, conservando la predicción de postura. Informar juntos cobertura, error de los aceptados, clases derivadas a revisión y carga de trabajo. No reportar solo «accuracy de los fáciles» como si cubriera todo el corpus. Una confianza de un LLM expresada en palabras, o dos ejecuciones concordantes, no equivalen a probabilidad calibrada de corrección.

Con nuestros datos, la calibración inicial sería contra **etiquetas IA**, no contra verdad humana independiente. Además, el pipeline completo incluye A: la confianza de B por sí sola no es la confianza de la salida final cuando A fuerza neutral.

### 4.5 Híbridos de reglas: una referencia y un límite

Snorkel trata las heurísticas como fuentes de supervisión débil con distinta cobertura, precisión y correlación, y combina señales en lugar de asumir que cada regla es verdad. R10: [5](https://arxiv.org/pdf/1711.10160).

Es una referencia útil para **no contar tres variantes de la misma expresión como tres evidencias independientes**. Pero aquí ya existen 1.352 etiquetas IA y el diccionario anterior no mejoró consistentemente. No hay evidencia revisada que justifique reetiquetarlas automáticamente con Snorkel. Una eventual expansión de etiquetas sería otra tarea, con autorización y validación propias.

## 5. Qué dicen los foros, y qué parte es fiable

| Fuente consultada | Consejo o experiencia | Contraste y decisión para nuestro caso |
|---|---|---|
| Stack Overflow, dígitos de un carácter, 2019 (R14) | Explica que el patrón predeterminado elimina `1`, pero conserva `11`. [1](https://stackoverflow.com/questions/57166660/in-what-way-the-tfidfvectorizer-deals-with-single-digit-numbers) | Confirmado por la API oficial R11. Añadir tokens de un carácter no conserva por sí solo un decimal completo ni su unidad. |
| Stack Overflow, números y fracciones, 2018; otra respuesta de 2020 (R15) | Propone `\S+` o un patrón limitado a letras ASCII, números y algunos signos. [4](https://stackoverflow.com/questions/50502999/token-pattern-for-numbers-in-tfidfvectorizer-sklearn-in-python) | Son soluciones a un ejemplo de materiales/fracciones, no a español monetario. `\S+` conserva puntuación pegada; el patrón ASCII no cubre letras acentuadas ni coma decimal. No copiar sin tests propios. |
| Hugging Face Forums, textos largos, 2023 (R16) | Enumera segmentar y combinar, truncar o usar modelos de contexto largo. La respuesta se recuperó explícitamente desde el mensaje 2. [1](https://discuss.huggingface.co/t/sentiment-analysis-for-long-text-canonical-solution/36897) | Es un menú técnico, no una comparación empírica monetaria. Resolver el error de longitud truncando puede borrar una conclusión. Hay que medir qué texto queda visible y conservar el contexto necesario. |
| Cross Validated, stacking, pregunta de 2020 y respuesta posterior (R17) | Hay explicaciones contrapuestas sobre para qué se usa la validación interna del ensamblado. [1](https://stats.stackexchange.com/questions/483888/cross-validation-in-stackingclassifier-scikit-learn) | La referencia decisiva es R13: el combinador aprende con predicciones fuera de muestra; esa CV no reemplaza la evaluación externa del pipeline completo. |
| DEV Community, pipeline de bancos centrales, 2026 (R19) | Describe separar acción, orientación futura, disenso y liquidez; ejecutar dos veces y revisar desacuerdos. También trata votar contra un alza como disenso dovish. [1](https://dev.to/aufklarer/building-an-nlp-pipeline-to-classify-225000-central-bank-sentences-gaf) | Es experiencia declarada, sin benchmark independiente documentado en la página leída. **Votar contra un alza no basta:** también podría quererse un alza mayor. La preferencia o razón del disenso debe estar en el texto. Dos temperaturas no son dos jueces independientes. |

Dos precisiones de implementación comprobadas en la documentación oficial:

- Un `tokenizer` personalizado preserva las etapas de preprocesamiento y generación de n-gramas. Un `analyzer` invocable produce directamente las características y deja de aplicar automáticamente `ngram_range`; no son intercambiables. R11: [1](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).
- `StackingClassifier` entrena el estimador final con predicciones cruzadas. Su opción `prefit` advierte un riesgo muy alto de sobreajuste cuando se usan predicciones de modelos ajustados sobre esos mismos registros; su CV interna no es la evaluación del modelo. R13: [1](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingClassifier.html).

**Balance de los foros:** sirven para detectar trampas de implementación y alternativas de diseño. No encontré en los hilos consultados una demostración controlada de que un arreglo concreto mejore H/D en intervenciones chilenas.

## 6. Arquitectura recomendada como hipótesis

No sería «modelo + lista de palabras que lo corrige». Sería:

```text
Intervención original e inmutable
  ├─ A: relevancia actual, congelada en la primera comparación
  └─ B: postura
       ├─ vista completa TF-IDF (1,4)
       ├─ vista numérica, solo en las variantes que la incluyen
       └─ vista de cláusulas de decisión, sesgo y argumentos con contexto
                         ↓
              combinación aprendida en train
                         ↓
              H / D / N + evidencia y bandera de revisión
```

**Preferencia inicial:** combinar características de las vistas con un clasificador regularizado, antes de añadir un meta-modelo de stacking. Permite preguntar si la representación contextual aporta sin incorporar de inmediato otra capa de selección y calibración.

Condiciones de diseño propuestas:

1. **Extraer candidatos no es decidir su postura.** Las reglas pueden ubicar cláusulas con TPM, opción, sesgo o estímulo; no decretar «mantener = D». Conservar negación, contraste y suficiente contexto dentro de la misma intervención.
2. **Conservar la vista completa.** Si no aparece una decisión explícita, aún puede existir inclinación por énfasis dominante. Si falla la extracción, registrar falta de evidencia; no convertirla automáticamente en neutral.
3. **Conservar pasado, futuro y condiciones.** Etiquetar el contexto de cada señal, sin invalidarla solo por ser histórica o condicional. Diferenciar una decisión pasada, una recomendación presente y un contrafactual no ocurrido conforme al texto y a v2.
4. **Conservar evidencia verificable.** Cada fragmento debe ser una subcadena del original, con posiciones; una explicación plausible no basta. Verificar la cita no garantiza que su interpretación sea correcta, por lo que ambos aspectos requieren control.
5. **No confundir contraste con contradicción real.** «Mantener hoy y subir después» puede ser coherente. La bandera debe reservarse para ambigüedades o desacuerdos no resueltos, no para toda mezcla de verbos.
6. **Tratar nombre y rol por separado.** Enmascarar apellidos sería primero una prueba de sensibilidad; no eliminar referencias necesarias ni reemplazar R5 por una regla rígida contra ciertos actores.
7. **No añadir datos externos al significado.** No usar etiquetas, fecha/identidad como atajo de postura histórica, decisión real de TPM ni textos de otras intervenciones para resolver una señal que v2 no permite heredar.

Un LLM podría producir esa estructura en español, o servir de comparador directo. Pero necesitaría versión exacta, prompt congelado, salidas inválidas registradas, citas verificadas y evaluación propia. Un encoder en español también necesitaría clasificación ajustada y un plan explícito para textos largos. **Ninguna de esas alternativas fue probada aquí.**

## 7. Comparación acotada propuesta, sujeta a autorización

### Paso 1 — Congelar el pequeño experimento

Primera ronda: **cuatro variantes**, sin búsqueda nueva de longitudes, sin nuevos diccionarios direccionales y manteniendo A y los parámetros base actuales. Detallar antes de entrenar el tokenizador, la vista contextual, sus límites y la escala de las características añadidas.

| Variante | Vista numérica corregida | Vista contextual | Pregunta |
|---|---|---|---|
| B0 | No | No | Referencia TF-IDF (1,4) ya seleccionada. |
| B1 | Sí | No | ¿Cuánto cambia al corregir la representación numérica? |
| B2 | No | Sí | ¿Qué aporta el contexto sin atribuirle una mejora del tokenizador? |
| B3 | Sí | Sí | ¿Son complementarios ambos cambios? |

Esto no presupone que B3 gane. No añadir automáticamente un quinto método tras ver resultados. Un transformer o un LLM serían una **segunda comparación autorizada** si el balance justificara el costo, no parte de una búsqueda ilimitada.

### Paso 2 — Comparar en desarrollo sin fingir independencia

La reserva de 793 ya se reutilizó y sus errores se inspeccionaron. Se puede emplear el mismo diseño para una comparación pareada de desarrollo; los resultados históricos deben permanecer intactos. **No llamar a sus nuevos resultados «test independiente».**

En cualquier nuevo entrenamiento, vocabulario, IDF, selección de rasgos, escalado y pesos se ajustan solo con train. Si se necesitara calibrador, umbral de revisión o stacking, aprenderlos en particiones internas de train, agrupadas por reunión; nunca sobre el fold externo evaluado. Una lista o prompt construido mirando los errores externos también es adaptación, aunque no cambie pesos.

Para una evaluación separada futura, prefijar control de duplicados antes de mirar resultados: reuniones y copias textuales deben quedar del mismo lado, por ejemplo mediante componentes que unan ambas relaciones. Si eso forma grupos demasiado grandes, documentarlo y acordar otra estrategia; no prometer cinco folds balanceados por defecto. No limpiar retrospectivamente los folds históricos para cambiar su puntuación.

### Paso 3 — Informar utilidad y daños, no solo el mejor promedio

Métrica principal propuesta: **macro-F1 de postura de la salida completa A+B**, con tres clases fijas y promedio por fold. Acompañar con:

- precisión, recall, F1 y soporte de H/D/N; matriz de confusión;
- H↔D, N→H/D y H/D→N, incluyendo errores nuevos introducidos;
- efecto por reunión y dispersión; cualquier intervalo debe respetar grupos, no asumir filas independientes;
- sensibilidad a nombres, formato decimal, opciones, negación, país y recomendación final;
- cobertura y errores de extracción, incluso fragmentos vacíos, inválidos o truncados;
- si hay revisión: cobertura global y por clase, error entre aceptados y número de casos derivados;
- tiempo, memoria y, si corresponde, costo de API y reproducibilidad.

A permanecería fija para aislar B, pero se seguirían informando sus errores. Mejorar B no puede resolver todos los problemas de relevancia.

**Criterio conservador:** una mejora de media sin estabilidad o acompañada de deterioro sustantivo en H/D no basta para adoptar. Las tolerancias prácticas deben prefijarse en el protocolo, no inventarse después de observar las tablas. Pasar los ejemplos conductuales conocidos es necesario para el comportamiento deseado, pero no demuestra generalización al corpus.

### Paso 4 — Confirmar antes de adoptar o puntuar todo

Los 306 humanos ya se examinaron y quedan fuera de este desarrollo. No volver a utilizarlos para elegir método, umbral o prompt y después presentarlos como prueba intacta. Una confirmación contra nuevas referencias humanas, o una evaluación de transferencia temporal, necesita diseño y autorización separados. Repartir de nuevo los mismos ejemplos conocidos no crea independencia.

Hasta entonces: **sin reajuste final con las 1.352, sin reemplazo del modelo guardado y sin scoring del corpus completo**. Si solo se dispone de evaluación IA reutilizada, la conclusión debe quedar limitada a desarrollo contra IA.

## 8. Recomendación final y límites de evidencia

| Conclusión | Fuerza de la evidencia |
|---|---|
| La tokenización actual puede fragmentar decimales y perder dígitos aislados. | Hecho de implementación: diagnóstico propio + documentación oficial. No demuestra por sí solo mejora de F1 al cambiarla. |
| Reglas léxicas simples pierden distinciones útiles para postura. | Evidencia en trabajos monetarios y casos propios; la mejor reparación local aún no está medida. |
| Representar emisor, objeto, apoyo y tiempo es una dirección razonable. | Apoyo conceptual de extracción estructurada, WCB y análisis por hablante; eficacia específica del híbrido pendiente. |
| Los modelos contextualizados merecen comparación. | Resultados favorables en tareas monetarias externas, con idiomas, unidades, métricas y protocolos diferentes. |
| El dataset internacional de Chile no debe importarse sin auditoría. | Diferencia de idioma/codebook e inconsistencia localizada en HTML v2; no auditoría de etiquetas externas. |
| Derivar dudas a revisión puede ser útil. | Marco de cobertura–riesgo; no garantía de error humano ni solución validada en nuestras reuniones. |

**En términos sencillos:** el siguiente paso no es enseñar que «bajar» significa D, sino representar si alguien **quiere bajar la TPM chilena**, con qué contexto y frente a qué alternativa. La investigación justifica probarlo; no permite afirmar todavía que mejorará el modelo.

## 9. Registro de fuentes y alcance de lectura

Identificadores Rxx propios de este informe. Los números de los enlaces corresponden a las referencias web; **no son una numeración bibliográfica única**. Consulta: **2026-09-16**. Se registran versiones y pasajes pertinentes, no copias completas de páginas, datasets o modelos.

| ID | Fuente / versión | Partes consultadas y función |
|---|---|---|
| R01 | Shah, Paturi, Chava. *Trillion Dollar Words: A New Financial Dataset, Task & Market Analysis*. ACL 2023. DOI 10.18653/v1/2023.acl-long.368. | PDF: introducción, dataset, métodos, resultados y tabla 5 (chunks 0–3). Inglés; frase; F1 ponderado. No reproducción ni lectura de todos los apéndices. |
| R02 | Tobback, Nardelli, Martens. *Between hawks and doves: measuring central bank communication*. ECB WP 2085, julio 2017. | PDF: resumen, §3.1, partes de §3.2 y §4, tablas 4–5 (chunks 0, 2, 4–5). Noticias inglesas; H/D; accuracy/AUC. No auditoría completa del corpus Factiva. |
| R03 | *Words That Unite The World: A Unified Framework for Deciphering Central Bank Communications*. arXiv **2505.17048v2**, noviembre 2025. | HTML: §§1–4 (chunks 0–3), apartado Chile y tablas 98–100 (74–75); navegación adicional 69–70. No lectura de los 80 chunks ni auditoría de los datasets. La alerta de Chile está verificada en HTML v2, no solo en un snippet v1; cotejo PDF/autores pendiente. |
| R04 | Peskoff y colaboradores. *GPT Deciphering Fedspeak: Quantifying Dissent Among Hawks and Doves*. Findings of EMNLP 2023. | PDF: §§2.3–2.4 y comienzo §3 (chunk 1); ficha bibliográfica localizada. Uso de contexto y unidad por hablante; no se extrae aquí una promesa cuantitativa para Chile. |
| R05 | Gambacorta, Kwon, Park, Patelli, Zhu. *CB-LMs: language models for central banking*. BIS WP 1215, octubre 2024. | Ficha oficial y PDF, introducción y §§4–7 (chunks 0, 2–5). Se usó el PDF bajo `/publications/`, pues el enlace antiguo `/publ/work1215.pdf` redirigió a la ficha. No lectura integral de apéndices; el extractor limita PDFs a 30 páginas. |
| R06 | Barnes y colaboradores. *SemEval 2022 Task 10: Structured Sentiment Analysis*. | PDF: resumen y §§1–4 (chunk 0). Estructura holder/target/expression/polarity y lenguas; no se trasladan puntuaciones de otros dominios. |
| R07 | Chen y colaboradores. *Overview of the NTCIR-15 FinNum-2 Task: Numeral Attachment in Financial Tweets*, 2020. | PDF: §§1–3 y tabla 5 (chunk 0). Se toma el problema de vinculación número–entidad; no se comparan sus scores con postura monetaria. |
| R08 | Ribeiro, Wu, Guestrin, Singh. *Beyond Accuracy: Behavioral Testing of NLP Models with CheckList*. ACL 2020. DOI 10.18653/v1/2020.acl-main.442. | Ficha y PDF, introducción y figura 1 (chunk 0). Funcionalidad, invariancia y dirección; no reproducción de sus experimentos. |
| R09 | Geifman, El-Yaniv. *Selective Classification for Deep Neural Networks*, 2017, arXiv 1705.08500. | PDF: introducción y comienzo de formulación (chunk 0); búsqueda primaria de definiciones cobertura–riesgo. Transferencia metodológica desde imágenes, no garantía local. |
| R10 | Ratner y colaboradores. *Snorkel: Rapid Training Data Creation with Weak Supervision*. PVLDB 2017. DOI 10.14778/3157794.3157797. | PDF: resumen, introducción y ejemplo 1.1 (chunk 0); búsqueda sobre funciones y correlación. Solo referencia conceptual, no implementación. |
| R11 | scikit-learn, `TfidfVectorizer`, documentación **1.9.1** consultada. | Parámetros `token_pattern`, `tokenizer`, `preprocessor`, `analyzer`, `ngram_range` (chunk 0). Fuente oficial para semántica de API. |
| R12 | scikit-learn, *Probability calibration*, documentación **1.9.1** consultada. | Curvas y §§1.16.2–3 (chunks 0–1). Separación de datos, predicciones cruzadas y límites de interpretar probabilidades. |
| R13 | scikit-learn, `StackingClassifier`, documentación **1.9.1** consultada. | Descripción y parámetros `cv`/`prefit` (chunk 0). No se probó su integración con nuestros grupos. |
| R14 | Stack Overflow, pregunta 57166660, 23-07-2019. | Pregunta y respuesta completas sobre tokens de un carácter. Consejo corroborado con R11. |
| R15 | Stack Overflow, pregunta 50502999, 24-05-2018; segunda respuesta 08-11-2020. | Pregunta y ambas respuestas (chunk 0; resto principalmente interfaz). Regex para fracciones; límites para español analizados aquí. |
| R16 | Hugging Face Forums, hilo 36897, 17/22-04-2023. | Pregunta y respuesta de `ccdv`, esta última en `/2`. Alternativas para secuencias largas, no benchmark. |
| R17 | Cross Validated, pregunta 483888, 2020 y respuestas posteriores. | Pregunta y discusión sobre fuga al entrenar el combinador (chunk 0 y texto indexado). No se adopta la explicación que confunde la CV interna con evaluación. Contraste oficial R13. |
| R18 | Banco Central de Chile, *Esquema de metas de inflación*, FAQ 7-3. | Contenido oficial recuperado en búsqueda: proyección de inflación a dos años en 3 %. Verificación puntual, no reconstrucción de todos los regímenes históricos. |
| R19 | DEV Community, *Building an NLP Pipeline to Classify 225,000 Central Bank Sentences*, 2026. | Cuerpo del artículo (chunk 0; resto interfaz/comentarios). Experiencia de practicante: no resultados de validación independiente. No se adoptan sus tasas actuales ni su equivalencia automática disenso=dovish. |
| R20 | Jiménez-Zafra, Morante, Blanco, Martín-Valdivia, Ureña-López. *Detecting Negation Cues and Scopes in Spanish*. LREC 2020. | PDF: introducción, corpus y metodología CRF (chunks 0–1). Se consultó el diseño de detección/alcance; no se trasladan sus resultados a Chile ni se reprodujo el sistema. |

### Límites de búsqueda y acceso

Se priorizaron fuentes primarias y documentación oficial sobre resúmenes comerciales. Búsquedas sobre modelos financieros genéricos devolvieron recursos de sentimiento positivo/negativo que se descartaron como evidencia directa de H/D. No se reprodujeron repositorios externos ni se verificaron licencias de datasets/modelos para una eventual importación: eso sigue siendo requisito antes de reutilizarlos.

La descarga directa del HTML de arXiv desde Python falló por TLS; la lectura se realizó con la herramienta de páginas, sin desactivar verificaciones de seguridad. Las conversiones HTML/PDF pueden introducir errores de tablas y fórmulas. Por eso, las cifras se usan con su métrica y contexto, no se transcriben gráficas aproximadas y la observación de la tabla chilena queda limitada explícitamente a la versión HTML consultada.

**Cierre:** solo documentación nueva y actualización del estado del proyecto. Las verificaciones de este cierre son de integridad de archivos y enlaces; no nuevas pruebas de rendimiento ni entrenamiento.
