# AVANCE — Proyecto D&H

## Decisión vigente: codebook v3 aprobado y revisión total autorizada

El investigador aprobó el 17-09-2026 la definición de **dirección monetaria respaldada** como `docs/codebook_v3.md` y autorizó revisar IA y humanas. V2, sus etiquetas y métricas quedan preservadas como historial; no se sobrescriben. Las 306 humanas dejan de ser test ciego para la futura referencia v3.

Inventario reproducible: **1.747 IDs distintos en 24 lotes** —19 rondas IA/1.352, cuatro tandas IA nuevas/89 y humanas/306— en `data/auditoria/migracion_v3/`. Cerrados: prioritarias77/77; pilotos r1 110/110, r2 88/88, r3 85/85, r4 17/17; escalados r5–r10 cerrados (561/561). Acumulado **938 revisados/809 pendientes**. R7 cambia5 etiquetas, r8 cambia8, r9 cambia4 y r10 cambia7; sin cambios de relevancia. Leer los informes `REVISION_*_V3.md`. Gestor40 `preparar-migracion-v3`; pruebas específicas aprobadas. No entrenamiento ni referencia v3 consolidada todavía.

## Consulta histórica: formato estructurado del plan B, sin ampliar la revisión

El investigador pide opinión antes de iniciar la revisión ampliada y presenta otra calibración con `tipo_accion`, `instrumento`, Nrelevantes y29595pendiente. Se considera mejor alineada conceptualmente; quedan controles de formato/trazabilidad, no otra redefinición de H/D/N. **No se inició revisión adicional de las77filas, importación o entrenamiento.**

Pendientes: mantener `etiqueta` solo H/D/N y pasar pendiente a `estado_revision`, con etiqueta vacía y uso_entrenamiento=0; completar citas de los Nrelevantes21910/31369/32169/32531; quitar la elipsis insertada de31986; preservar UF cuando se cita el valor de21716 (su cita completa previa tenía291caracteres y cabía). En22078la nota afirma aislamiento pero la salida solo muestra texto original con otro acuerdo: si hay segmentación, registrar texto_unidad/offsets sin borrar el original. Añadir IDdeacta/reunión real para agrupar propuestas, votos y comunicado. No inferir unanimidad en33554solo de “los demás también están de acuerdo”.

`tipo_accion` funciona en realidad como tipo de acto discursivo; acordar vocabulario breve y distinguirlo de subir/bajar/mantener. Esos campos, notas y citas son anotación/auditoría: no suministrarlos automáticamente como entradas del modelo; cualquier uso de rasgos derivados exige disponibilidad/obtención equivalente y sin etiquetas en inferencia. Procedencia IA/fecha de anotación/versión de guía deben quedar registradas. Guías congeladas, resultados y datos previos sin cambios.

## Cierre actual: compatibilidad original auditada parcialmente, no reclasificada

Se contrastaron v2, las convenciones históricas, documentación del instrumento humano y los19CSV/1.352IA. **Hallazgo confirmado:** parte del training IA usó pausa en alzas=D y mantener contra recorte=Hrelativo, según `CONVENCIONES_ETIQUETADO.md` y cuatro notas explícitas. Esas convenciones no son automáticamente equivalentes a dirección respaldada en la propia unidad. No significa que las1.352estén mal ni que cada caso de esa familia cambie necesariamente de clase.

La separación N/relevancia **ya estaba en la guía y en los datos**: originales H116/D89/Nrelevante878/Nirrelevante269; vista v2 H125/D89/Nrelevante869/Nirrelevante269, tras16cambios aceptados que no son nuevos. El error de N=irrelevante de la calibración externa no se extrapola a toda nuestra base.

Se leyeron12textos completos (27.887caracteres/4.591palabras):4focos por notas y8controles por hash/estrato no seleccionados por error de modelo. Cinco controles compatibles, dos fronteras de criterio y uno de evaluabilidad; no es estimación de proporción de errores. El control292:1muestra una pausa fuera de los dos archivos prioritarios. Estos contienen41+36=77filas, punto de partida, no número de etiquetas malas ni límite del problema.930notasvacías eran permitidas en relevantes y limitan el tamiz textual, no invalidan esas etiquetas.

**Tus306humanas no se abrieron ni reevaluaron.** Se revisó documentación, no se comprobó qué regla siguió cada respuesta. No declarar inválida esa referencia ni asegurar compatibilidad total con otra definición. Originales, decisiones y métricas intactos. Recomendación: acordar la frontera de criterio y revisar las familias identificadas en una nueva capa, sin corregir por mejora de score.

[Informe](AUDITORIA_COMPATIBILIDAD_CRITERIOS_V1.md), evidencia en `data/auditoria/compatibilidad_criterios_v1/`. Auditor reproducible de solo lectura en gestor40 `auditar-compatibilidad`; no clasifica automáticamente ni entrena. Replay byte a byte y **122pruebas aprobadas,0omitidas**. **Cero etiquetas modificadas.** No auditoría semántica exhaustiva, nueva estimación de generalización o entrenamiento. La ampliación300/300 no se cancela, pero no se incorporan nuevas filas mientras se resuelve compatibilidad.

## Aclaración vigente: compatibilidad de las anotaciones originales y tercera calibración

El investigador aclara que su pregunta sobre “las1000tuyas+300mías” se refería al conjunto original IA/humano, no solo a las89nuevas. **No se puede declarar que las1.352IA y306humanas estén mal en bloque ni que sean totalmente compatibles sin revisión.** Separar errores de aplicación de reglas existentes de cambios de variable/definición; cambiar después el objetivo no convierte automáticamente la etiqueta anterior en equivocada. No se sabe cuántas cambiarían. No se reabrieron306respuestas ni se ejecutó reclasificación.

Nueva salida de calibración histórica mejora Nrelevante=1 y otras distinciones, pero aún requiere:29595noNalta por falta de voto (hay propuestas);31986sin Hrelativo automático ni cita con`[...]`; citas paraNrelevantes;33553sin afirmar sesgo al alza inequívoco mientras se sostiene N;27863propuesta distinta de adopción. Cita21716comprobada en291caracteres: cumple300y no requiere recorte, corrigiendo la sugerencia anterior. Detalle en `docs/CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md`.

Solo evaluación/documentación de fragmentos pegados. No nuevos datos, etiquetas, código o entrenamientos; las propuestas no sustituyen v2 ni las referencias históricas.

## Última actualización: definiciones destacadas y revisión de etiquetas pendiente

El investigador pidió anotar las definiciones en README y otra parte, destacando su importancia, y preguntó si hay que reclasificar lo anterior. Se añadieron una sección visible en `README.md` y la regla13 en `docs/REGLAS.md`, con enlaces a los borradores: orientación respaldada, **N relevante ≠ irrelevante**, dirección frente a magnitud relativa, mantención contextual, historia/pregunta sin adhesión y texto original.

Recomendación: **auditoría de consistencia, no reclasificación masiva automática**. Empezar por las89anotaciones IA nuevas; después revisar familias de riesgo en las1.352 y casos de control, sin limitarse a los errores del modelo. No sabemos todavía cuántas etiquetas cambiarían. Las discrepancias de criterio, si se confirman y autorizan, deben versionarse preservando originales/adjudicaciones y separando el efecto de nueva referencia del de nuevo entrenamiento. No abrir las306respuestas.

Solo documentación en esta actualización: **no se revisaron/reclasificaron filas, no se modificó v2/A/folds, no se importó planB ni se entrenó**. Los borradores generales no se convierten por esta instrucción en una migración aprobada. El deterioro +59 no prueba por sí solo etiquetas erróneas; hay fallos de representación ya documentados.

## Consulta vigente: criterio del plan B centrado en tasa de política

El investigador pidió detener la continuación y definir el criterio antes de seguir. Presentó15ejemplos de1995–1999 extraídos por un filtro de TPM. Revisión en `docs/CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md`: extracción más pertinente, pero **N no implica irrelevancia** (31369/32169/32531 deben conservar relevancia monetaria en este criterio); no ranking de H/D entre alternativas (bajar50 frente a70 sigue siendoD); historia de bajas no equivale a postura actual (21910);29595 contiene contenido sustantivo después de la apertura y no admiteN/0alta automática.

Criterio recomendado: orientación monetaria doméstica respaldada, incluyendo los nombres históricos del instrumento/tasa de instancia.31986 puede serHmedia por rechazar estímulo excesivo, no por disenso;33553 no se acepta comoDalta por una espera operativa. Separar acción, sesgo, acto discursivo y unidad por actor/acuerdo. `texto_corregido` no sustituye al original sin cotejo; no son solo tildes en todos los casos.

También quedó guardado el borrador de investigación `docs/DEFINICION_POSTURA_MONETARIA_PROPUESTA_V1.md`: papers y FMI/BIS, distinción funcional y matiz de que crédito dirigido/refinanciamiento puede ser instrumento monetario histórico. **Ambos son propuestas, no codebook vigente.** No etiquetas finales importadas, datos históricos, entrenamiento, modificación de v2/validación o continuación de anotación del plan A en esta consulta.

## Consulta más reciente: plan B histórico en calibración, no ejecutado

El investigador presentó fragmentos de actas de 1977/1982/1986/1992 con etiquetas tentativas y pidió opinión antes de comenzar. Se revisó el encaje conceptual en [CALIBRACION_PLAN_B_ACTAS_HISTORICAS](CALIBRACION_PLAN_B_ACTAS_HISTORICAS.md). **No se importó el corpus ni se asignaron etiquetas finales, se entrenó o se modificó el codebook.**

Hallazgo central: ayuda focalizada/refinanciamiento/reprogramación o flexibilización de multas no equivalen automáticamente a D monetaria; control normativo no implica H. Destacan la multa de30→20 del ID78 (no tasa de política), deuda de Bolivia4480/4481 (no postura chilena), excepción a una prohibición en42 (no resumir como endurecimiento), y el cambio5→10 de18566, cuyo parámetro no está identificado (no declararlo rutinario con alta confianza). Hay inconsistencias entre ratificaciones etiquetadas N/0 y ayudas similares D/1, además de filas que mezclan varios acuerdos.

Recomendación de calibración: definir unidad semántica por asunto/discusión-resolución, función/instrumento/alcance y cambio respecto de la norma previa antes de H/D/N; separar fuera de alcance/contexto insuficiente de neutralidad sustantiva. No exigir literalmente TPM a toda medida histórica ni tratar toda operación monetaria como macro-direccional. Revisión limitada a textos del chat; no originales/anexos/normas anteriores. Contexto histórico apoyado en fuentes BCCh: flotación1999 y nominalización2001. Mantener el plan B separado y no usarlo para completar300 por cuota. Esta consulta no altera el diagnóstico ni los resultados vigentes.

## Último cierre: diagnóstico de los nuevos errores TF-IDF

El investigador pidió revisar los errores nuevos y pensar por qué falla. Se leyeron **los 16 textos completos con cambios (57.722 caracteres): nueve errores nuevos, tres corregidos y cuatro errores que cambian de tipo**. [Diagnóstico](DIAGNOSTICO_AMPLIACION_TFIDF_59_V1.md). No se modificó ninguna referencia, etiqueta o cohorte y no se ensayó otra variante.

Se reconstruyeron las dos condiciones del ensayo +59 y se reprodujeron **A/B/final sobre los 793 casos de cada una**. Se guardaron **12.005 contribuciones** y márgenes con cierre algebraico, 48 vecinos exclusivamente del nuevo train permitido, reajustes de vocabulario/balanced y frecuencias de términos. Replay byte a byte de los artefactos cuantitativos; **116 pruebas aprobadas, 0 omitidas**, 16 citas exactas verificadas. El gestor incorpora `diagnosticar-ampliacion-tfidf`, sin nuevo script numerado ni pesos guardados.

Hallazgos: pregunta de adhesión confundida con adhesión real; nombres/cargos y fórmulas compartidas ganan peso hacia D incluso frente a una recomendación de alza; recorte rechazado y sesgo retirado reciben señal de las palabras de recorte/sesgo; riesgos extranjeros y mantención sin compromiso se parecen a textos D. En 8/9 errores nuevos, el componente de coeficientes es el mayor en magnitud de la descomposición simétrica, mientras representación se opone al cambio en 7/9. **Es descripción matemática, no prueba causal ni diagnóstico de un ejemplo individual como culpable.**

Se señalaron fronteras de criterio —incluido un acierto nuevo contra v2— sin proponer/recalcular etiquetas alternativas. Recomendación: uniformar la aplicación de dirección respaldada y buscar contrastes reales de acto discursivo, no N al azar ni solo más H/D. No meter los 16 casos en su propio train ni cambiar el score por depuración retrospectiva. Meta300/300 y colaG siguen registradas, pero no se avanzó anotación ni entrenamiento de variantes en este diagnóstico.

Evidencia: `data/auditoria/diagnostico_ampliacion_tfidf_59_v1/`; protocolo previo `docs/PROTOCOLO_DIAGNOSTICO_AMPLIACION_TFIDF.md`. Paquete BETO, resultados del ensayo, originales y métricas permanecen intactos. No causalidad, segunda anotación independiente, sintéticos, refit global o adopción.

## Cierre actual: TF-IDF probado con los 59 aumentos, sin mejora

El investigador pidió «prueba tfidf con estos aumentos haber si cambia algo». Se ejecutó aquí una comparación controlada en CPU: base v2 frente al mismo B ampliado con 59 IDs H/D altos (29 H/30 D), purgados por reunión/texto frente a cada validación. **53/51/52/50/53 adiciones por fold**, A entrenada solo con originales y compartida, mismos parámetros y referencias.

**F1 H/D media 0,747060 → 0,713526; macro-F1 media 0,822250 → 0,798866; errores 51→57; H↔D 15→17; H/D→N 12→12; N→H/D 24→28.** Solo mejora 1/5 folds. Cambian 16 predicciones: tres errores corregidos, nueve aciertos perdidos y cuatro errores que cambian de tipo. **No se adopta la ampliación como reemplazo del control.** [Informe](RESULTADOS_AMPLIACION_TFIDF_59_V1.md).

El control reproduce exactamente las 793 predicciones anteriores A/B/final. Dos corridas completas reproducen byte a byte predicciones, comparación, inclusiones y métricas; protocolo/ejecución idénticos salvo fecha/tiempos. Cuenta aritmética independiente confirma matrices/F1. **111 pruebas aprobadas, 0 omitidas** (106 previas + 5 nuevas). Se recreó el entorno de preparación; la primera pasada sin transformers falló y se repitió completa tras instalar los requisitos fijados. No se omitieron controles.

Protocolo previo al fit en `docs/PROTOCOLO_AMPLIACION_TFIDF_59_V1.md`, datos en `data/evaluacion/ampliacion_tfidf_59_v1/`. Gestor 40: `evaluar-ampliacion-tfidf`, módulo `scripts/evaluar_ampliacion_tfidf.py`. Vocabulario/IDF y class_weight=balanced de B se recalculan dentro del train respectivo; no búsqueda de hiperparámetros. No modelos guardados, refit global, scoring completo, ejecución BETO ni cambio de fuentes/paquete f7aa1589….

## Ampliación IA y meta que siguen registradas

89 nuevos IDs anotados en cuatro tandas, 299.397 caracteres: H30/D37/N22. Núcleo utilizable H29/D30, catálogo base+preparados **H154/D119**, faltan **H146/D181** para 300/300. Reservas H1/D6 y E009 descartado por copia cercana no cuentan. El entrenamiento experimental ahora está realizado; no confundirlo con incorporación permanente al corpus o adopción global, que siguen sin hacerse.

La cola G001–G020 está preparada y **sin anotar**, 15.056 palabras. La meta no se cancela automáticamente, pero tras este resultado se recomienda revisar consistencia/representatividad del enriquecimiento antes de seguir acumulando solo por cantidad. No cambiar referencias ni retirar ejemplos porque perjudican el score. No pedir anotación al usuario ni nueva autorización por cada tanda de la ampliación ya aprobada.

## Estado científico vigente

- Referencia v2 fija: 19 decisiones aceptadas / 16 cambios efectivos; 12 ambiguos originales sin modificar. H125/D89/N1138; relevantes para B: H125/D89/N869.
- Control TF-IDF vigente: F1 H/D media **0,747060**, 51 errores sobre 793; 15 inversiones H↔D, 12 H/D→N y 24 N→H/D.
- **BETO v1 recibido y no adoptado:** cinco folds externos, F1 H/D media **0,625043**, 66 errores; 25 H↔D, 14 H/D→N, 27 N→H/D. Solo mejora 1/5 folds. Corrige 19 errores pero pierde 34 aciertos. [Informe y procedencia](RESULTADOS_BETO_V1.md).
- Métricas externas reconsolidadas exactamente y comprobadas aritméticamente. Registros declaran RTX 5060 y smoke exitoso; no se repitió aquí entrenamiento/tokenización oficial. El investigador confirmó que no se modificaron los scripts; esa declaración está separada en `data/auditoria/recepcion_beto_v1/confirmacion_usuario.json`. No volver a pedirla. Entorno/CUDA completo y hashes remotos siguen sin recibirse, sin exigirlos ahora.
- Paquete BETO **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`**, 1.352 textos / 1.997.823 caracteres / 793 validaciones, intacto. Ninguna referencia/fold/A cambió por la selección.
- Diez inversiones TF-IDF diagnosticadas previamente y cinco ambiguas desglosadas. La lectura posterior de 20 inversiones nuevas BETO y siete corregidas se inició, pero no tiene informe cerrado ni causa demostrada del deterioro.
- La [investigación web](INVESTIGACION_SOTA_POSTURA_MONETARIA.md) registra 20 fuentes y candidatos, no adopciones ni autorización de entrenar todas las alternativas.

## Qué sigue y qué no

1. Diagnóstico completado: aplicar consistentemente el criterio y priorizar contrastes de decisión/adhesión/negación antes de otra prueba. No añadir N indiscriminadamente ni ajustar a los 16 casos conocidos; meta300/300 y G001–G020 pendientes siguen registradas.
2. Completar y revisar la capa IA de entrenamiento; no reabrir las 306 respuestas ni rehacer las 30 anotaciones humanas anteriores. En una selección futura excluir también los nuevos IDs ya anotados.
3. Mantener el TF-IDF de control. El ensayo ampliado ya se ejecutó; no fue adoptado. Sin refit global, scoring del corpus, cambios de referencias, sintéticos o datasets externos por esta prueba.
4. **Idea sintética solo registrada**, PLAN §9.24: no generar ahora. La meta autorizada ahora es 300 H/300 D, sin forzar respuestas para cumplirla.
5. **Limpieza extrema final obligatoria y pendiente**, REGLAS §12: reducir de verdad la entrega a una entrada y pocos módulos esenciales. El gestor sobre los scripts históricos no cumple por sí solo el cierre.

## Continuidad y publicación

Leer [CONTINUIDAD](CONTINUIDAD.md), [EMPEZAR_AQUI](../EMPEZAR_AQUI.md) y [PLAN](../PLAN.md), especialmente §§9.20–9.25. Se conserva el PR #4, sin cerrarlo/fusionarlo por el agente. Descargar no requiere cerrar; integrar a main requiere Merge. Los ZIP anteriores no se actualizan automáticamente.

La historia y comprobaciones anteriores —incluida la instalación limpia desde ZIP con 90 pruebas— están en PLAN y `data/auditoria/entrega_portable_v1/`; no equivalen a verificar una ejecución GPU ni a terminar la limpieza final.
