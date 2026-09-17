# Investigación: postura monetaria, modelos actuales y límites del «SOTA»

**Corte de búsqueda: 16-09-2026.** Investigación documental realizada mientras el investigador informa que otro agente, mediante Antigravity, prepara la ejecución de BETO. No se recibieron todavía resultados ni una prueba GPU verificable de ese entorno. **Este informe no cambia la corrida, las referencias, el código ni las dependencias.**

## 1. Conclusión para nuestro proyecto

1. **Terminar y revisar BETO antes de cambiar de candidato.** No sabemos aún si mejora nuestro control. Una novedad publicada no justifica interrumpir la comparación autorizada.
2. **MrBERT-es es el candidato nuevo que priorizaría si hiciera falta otra comparación.** La ficha del BSC lo describe como un encoder español–inglés de 150M parámetros y 8.192 tokens; el paper de febrero de 2026 reporta el mejor promedio de su comparación española. Es una razón para probarlo, no evidencia de superioridad en nuestras actas. [1](https://huggingface.co/BSC-LT/MrBERT-es) [7](https://arxiv.org/pdf/2602.21379)
3. **No equiparar «modelo más grande/nuevo» con mejor clasificador monetario.** WCB encuentra que RoBERTa-Large ajustado supera, en promedio, a sus LLM evaluados mediante zero-shot; también que ModernBERT-Large no gana globalmente. Es una comparación de estrategias concretas, no una prueba de inferioridad universal de los LLM. [8](https://arxiv.org/html/2505.17048v1)
4. **Si persisten errores de negación, objeto de la acción o respaldo, una clasificación estructurada podría ser más informativa que seguir cambiando encoders.** Ornithologist ofrece una referencia de taxonomías y decisiones explícitas, pero sus resultados tampoco autorizan a prometer mayor precisión. [2](https://arxiv.org/abs/2505.09083)
5. **No encontré una comparación pública que establezca el SOTA exacto de nuestra tarea:** intervención completa, español chileno, referencia v2, mismos folds y A, con evaluación de H↔D y H/D→N. Esta es una conclusión limitada a la búsqueda realizada, no prueba de que tal trabajo no exista.

**Mi recomendación:** mantener una lista corta de alternativas condicionada por los resultados, no construir otro conjunto de decenas de scripts. La limpieza extrema final sigue siendo obligatoria.

## 2. Qué significa SOTA aquí

Hay que separar cuatro preguntas:

| Pregunta | Qué evidencia serviría | Qué no basta |
|---|---|---|
| ¿Qué modelo comprende mejor español? | Comparación española con tareas, particiones y métricas explícitas | Liderar un promedio de NER, QA y clasificación no prueba H/D/N |
| ¿Qué modelo clasifica postura monetaria? | Dataset de postura y comparación controlada | Sentimiento financiero positivo/negativo o reconocimiento de jerga |
| ¿Qué modelo resuelve intervenciones completas? | Documento como unidad, cobertura y contexto entre segmentos | Resultados sobre frases aisladas o una ventana truncada |
| ¿Qué modelo mejora FASE_2? | Mismos datos v2/folds/A y criterios fijados, seguido después por confirmación nueva | Comparar nuestra F1 H/D con otra accuracy o F1 ponderada |

Nuestro punto de partida interno es **F1 H/D medio 0,747060**, 15 inversiones H↔D, 12 H/D→N y 24 N→H/D sobre 793 validaciones. Es desarrollo reutilizado y asistido. Ninguna cifra externa de este informe se presenta como directamente comparable con esos valores.

## 3. Trabajos directamente relacionados con bancos centrales

### 3.1 WCB — *Words That Unite The World* (2025)

**Qué estudia.** Tres tareas separadas: postura, temporalidad e incertidumbre. La postura tiene cuatro clases: H, D, N e irrelevante. La selección de bancos utiliza documentos disponibles en inglés; no es un benchmark nativo de español chileno. [8](https://arxiv.org/html/2505.17048v1)

**Resultado que sí conviene retener.** En el escenario General/All-Banks, los autores reportan media de F1 ponderada **0,740 para RoBERTa-Large ajustado**, **0,723 para ModernBERT-Large** y **0,620 para Llama-3-70B en zero-shot**. La fila Chile reporta 0,799 para RoBERTa-Large en ese escenario. El propio texto identifica a RoBERTa-Large como mejor modelo promedio para postura. Las variantes de few-shot y guía de anotación dan mejoras marginales de postura en los experimentos adicionales descritos. [8](https://arxiv.org/html/2505.17048v1)

**Lectura crítica.** No significa que RoBERTa gane a cualquier LLM ajustado, que 0,799 sea alcanzable aquí, ni que nuestro 0,747 sea peor/mejor: cambian idioma, unidad, datos, clases y métrica. El componente de comparación humana usa una muestra pequeña y una persona sin guía; no es evidencia general de superioridad sobre especialistas. [8](https://arxiv.org/html/2505.17048v1)

**Aplicación propuesta, no ejecutada.** Mantener separados «temporalidad», «incertidumbre» y «dirección». No convertir cada condicional en N ni cada expectativa en postura. El piloto WCB previo del proyecto sigue siendo limitado y no autoriza incorporar ahora sus datos o traducir nuestras actas para usar sus modelos.

### 3.2 BIS — *CB-LMs: language models for central banking* (2024)

**Qué estudia.** Adaptación de BERT/RoBERTa con discursos y papers de banca central, seguida de ajuste para postura de frases FOMC. La evaluación descrita usa **1.243 frases**, particiones aleatorias **80/20** y 30 divisiones seleccionadas para conservar aproximadamente la distribución de etiquetas. No equivale a nuestra separación por reunión con purga. [7](https://www.bis.org/publ/work1215.pdf)

**Resultado.** El texto reporta aproximadamente **84% de accuracy** para el mejor CB-LM frente a **81%** para RoBERTa base; los BERT adaptados no muestran la misma mejora clara. El paper distingue además el problema de frases oficiales del de noticias extensas, donde los modelos generativos grandes pueden rendir mejor. [7](https://www.bis.org/publ/work1215.pdf)

**Lección.** La adaptación al dominio puede ayudar, pero no siempre. Mi inferencia para FASE_2: no iniciar un preentrenamiento adicional costoso solo porque aparece la palabra «financiero». Si más adelante se prueba adaptación no supervisada con nuestro corpus, debe definirse antes qué reuniones quedan excluidas; usar todo el corpus sin control puede introducir exposición transductiva a la validación. No es parte del ensayo actual.

No reutilizo como datos las tablas que el parser construye a partir de figuras, ni afirmaciones accesorias sobre tamaños no publicados de modelos comerciales. Las cifras anteriores provienen del texto de la sección 5.

### 3.3 RBA — *Ornithologist* (2025)

**Qué propone.** Taxonomía económica y árboles de decisión redactados por personas; un recuperador asigna temas y un LLM genera respuestas restringidas por una gramática. En los experimentos se usan Llama 3.2 3B y Phi 3.5 mini cuantizados, con clasificación a nivel de párrafo y frase. [2](https://arxiv.org/abs/2505.09083)

**Distinción crucial de métricas.** El **91% de micro-F1** corresponde al recuperador de temas y su validación de pares frase–tema. **No es 91% de precisión H/D/N.** En la validación manual de 100 párrafos, la tabla reporta para Llama **65% de accuracy de párrafo en tres clases** y **58% en cinco clases**. El propio autor advierte diferencias de contexto y evaluación respecto de otros estudios. [2](https://arxiv.org/abs/2505.09083)

**Qué tomaría.** Una salida breve y verificable con: acción monetaria, dirección, objeto, temporalidad, respaldo/rechazo y evidencia literal. Son campos propuestos para ordenar la decisión, no etiquetas nuevas ya aceptadas ni acceso al razonamiento interno de un modelo.

**Qué no asumiría.** Una gramática garantiza una forma válida de respuesta, no que la interpretación sea verdadera. Una explicación convincente puede justificar una clase equivocada. Tampoco copiaría árboles que necesitan inflación observada u otra información exterior, porque nuestro codebook exige resolver la unidad textual sin traer dirección de otra intervención.

### 3.4 *Mind the Shift / Delta-Consistent Scoring* (2026)

**Qué propone.** Representaciones congeladas de LLM, proyecciones para postura absoluta y cambio entre reuniones, y una pérdida que alinea ambos movimientos. Usa 200 comunicados FOMC de 2003–2025, filtrado de frases y anclas H/D posteriores para fijar el signo del eje aprendido. Es un preprint de marzo de 2026. [2](https://arxiv.org/html/2603.14313v1)

**Resultado publicado.** La tabla 1 reporta accuracy **0,7108** para Qwen3-4B/DCS. No traslado su F1 al indicador del proyecto: la tabla dice «F1» y el texto la describe como macro-F1; no se verificó esa definición contra implementación ni el tratamiento de neutrales. Además, el apéndice E configura **Max Length=512**, aunque se discuten comunicados completos. No auditamos su cobertura efectiva. [2](https://arxiv.org/html/2603.14313v1)

**Por qué no lo adoptaría ahora.** Cambia la pregunta hacia una trayectoria relativa entre reuniones. Sus anclas incluyen pausas o menor ritmo de endurecimiento como ejemplos D, lo que no coincide automáticamente con nuestras decisiones. «Sin etiquetas en el entrenamiento» tampoco significa ausencia total de decisiones humanas: existen prompts, filtros y anclas semánticas. [2](https://arxiv.org/html/2603.14313v1)

Mi evaluación: interesante para una futura serie agregada, no sustituto directo de la clasificación por intervención. Una correlación con inflación o niveles de rendimientos no verifica cada etiqueta ni demuestra causalidad de comunicación.

### 3.5 IMF — *From Text to Quantified Insights* (2025)

**Qué aporta.** Un marco de cuatro dimensiones: tema, orientación temporal, audiencia y sentimiento. En su terminología, «communication stance» significa **forward/backward-looking**, mientras que H/D aparece en otra dimensión junto con categorías adicionales. El trabajo aplica clasificación de frases a una colección multilingüe de 74.882 documentos de 169 bancos. [1](https://www.imf.org/en/publications/wp/issues/2025/06/06/from-text-to-quantified-insights-a-large-scale-llm-analysis-of-central-bank-communication-567522) [4](https://www.ecb.europa.eu/press/conferences/shared/pdf/20260323_forecasting/Gregarek_paper.pdf)

El texto metodológico consultado distingue el origen económico de una acción de sus efectos y advierte que la temporalidad no se obtiene solo del tiempo verbal. Por ejemplo, una frase de endurecimiento con efectos sobre estabilidad financiera no tiene por eso como tema principal «estabilidad financiera». Esa separación tiene relación directa con nuestros problemas de objeto/diagnóstico/decisión. [4](https://www.ecb.europa.eu/press/conferences/shared/pdf/20260323_forecasting/Gregarek_paper.pdf)

**Límite de lectura.** Se leyeron introducción y partes de metodología mediante una copia institucional alojada en el ECB. Algunas peticiones fallaron y el parser dedicó gran parte de la salida a tablas aproximadas de gráficos; esas tablas no se usan. El índice del buscador para el PDF oficial describe 840 ejemplos de train y 360 reales para validación, pero no se auditó su implementación ni el agrupamiento por documento. No afirmo haber reproducido métricas, verificado todos sus splits o descargado un clasificador. [2](https://www.imf.org/en/-/media/files/publications/wp/2025/english/wpiea2025109-print-pdf.pdf)

### 3.6 Türkiye — *Fine-Tuning Language Models to Decode Monetary Policy Tone* (2026)

El resumen de *Computational Economics*, publicado el 31-07-2026, describe un RoBERTa-Large específico para el CBRT y una evaluación ordenada temporalmente, con análisis por regímenes y autoridades. Es una referencia reciente en una economía emergente. [6](https://link.springer.com/article/10.1007/s10614-026-11397-6)

**Solo se tuvo acceso al resumen, notas y disponibilidad de datos/código; el cuerpo está bajo suscripción.** No compré acceso ni descargué el dataset. No verifico cifras de clasificación, diseño detallado de anotaciones o ausencia de fuga solo porque el resumen mencione time-order split. Para nuestro proyecto su aporte es recordar que una confirmación temporal futura responde una pregunta distinta a la validación de desarrollo que ya reutilizamos.

### 3.7 RAG para informes monetarios — por qué no basta un «score de validación»

El artículo *Hawkish or Dovish? That Is the Question: Agentic Retrieval of FED Monetary Policy Report* presenta un sistema RAG para informes largos y reporta un indicador integrado de validación de 0,796, combinando diagnósticos semánticos, numéricos y de estabilidad. **Ese número no debe interpretarse como 79,6% de accuracy H/D/N.** La descripción indexada de metodología/evaluación se revisó, pero no se auditó de extremo a extremo el sistema ni una comparación con nuestro problema. [4](https://www.mdpi.com/2227-7390/13/20/3255)

Mi recomendación: no añadir por ahora un buscador/vector DB/agentes a un problema que ya tiene la intervención completa disponible. Recuperar fragmentos puede ser útil más adelante, pero podría omitir una negación o conclusión que cambia la dirección.

## 4. Modelos: lista corta y prioridades, no una orden de entrenarlos todos

| Familia / candidato | Evidencia y encaje | Prioridad propuesta después de recibir BETO |
|---|---|---|
| **BETO actual** | Candidato ya autorizado; protocolo propio congelado. Sigue sin resultados recibidos aquí | Terminar primero |
| **MrBERT-es** | 150M, español–inglés, 8.192 tokens, Apache-2.0; promedio 89,83 en la comparación EvalES de los autores | Primer candidato nuevo si los resultados justifican otro ensayo |
| **mmBERT** | Encoder multilingüe moderno; paper reporta mejoras frente a XLM-R en sus benchmarks | Alternativa si ampliar idiomas fuera necesario; no entrenarlo además de MrBERT por inercia |
| **MarIA / RoBERTa-BNE** | Encoder español clásico; la ficha actual de `PlanTL-GOB-ES/roberta-base-bne` advierte que está deprecado y remite a BSC-LT | Referencia histórica/compatibilidad, no llamarlo SOTA actual |
| **BGE-M3 + clasificador lineal** | Embeddings multilingües, 8.192 tokens; la cabeza propia podría aprender H/D/N sin ajustar todo el encoder | Alternativa de menor coste de entrenamiento, no necesariamente menor coste total de inferencia |
| **Qwen3.5-4B con salida estructurada** | Familia generativa abierta, modelo concreto accesible y multilingüe; no es una comparación monetaria validada | Diagnóstico semántico posterior, si persisten errores de objeto/negación/respaldo |
| **Gemma 4 E4B** | Otra alternativa generativa actual; «E4B» alude a parámetros efectivos, no a 4B totales | Reserva condicionada a recursos y licencias verificadas, no otro ensayo automático |

Fuentes de la tabla: MrBERT [1](https://huggingface.co/BSC-LT/MrBERT-es); mmBERT [8](https://arxiv.org/html/2509.06888v1); aviso MarIA [2](https://huggingface.co/PlanTL-GOB-ES/roberta-base-bne); BGE-M3 [4](https://huggingface.co/BAAI/bge-m3); familia Qwen y disponibilidad de 4B [1](https://github.com/QwenLM/Qwen3.8); Gemma [2](https://huggingface.co/google/gemma-4-E4B).

### Detalles que cambian la elección

**MrBERT-es no es «89,83% de acierto monetario».** La tabla mezcla F1, accuracy y correlación de tareas generales, con modelos de comparación seleccionados por sus autores. En tareas individuales no gana siempre. No se verificó una réplica independiente ni un benchmark de nuestras actas. La ficha presenta el artefacto como modelo fundacional de masked language modeling: necesita una cabeza y ajuste para clasificar nuestras etiquetas. [1](https://huggingface.co/BSC-LT/MrBERT-es) [7](https://arxiv.org/pdf/2602.21379)

**8.192 tokens no significan memoria gratuita ni cobertura demostrada del corpus.** Habría que tokenizar con su propio tokenizer, medir desbordes y memoria real. El contexto largo permite comunicación entre más partes del texto, pero no garantiza que la decisión final reciba el peso correcto.

**Embedding no equivale a postura.** BGE-M3 está diseñado para varias modalidades de recuperación y similitud; la dirección H/D necesita una evaluación propia. La ficha también documenta una corrección previa de su evaluación MIRACL, ejemplo de por qué hay que registrar versión y no copiar sin más un número de leaderboard. [4](https://huggingface.co/BAAI/bge-m3)

**No escoger por el nombre comercial del tamaño.** La ficha de Gemma 4 E4B distingue 4,5B efectivos de 8B con embeddings. Tampoco «parámetros activos» de un MoE equivale a memoria de todos sus pesos. No se presupone que un modelo quepa en una T4 por su nombre. [2](https://huggingface.co/google/gemma-4-E4B)

**Qwen3.5-4B no se presenta como el último lanzamiento.** El repositorio oficial consultado ya agrupa Qwen3.5/3.6/3.8. Se incluye 4B como ejemplo concreto de generador relativamente manejable, no como ganador vigente de un ranking de chat. La ficha leída anuncia contexto largo y resultados generales, no una evaluación H/D/N de Chile. [1](https://github.com/QwenLM/Qwen3.8) Ficha consultada: https://huggingface.co/Qwen/Qwen3.5-4B.

**FinBERT requiere mirar el checkpoint exacto.** La ficha de `ProsusAI/finbert` produce positivo/negativo/neutral, no H/D/N; no se pueden renombrar esas salidas. Otras variantes financieras son modelos de preentrenamiento y no deben confundirse con ese clasificador. La falta de liderazgo de FinBERT-Pretrain en WCB refuerza la necesidad de evaluar la tarea, no solo el dominio del nombre. [8](https://arxiv.org/html/2505.17048v1) Ficha consultada: https://huggingface.co/ProsusAI/finbert.

## 5. Documentos largos: dos problemas diferentes

**Cobertura:** que todos los tokens entren al sistema. Nuestro BETO propuesto procesa ventanas completas y promedia logits por intervención.

**Integración:** que el sistema relacione la alternativa mencionada, su negación y la preferencia final. El promedio de logits no convierte ventanas independientes en razonamiento documental. Esta limitación ya estaba declarada en el protocolo propio.

*Lost in the Middle* encuentra sensibilidad a la posición de información relevante en tareas de QA multidocumento y recuperación de claves. Su abstract apoya separar longitud admitida de aprovechamiento real, pero no prueba que BETO o MrBERT fallen en nuestras actas de esa misma forma. [2](https://aclanthology.org/2024.tacl-1.9/)

Los trabajos de clasificación jerárquica y comparación de estrategias largas ya revisados están registrados en `INVESTIGACION_Y_PROTOCOLO_BETO_V1.md`. No se releen ni se reproducen íntegramente aquí. Una agregación aprendida de segmentos podría ser un candidato futuro; con pocos ejemplos direccionales también puede sobreajustar. No la introduciría a mitad de la corrida ni entrenaría cada ventana copiando ciegamente la etiqueta documental.

## 6. Foros e incidencias: utilidad práctica, no evidencia de precisión

### Caso verificado: ModernBERT y FlashAttention

El issue **Transformers #35879**, de enero de 2025, describe un fallo en V100 al cambiar a SDPA después de cargar el modelo. **Está cerrado como resuelto**, no es evidencia de que ModernBERT siga siendo incompatible con esas GPU. La discusión enlazada contiene la sugerencia de Tom Aarsen: indicar `attn_implementation` al cargar, en lugar de cambiar un atributo después; el autor del reporte confirma que SDPA/eager le funcionó. [2](https://github.com/huggingface/transformers/issues/35879)

Discusión consultada completa: https://huggingface.co/answerdotai/ModernBERT-base/discussions/56.

**Lección aplicable:** comprobar modelo, versión, GPU y backend de atención como conjunto. No instalar FlashAttention por rutina ni trasladar una solución de 2025 como garantía universal. La documentación actual consultada de Transformers muestra APIs de una versión posterior a la fijada para BETO; no se deben copiar instrucciones de `main` como si pertenecieran a nuestro lock. Documentación consultada: https://huggingface.co/docs/transformers/model_doc/modernbert.

### Caso metodológico: duplicar etiquetas al dividir ejemplos

En el hilo de Hugging Face sobre `Dataset.map`, una respuesta explica cómo repetir una etiqueta para cada fragmento. La respuesta aparece en el contenido indexado del buscador; el render del hilo no devolvió todos los cuerpos de respuestas. Es una solución de representación de datos, **no una validación de que cada fragmento conserve la postura del documento**. [2](https://discuss.huggingface.co/t/weird-example-of-batching-in-dataset-map-document/24861)

Mi evaluación: copiar esa receta aquí puede asignar H a una ventana que solo cita una alternativa rechazada o D a un diagnóstico sin adhesión. El protocolo actual evita tratar cada segmento como observación etiquetada independiente.

### Qué no tomé como prueba

Las búsquedas de Reddit devolvieron sobre todo anuncios y enlaces a lanzamientos; se usaron para localizar fuentes, no como benchmarks independientes ni consenso de usuarios. Los blogs de rendimiento, precios de proveedores y resúmenes automáticos tampoco justifican cifras de memoria o precisión para nuestra carga. Un reporte de «me funciona» prueba, a lo sumo, esa combinación concreta relatada por su autor.

## 7. Qué haría con los resultados que lleguen

### Paso 1 — verificar antes de interpretar

- Procedencia del ZIP, versión de scripts/dependencias y cualquier cambio hecho por el agente externo.
- Mismo paquete/folds/A/referencia; cinco grupos completos, sin mezclar versiones.
- Prueba real GPU y cobertura de todos los documentos; pérdida finita, predicciones y probabilidades válidas.
- No tratar una instalación terminada, una pérdida baja o un JSON de salida como una prueba suficiente de entrenamiento válido.

### Paso 2 — comparación que ya está autorizada

Mantener los criterios fijados: menos H↔D sin más H/D→N; F1 H/D medio al menos +0,02 y mejora en ≥3/5 folds, guardas macro/recall. Ver también N→H/D y matriz completa. Los cinco ambiguos conocidos se muestran aparte, pero no desaparecen del resultado principal.

### Paso 3 — escoger como máximo el siguiente movimiento útil

| Resultado observado | Siguiente decisión propuesta, no automática |
|---|---|
| BETO mejora y cumple las guardas | Revisar estabilidad y diseñar confirmación realmente nueva; no entrenar otra familia por moda |
| BETO empeora o es inestable con pocos direccionales | Conservar TF-IDF; revisar entrenamiento/referencias ya fijadas y considerar una única alternativa de representaciones congeladas |
| Errores se concentran en intervenciones con evidencia repartida | Considerar MrBERT-es de contexto largo con cobertura medida; probar una hipótesis concreta |
| Persisten confusiones de objeto/negación/adhesión incluso con contexto suficiente | Considerar una única comparación estructurada inspirada en taxonomías, con prompt fijado y evidencia verificable |
| BETO aún no puede ejecutar la prueba técnica | Resolver entorno/código y registrar cambios; no interpretar el bloqueo como fracaso predictivo del modelo |

No optimizar reiteradamente prompts o hiperparámetros sobre los diez casos conocidos. Si se emplean ejemplos few-shot, deben proceder exclusivamente del train del fold correspondiente, sin reuniones/textos de validación. Las explicaciones generadas no sustituyen adjudicación independiente.

## 8. Alcance de la investigación y registro de lectura

**No es una revisión sistemática exhaustiva ni una reproducción experimental.** Se buscaron postura monetaria, trabajos de bancos centrales de 2024–2026, encoders españoles/multilingües, documentos largos, modelos abiertos actuales y discusiones técnicas. Se priorizaron papers/fichas de autores; las fuentes secundarias se trataron como pistas.

No se descargaron modelos/datasets para entrenar, no se contrataron servicios y no se añadieron scripts de experimentos. Se excluyeron como evidencia cuantitativa los gráficos convertidos automáticamente en tablas, los anuncios sin comparación y los artículos cuyo cuerpo no quedó accesible.

| Registro | Fuente / versión consultada | Lectura efectiva y límite |
|---|---|---|
| R01 | WCB, arXiv 2505.17048v1 [8](https://arxiv.org/html/2505.17048v1) | Chunks 1,3,4,5,6: definición, modelos, tabla y discusión. No todos los 82 chunks/apéndices |
| R02 | BIS WP1215, octubre 2024 [7](https://www.bis.org/publ/work1215.pdf) | Página institucional y PDF en URL nueva, chunks 0,2,3. Texto de métodos/resultados; no tablas inferidas de gráficos |
| R03 | Ornithologist, arXiv 2505.09083v1 [2](https://arxiv.org/abs/2505.09083) | HTML chunks 0 y 2: motivación, generador y tabla de validación. No reproducción ni lectura completa econométrica |
| R04 | DCS, arXiv 2603.14313v1 [2](https://arxiv.org/html/2603.14313v1) | Chunks 2,3,8,9: objetivo, evaluación, anclas, filtro e hiperparámetros. Código/métricas no auditados |
| R05 | IMF WP25/109, copia institucional ECB [4](https://www.ecb.europa.eu/press/conferences/shared/pdf/20260323_forecasting/Gregarek_paper.pdf) | Chunks 0,4,5,10,12; intentos de 11 fallidos. Secciones de texto, no gráficos. PDF IMF directo falló |
| R06 | IMF, extracto indexado de metodología [2](https://www.imf.org/en/-/media/files/publications/wp/2025/english/wpiea2025109-print-pdf.pdf) | Extracto de buscador sobre train/validación; no código ni apéndice completo |
| R07 | CBRT, Computational Economics, julio 2026 [6](https://link.springer.com/article/10.1007/s10614-026-11397-6) | Resumen/notas/disponibilidad. Cuerpo bajo suscripción; repositorio de datos no importado |
| R08 | RAG/MPR, Mathematics 2025 [4](https://www.mdpi.com/2227-7390/13/20/3255) | Resumen/metodología indexados; fetch inicial dominado por navegación. No auditoría completa |
| R09 | MrBERT, arXiv 2602.21379v1 [7](https://arxiv.org/pdf/2602.21379) | HTML chunks 0 y 3: motivación y evaluación; preprint, no aceptación de congreso inferida de plantilla |
| R10 | MrBERT-es, ficha oficial BSC [1](https://huggingface.co/BSC-LT/MrBERT-es) | Dos chunks completos de ficha; tamaño, contexto, tablas, licencia. No pesos descargados |
| R11 | mmBERT, arXiv 2509.06888v1 [8](https://arxiv.org/html/2509.06888v1) | Introducción y resultados indexados; no auditoría del preentrenamiento completo |
| R12 | MarIA/RoBERTa-BNE [2](https://huggingface.co/PlanTL-GOB-ES/roberta-base-bne) | Ficha indexada: aviso actual de deprecación, arquitectura y licencia. No confundir fecha del índice con lanzamiento |
| R13 | ModernBERT, ACL 2025 [1](https://aclanthology.org/2025.acl-long.127.pdf) | Resultados indexados y documentación oficial; no reproducción de velocidad |
| R14 | Lost in the Middle, TACL 2024 [2](https://aclanthology.org/2024.tacl-1.9/) | Ficha/abstract completos. No se extrapola su tasa de error a nuestros modelos |
| R15 | BGE-M3, autores [4](https://huggingface.co/BAAI/bge-m3) | Ficha indexada con funcionalidades y corrección MIRACL; no clasificación H/D/N propia |
| R16 | Qwen, repositorio oficial actual [1](https://github.com/QwenLM/Qwen3.8) | Noticias de disponibilidad indexadas; ficha Qwen3.5-4B chunk 0 leída. No confundir modelo considerado con último lanzamiento |
| R17 | Gemma 4 E4B, ficha Google [2](https://huggingface.co/google/gemma-4-E4B) | Chunk 0: parámetros efectivos/totales, arquitectura, contexto y licencia. No descarga ni medida de VRAM |
| R18 | Transformers issue #35879 [2](https://github.com/huggingface/transformers/issues/35879) | Cuerpo y resolución leídos; discusión HF #56 leída completa. Incidencia cerrada de enero 2025 |
| R19 | HF Dataset.map [2](https://discuss.huggingface.co/t/weird-example-of-batching-in-dataset-map-document/24861) | Inicio del hilo + respuestas indexadas; el render no devolvió todas las respuestas |
| R20 | ProsusAI/finbert | Ficha completa leída en https://huggingface.co/ProsusAI/finbert; se verificó que las salidas son sentimiento |

Las fichas web son mutables. Si se decide ejecutar cualquiera de estos candidatos, el primer paso será fijar revisión, hashes, licencia, tokenizer y entorno, **en una etapa nueva**. Los enlaces no constituyen un lock de pesos.

## 9. Decisión de esta continuación

**Investigación terminada en el alcance descrito; ninguna nueva variante adoptada o ejecutada.** Esperar evidencia del BETO que prepara el otro agente. MrBERT-es queda como primer candidato nuevo condicionado a necesidad, y la clasificación estructurada como alternativa para una hipótesis semántica concreta. No ampliar ahora la lista de scripts ni el dataset. Mantener la limpieza extrema final de `REGLAS.md` §12 como requisito de cierre.
