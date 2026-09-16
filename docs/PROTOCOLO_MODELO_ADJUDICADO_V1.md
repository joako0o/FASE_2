# Modelo con adjudicaciones v1 — protocolo previo al ajuste

## 1. Autorización y alcance

El investigador aceptó las seis propuestas y pidió continuar con el modelo. Esta unidad incorpora esas decisiones **solo en una vista experimental**, sin editar L0, corridas IA, primera devolución humana, codebook v2 ni resultados anteriores. No importa canónicamente las 30 anotaciones incompletas ni reconstruye citas humanas.

La adjudicación asistida ya es información de desarrollo. El acuerdo original de 24/30 se conserva; no se recalcula como una mejora independiente. Las 306 respuestas anteriores no se leen ni predicen. El cargador histórico solo utiliza su marco de IDs para exclusión.

## 2. Datos y aislamiento del efecto de las etiquetas

Dos condiciones cerradas, mismos textos y parámetros:

- `original`: las 1.352 etiquetas IA históricas, como control reproducido.
- `adjudicada`: aplicar en memoria las seis decisiones aprobadas; solo R01 N→H, R03 D→N y R12 D→H cambian la etiqueta IA. R08/R17/R21 ya eran D. No propagar cambios a textos similares ni otras intervenciones.

Comprobar IDs, etiqueta anterior y SHA256 del texto contra la aceptación y propuesta congeladas. Las seis deben estar en el grupo fijo de descubrimiento (fold 0) y en todos los train purgados, nunca en validación. Conservar el flag de relevancia **IA**, sin presentarlo como revisión humana; las seis deben tener flag IA=1. La confianza del agente no se usa como confianza humana ni peso de entrenamiento.

Cinco folds por reunión y purga de copias exactamente iguales al experimento 26: train limpio 1.178/1.178/1.178/1.183/1.183; validación total 793, sin alterar sus etiquetas. Es desarrollo reutilizado, no un nuevo test ni estimación independiente. Las 559 de descubrimiento son un grupo fijo solo de train, no entrenamiento de un test-retest.

## 3. Comprobación ejecutable aquí: referencia TF-IDF

A: unigramas, min_df=3, max_df=0,9, strip_accents=unicode, lowercase, sublinear_tf, norma L2. B: mismo vectorizador con palabras 1–4; solo train IA relevante. Ambas LR: C=2, balanced, max_iter=2000, semilla 20260915. Reutilizar funciones congeladas de 26; no lanzar sus otras variantes ni regenerar su protocolo/checkpoint. Una advertencia de convergencia detiene el ajuste.

La condición original debe reproducir **todas** las predicciones A/B/finales de `B0_limpia`, no el ancla sin purga. La condición adjudicada debe tener la misma A y los mismos vocabularios; solo cambia la supervisión B y, como consecuencia natural de `balanced`, sus pesos por clase. No hay rejilla ni ajuste por los resultados.

Principal: media por fold de (F1_H + F1_D)/2 sobre todas las filas, incluyendo falsas alarmas en neutrales. Secundarias: macro-F1, precisión/recall/F1 por clase, matrices, cambios de predicción, errores corregidos/nuevos y deltas pareados. No declarar significación con cinco folds dependientes.

**Regla de cierre:** medir el efecto de tres adjudicaciones, no seleccionar cuál verdad conviene por mayor score contra IA. Aunque baje una métrica, no revertir decisiones humanas aprobadas para maximizar acuerdo con las etiquetas IA. No reemplazar el modelo histórico, no refit sobre 1.352 ni scoring completo. La condición adjudicada es la referencia que deberá compararse con BETO en igualdad de supervisión.

## 4. BETO: bloqueo actual y diseño de la siguiente ejecución

Comprobación de acceso en esta sesión: las peticiones HTTPS a `https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased/resolve/main/config.json` y `https://huggingface.co/api/models/dccuchile/bert-base-spanish-wwm-cased` fallaron con `URLError: TLS/SSL connection has been closed (EOF)`. Dos CPU lógicas y sin comando `nvidia-smi`; no GPU detectada. No se desactiva la verificación TLS ni se instalan bibliotecas grandes para fingir progreso. Sin pesos, no hay entrenamiento ni evaluación BETO. Este chequeo no diagnostica exhaustivamente el proveedor/red ni demuestra que BETO sea malo.

Diseño fijado antes de resultados BETO, **todavía no implementado ni validado con pesos reales**:

- Checkpoint `dccuchile/bert-base-spanish-wwm-cased`, revisión inmutable y hashes a registrar cuando se obtenga. Sin datasets externos ni pesos de procedencia no verificada.
- Misma vista adjudicada, folds/purga y puerta A que la referencia TF-IDF. B aprende solo de intervenciones relevantes. Comparar arquitectura sin mezclar cambios de etiquetas.
- Tokenizador del checkpoint; segmentos de hasta 512 tokens incluidos especiales, solapamiento de 64 tokens de contenido, cobertura de todo el texto incluido el final. No tomar solo los primeros 512 ni elegir frases con las citas/etiquetas. Exportar por caso longitud, número de segmentos y cobertura; exceso de recursos detiene el ensayo, no trunca silenciosamente.
- Encoder y cabeza H/D/N ajustables; media de logits de todos los segmentos de una intervención, una pérdida de entropía cruzada por intervención. El peso de una intervención no aumenta por tener más segmentos. Pesos de clases balanced calculados solo sobre las intervenciones relevantes del train. La media puede diluir una frase decisiva: limitación explícita, no extractor semántico garantizado.
- Primer ensayo cerrado: tres épocas, AdamW lr=2e-5, weight_decay=0,01, warmup 10%, clip gradiente 1, semilla 20260915, un documento por microbatch y acumulación de ocho documentos (ajuste correcto del último grupo incompleto). FP32/gradient checkpointing; no seleccionar la mejor época usando las 793 etiquetas: evaluar la última. Registrar dependencias, hardware y determinismo efectivo al preparar la ejecución real. GPU recomendada; si no cabe, detener y documentar antes de cambiar configuración.
- Principal y secundarias como arriba. Para proponer confirmación nueva: mejora ≥0,02 F1 H/D medio, mejora en ≥3/5 folds, pérdida macro-F1 ≤0,005 y pérdida de recall H y D ≤0,02; además no perder >0,05 de exactitud en la batería conductual conocida del experimento 26. La batería es diagnóstico, no test. No ampliar rejilla para hacer pasar estos umbrales.
- Solo si el desarrollo resulta favorable: congelar candidato y preparar confirmación humana realmente nueva, con suficientes H/D, reuniones/copias controladas. Las 306 anteriores no vuelven a ser test intacto.

## 5. Trazabilidad, pruebas y limpieza

Script 31 con preparación antes del primer `fit`, hashes, vista de cambios y controles de folds. Salidas exclusivas en `data/evaluacion/adjudicacion_modelo_v1/`; no duplicar el corpus ni guardar modelos. Reproducción en carpeta temporal usando el mismo protocolo preparado, sin reconsultar las 306 respuestas. Comparar CSV/JSON/informe salvo timestamps/manifiestos de ejecución.

Pruebas específicas de aplicación por ID, procedencia, rechazo de validación, texto/etiqueta discordante, clases/relevancia inválidas, purga, métricas con falsos positivos N y ancla histórica. No ejecutar la suite general que abre el examen antiguo. Los scripts 15–30 y resultados previos permanecen congelados. Este protocolo distingue trabajo ejecutado (referencia TF-IDF) de trabajo pendiente (BETO); no se crea un runner transformer vacío.
