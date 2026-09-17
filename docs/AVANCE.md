# AVANCE — Proyecto D&H

## Estado actual: meta 300 H / 300 D, cuatro tandas IA cerradas

El investigador reiteró la meta de 300 H/300 D; no hace falta otra autorización por tanda ni respuestas al Excel. Se cuentan la base v2 fija y los nuevos IDs H/D altos sin descarte. **Disponibles para preparar: H154/D119; faltan H146/D181.** El modelo vigente todavía utiliza H125/D89. Cero nuevas incorporaciones a train y cero entrenamientos.

Cuatro tandas: **89 nuevas intervenciones íntegras leídas, 299.397 caracteres**, anotadas como H30/D37/N22. De ellas, **H29/D30 = 59** son de alta confianza y utilizables; H1/D6 medios quedan reservados y un D alto se descarta por copia cercana. Los N no se fuerzan a dirección. Contador/objetivo en `data/auditoria/meta_hd_300_v1/`; [informe](ANOTACION_IA_AMPLIACION_HD_V1.md).

En esta continuación se completaron E001–E020 y F001–F009: 96.608 caracteres / 15.702 palabras, dentro del presupuesto de 20.000. Aportan **H12/D12 altos**. E009 es D pero casi repite C35 (Jaccard 0,80645): se conserva etiquetado y **no cuenta para la meta**. Las dos nuevas D medias se reservan y E012 se registra como N dudoso. Datos en `data/auditoria/meta_hd_300_v1/anotacion_ia_v1/tanda_03/` y `tanda_04/`.

**Siguiente: G001–G020**, cola sin etiquetas ya preparada en `data/auditoria/meta_hd_300_v1/seleccion_05/cola.json`, 15.056 palabras. Excluye originales, marco humano y los 89 nuevos revisados. Prioridad a recomendación/voto/sesgo doméstico/acuerdo; canales 9 H/11 D no son etiquetas ni se suman al contador. Umbral de casi copia endurecido a 0,80 para la cola nueva, de forma explícita tras detectar E009; no se alteraron tandas anteriores.

### Controles y límites

Citas exactas, textos completos, manifiestos, exclusiones y planes contrastados. Los 59 altos permitirían **53/51/52/50/53** incorporaciones por fold, nunca las 59 en todos. El lector IA, no el modelo ni una cuota, asigna las etiquetas; confianza no calibrada, sin doble revisión semántica independiente.

No cambios de scripts, tests, L0, etiquetas originales, v2/folds/A ni paquete BETO. No nuevos modelos, métricas o sintéticos. Los 106 tests de software son del cierre anterior de selección/Excel; esta continuación añade comprobaciones de datos, citas, planes y contador. Si el corpus no alcanza 300 válidos por clase, informar sin inventar, duplicar o bajar el estándar para llenar cuotas.

## Estado científico vigente

- Referencia v2 fija: 19 decisiones aceptadas / 16 cambios efectivos; 12 ambiguos originales sin modificar. H125/D89/N1138; relevantes para B: H125/D89/N869.
- Control TF-IDF vigente: F1 H/D media **0,747060**, 51 errores sobre 793; 15 inversiones H↔D, 12 H/D→N y 24 N→H/D.
- **BETO v1 recibido y no adoptado:** cinco folds externos, F1 H/D media **0,625043**, 66 errores; 25 H↔D, 14 H/D→N, 27 N→H/D. Solo mejora 1/5 folds. Corrige 19 errores pero pierde 34 aciertos. [Informe y procedencia](RESULTADOS_BETO_V1.md).
- Métricas externas reconsolidadas exactamente y comprobadas aritméticamente. Registros declaran RTX 5060 y smoke exitoso; no se repitió aquí entrenamiento/tokenización oficial. El investigador confirmó que no se modificaron los scripts; esa declaración está separada en `data/auditoria/recepcion_beto_v1/confirmacion_usuario.json`. No volver a pedirla. Entorno/CUDA completo y hashes remotos siguen sin recibirse, sin exigirlos ahora.
- Paquete BETO **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`**, 1.352 textos / 1.997.823 caracteres / 793 validaciones, intacto. Ninguna referencia/fold/A cambió por la selección.
- Diez inversiones TF-IDF diagnosticadas previamente y cinco ambiguas desglosadas. La lectura posterior de 20 inversiones nuevas BETO y siete corregidas se inició, pero no tiene informe cerrado ni causa demostrada del deterioro.
- La [investigación web](INVESTIGACION_SOTA_POSTURA_MONETARIA.md) registra 20 fuentes y candidatos, no adopciones ni autorización de entrenar todas las alternativas.

## Qué sigue y qué no

1. El agente continúa con G001–G020 y después amplía la búsqueda hasta intentar 300 H/300 D. C01–C60, E001–E020 y F001–F009 están cerrados; no repetirlos.
2. Completar y revisar la capa IA de entrenamiento; no reabrir las 306 respuestas ni rehacer las 30 anotaciones humanas anteriores. En una selección futura excluir también los nuevos IDs ya anotados.
3. Mantener TF-IDF. No nuevo entrenamiento, refit global, scoring del corpus, cambios de referencias o datasets externos por la mera creación del Excel.
4. **Idea sintética solo registrada**, PLAN §9.24: no generar ahora. La meta autorizada ahora es 300 H/300 D, sin forzar respuestas para cumplirla.
5. **Limpieza extrema final obligatoria y pendiente**, REGLAS §12: reducir de verdad la entrega a una entrada y pocos módulos esenciales. El gestor sobre los scripts históricos no cumple por sí solo el cierre.

## Continuidad y publicación

Leer [CONTINUIDAD](CONTINUIDAD.md), [EMPEZAR_AQUI](../EMPEZAR_AQUI.md) y [PLAN](../PLAN.md), especialmente §§9.20–9.25. Se conserva el PR #4, sin cerrarlo/fusionarlo por el agente. Descargar no requiere cerrar; integrar a main requiere Merge. Los ZIP anteriores no se actualizan automáticamente.

La historia y comprobaciones anteriores —incluida la instalación limpia desde ZIP con 90 pruebas— están en PLAN y `data/auditoria/entrega_portable_v1/`; no equivalen a verificar una ejecución GPU ni a terminar la limpieza final.
