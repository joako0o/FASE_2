# BETO: investigación dirigida y protocolo ejecutable v1

## 1. Qué aporta la investigación

La investigación de esta continuación fue dirigida, no una revisión sistemática exhaustiva ni una reproducción de los trabajos externos. No se incorporaron datasets ni etiquetas extranjeros.

| Fuente primaria y lectura realizada | Hallazgo pertinente | Decisión para nuestro proyecto |
|---|---|---|
| Bundesbank, *Monetary policy communication according to artificial intelligence*, marzo de 2025; introducción y sección de metodología (chunks 0 y 4). [5](https://publikationen.bundesbank.de/publikationen-en/reports-studies/monthly-reports/monthly-report-march-2025-952320?article=monetary-policy-communication-according-to-artificial-intelligence-952332) | MILA separa decisiones/perspectivas de tasas del relato económico, usa contexto y distingue postura de sentimiento. Sus cinco grados y su contexto macro no coinciden exactamente con nuestra tarea. | No etiquetar D por pesimismo ni confundir diagnóstico con voto. La separación es una guía interpretativa, no autorización para introducir contexto externo o cambiar el codebook. |
| Bernoth, DIW DP 2137, *Dovish Coos or Hawkish Screech?*, septiembre de 2025; introducción, metodología y otros fragmentos (0,1,2,5,8). [4](https://www.diw.de/documents/publikationen/73/diw_01.c.972687.de/dp2137.pdf) | Adapta un clasificador RoBERTa de comunicaciones Fed al BCE y agrega clasificaciones de frases. El método remite al apéndice A para ajuste. | Apoya evaluar adaptación al dominio, no transferir sus cifras a Chile. El apéndice no quedó accesible dentro de los 30 folios devueltos: no verificamos su partición ni su precisión. No usamos las tablas generadas por el parser a partir de gráficos. |
| Pappagari et al., *Hierarchical Transformers for Long Document Classification*, 2019; abstract, introducción y comienzo del método (PDF, chunk 0). [1](https://arxiv.org/pdf/1910.10781) | Segmenta documentos, obtiene representaciones BERT y agrega mediante LSTM/Transformer; preserva información temporal de conversaciones largas. | Fundamenta no truncar al inicio. Nuestro primer candidato de media de logits es más simple: no se presenta como implementación de ToBERT ni como equivalente a su agregación contextual. |
| Park, Vyas y Shah, *Efficient Classification of Long Documents Using Transformers*, 2022; abstract, introducción y métodos iniciales (HTML, chunk 0). [4](https://ar5iv.labs.arxiv.org/html/2203.11258) | Encuentra resultados inconsistentes de métodos complejos frente a baselines y compara precisión, tiempo y memoria. | Conservar TF-IDF como control, registrar coste y no dar por hecho que BETO o una jerarquía resolverán los diez ejemplos. |
| BETO, documentación de los autores y tarjeta HF. [5](https://github.com/dccuchile/beto/blob/master/README.md) [1](https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased/blob/main/README.md) | Modelo preentrenado en español, versiones cased/uncased, enlaces oficiales y cautela de licencias de corpus. | Usar cased y revisión fija, sin sustituir vocabulario o checkpoint por otro que solo tenga nombre parecido. Sus resultados generales no son resultados H/D/N locales. |

También se localizaron trabajos RAG y resúmenes secundarios, pero no se usaron para elegir un sistema nuevo ni para afirmar una precisión reproducida. No cambiamos el criterio de las referencias v2 tras leer la literatura.

## 2. Bloqueo comprobado y procedencia

`data/auditoria/preparacion_beto_v1/acceso.json` registra peticiones HTTPS reales: HF API/config/pesos, descarga histórica de los autores y servidor de wheels CPU de PyTorch fallan con TLS EOF. GitHub API y PyPI responden. Dos CPU lógicas, aproximadamente 4 GB RAM y sin dispositivos NVIDIA detectados. No desactivar TLS ni pedir contraseñas para un checkpoint público.

El navegador de investigación pudo leer metadatos del Hub, pero **no transfirió los pesos al entorno de entrenamiento**. La revisión se fija en `c4d86612f51b4f46759c8390d1798c2febe71b93`. La lista oficial contiene `pytorch_model.bin` (439.621.341 bytes), no `model.safetensors`. El registro `checkpoint.json` transcribe tamaños, Git blob IDs de archivos pequeños y SHA256 LFS del peso desde la API de esa revisión. El downloader debe comprobarlos todos antes de cargar.

El vocabulario recuperado del GitHub histórico de los autores tiene 242.120 bytes y blob distinto al vocabulario HF de 241.796 bytes. Se rechaza como sustituto. No se declara tokenización real de todo el corpus con un vocabulario aproximado. Los archivos exploratorios quedan fuera de Git y no son insumos de entrenamiento.

## 3. Entrada fija y aislamiento

Script 38 materializa un paquete de 1.352 registros desde la vista corregida v2, después de verificar la aceptación y los manifiestos históricos con el cargador de 36. Conserva los cinco train/validación purgados de 26 y las predicciones A congeladas de 36. No reentrena A ni usa citas del agente como entradas. Guarda solo ID, texto, hash, clase corregida y relevancia; las citas/notas no se exportan al modelo.

Las respuestas antiguas de 306 no se abren; el cargador histórico usa únicamente IDs de exclusión. Las 793 etiquetas de validación siguen siendo desarrollo reutilizado. Hay 19 decisiones aceptadas y 16 cambios efectivos frente a IA; no modificar los 12 ambiguos ni introducir una copia de la reunión validada en su propio train.

El paquete y cualquier resultado/checkpoint se guardan bajo `data/checkpoints/`, ignorado por Git. La preparación resumida y sus hashes sí quedan auditados. No publicar otra copia masiva del corpus o pesos. El notebook reconstruye el paquete desde una revisión del código fijada, no desde una rama mutable sin controles.

## 4. Candidato y entrenamiento

- BETO cased, checkpoint fijado, `BertForSequenceClassification` con tres clases ordenadas H/D/N; encoder y cabeza ajustables. No modelo remoto con código arbitrario: `trust_remote_code=False`, carga local tras hashes y `weights_only=True` con torch 2.6.0.
- Tokenizador del checkpoint, sin truncar. Primero tokenizar todo el documento sin especiales; ventanas de 510 tokens de contenido, solapamiento 64, más CLS/SEP: máximo 512. Registrar límites/longitudes de todos los documentos. Unir los tramos no repetidos debe reproducir exactamente la secuencia de IDs tokenizada, incluido el final. Esto es cobertura de tokens, no identidad de la decodificación con caracteres de entrada.
- Una predicción por intervención: media de logits de todos sus segmentos. Una sola pérdida por intervención, nunca repetir su etiqueta como si cada segmento fuera una observación independiente. Ventanas solapadas y media pueden diluir la conclusión; limitación explícita.
- Tres épocas, AdamW 2e-5, weight_decay=0,01, warmup 10%, clipping 1, FP32, gradient checkpointing, semilla 20260915. Orden aleatorio determinista por fold; no seleccionar época con validación.
- Acumulación de ocho documentos. Cada pérdida CE sin reducción se multiplica por el peso balanced de su clase calculado solo en train relevante y se divide por el tamaño real del grupo; el último grupo incompleto usa su tamaño, no ocho. **No usar CE ponderada con reducción mean sobre un único ejemplo**, porque normalizar por su propio peso lo cancelaría.
- Evaluar solo al terminar la tercera época; registrar las tres probabilidades B y predicción final con puerta A congelada. Guardar resultados por fold para no perder lo ya completado. No elegir variantes por las diez citas conocidas.
- Detener ante OOM, datos/hashes incompatibles, NaN o incumplimiento de cobertura. No bajar silenciosamente la longitud, usar solo la primera ventana ni cambiar el protocolo para que termine.

## 5. Prueba técnica antes de entrenar

El notebook exige GPU y versiones previstas. Descarga y verifica el checkpoint; ejecuta forward/backward y un paso de optimización con dos intervenciones completas de **train** del fold 1 (una larga incluida), comprueba pérdida/gradientes finitos, cambio de la cabeza y de un parámetro del encoder, y registra memoria/tiempo. Esa instancia se descarta: cada fold vuelve a cargar el checkpoint inicial y reinicia la semilla. No se puntúan estos ejemplos como evaluación.

La disponibilidad de los pesos y la prueba real son condiciones de entrada. En el entorno actual no hay pesos ni torch instalado: **no se declara aprobada la prueba con BETO**. Las pruebas locales cubren preparación, hashes, segmentación, combinación de logits y ponderación con cálculos de referencia; no sustituyen forward/backward con el encoder real. El runner y notebook GPU deben pasar esa prueba antes del experimento.

## 6. Cierre y comparación

Solo cuando existan los cinco folds verificados se genera una comparación completa contra el TF-IDF `seis_mas_trece`, con la misma referencia v2. Si falta uno, no emitir score final ni decisión de adoptar. Incluir matriz completa, H→D, D→H, H/D→N, N→H/D, F1 H/D medio, macro-F1 y recall H/D. Denominadores fijos, no solo casos predichos direccionales. Se desglosan las 15 inversiones conocidas, marcando las cinco ambiguas de 37, y se añade un suplemento sin esas cinco; los criterios principales siguen usando los 793, sin excluir errores oportunistamente.

Criterios de desarrollo ya fijados: delta F1 H/D ≥0,02 y mejora en ≥3/5 folds; pérdida macro ≤0,005 y recall H/D ≤0,02; menos inversiones sin aumentar H/D→N. Ni cumplirlos ni acertar los diez casos conocidos demuestra generalización. No reemplazar modelo histórico ni reabrir el examen antiguo; una confirmación realmente nueva sería posterior.

## 7. Estado de implementación y reproducibilidad

La preparación y controles sin encoder se ejecutan aquí. La descarga con hashes, entrenamiento y prueba real GPU quedan en scripts 38/39 y un notebook portátil. **Implementado no significa ejecutado con pesos reales**: el informe de esta etapa distingue esas dos cosas y lista los controles pendientes. No se fabrican métricas BETO.

Versiones adicionales en `requirements-beto.txt`, separadas del lock histórico. Registro de investigación/procedencia y controles en `data/auditoria/preparacion_beto_v1/`. Scripts/documentos históricos permanecen congelados. Los pesos, paquetes, resultados GPU y dependencias no se incluyen en el PR.
