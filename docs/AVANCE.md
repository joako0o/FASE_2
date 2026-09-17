# AVANCE — Proyecto D&H

## Cierre actual: resultados BETO externos recibidos, no adoptados

El investigador subió seis ZIP a `main` en `af99d510da75b5a54f63fe46b56af3bcbb55217b`. Son respaldos acumulativos; el final `resultados_beto_20260917T012512_748901Z.zip` contiene cinco folds y comparación. [Informe](RESULTADOS_BETO_V1.md); evidencia en `data/auditoria/recepcion_beto_v1/` y tabla alineada en `data/evaluacion/comparacion_beto_v1/`. No se borraron los originales remotos ni se duplicaron ZIP versionados.

**Métricas recalculadas:** F1 H/D media **0,747060 → 0,625043**; macro-F1 media **0,822250 → 0,739629**; errores **51 → 66**; inversiones **15 → 25** (H→D 6→8, D→H 9→17); H/D→N **12→14**, N→H/D **24→27**. Recall H igual (62/76), D **38/51→26/51**. Solo mejora 1/5 folds; **no cumple criterios y no se adopta**. 19 errores corregidos, 34 nuevos; de las 15 inversiones conocidas corrige 7, lleva 3 a N y conserva 5, pero crea 20 inversiones nuevas en casos antes correctos.

Verificados ZIP/blobs/hashes, cadena acumulativa, IDs/v2/folds/A, probabilidades y argmax, cinco manifiestos, pesos de clase/pasos/épocas, cobertura declarada de 1.352 textos y smoke coherente con los documentos previstos. Reconsolidación exacta como JSON con 39 y cuenta aritmética independiente. Se añadió `auditar-resultados` al gestor 40, **sin script 41 ni cambios en 38/39 o su paquete**. **98 pruebas aprobadas, 0 omitidas** (14 + 20 + 64), sin abrir las 306 respuestas.

Los registros reportan RTX 5060, smoke exitoso y unas 30,59 min sumadas de folds. No se repitió aquí entrenamiento/tokenización oficial. El ZIP no incluye código/pesos remotos y su commit informativo es null: **cerrar procedencia con el agente externo antes de atribuir el resultado a una implementación plenamente auditada**. No confundir el campo estático `hardware.entrenamiento_realizado=false` con el estado del fold.

**Siguiente:** mantener TF-IDF; solicitar cambios/diff, entorno/CUDA y manifiesto usados; diagnosticar nuevas inversiones sin cambiar referencias. No más entrenamiento automático, refit/scoring, datasets externos ni confirmación humana de una mejora inexistente. Limpieza extrema final sigue pendiente. Las notas siguientes describen etapas previas, no sustituyen este cierre.

## Actualización: investigación web mientras BETO se prepara en otro equipo

El investigador informa que un agente Gemini mediante Antigravity está preparando dependencias/modelo y pidió investigar papers, modelos actuales/SOTA y foros. **No se recibieron resultados ni prueba GPU del entorno externo; no podemos verificar su avance automáticamente.** Los bloqueos anteriores describen este entorno, no necesariamente el otro PC.

[Informe único de investigación](INVESTIGACION_SOTA_POSTURA_MONETARIA.md), corte 2026-09-16: 20 registros de fuentes con alcance de lectura. WCB/BIS/Ornithologist/DCS/IMF/CBRT, encoders españoles y multilingües, modelos generativos actuales y discusiones técnicas. Búsqueda dirigida, no revisión exhaustiva ni reproducción de benchmarks; no proclamar un SOTA probado para nuestras actas.

Recomendación documental: terminar BETO primero; **MrBERT-es** como primer candidato nuevo solo si los resultados justifican otro ensayo; clasificación estructurada como alternativa ante errores semánticos persistentes. No adoptar variantes ni comparar F1 ponderada/accuracy externas con nuestra F1 H/D. La lista no es una orden de entrenar todos los modelos.

**Sin cambios de scripts, tests, datos, referencias, folds, A, dependencias o protocolo BETO.** Sin descargas de modelos/datasets para entrenar, pagos, nuevos scripts o apertura de las 306 respuestas. Se verifica que el paquete actual mantiene su identidad. La limpieza extrema final sigue pendiente y no debe ejecutarse en medio de la corrida externa. Informe e índices/continuidad solamente; los ZIP anteriores no se actualizan automáticamente.

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
- BETO: ya hay resultados externos negativos y evaluación recalculada (ver cierre actual). Los bloqueos anteriores de este entorno no describen necesariamente el PC externo; no se repitió el encoder localmente.
- Etapa anterior: 78 pruebas aprobadas (14 sin encoder + 64 regresiones), paquete reproducido y 313 archivos anteriores intactos. La nueva organización añade controles de exportación, no evidencia neuronal.

## Siguiente acción concreta

1. Leer RESULTADOS_BETO_V1 y verificar el ZIP final con `auditar-resultados` si se retoma en otro PC.
2. Cerrar con el agente externo la procedencia del código/entorno; no descargar pesos aquí para esta auditoría.
3. Conservar TF-IDF. Diagnosticar nuevas inversiones, sin volver a etiquetar ni iniciar otra familia automáticamente.
4. Respetar la limpieza extrema final pendiente y la continuidad; no cerrar/fusionar PR sin autorización.

Historia detallada: [PLAN](../PLAN.md), [evaluación v2](EVALUACION_REFERENCIAS_CORREGIDAS_V2.md), [diagnóstico H/D](LECTURA_DIAGNOSTICO_INVERSIONES_HD_V1.md), [protocolo BETO](INVESTIGACION_Y_PROTOCOLO_BETO_V1.md). Las propuestas que aparecen como pendientes en documentos históricos no sustituyen las aceptaciones posteriores.
