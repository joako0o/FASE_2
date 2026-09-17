# AVANCE — Proyecto D&H

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

1. Informar el resultado negativo y revisar consistencia/representatividad antes de otra prueba. La meta 300/300 y G001–G020 pendientes siguen registradas; no convertirla en una cuota que fuerce etiquetas.
2. Completar y revisar la capa IA de entrenamiento; no reabrir las 306 respuestas ni rehacer las 30 anotaciones humanas anteriores. En una selección futura excluir también los nuevos IDs ya anotados.
3. Mantener el TF-IDF de control. El ensayo ampliado ya se ejecutó; no fue adoptado. Sin refit global, scoring del corpus, cambios de referencias, sintéticos o datasets externos por esta prueba.
4. **Idea sintética solo registrada**, PLAN §9.24: no generar ahora. La meta autorizada ahora es 300 H/300 D, sin forzar respuestas para cumplirla.
5. **Limpieza extrema final obligatoria y pendiente**, REGLAS §12: reducir de verdad la entrega a una entrada y pocos módulos esenciales. El gestor sobre los scripts históricos no cumple por sí solo el cierre.

## Continuidad y publicación

Leer [CONTINUIDAD](CONTINUIDAD.md), [EMPEZAR_AQUI](../EMPEZAR_AQUI.md) y [PLAN](../PLAN.md), especialmente §§9.20–9.25. Se conserva el PR #4, sin cerrarlo/fusionarlo por el agente. Descargar no requiere cerrar; integrar a main requiere Merge. Los ZIP anteriores no se actualizan automáticamente.

La historia y comprobaciones anteriores —incluida la instalación limpia desde ZIP con 90 pruebas— están en PLAN y `data/auditoria/entrega_portable_v1/`; no equivalen a verificar una ejecución GPU ni a terminar la limpieza final.
