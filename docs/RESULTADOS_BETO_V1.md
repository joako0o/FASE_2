# Resultados BETO v1: recepción externa y comparación verificada

**Fecha local: 16-09-2026, America/Santiago.**

## Conclusión

**Esta ejecución de BETO no mejora el control TF-IDF y no cumple los criterios fijados. No se adopta.**

Las métricas fueron recalculadas desde los cinco CSV de predicciones, con el código local congelado y la referencia v2. El JSON de comparación resultante coincide exactamente en contenido con el recibido. Una segunda cuenta aritmética, sin las funciones de métricas del runner, confirmó las matrices y F1 medias.

Esto verifica la integridad y evaluación de **los resultados entregados**; no equivale a haber repetido aquí el entrenamiento GPU ni a una auditoría independiente de los binarios/código utilizados en el PC externo.

## 1. Qué se recibió y qué ZIP importa

El investigador subió seis respaldos en el commit de `main`:

`af99d510da75b5a54f63fe46b56af3bcbb55217b`.

**Respaldo final completo:**

[`resultados_beto_20260917T012512_748901Z.zip`](https://github.com/joako0o/FASE_2/raw/af99d510da75b5a54f63fe46b56af3bcbb55217b/resultados_beto_20260917T012512_748901Z.zip)

- 420.994 bytes comprimidos.
- SHA-256: `b1e70825fff7f999b9ccf99c1cc753d2f20c2f4b2565aba85b3e4bddf7ced5a4`.
- 27 archivos de resultados con hashes, más el manifiesto de entrega.
- Cinco grupos, tres épocas por grupo, prueba técnica y comparación.
- Los cinco ZIP anteriores son respaldos acumulativos. Se comprobaron sus blobs Git, hashes, inventarios y que cada archivo anterior permanece idéntico en el siguiente. **No son seis experimentos ni 30 folds.**
- No se borraron ni modificaron los archivos subidos por el investigador. Los ZIP no se duplican como nuevos binarios versionados en esta rama; se conserva origen y hashes para recuperarlos.

Los nombres están en UTC. El registro de smoke `2026-09-17T00:53:10Z` corresponde al **16 de septiembre, 21:53 en Santiago**. El quinto grupo finaliza a las 22:24 locales. No es necesario corregir fechas de anotaciones.

## 2. Comparación principal: todos los 793 casos

| Indicador | TF-IDF fijo | BETO recibido | Lectura |
|---|---:|---:|---|
| **F1 H/D media de cinco folds** | **0,747060** | **0,625043** | Baja 0,122016 |
| Macro-F1 media de cinco folds | 0,822250 | 0,739629 | Baja 0,082620 |
| Errores totales | 51 | 66 | 15 errores adicionales |
| **Inversiones H↔D** | **15** | **25** | 10 adicionales |
| H→D | 6 | 8 | Empeora |
| D→H | 9 | 17 | Principal deterioro direccional |
| H/D→N | 12 | 14 | No resuelve el problema ocultándolo en N |
| N→H/D | 24 | 27 | Aumentan falsos positivos direccionales |
| Recall H | 81,58% | 81,58% | Igual: 62 de 76 |
| **Recall D** | **74,51%** | **50,98%** | **Baja de 38 a 26 aciertos entre 51 D** |
| Accuracy conjunta | 93,57% | 91,68% | No es la métrica principal por el predominio N |

**No confundir media por fold con métrica agrupada.** La F1 H/D calculada sobre la matriz conjunta es 0,743528 para TF-IDF y 0,630660 para BETO. El criterio del protocolo usa la **media de los cinco folds**, mostrada primero.

### Matrices completas

Filas: referencia H, D, N. Columnas: predicción H, D, N.

| Referencia | TF-IDF: H | D | N | BETO: H | D | N |
|---|---:|---:|---:|---:|---:|---:|
| H (76) | 62 | 6 | 8 | 62 | 8 | 6 |
| D (51) | 9 | 38 | 4 | 17 | 26 | 8 |
| N (666) | 10 | 14 | 642 | 10 | 17 | 639 |

### F1 H/D por grupo

| Fold | TF-IDF | BETO | Diferencia |
|---|---:|---:|---:|
| 1 | 0,778571 | 0,535885 | −0,242686 |
| 2 | 0,799242 | 0,723214 | −0,076028 |
| 3 | 0,738739 | 0,583333 | −0,155405 |
| 4 | 0,686603 | 0,549451 | −0,137152 |
| 5 | 0,732143 | 0,733333 | +0,001190 |

Solo mejora **1 de 5**, y muy poco. No atribuir el resultado a un único grupo desfavorable.

### Criterios previamente fijados

| Criterio | Resultado |
|---|---|
| F1 H/D media: mejora ≥0,02 | No |
| Mejora en ≥3/5 folds | No |
| Pérdida macro-F1 media ≤0,005 | No |
| Pérdida recall H ≤0,02 | Sí |
| Pérdida recall D ≤0,02 | No |
| Menos inversiones H↔D | No |
| No aumentar H/D→N | No |

Se cumple **1 de 7 condiciones**, no el conjunto requerido.

## 3. ¿Corrigió algunos errores aunque el saldo fuera negativo?

Sí. Cambian 60 predicciones finales:

- **19 errores anteriores se corrigen.**
- **34 aciertos anteriores se pierden.**
- Los otros 7 cambios pasan de un error a otro: tres inversiones pasan a N y cuatro falsos positivos neutrales cambian de dirección.
- 708 casos siguen correctos con ambos modelos.

De las **15 inversiones conocidas** del TF-IDF:

- 7 quedan correctas con BETO.
- 3 pasan a N: siguen siendo errores.
- 5 continúan invertidas.
- Pero BETO crea **20 inversiones nuevas en casos que TF-IDF resolvía correctamente**. Por eso el total sube de 15 a 25.

Entre los diez casos menos ambiguos diagnosticados previamente: 5 corregidos, 2 pasan a N y 3 siguen invertidos. Entre los cinco ambiguos conocidos: 2 corregidos contra la referencia fija, 1 pasa a N y 2 siguen invertidos. Son desgloses de desarrollo conocido, **no dos nuevos tests**.

Como suplemento, al quitar los cinco ambiguos de ambos modelos, las inversiones son **10 frente a 23**. La conclusión negativa no depende de incluir esos cinco casos. El criterio principal sigue calculado sobre todos los 793.

No se reabren etiquetas ni se propone corregir la referencia a partir de estas nuevas predicciones.

## 4. Qué se verificó técnicamente

### Verificado desde los archivos

- ZIP final y cadena de seis respaldos: inventarios, hashes, tamaños, ausencia de rutas extrañas/duplicadas, sin ejecutar código contenido en archivos externos.
- Identidad del paquete **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`** y conservación de las fuentes locales fijadas.
- 793 IDs únicos con los folds, reuniones, etiquetas v2 y filtro A originales. Regla final A/B y argmax de B coherentes con probabilidades finitas, acotadas y normalizadas.
- Cinco manifiestos de grupo completos, con tres épocas y pasos consistentes con train relevante/acumulación 8.
- Train relevante por fold: **946 / 959 / 962 / 959 / 958**. Son subconjuntos relevantes de los conjuntos purgados, no sustituyen sus tamaños totales.
- Pasos de optimización declarados: **357 / 360 / 363 / 360 / 360**; pesos de clase coincidentes con el train de cada grupo.
- Cobertura declarada idéntica entre folds: **1.352 documentos, 397.443 tokens de contenido, 1.765 segmentos**, 243 documentos multisegmento y máximo de 14 segmentos.
- Hash de cada texto y rangos de ventanas de 510 tokens con solapamiento 64 coherentes. **Esto no vuelve a ejecutar el tokenizer oficial para verificar la cuenta de tokens.**
- La prueba técnica registrada usa los dos documentos previstos del train del fold 1; declara actualización de cabeza y encoder, descarte del modelo de prueba y segmentos 14/1.
- Reconsolidación local de `comparacion.json`, idéntica como JSON, sin sobrescribir la original. Comprobación aritmética adicional de matrices/F1 y transiciones.
- **98 pruebas de software aprobadas, 0 omitidas**: 14 preparación + 20 gestor/recepción + 64 regresiones acotadas. No se abrió el antiguo examen de 306 respuestas.

### Lo que reporta el entorno externo

Los registros declaran **NVIDIA GeForce RTX 5060**, 8.518.041.600 bytes de memoria, PyTorch 2.6.0, Transformers 4.57.6, Tokenizers 0.22.2, Hugging Face Hub 0.36.2 y NumPy 2.4.6.

La suma de tiempos declarados de los cinco grupos es **1.835,20 segundos, unos 30,59 minutos**. No incluye preparación/descargas. Las pérdidas medias de entrenamiento descienden entre primera y tercera época en los cinco grupos; eso no prueba mejora de generalización.

### Límites de procedencia que siguen abiertos

El respaldo tiene `git_commit_informativo: null` y no incluye el código ejecutado, versiones completas del entorno/CUDA, logs completos de consola ni los binarios de pesos. Por eso no puedo certificar solo con este ZIP que no hubo modificaciones, ni verificar aquí los hashes de los pesos usados remotamente. **No es una acusación de irregularidad; es el alcance de la evidencia disponible.**

**Actualización posterior:** el investigador confirma que el agente no modificó los scripts; véase `data/auditoria/recepcion_beto_v1/confirmacion_usuario.json`. Se acepta como declaración del investigador, no como comparación independiente de hashes remotos. No hace falta volver a pedir esa confirmación. Las versiones completas quedan pendientes para cuando pueda aportarlas.

La lista original de evidencias de procedencia era:

1. Si cambió código, parámetros o dependencias: lista de cambios/diff, especialmente scripts 38/39, requisitos y utilidades involucradas. Si no cambió nada, dejarlo expresamente indicado.
2. Python, sistema operativo, `pip freeze`, versión CUDA de PyTorch y registro de GPU; salidas de comprobación/smoke y entrenamiento si las conserva.
3. Manifiesto de entrada utilizado y evidencia de verificación del checkpoint. No necesita subir pesos, `.venv`, cachés ni el proyecto comprimido completo.

**Dos campos que pueden confundir:**

- `hardware.entrenamiento_realizado: false` es un valor estático generado por `entorno()` en el runner original, también al entrenar. No invalida por sí solo los logs y predicciones, ni se interpreta como «no hubo entrenamiento».
- La carga registra inicialización de clasificador y pooler. El cargador congelado permite esas claves faltantes de forma explícita. No se cambia retroactivamente esa decisión para reinterpretar el resultado como un éxito o descartar una corrida desfavorable.

## 5. Reproducir la auditoría, sin GPU

Usar el gestor actualizado en esta rama, no el ZIP de código anterior a esta recepción. Descargar únicamente el ZIP final de resultados enlazado arriba. Con el entorno de preparación instalado, desde la raíz:

```bash
python scripts/40_gestionar_proyecto.py auditar-resultados resultados_beto_20260917T012512_748901Z.zip --salida entregas/auditoria_beto_recibido.json
```

La ruta del ZIP debe apuntar a donde se descargó. El comando exige un respaldo final completo, verifica el paquete local, contrasta registros, reconsolida en una carpeta temporal y recalcula matrices/F1/transiciones. No instala pesos, no entrena, no ejecuta archivos del ZIP ni sobrescribe el resultado original o una auditoría anterior. Si ya existe la salida, elegir otro nombre.

No es necesario ejecutar individualmente los scripts numerados. **No se añadió un script 41**: la recepción se integra en el gestor existente.

### Evidencia persistida

- [`data/auditoria/recepcion_beto_v1/origen.json`](../data/auditoria/recepcion_beto_v1/origen.json): revisión GitHub, hashes y cadena acumulativa.
- [`auditoria.json`](../data/auditoria/recepcion_beto_v1/auditoria.json): validaciones, metadatos, comparación recalculada y transiciones.
- [`verificacion.json`](../data/auditoria/recepcion_beto_v1/verificacion.json): pruebas de software y hash de la tabla comparada.
- [`predicciones_comparadas.csv`](../data/evaluacion/comparacion_beto_v1/predicciones_comparadas.csv): los 793 casos alineados, probabilidades recibidas y ambos resultados, sin duplicar textos completos.

## 6. Qué sigue y qué no

1. **Conservar TF-IDF como control vigente. No adoptar BETO v1.**
2. Cerrar procedencia con el agente externo y analizar las nuevas inversiones antes de modificar arquitectura o hiperparámetros. La causa del deterioro todavía no está establecida.
3. No suponer automáticamente que falta contexto, que hacen falta más épocas o que hay que cambiar etiquetas. Un encoder más reciente es una hipótesis posterior, no una solución demostrada.
4. No realizar refit final, scoring del corpus completo ni nueva confirmación humana para validar una mejora que aquí no se observó.
5. Mantener v2/folds/A, no reutilizar las 306 respuestas y no agregar datasets externos. La limpieza extrema final sigue pendiente; no implica borrar la evidencia de una comparación negativa.

Esta es evidencia de **desarrollo reutilizado/asistido**, no una estimación independiente de generalización. El ensayo externo aportó resultados útiles: permite rechazar esta configuración como reemplazo del control, sin concluir que todos los modelos contextuales serán peores.
