# Plan B: calibración de actas anteriores a 2000

**Consulta del investigador, 17-09-2026. Solo opinión metodológica sobre los textos pegados en el chat.** No se importó este corpus, no se asignaron etiquetas definitivas, no se modificó el codebook vigente ni se inició entrenamiento histórico.

## Dictamen

El corpus podría servir para estudiar transferencia temporal o un objetivo histórico más amplio, pero **no conviene mezclar las etiquetas mostradas con H/D/N de las intervenciones monetarias 2005–2015 sin corregir la definición de la tarea**. En la calibración aparecen como equivalentes cosas distintas: alivio de deuda, rescate o liquidez focalizada, crédito sectorial, regulación cambiaria y postura monetaria agregada.

Regla central: **beneficiar financieramente a un destinatario no demuestra por sí solo una postura monetaria dovish para Chile; restringir una operación no demuestra una postura hawkish**. Tampoco toda ratificación es solo administración: hay que identificar qué decisión sustantiva ratifica y su alcance.

## No es solo un cambio de fecha

El BCCh documenta la nominalización del instrumento en agosto de 2001, cuando pasó de una tasa indexada a UF a una nominal en pesos. También documenta la flotación cambiaria desde septiembre de 1999 y su articulación con metas de inflación. Por tanto, “pre-2000” no representa automáticamente el mismo régimen/instrumento que el corpus actual. Esto no significa que antes de 2001 no existiera política monetaria o instrumentos direccionales. [1](https://www.bcentral.cl/en/content/-/detalle/ver-mas-preguntas-frecuentes-7-2) [2](https://www.bcentral.cl/en/content/-/detalle/documentos-de-politica-economica-n-72)

Como ilustración conceptual, no como regla histórica aplicable a Chile en 1977, la documentación del ECB distingue asistencia de liquidez de emergencia de operaciones de política monetaria. El hecho de aportar liquidez no identifica por sí solo un cambio de postura agregada. No se comprobó aquí si las ayudas chilenas citadas se esterilizaban o tenían otra función. [1](https://www.ecb.europa.eu/pub/pdf/other/201402_elaprocedures.en.pdf)

No extrapolar automáticamente las actuales instituciones/reglas a cada década. Si se desea clasificar la postura histórica, habrá que definir qué instrumentos cuentan en cada régimen y qué evidencia textual permite determinar su orientación.

## Observaciones sobre los ejemplos, no adjudicaciones

| IDs del material pegado | Observación de calibración |
|---|---|
| 2, 3, 5, 17, 34, 37, 50, 88, 90 | Las etiquetas de fuera del objetivo monetario son razonables para multas individuales, personal y trámites descritos. No deducir H de sanciones ni D de condonaciones. |
| 26, 57 | Ayuda bancaria y refinanciamiento focalizado/sectorial no prueban por sí solos flexibilización monetaria agregada. No validaría D de confianza alta solo con lo mostrado. |
| 12, 23, 41, 45, 58 | Se repiten familias de refinanciamiento, reprogramación y ayuda de encaje, unas marcadas N/0 y otras D/1. Hace falta el mismo criterio de función, alcance y discrecionalidad, no “ayuda=D” y “ratificación=N”. Varias filas mezclan acuerdos distintos. |
| 42 | La justificación H es problemática: no se conoce el régimen anterior para interpretar los nuevos plazos y la segunda parte introduce una excepción: la prohibición no será aplicable a ciertas ventas/cesiones. No es suficiente resumirlo como mantenimiento de control restrictivo. Separar acuerdos y no inferir el efecto neto de la fila mixta. |
| 4480, 4481 | Reprogramación/ayuda a Bolivia: financiación o cooperación internacional, no evidencia directa de postura monetaria chilena. No tratar “acomodaticio internacional” como la misma D del clasificador actual. |
| 8713 | Posición de cambios y registro extemporáneo; el propio texto disputa el posible efecto sobre reservas. No hay efecto monetario agregado demostrado. |
| 69, 70, 73, 8723 | Organización/regulación cambiaria, transferibilidad y procedimientos de divisas. Registrar esa función; no identificar automáticamente control con H o flexibilización con D. Puede ser materia sustantiva aunque quede fuera del objetivo H/D actual. |
| 78 | Baja la tasa de una **sanción a exportadores**, no la tasa de política monetaria. No validaría D monetaria por el cambio 30→20. |
| 89 | Exenciones/anulaciones vinculadas a operaciones de exportadores. El alivio al destinatario no basta para D monetaria; criterio inconsistente con otros trámites similares marcados N/0. |
| 18551 | Provisiones y estados financieros: fuera del objetivo H/D monetario parece razonable con lo mostrado. |
| 18566 | No tratar toda la fila como publicación rutinaria: contiene un cambio normativo de 5% a 10% cuyo parámetro no se identifica en el fragmento. No asumir qué significa; “N/0 alta” necesita revisión de contexto. |
| 18572 | Tasas contractuales de programas específicos y fórmulas BIRF/TIP; no equivalen automáticamente a una tasa de política. Identificar tipo de tasa y discrecionalidad, no solo sus valores. |
| 44 | Costos y reembolsos operativos de pagarés usados en política monetaria. Tema monetario no implica cambio de orientación; distinguir implementación/contabilidad de decisión direccional. |
| 91, 92 | Tomar conocimiento de circulares/listados y ascensos no equivale a adoptar toda política mencionada en los títulos. No inferir orientación de la palabra encaje o crédito en un listado. |

Estas observaciones se limitan a los fragmentos enviados: **no se consultaron actas originales, anexos, normas previas ni datos macro de cada decisión**. No equivalen a etiquetas finales listas para entrenar. En particular, no se convierte todo caso dudoso o fuera de alcance en un N de alta confianza.

## Corrección prioritaria: unidad de observación

Varias filas contienen finales e inicios de acuerdos diferentes: 26 mezcla ayuda bancaria y refinanciamiento agrícola; 42 contiene ratificación, regla de encaje y excepción crediticia; 45 contiene ayuda de encaje y aporte de capital exterior. También hay comienzos y finales cortados, remisiones y beneficiarios omitidos.

Antes de etiquetar masivamente, preservar el texto bruto y definir unidades semánticas trazables, por ejemplo **discusión y resolución de un mismo asunto/acuerdo**, identificadas por acta, fecha y número de asunto. No dividir por un número arbitrario de caracteres ni mezclar varios asuntos bajo una sola clase. Si se cambia respecto de la unidad actual por intervención, debe declararse: no son observaciones directamente equivalentes.

No rellenar nombres/fragmentos faltantes o reconstruir tasas. Si una orientación depende de la norma previa o de un anexo, o se incluye ese contexto de modo consistente en el nuevo diseño o se registra contexto insuficiente; no etiquetar usando información que el modelo no recibirá. Las citas justificantes de una futura capa compatible deben ser literales y cumplir el límite de 300 caracteres, sin recortar la unidad de entrenamiento.

## Propuesta de anotación histórica, pendiente de acuerdo

Separar las preguntas, en este orden:

1. **Función de la medida:** monetaria agregada; liquidez/estabilidad financiera focalizada; crédito sectorial; regulación/cambios/capitales; deuda/pagos internacionales; administración.
2. **Instrumento y destinatario:** tasa de política, tasa de préstamo, tasa de multa, encaje, compra/venta de activos, plazo, cupo, etc.; alcance general, sectorial o individual. Moneda, indexación y periodicidad de tasas explícitas, sin comparaciones nominal/real o mensual/anual indebidas.
3. **Acción y cambio:** decisión nueva, ratificación, implementación, mera mención; expansión/restricción respecto de qué situación previa. Una nueva norma que fija un límite no necesariamente endurece el límite anterior.
4. **Dirección monetaria asignable:** H/D/N solo cuando la unidad permita determinarla dentro del objetivo definido. Usar un estado de fuera de alcance/contexto insuficiente cuando corresponda, separado del N sustantivo.
5. **Confianza y evidencia:** no “alta” si se desconoce qué instrumento cambia, el efecto direccional o si la unidad mezcla asuntos. Procedencia real/IA/humana debe quedar declarada.

No se trasladan estos campos a la A actual ni se cambia su definición sin un protocolo nuevo. La relevancia siempre depende del objetivo: “no cambia una tasa” no es un criterio universal de irrelevancia, y una regulación de encaje general puede ser monetariamente relevante.

## Cómo evaluaría el plan B, si después se autoriza

- Mantener corpus histórico y etiquetas separados de L0 y del catálogo actual. No sumar supuestos D/H históricos para alcanzar la meta 300 por cuota.
- Empezar con una pequeña calibración de casos de distintas funciones/regímenes, no etiquetar miles con el criterio actual. La revisión de incertidumbres puede seguir a cargo de la IA, declarando ese origen.
- Priorizar inicialmente períodos e instrumentos más comparables dentro de los noventa si el objetivo sigue siendo 2005–2015; esto es una estrategia de exploración, no garantía de mejor transferencia.
- Si el objetivo es postura monetaria histórica más amplia, crear un codebook separado; no confundir dirección de regulación o ayuda al deudor con la D/H actual.
- Solo después comparar entrenamiento actual frente a actual + histórico compatible, con un diseño fijado y evaluación real intacta. Separar resultados por régimen y comprobar copias/solapes. Fechas más antiguas no convierten la validación ya utilizada en un test independiente.

**Estado: idea de plan B en calibración. No datos incorporados, nuevas etiquetas, entrenamientos o cambios del proyecto principal.**
