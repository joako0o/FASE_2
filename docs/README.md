# Documentación: orden de lectura

## Trabajo actual

**Trabajo vigente:** migración al [codebook v3 aprobado](codebook_v3.md). Inventario: 1.352 IA base + 89 IA nuevas + 306 humanas = 1.747 IDs distintos. Cerrados [prioritarias](REVISION_RONDAS_PRIORITARIAS_V3.md), pilotos [r1](REVISION_PILOTO_R1_V3.md), [r2](REVISION_PILOTO_R2_V3.md), [r3](REVISION_PILOTO_R3_V3.md), [r4](REVISION_PILOTO_R4_V3.md) y escalados [r5](REVISION_ESCALADO_R5_V3.md) a [r17](REVISION_ESCALADO_R11_R17_V3.md): **1.352 revisados, 395 pendientes**. Las 19 rondas IA originales están cerradas. V2 permanece como historial reproducible y no se entrena hasta consolidar v3.

**Antecedentes:** [auditoría inicial de compatibilidad](AUDITORIA_COMPATIBILIDAD_CRITERIOS_V1.md), [criterio acotado del plan B](CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md) y [fundamentos generales](DEFINICION_POSTURA_MONETARIA_PROPUESTA_V1.md).

**Consulta de calibración:** [plan B con actas históricas](CALIBRACION_PLAN_B_ACTAS_HISTORICAS.md), solo opinión; no corpus importado ni etiquetas finales.

**Último análisis:** [por qué se deterioró TF-IDF +59](DIAGNOSTICO_AMPLIACION_TFIDF_59_V1.md), lectura de los 16 cambios y descomposición de márgenes. Sin nueva variante ni etiquetas corregidas.

**Último ensayo:** [TF-IDF con 59 ejemplos nuevos](RESULTADOS_AMPLIACION_TFIDF_59_V1.md): comparación ejecutada, sin mejora y sin reemplazo del control.

**Trabajo vigente:** [anotación IA para ampliar entrenamiento](ANOTACION_IA_AMPLIACION_HD_V1.md), meta 300 H/300 D; 89 casos terminados y G001–G020 pendientes. El Excel de 60 no es una tarea humana requerida; no hay sintéticos ni nuevo entrenamiento.

**Último resultado:** [BETO v1 recibido y no adoptado](RESULTADOS_BETO_V1.md): cinco folds, métricas verificadas y límites de procedencia.

1. [EMPEZAR_AQUI](../EMPEZAR_AQUI.md): otro PC, instalación y ejecución.
2. [CONTINUIDAD](CONTINUIDAD.md): instrucciones para la siguiente sesión.
3. [AVANCE](AVANCE.md): último cierre y pendientes concretos.
4. [Investigación/protocolo BETO](INVESTIGACION_Y_PROTOCOLO_BETO_V1.md): método fijado y límites; documento histórico anterior a la recepción externa.
5. [Guía Colab](GUIA_EJECUTAR_BETO_COLAB_V1.md): alternativa si el PC no dispone de GPU.

6. [Investigación web de modelos y postura monetaria](INVESTIGACION_SOTA_POSTURA_MONETARIA.md): papers, candidatos actuales y foros; no cambia la corrida BETO.

## Reglas y resultados de referencia

- [Reglas de trabajo](REGLAS.md), [codebook v3 vigente](codebook_v3.md) y [codebook v2 histórico](codebook_v2.md).
- [Evaluación con referencias corregidas](EVALUACION_REFERENCIAS_CORREGIDAS_V2.md): control TF-IDF vigente.
- [Diagnóstico H/D, síntesis](LECTURA_DIAGNOSTICO_INVERSIONES_HD_V1.md) y [detalle técnico](DIAGNOSTICO_INVERSIONES_HD_V1.md).
- [PLAN](../PLAN.md): decisiones metodológicas y cronología detallada, no lista de comandos que ejecutar ahora.

## Archivo histórico conservado

Los documentos de TF-IDF/gold, léxico, n-gramas, híbrido, WCB, revisión humana, adjudicaciones y revisión de errores registran etapas cerradas. Sus propuestas pendientes **en aquella fecha** no anulan aceptaciones posteriores. Para conocer el estado vigente, leer CONTINUIDAD, no deducirlo de un informe viejo.

No se movieron ni renombraron: varios tienen hashes fijados en manifiestos. Se retiraron de la portada las instrucciones repetidas de formularios ya devueltos. No hace falta volver a leer todo el historial para continuar.
