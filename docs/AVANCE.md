# AVANCE — Proyecto D&H

## Estado actual: 60 candidatos reales entregados; esperar respuestas

El investigador autorizó preparar una muestra dirigida H/D y pidió continuar. Ya está creado **`data/auditoria/ampliacion_hd_60_v1/revision_60_candidatos.xlsx`**, con seis bloques de diez, texto completo, guía, enlaces de navegación y celdas amarillas vacías. Puede devolver el mismo XLSX, incluso parcial. **No regenerarlo ni usar el importador de las 30 anotaciones anteriores.**

- Selección reproducible desde 667 candidatos con pistas: dos canales de búsqueda de 30, no clases confirmadas. Por canal, diez patrones de decisión, diez de trayectoria y diez de contraste.
- **56 reuniones, 29 actores, 2005–2015, 202.789 caracteres íntegros**. Veinte textos cortos, veinte medios y veinte largos; máximo dos por reunión y cinco por actor en esta muestra.
- Excluidos 1.352 IDs anotados y 306 del marco humano, copias normalizadas y casi copias según Jaccard de trigramas ≥0,85. Cero solapes verificados. Del marco humano solo se usan IDs, no sus respuestas.
- La muestra es enriquecida para desarrollo/entrenamiento: no es representativa ni un test independiente. H/D/N y dudas se decidirán al revisar; no forzar cuotas.
- Plan por caso de folds potenciales/prohibidos según reunión/texto, **sin incorporación a train**. La futura recepción deberá validar identidad, citas, pendientes, fecha/ayuda declaradas y purga antes de cualquier ampliación autorizada.

Protocolo: [AMPLIACION_HD_60_V1](AMPLIACION_HD_60_V1.md). Evidencia en la carpeta de muestra: manifiesto, resumen y verificación. El archivo `NO_CONSULTAR_antes_de_responder_seleccion.json` contiene pistas técnicas; no consultarlo ni mostrárselo al investigador antes de que responda.

### Verificación de esta entrega

**106 pruebas aprobadas, 0 omitidas**: 98 anteriores y ocho de muestreo/libro. Selección idéntica al invertir el orden del corpus; 60 textos recuperados del XLSX idénticos a L0; 240 celdas de respuesta vacías; sin hojas ocultas, macros ni enlaces externos. Se comprobó con openpyxl, **no se ejecutó Excel/LibreOffice**.

Comando reproducible: `python scripts/40_gestionar_proyecto.py preparar-muestra-hd --salida RUTA_NUEVA`. El gestor delega en `scripts/muestreo_revision.py`, reutilizando utilidades Excel de 29 sin editar etapas congeladas. No nuevo script numerado 41 ni variante de modelo. La muestra ya existe: no hace falta ejecutar código para responder.

## Estado científico vigente

- Referencia v2 fija: 19 decisiones aceptadas / 16 cambios efectivos; 12 ambiguos originales sin modificar. H125/D89/N1138; relevantes para B: H125/D89/N869.
- Control TF-IDF vigente: F1 H/D media **0,747060**, 51 errores sobre 793; 15 inversiones H↔D, 12 H/D→N y 24 N→H/D.
- **BETO v1 recibido y no adoptado:** cinco folds externos, F1 H/D media **0,625043**, 66 errores; 25 H↔D, 14 H/D→N, 27 N→H/D. Solo mejora 1/5 folds. Corrige 19 errores pero pierde 34 aciertos. [Informe y procedencia](RESULTADOS_BETO_V1.md).
- Métricas externas reconsolidadas exactamente y comprobadas aritméticamente. Registros declaran RTX 5060 y smoke exitoso; no se repitió aquí entrenamiento/tokenización oficial. El investigador confirmó que no se modificaron los scripts; esa declaración está separada en `data/auditoria/recepcion_beto_v1/confirmacion_usuario.json`. No volver a pedirla. Entorno/CUDA completo y hashes remotos siguen sin recibirse, sin exigirlos ahora.
- Paquete BETO **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`**, 1.352 textos / 1.997.823 caracteres / 793 validaciones, intacto. Ninguna referencia/fold/A cambió por la selección.
- Diez inversiones TF-IDF diagnosticadas previamente y cinco ambiguas desglosadas. La lectura posterior de 20 inversiones nuevas BETO y siete corregidas se inició, pero no tiene informe cerrado ni causa demostrada del deterioro.
- La [investigación web](INVESTIGACION_SOTA_POSTURA_MONETARIA.md) registra 20 fuentes y candidatos, no adopciones ni autorización de entrenar todas las alternativas.

## Qué sigue y qué no

1. El investigador puede empezar por **Bloque 1** y devolver avances. No hay etiquetas nuevas aceptadas todavía.
2. Recibir y verificar este libro como una muestra nueva; no reabrir las 306 respuestas ni rehacer las 30 anotaciones anteriores.
3. Mantener TF-IDF. No nuevo entrenamiento, refit global, scoring del corpus, cambios de referencias o datasets externos por la mera creación del Excel.
4. **Idea sintética solo registrada**, PLAN §9.24: no generar ahora. El objetivo de acercarse a 200 H/200 D es orientativo y posterior, no una cuota que imponer a las respuestas.
5. **Limpieza extrema final obligatoria y pendiente**, REGLAS §12: reducir de verdad la entrega a una entrada y pocos módulos esenciales. El gestor sobre los scripts históricos no cumple por sí solo el cierre.

## Continuidad y publicación

Leer [CONTINUIDAD](CONTINUIDAD.md), [EMPEZAR_AQUI](../EMPEZAR_AQUI.md) y [PLAN](../PLAN.md), especialmente §§9.20–9.25. Se conserva el PR #4, sin cerrarlo/fusionarlo por el agente. Descargar no requiere cerrar; integrar a main requiere Merge. Los ZIP anteriores no se actualizan automáticamente.

La historia y comprobaciones anteriores —incluida la instalación limpia desde ZIP con 90 pruebas— están en PLAN y `data/auditoria/entrega_portable_v1/`; no equivalen a verificar una ejecución GPU ni a terminar la limpieza final.
