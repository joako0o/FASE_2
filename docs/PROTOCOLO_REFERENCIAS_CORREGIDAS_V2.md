# Referencias corregidas v2 — protocolo previo al entrenamiento

## Autorización y referencia activa

El investigador pidió «corrige las referencias, e ittenta mandar el modelo en tu entorno» y después «sigue». Se aplican las **13 propuestas concretas** del cierre de los 66 desacuerdos. Se conservan las 12 referencias ambiguas sin adjudicar; no se inventa N. La decisión se registra en `data/auditoria/revision_errores_adjudicada_v1/adjudicacion_cierre_66_v1/aceptacion.json`, con IDs, etiquetas originales/corregidas, SHA256 de texto y procedencia.

Es aceptación de propuestas asistidas después de conocer IA/predicciones, no anotación humana ciega. Las citas, razones y confianzas siguen siendo del agente. La fecha de registro no se presenta como fecha de anotación original. Las seis adjudicaciones Rxx anteriores siguen vigentes y no se vuelven a solicitar.

La referencia corregida se materializa en **`data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv`**, una vista versionada de 1.352 registros, usada efectivamente por el experimento 36. Conserva etiqueta IA, versión con seis adjudicaciones y versión con seis más trece, fold y relevancia IA. Hay 19 decisiones aceptadas y 16 cambios efectivos respecto de IA: 3 de las seis anteriores y 13 nuevos. No sobrescribir las corridas históricas `data/etiquetas/etiquetas_*.csv`, el codebook v2 ni los resultados 15–35. Los scripts históricos siguen reproduciendo sus referencias antiguas; no hay cambio implícito de sus cargadores.

## Comparación cerrada 2 × 2

Mismos textos, cinco folds por reunión y purga de copias del experimento 26. Las 559 observaciones de descubrimiento siguen siendo solo train; las 793 de validación son **desarrollo reutilizado**. Las trece nuevas adjudicaciones están en ese bloque de validación y se aplican en train solo cuando pertenecen al train de otro fold, nunca introduciendo su propio texto/reunión/copia en el train de su fold. El diseño no elimina la contaminación por decisiones post-predicción: no se presenta como evaluación independiente.

Dos supervisiones, sin búsqueda de parámetros:

1. `seis_previas`: reproducir el modelo adjudicado del experimento 31.
2. `seis_mas_trece`: misma supervisión anterior más las 13 correcciones nuevas.

Cada juego de predicciones se puntúa frente a **ambas** referencias: `ia_original` y `corregida_v2`. Exportar etiquetas y predicciones por separado. Esto permite distinguir:

- **Efecto de referencia:** cambiar la referencia manteniendo las predicciones del control fijas. No es mejora del modelo.
- **Efecto de entrenamiento:** cambiar las predicciones, comparando ambos modelos contra la misma referencia corregida. Solo diagnóstico de desarrollo post-revisión, no generalización.

A: unigramas TF-IDF, min_df=3, max_df=0,9, strip_accents=unicode, lowercase, sublinear_tf, norma L2. B: palabras 1–4, solo train relevante. LR: C=2, class_weight=balanced, max_iter=2000, semilla 20260915; reutilizar funciones congeladas de 26. Relevancia IA, A, vocabularios e IDF deben permanecer iguales entre modelos; solo cambia supervisión B y sus pesos balanced. ConvergenceWarning detiene el ajuste.

Diez ajustes por fold en total: cinco para cada supervisión. El control debe reproducir exactamente las predicciones A/B/finales de la variante `adjudicada` de 31. No refit final sobre todo el corpus, scoring general ni reemplazo del checkpoint histórico. No se revierten adjudicaciones por subir/bajar puntuaciones.

Métrica principal: media por fold de (F1 H + F1 D)/2, incluyendo falsas alarmas neutrales. Secundarias: macro-F1, métricas por clase, matriz de confusión, errores y cambios de predicción. Mostrar los cuatro cruces, deltas pareados por fold y límites. No calcular significación con cinco folds dependientes. No usar las 306 respuestas anteriores; el cargador solo consulta IDs de exclusión, nunca sus etiquetas.

## BETO: intento real de disponibilidad

En esta continuación se consultaron API/config del checkpoint oficial `dccuchile/bert-base-spanish-wwm-cased` con urllib y se contrastó config con curl. Fallaron de nuevo: TLS EOF en urllib y SSL_ERROR_SYSCALL (exit 35) en curl. Registro de peticiones y hardware en `adjudicacion_cierre_66_v1/beto_disponibilidad.json`: dos CPU lógicas, sin `nvidia-smi`. No se desactivó TLS. No hay pesos descargados ni ajuste de BETO; no confundir bloqueo de acceso con resultado negativo de calidad.

Se conserva el diseño previo de cobertura completa por segmentos y agregación por intervención, pero no se declara un runner transformer implementado/probado. No instalar bibliotecas o pesos enormes sin resolver acceso. Los modelos/dependencias locales quedan fuera de Git.

## Ejecución e integridad

`36_evaluar_referencias_corregidas.py --preparar` valida aceptación, fuentes, particiones y materializa la vista antes del primer fit; `--ejecutar` verifica hashes y corre únicamente las dos supervisiones. Salidas e informe exclusivos; replay en rutas temporales nuevas. Las rutas de aceptación son estables, no se regenera una aceptación histórica para reproducir un experimento.

Pruebas de aplicación exacta por ID/hash/etiqueta, ambigüedades sin cambios, relevancia inalterada, aislamiento fold, efecto de referencia sin cambiar predicciones, ancla exacta, salidas/versiones y negativa a sobrescribir. Ejecutar pruebas específicas 31–36; no la suite histórica que abre las 306 respuestas. Verificar hashes de los artefactos previos y mantener un registro de reproducción. Las pruebas garantizan integridad y consistencia, no verdad semántica.
