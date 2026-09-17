# AVANCE — Proyecto D&H

## Estado actual: meta 300 H / 300 D, ampliación IA en curso

El investigador pidió «intentemos llevar cada uno a 300». Meta registrada el **17-09-2026** en `data/auditoria/meta_hd_300_v1/objetivo.json`: base v2 fija más nuevos casos H/D de alta confianza. No son 300 nuevos ni 300 por fold. Sin etiquetas forzadas, duplicados o sintéticos para alcanzar la cifra.

**60 candidatos iniciales completamente leídos en dos tandas**, 202.789 caracteres: 18 H, 22 D y 20 N según la IA. Nuevos H/D altos: **17 H + 18 D**. Sumados a la base vigente H125/D89, hay **142 H / 107 D preparados en el catálogo**, aún sin incorporar a train. **Faltan 158 H y 193 D.** Las reservas medias H1/D4 no cuentan; las dos dudas N tampoco se convierten en dirección.

Segunda tanda cerrada C31–C60: 94.993 caracteres / 15.608 palabras, 11 H/9 D/10 N; núcleo alto 11 H/6 D. Datos en `data/auditoria/ampliacion_hd_60_v1/anotacion_ia_v1/tanda_02/`. Primera tanda intacta. [Informe](ANOTACION_IA_AMPLIACION_HD_V1.md), contador con hashes en `data/auditoria/meta_hd_300_v1/progreso.json`.

**Siguiente: anotar E001–E020**, cola nueva en `data/auditoria/meta_hd_300_v1/seleccion_03/cola.json`. Son 20 candidatos sin etiquetas, 14.146 palabras, 17 reuniones y 15 actores. Prioridad a recomendación/voto, sesgo doméstico y acuerdo institucional para evitar gastar la tanda en exposiciones puramente extranjeras. Canales 9 H/11 D son búsqueda, no anotaciones; no sumarlos a la meta. Un intento de 30 solo alcanzó 29 con el presupuesto; se redujo la cola a 20 antes de leerla, sin relajar controles. No garantiza que el corpus alcance la meta completa.

### Controles y límites

60 citas literales verificadas acumuladas; campos/hashes/IDs/textos comprobados. Sin solapes con 1.352 originales, 306 del marco humano o entre tandas, incluyendo control de casi copias Jaccard ≥0,85. Payloads altos conservan **35 intervenciones completas**, no solo citas. El plan acumulado permitiría 32/30/29/32/33 incorporaciones por fold tras purga; efectivamente se incorporaron **cero**.

No se modificaron scripts, etiquetas originales, v2/folds/A o paquete BETO. No hubo entrenamiento ni nuevas métricas. La confianza es juicio de la IA, no probabilidad calibrada ni revisión humana independiente. Los 106 tests de software son del cierre anterior de selección/Excel; en esta tanda se verificaron datos, citas, manifiestos, planes y contador.

El agente es responsable de seguir anotando; **no esperar el Excel del investigador**. El libro vacío permanece como antecedente, nunca como supuesta respuesta humana. Las próximas tandas deben excluir también estos 60 IDs (incluidos N, reservas y dudas) y usar los textos originales completos. Si faltan casos válidos, informar, no inventar.

## Estado científico vigente

- Referencia v2 fija: 19 decisiones aceptadas / 16 cambios efectivos; 12 ambiguos originales sin modificar. H125/D89/N1138; relevantes para B: H125/D89/N869.
- Control TF-IDF vigente: F1 H/D media **0,747060**, 51 errores sobre 793; 15 inversiones H↔D, 12 H/D→N y 24 N→H/D.
- **BETO v1 recibido y no adoptado:** cinco folds externos, F1 H/D media **0,625043**, 66 errores; 25 H↔D, 14 H/D→N, 27 N→H/D. Solo mejora 1/5 folds. Corrige 19 errores pero pierde 34 aciertos. [Informe y procedencia](RESULTADOS_BETO_V1.md).
- Métricas externas reconsolidadas exactamente y comprobadas aritméticamente. Registros declaran RTX 5060 y smoke exitoso; no se repitió aquí entrenamiento/tokenización oficial. El investigador confirmó que no se modificaron los scripts; esa declaración está separada en `data/auditoria/recepcion_beto_v1/confirmacion_usuario.json`. No volver a pedirla. Entorno/CUDA completo y hashes remotos siguen sin recibirse, sin exigirlos ahora.
- Paquete BETO **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`**, 1.352 textos / 1.997.823 caracteres / 793 validaciones, intacto. Ninguna referencia/fold/A cambió por la selección.
- Diez inversiones TF-IDF diagnosticadas previamente y cinco ambiguas desglosadas. La lectura posterior de 20 inversiones nuevas BETO y siete corregidas se inició, pero no tiene informe cerrado ni causa demostrada del deterioro.
- La [investigación web](INVESTIGACION_SOTA_POSTURA_MONETARIA.md) registra 20 fuentes y candidatos, no adopciones ni autorización de entrenar todas las alternativas.

## Qué sigue y qué no

1. El agente continúa con E001–E020 y después amplía la búsqueda hasta intentar 300 H/300 D. Los C01–C60 están cerrados; no volver a etiquetarlos.
2. Completar y revisar la capa IA de entrenamiento; no reabrir las 306 respuestas ni rehacer las 30 anotaciones humanas anteriores. En una selección futura excluir también los nuevos IDs ya anotados.
3. Mantener TF-IDF. No nuevo entrenamiento, refit global, scoring del corpus, cambios de referencias o datasets externos por la mera creación del Excel.
4. **Idea sintética solo registrada**, PLAN §9.24: no generar ahora. La meta autorizada ahora es 300 H/300 D, sin forzar respuestas para cumplirla.
5. **Limpieza extrema final obligatoria y pendiente**, REGLAS §12: reducir de verdad la entrega a una entrada y pocos módulos esenciales. El gestor sobre los scripts históricos no cumple por sí solo el cierre.

## Continuidad y publicación

Leer [CONTINUIDAD](CONTINUIDAD.md), [EMPEZAR_AQUI](../EMPEZAR_AQUI.md) y [PLAN](../PLAN.md), especialmente §§9.20–9.25. Se conserva el PR #4, sin cerrarlo/fusionarlo por el agente. Descargar no requiere cerrar; integrar a main requiere Merge. Los ZIP anteriores no se actualizan automáticamente.

La historia y comprobaciones anteriores —incluida la instalación limpia desde ZIP con 90 pruebas— están en PLAN y `data/auditoria/entrega_portable_v1/`; no equivalen a verificar una ejecución GPU ni a terminar la limpieza final.
