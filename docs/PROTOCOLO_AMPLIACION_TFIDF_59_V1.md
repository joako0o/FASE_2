# Ensayo TF-IDF con la ampliación disponible: 59 H/D nuevos

## Autorización y pregunta

El investigador pidió «prueba tfidf con estos aumentos haber si cambia algo». Se autoriza esta comparación antes de llegar a la meta de 300 H/300 D, no una búsqueda de parámetros o un cambio de referencias. Dos condiciones: control v2 y mismo TF-IDF B ampliado con la cohorte de alta confianza disponible.

## Fijado antes de ajustar

- Base: paquete `f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`, 1.352 documentos y 793 validaciones, cinco folds originales purgados. Se reconstruye/verifica con el script 38; no requiere encoder BETO.
- Cohorte: 59 nuevos IDs (29 H, 30 D) de los payloads de alta confianza de tandas 01–04. No se incluyen las reservas medias, N, dudas, E009 repetido ni la cola G pendiente. El corpus total potencial tiene 154 H/119 D, pero no todas las adiciones entran en cada fold.
- Para cada fold, excluir nuevos casos que compartan reunión o texto normalizado con su validación. Deben coincidir con los planes ya registrados: **53/51/52/50/53** altas. Las citas y textos se comprueban contra L0; no se abren las respuestas humanas de 306.
- A: TF-IDF unigramas y regresión logística ajustados únicamente sobre el train original de ese fold. Se comparten las mismas predicciones A en ambas condiciones; no se agregan casos a su entrenamiento.
- B: palabras n-gramas 1–4; strip_accents=unicode, lowercase, min_df=3, max_df=0,9, sublinear_tf; regresión logística C=2, class_weight=balanced, max_iter=2000, semilla 20260915. Sin otras variantes, selección de épocas, umbrales o búsqueda.
- Control: ajuste original usando los textos/etiquetas v2 del train original. **Debe reproducir exactamente A, B y predicción final** del control guardado antes de aceptar resultados ampliados.
- Ampliado: originales relevantes más nuevos permitidos; ajuste B desde cero. Vocabulario e IDF de B y ponderación balanced se recalculan exclusivamente con ese train ampliado. No se congelan artificialmente los IDF originales: su cambio es parte normal del efecto de añadir documentos. Ningún vocabulario se ajusta en validación.
- No truncar las intervenciones ni entrenar solo con las citas. No modificar OCR o traer dirección de otras unidades.

## Evaluación y decisión

Sobre los mismos 793 casos: F1 H/D media por fold, macro-F1 media, recalls H/D, matrices completas, H→D, D→H, H/D→N, N→H/D y cambios pareados. Reportar también el suplemento sin los cinco ambiguos conocidos, pero no quitarlos del criterio principal.

Se conservan como guardas de desarrollo: aumento de F1 H/D media ≥0,02, mejora en ≥3/5 folds, pérdida macro ≤0,005 y de recall H/D ≤0,02, menos inversiones sin más H/D→N. El resultado se reporta aunque no cumpla; no hay adopción automática.

La validación es desarrollo reutilizado/asistido, no test independiente. Los nuevos ejemplos fueron etiquetados por IA, no son gold humano. Un efecto favorable no prueba generalización. La lectura de errores posteriores no autoriza cambiar etiquetas para mejorar el score.

## Reproducción y limpieza

`python scripts/40_gestionar_proyecto.py evaluar-ampliacion-tfidf --salida RUTA_NUEVA`

Requiere entorno CPU instalado; no GPU, pesos BETO o APIs. El módulo `scripts/evaluar_ampliacion_tfidf.py` reutiliza el control histórico y registra protocolo/hashes **antes** de los ajustes. Exige salida inexistente y detiene ante falta de convergencia o fallo del control. Para repetir, otra ruta nueva. No persiste modelos, no hace refit global ni scoring general.

Las salidas contienen protocolo, inclusión/exclusión de los 59 por fold, predicciones de ambas condiciones, comparación pareada, métricas, ejecución y manifiesto. Las nuevas etiquetas siguen separadas del glob original: usarlas en este ensayo no equivale a reemplazar la base o el modelo de producción.
