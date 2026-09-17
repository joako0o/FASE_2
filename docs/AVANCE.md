# AVANCE — Proyecto D&H

## Actualización: limpieza extrema final exigida, todavía pendiente

El investigador indicó que unos 40 scripts no son una entrega adecuada y pidió dejar anotada una limpieza extrema al finalizar. Se incorporó como regla obligatoria en `docs/REGLAS.md` §12 y en AGENTS/CONTINUIDAD/PLAN. No basta con el gestor 40 ni con eliminar caches: hay que reducir de verdad el flujo a una entrada y pocos módulos esenciales, retirar duplicados y separar el histórico recuperable de la entrega operativa. Verificar equivalencia y ejecución limpia antes de declarar cierre.

Esta actualización es documental: no se eliminaron scripts, no se refactorizó todavía ni se cambiaron datos/modelos. Los controles de traslado que siguen describen el cierre anterior; no certifican la limpieza final exigida ahora. Los ZIP ya descargados son instantáneas anteriores y no incorporan automáticamente esta nota.

## Cierre anterior: organización, traslado y continuidad

El investigador pidió ordenar todo el proyecto, eliminar lo innecesario, dejar código/datos y pasos claros para otro PC y permitir que otra sesión continúe. No pidió fusionar ni cerrar el PR. Se mantiene PR #4 y la rama de esta sesión; para otra sesión manda la rama que asigne su entorno.

### Entrega preparada

- **`EMPEZAR_AQUI.md`**: instrucciones breves para el investigador, comandos CPU/GPU, ZIP completo, respaldo y diferencia entre cerrar/fusionar PR.
- **`AGENTS.md` y `docs/CONTINUIDAD.md`**: estado, decisiones ya tomadas, datos activos, métricas de control, bloqueos y siguiente tarea. No dependen de la memoria del chat.
- **`scripts/40_gestionar_proyecto.py`**: punto único de entrada. Instalación aislada local, preparación idempotente, pruebas acotadas, delegación al runner congelado y exportación por inventario.
- **`scripts/README.md`, `data/README.md`, `docs/README.md`**: mapa de código, datos y lectura. Portada README sustituida por una guía corta; retiradas instrucciones repetidas de revisiones ya cerradas. La cronología extensa sigue en PLAN, informes específicos y Git.
- **`entrega/archivos_proyecto.txt`**: lista explícita de fuentes exportables. ZIP con corpus, etiquetas, referencia v2, evidencia, código y paquete BETO. No `.git`, `.venv`, caches, pesos ni archivos personales no declarados.
- Se eliminan caches regenerables. No se eliminan/mueven artefactos históricos utilizados por dependencias/manifiestos. Los Excel vacíos obsoletos ya se habían retirado en la limpieza inicial; se conservan originales y devoluciones humanas, sin pedir nuevos formularios.
- Datos regenerables/resultados bajo `data/checkpoints/` y ZIP bajo `entregas/`, fuera de Git. Un push no basta para respaldar resultados GPU.

### Verificación de esta entrega

**Verificado en Linux/Python 3.11:** instalación limpia desde ZIP, sin `.git` ni entorno previo, ruta con espacios y comandos iniciados fuera de la raíz; **90 pruebas aprobadas, 0 omitidas** (14 preparación + 12 traslado + 64 regresiones). Cinco archivos del paquete reproducidos exactamente, reexportación sin Git verificada y **330 archivos previos protegidos intactos**. Retirados 29 caches (631.950 bytes). Evidencia en `data/auditoria/entrega_portable_v1/`. Las pruebas del gestor usan fixtures para los fallos/respaldos de entrenamiento; no entrenan BETO. Windows/macOS/Colab/GPU no ejecutados.

## Estado científico que no cambió

- Referencias corregidas v2, cinco folds purgados y puerta A fijos. Seis decisiones previas + trece aceptadas; 19 decisiones / 16 cambios efectivos, 12 ambiguos intactos.
- Control TF-IDF contra referencia v2: F1 H/D **0,747060**, 51 errores de 793; **15 H↔D, 12 H/D→N, 24 N→H/D**. Desarrollo reutilizado/asistido, no test independiente.
- Diagnóstico de diez inversiones terminado, cinco ambiguas aparte. No confundir contribuciones léxicas o sondas de primera cita con causalidad/mejora automática.
- Paquete BETO: **1.352 textos íntegros / 1.997.823 caracteres**, 793 validaciones. ID **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`**.
- **BETO NO ejecutado**: sin pesos, torch local ni GPU. Conexión a servidores HF/DCC/PyTorch falló TLS EOF; GitHub API/PyPI funcionaron. Notebook/código preparados, no prueba real aprobada.
- Etapa anterior: 78 pruebas aprobadas (14 sin encoder + 64 regresiones), paquete reproducido y 313 archivos anteriores intactos. La nueva organización añade controles de exportación, no evidencia neuronal.

## Siguiente acción concreta

1. Descargar/extraer el ZIP completo y abrir EMPEZAR_AQUI.
2. Nueva sesión: leer CONTINUIDAD y verificar paquete/pruebas; no rehacer anotaciones ni búsquedas descartadas.
3. Con GPU CUDA y acceso a pesos: instalar entorno BETO, superar prueba técnica real, ejecutar cinco grupos y comparar. Si falta GPU/red o falla el código, conservar error y registrar el bloqueo; no saltarse controles.
4. Si llegan resultados GPU, verificar procedencia y paquete antes de aceptar métricas. Menos H↔D sin aumentar H/D→N, junto con guardas F1/recall/macro. No refit final ni scoring global todavía.

Historia detallada: [PLAN](../PLAN.md), [evaluación v2](EVALUACION_REFERENCIAS_CORREGIDAS_V2.md), [diagnóstico H/D](LECTURA_DIAGNOSTICO_INVERSIONES_HD_V1.md), [protocolo BETO](INVESTIGACION_Y_PROTOCOLO_BETO_V1.md). Las propuestas que aparecen como pendientes en documentos históricos no sustituyen las aceptaciones posteriores.
