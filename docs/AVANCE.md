# AVANCE — Proyecto D&H

## Estado actual: el agente anota ejemplos para entrenamiento; no esperar Excel humano

El investigador aclaró que quiere que **la IA busque y puntúe las intervenciones de entrenamiento**, no otra tarea de anotación para él. Esto sustituye la espera de respuestas al Excel de 60 candidatos. El libro vacío se conserva como artefacto de selección, sin hacerlo pasar por una respuesta humana.

**Primera tanda IA terminada, C01–C30:** 30 textos íntegros, **107.796 caracteres / 17.674 palabras**. Resultado: **7 H, 13 D, 10 N**. Núcleo propuesto de alta confianza: **6 H + 12 D = 18 intervenciones completas**. C13 H y C15 D tienen confianza media y quedan en reserva. C03 se registra como N de baja confianza/duda y no se incorpora. No se fuerzan los N a H/D.

Archivos en `data/auditoria/ampliacion_hd_60_v1/anotacion_ia_v1/tanda_01/`: decisiones del agente, CSV de 30 anotaciones, JSON con los 18 textos H/D altos, plan por fold, resumen, manifiesto y verificación. Método `ia_lectura_integra`, no gold humano ni evaluación independiente. [Detalle](ANOTACION_IA_AMPLIACION_HD_V1.md).

**Pendientes C31–C60**, a leer y anotar por la IA en una segunda tanda respetando el presupuesto de 20.000 palabras. No preguntar al investigador si completó el Excel ni inventar etiquetas de los casos pendientes. No esperar revisión humana para seguir la tarea autorizada; si llega alguna, conservarla como fuente separada y declarar exposición a IA.

### Controles y límites

30 citas verificadas como subcadenas literales exactas (máximo 260 caracteres), campos válidos con utilidades compartidas, hashes de todos los textos contra L0, cero solapes con 1.352 anotados/306 del marco humano y cero casi copias Jaccard ≥0,85. Payload H/D de alta confianza conserva 18 textos completos, no solo citas. Las 150 filas del plan por fold respetan exclusiones por reunión/texto; permitirían **16/15/16/17/17** de esos 18 casos respectivamente, pero **no se incorporó ninguno a train**.

No se modificó código en esta tanda. El paquete BETO y sus fuentes congeladas se verificaron intactos. Los 106 tests de software pertenecen al cierre previo de selección/Excel; la nueva evidencia es de integridad de anotaciones, **no de entrenamiento ni doble revisión semántica**. La confianza es juicio del agente, no calibración probabilística.

La selección de origen sigue siendo de 60 candidatos reales, 56 reuniones, 29 actores, 202.789 caracteres y dos canales lexicales de 30. Esos canales no eran etiquetas y el muestreo no es representativo. El archivo técnico de selección no debe usarse como verdad. [Protocolo de selección, ahora histórico respecto del encargo humano](AMPLIACION_HD_60_V1.md).

## Estado científico vigente

- Referencia v2 fija: 19 decisiones aceptadas / 16 cambios efectivos; 12 ambiguos originales sin modificar. H125/D89/N1138; relevantes para B: H125/D89/N869.
- Control TF-IDF vigente: F1 H/D media **0,747060**, 51 errores sobre 793; 15 inversiones H↔D, 12 H/D→N y 24 N→H/D.
- **BETO v1 recibido y no adoptado:** cinco folds externos, F1 H/D media **0,625043**, 66 errores; 25 H↔D, 14 H/D→N, 27 N→H/D. Solo mejora 1/5 folds. Corrige 19 errores pero pierde 34 aciertos. [Informe y procedencia](RESULTADOS_BETO_V1.md).
- Métricas externas reconsolidadas exactamente y comprobadas aritméticamente. Registros declaran RTX 5060 y smoke exitoso; no se repitió aquí entrenamiento/tokenización oficial. El investigador confirmó que no se modificaron los scripts; esa declaración está separada en `data/auditoria/recepcion_beto_v1/confirmacion_usuario.json`. No volver a pedirla. Entorno/CUDA completo y hashes remotos siguen sin recibirse, sin exigirlos ahora.
- Paquete BETO **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`**, 1.352 textos / 1.997.823 caracteres / 793 validaciones, intacto. Ninguna referencia/fold/A cambió por la selección.
- Diez inversiones TF-IDF diagnosticadas previamente y cinco ambiguas desglosadas. La lectura posterior de 20 inversiones nuevas BETO y siete corregidas se inició, pero no tiene informe cerrado ni causa demostrada del deterioro.
- La [investigación web](INVESTIGACION_SOTA_POSTURA_MONETARIA.md) registra 20 fuentes y candidatos, no adopciones ni autorización de entrenar todas las alternativas.

## Qué sigue y qué no

1. El agente debe continuar con C31–C60. Ya hay una primera capa de 30 anotaciones IA, sin aceptación humana por caso ni integración al modelo.
2. Completar y revisar la capa IA de entrenamiento; no reabrir las 306 respuestas ni rehacer las 30 anotaciones humanas anteriores. En una selección futura excluir también los nuevos IDs ya anotados.
3. Mantener TF-IDF. No nuevo entrenamiento, refit global, scoring del corpus, cambios de referencias o datasets externos por la mera creación del Excel.
4. **Idea sintética solo registrada**, PLAN §9.24: no generar ahora. El objetivo de acercarse a 200 H/200 D es orientativo y posterior, no una cuota que imponer a las respuestas.
5. **Limpieza extrema final obligatoria y pendiente**, REGLAS §12: reducir de verdad la entrega a una entrada y pocos módulos esenciales. El gestor sobre los scripts históricos no cumple por sí solo el cierre.

## Continuidad y publicación

Leer [CONTINUIDAD](CONTINUIDAD.md), [EMPEZAR_AQUI](../EMPEZAR_AQUI.md) y [PLAN](../PLAN.md), especialmente §§9.20–9.25. Se conserva el PR #4, sin cerrarlo/fusionarlo por el agente. Descargar no requiere cerrar; integrar a main requiere Merge. Los ZIP anteriores no se actualizan automáticamente.

La historia y comprobaciones anteriores —incluida la instalación limpia desde ZIP con 90 pruebas— están en PLAN y `data/auditoria/entrega_portable_v1/`; no equivalen a verificar una ejecución GPU ni a terminar la limpieza final.
