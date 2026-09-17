# Código: qué ejecutar ahora

**Entrada para el investigador: `40_gestionar_proyecto.py`.** Instrucciones completas en [EMPEZAR_AQUI](../EMPEZAR_AQUI.md).

| Archivo | Función | ¿Ejecutarlo ahora? |
|---|---|---|
| `40_gestionar_proyecto.py` | Instalar, preparar, probar, delegar BETO y exportar | Sí, con el subcomando indicado. |
| `38_preparar_beto.py` | Reconstruir/verificar 1.352 textos, folds y control | Lo llama 40. No descarga pesos. |
| `39_ejecutar_beto.py` | Prueba GPU, entrenamiento por fold y comparación | Lo llama 40, después de instalar GPU y superar `smoke`. |
| `36_evaluar_referencias_corregidas.py` | Evaluación TF-IDF de referencia v2 ya ejecutada | No repetir sobre sus salidas existentes. 38 reutiliza su cargador. |
| `37_diagnosticar_inversiones_hd.py` | Diagnóstico ya terminado de diez inversiones | Solo reproducción explícita en rutas nuevas si fuera necesaria. |
| `01`–`35` y auxiliares | Preparación, modelos, evaluación y adjudicaciones previas | Conservados por dependencias/procedencia. No ejecutarlos todos. |
| `plantillas/` | Instrumento histórico de revisión de 30 casos | No requiere nuevas respuestas. |

La numeración describe el historial metodológico, **no una receta para volver a generar todo**. Algunos scripts se importan transitivamente por el flujo actual; borrarlos o moverlos rompe la carga y los hashes.

`17_auditar_estado_gold.py`, `19_evaluar_tfidf_gold.py`, el importador gold y ciertas pruebas integrales pertenecen a tareas cerradas: no usarlos para el experimento BETO. La puerta de entrada 40 no los ejecuta para volver a evaluar respuestas humanas.

No modificar 38/39 dentro de una corrida iniciada. Un cambio necesario después del primer error GPU requiere nueva versión/paquete y una decisión explícita sobre resultados parciales.

Para resultados recibidos: `python scripts/40_gestionar_proyecto.py auditar-resultados ARCHIVO.zip --salida AUDITORIA_NUEVA.json`. Verifica un ZIP final y recalcula la comparación sin GPU, sin ejecutar código externo ni sobrescribir el original. BETO v1 recibido no superó al control; ver `docs/RESULTADOS_BETO_V1.md`.

Muestreo de revisión: `40_gestionar_proyecto.py preparar-muestra-hd --salida RUTA_NUEVA` delega en `muestreo_revision.py` y reutiliza el formato de 29. **La primera muestra de 60 ya está creada**: no hace falta ejecutar de nuevo para responder el Excel. No etiqueta ni entrena.

`40_gestionar_proyecto.py evaluar-ampliacion-tfidf --salida RUTA_NUEVA` reproduce el ensayo controlado con los 59 altos de tandas01–04. Delega en `evaluar_ampliacion_tfidf.py`; CPU, A/referencias/folds fijos, sin guardar modelos o sustituir el control. Ya se ejecutó y no mejoró.
