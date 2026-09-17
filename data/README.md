# Datos incluidos y fuentes de verdad

## Para el trabajo actual

| Ruta | Contenido / uso |
|---|---|
| `auditoria/ampliacion_hd_60_v1/` | Selección real de 60 y capa `anotacion_ia_v1/tanda_01/` con 60 etiquetas IA en dos tandas; 35 H/D altos preparados, no incorporados al modelo. No esperar respuestas humanas. |
| `auditoria/meta_hd_300_v1/` | Meta 300 H/300 D, progreso con hashes y cola siguiente sin etiquetas E001–E020. |
| `L0/corpus.csv` | Corpus completo inmutable: 9.725 intervenciones. No corregir OCR ni reconstruir textos manualmente. |
| `etiquetas/etiquetas_*.csv` | 1.352 anotaciones IA originales, conservadas. No sobrescribirlas. |
| `evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv` | Vista activa de 1.352 IDs; referencia original, seis adjudicaciones y versión con trece correcciones adicionales. |
| `evaluacion/referencias_corregidas_v2/predicciones_validacion.csv` | Control de 793 casos por supervisión. Usar **`seis_mas_trece`**, puntuado contra **`etiqueta_corregida_v2`**. |
| `evaluacion/clasificadores_hd_v1/asignacion_folds.csv` | Asignación fija de validación; el cargador reconstruye/purga el train original. |
| `auditoria/preparacion_beto_v1/` | Lock del checkpoint, bloqueos reales, protocolo de entrada y pruebas sin encoder. |
| `checkpoints/beto_v1/entrada/` | `documentos.json`, `folds.json`, `baseline.json`, `checkpoint.json`, `manifest.json`. Paquete listo en ZIP portable; el gestor lo regenera si falta. |
| `auditoria/recepcion_beto_v1/` | Origen GitHub, auditoría de cinco folds BETO y métricas recalculadas; no adoptado. |
| `evaluacion/comparacion_beto_v1/predicciones_comparadas.csv` | 793 resultados externos alineados con el control, sin duplicar los textos. |
| `checkpoints/beto_v1/ejecucion/` | Resultados BETO futuros/recibidos. Verificar manifiestos y procedencia; no presumir entrenamiento por mera presencia de un archivo. |

**Identidad esperada del paquete actual:**
`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`.

Los 1.352 textos íntegros suman **1.997.823 caracteres**. No se entregan citas aisladas como entrenamiento. El paquete exportado no añade notas de adjudicación al texto. Filtro A y referencias permanecen fijos.

## Evidencia que se conserva, no tareas por repetir

- `auditoria/revision_entrenamiento_30_v1/`: devolución humana, seis decisiones aceptadas e instrumentos históricos. No rellenar de nuevo.
- `auditoria/revision_errores_adjudicada_v1/`: revisión de 66 desacuerdos, aceptación de 13 correcciones y 12 casos ambiguos sin cambiar.
- `auditoria/inversiones_hd_v1/`: diez inversiones diagnosticadas, cinco ambiguas aparte y contribuciones del TF-IDF.
- `evaluacion/` y `lexico/`: resultados de modelos/búsquedas anteriores. Permiten justificar decisiones y no repetir experimentos descartados.
- `muestras/`: marcos y particiones originales; parte de su contenido se usa para exclusión/integridad. No se vuelve a evaluar el antiguo examen humano.
- `L2/`: derivados históricos de metadata/macro/series.
- `externos/`: piloto WCB histórico de alcance limitado, **no incorporarlo al nuevo BETO**.

No se borran estos archivos por ser antiguos: varios son dependencias o evidencia verificable. `checkpoints/` está ignorado por Git; **un push no respalda esa carpeta**. Usar `exportar`/`respaldar` y guardar el ZIP fuera del entorno.
