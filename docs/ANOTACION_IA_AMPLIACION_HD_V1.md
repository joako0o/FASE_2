# Ampliación H/D: anotación de IA para entrenamiento

## Cambio de encargo

El investigador aclaró que **el agente debe buscar y puntuar los ejemplos de entrenamiento**, no delegarle otra ronda de anotación humana. Desde esta aclaración no se espera que complete el Excel de 60 candidatos. El libro vacío se conserva como artefacto de selección, no se rellena ni se presenta como respuesta humana.

Se utilizan intervenciones reales completas de L0. La cita es evidencia de la decisión, **no el texto que reemplaza a la intervención al entrenar**. No se generan ejemplos ficticios ni se fuerza una cuota H/D.

## Meta vigente: 300 H y 300 D

El 17-09-2026 el investigador pidió «intentemos llevar cada uno a 300». Se entiende como **300 por clase en el catálogo total**, contando la referencia v2 fija y los nuevos IDs de alta confianza; no como 300 nuevos ni 300 dentro de cada fold tras purga. No se rebaja la confianza ni se fuerzan etiquetas para completar el objetivo.

| Contador | H | D |
|---|---:|---:|
| Base vigente usada por los modelos | 125 | 89 |
| Nuevos de alta confianza preparados, cuatro tandas | 29 | 30 |
| **Base + preparados** | **154** | **119** |
| **Faltan para 300** | **146** | **181** |
| Reservas de confianza media, no contadas | 1 | 6 |

Los 60 candidatos iniciales se cerraron en las primeras dos tandas: 18 H, 22 D y 20 N según la IA. Solo 35 de los 40 direccionales son de alta confianza. Ninguna nueva anotación está integrada todavía al train activo. El objetivo y el contador auditado están en `data/auditoria/meta_hd_300_v1/objetivo.json` y `progreso.json`.

**Segunda tanda C31–C60:** 94.993 caracteres / 15.608 palabras; 11 H, 9 D, 10 N. Aporta 11 H y 6 D de alta confianza. C32/C40/C56 son D medios en reserva; C60 es N de baja confianza/duda. Se conservaron las mismas reglas: sesgo al alza con mantención puede ser H (C52/C54), recorte con sesgo neutral sigue siendo D (C53), y descripción de tasas/encuestas extranjeras no es postura chilena. No se alteran las decisiones de la primera tanda.

**Avance adicional de las tandas 03 y 04:** 29 intervenciones reales completas, 96.608 caracteres / 15.702 palabras. E001–E020: 7 H, 11 D, 2 N; núcleo utilizable 7 H/8 D. F001–F009: 5 H/4 D, todos de alta confianza. Se completaron 89 nuevas anotaciones en total (30 H/37 D/22 N), de las cuales **59 H/D altos sin descarte** cuentan para la meta. No hay entrenamiento nuevo ni integración al paquete activo.

**E009 se excluye aunque su etiqueta D sea clara.** Repite casi la misma plantilla que C35, de otra reunión; el Jaccard de trigramas es 0,80645, por debajo del filtro inicial 0,85. Se conserva la anotación y el vínculo al original, pero no se usa para inflar la variedad ni el contador. Las dos nuevas decisiones D medias E010/E015 quedan en reserva; E012 es N dudoso. No se reescriben tandas anteriores ni referencias de validación.

La tanda breve F001–F009 complementa el lote largo y contiene todos los remanentes de prioridad doméstica de 200–1.600 caracteres que pasaron exclusiones. No es una muestra representativa ni prueba de que solo necesitemos votos fáciles. La suma de palabras leídas en esta continuación permanece bajo 20.000.

**Próxima cola G001–G020**, aún sin etiquetas, en `data/auditoria/meta_hd_300_v1/seleccion_05/cola.json`: 15.056 palabras. Excluye los 89 nuevos casos ya vistos, incluidos N, reservas y duplicados descartados, además de los marcos originales. Para esta nueva selección se endurece explícitamente la exclusión de casi copias a Jaccard ≥0,80, motivada por E009; no se modifican retroactivamente los filtros ni anotaciones anteriores. Los canales 9 H/11 D son búsqueda, no etiquetas. La inspección semántica sigue siendo necesaria.

El usuario mantiene la meta 300/300; no necesita autorizar cada tanda ni anotar el Excel. Si no hay suficientes casos válidos en el corpus, se debe informar el límite en vez de completar con duplicados, sintéticos o etiquetas forzadas.

## Primera tanda terminada: C01–C30

Se leyeron **30 intervenciones íntegras, 107.796 caracteres y 17.674 palabras**, dentro del presupuesto vigente de 20.000 palabras por tanda. Se registra etiqueta, confianza, cita literal, explicación y procedencia IA por caso.

| Resultado de la lectura IA | Cantidad |
|---|---:|
| Hawkish | 7 |
| Dovish | 13 |
| Neutral | 10 |
| Total revisado | 30 |

**Núcleo propuesto de alta confianza para ampliar H/D: 18 casos (6 H + 12 D).** Se prepararon sus textos completos, sin añadirlos todavía al train activo. Las otras dos decisiones direccionales —C13 H y C15 D— tienen confianza media y quedan en reserva. Los diez N no se fuerzan a H/D; C03 se marca además como duda y se excluye de incorporación. Confianza es el juicio del agente, no una probabilidad calibrada ni validación humana.

La primera tanda no agotaba los 60; C31–C60 se completaron después en `tanda_02/`, sin tomar sus canales de búsqueda como etiquetas. No hace falta esperar respuestas del investigador para continuar la ampliación.

## Decisiones y problemas detectados

| Caso | Etiqueta IA | Confianza | Motivo resumido |
|---|---|---|---|
| C01 | N | Alta | Sesgos de la canasta del IPC, no de la TPM |
| C02 | H | Alta | Adhesión a subir 50 pb |
| C03 | N / duda | Baja | Pausa, alzas previas y panorama futuro sin resolución clara; no incorporar |
| C04 | D | Alta | Voto por reducir 25 pb |
| C05 | H | Alta | Subir 25 en vez de 50 sigue siendo alza |
| C06 | D | Alta | Recomienda iniciar recortes y anunciar sesgo a la baja |
| C07 | N | Alta | Discusión de desanclaje/coordinación sin dirección de TPM fijada |
| C08 | H | Alta | Voto por alza de 25 pb |
| C09 | D | Alta | Recorte de 25 pb y sesgo expansivo |
| C10 | D | Alta | Voto por recortar 200 pb |
| C11 | D | Alta | Recortar 25 en vez de 50 sigue siendo baja |
| C12 | D | Alta | Recorte de 250 pb y sesgo a la baja |
| C13 | H | Media | Trayectoria de menor impulso dentro de escenario técnico; reserva |
| C14 | D | Alta | Normalización aquí significa bajar: voto de recorte explícito |
| C15 | D | Media | Cambio de sesgo ante deterioro, sin recorte explícito; reserva |
| C16 | H | Alta | Recomendación explícita de alza del staff |
| C17 | N | Alta | Tasas y políticas extranjeras sin recomendación doméstica |
| C18 | N | Media | Mantención/sesgo neutral y discusión de normalización condicionada |
| C19 | N | Alta | Tasas de Francia, Alemania y Estados Unidos |
| C20 | D | Alta | Mantener hoy y recomendar sesgo negativo no condicional |
| C21 | N | Alta | Recorte de México y descripción internacional |
| C22 | H | Alta | Adhesión a alza de 50 pb y sesgo al alza |
| C23 | N | Alta | Diagnóstico y referencia a alza pasada, sin nueva orientación propia |
| C24 | D | Alta | Recomendación de mantener el sesgo a la baja |
| C25 | N | Alta | Recapitulación por el staff de la decisión/anuncio de julio |
| C26 | H | Alta | Acuerdo institucional actual de alza de 25 pb |
| C27 | D | Alta | Justifica mayor expansividad ante actividad débil y menores presiones |
| C28 | N | Alta | Contrasta encuestas sin hacer propia una trayectoria |
| C29 | D | Alta | Recomienda bajar 25 pb en la reunión |
| C30 | D | Alta | Voto/acuerdo de baja y perspectiva de relajamiento adicional |

Las citas y notas completas están en los archivos de datos, con los IDs originales y hashes. R1/R2/R3/R5/R7/R9 se aplican con las aclaraciones posteriores aceptadas: historia/mención no equivale a adhesión; normalización no implica H automáticamente; una pausa no determina N; menor ritmo de endurecimiento no significa D; la dirección futura respaldada sí cuenta.

**Conclusión sobre el muestreo, no sobre precisión de un modelo:** la búsqueda lexical también encuentra tasas extranjeras, expectativas ajenas y objetos distintos de la TPM. Esos candidatos se etiquetan N cuando corresponde. El canal H/D de selección nunca se usa como etiqueta verdadera.

## Separación y control de calidad

- Cero solapes de IDs y textos normalizados con los 1.352 anotados originales y los 306 del marco humano. El marco humano se consulta solo por ID para exclusión; no se abrieron sus respuestas.
- Las 30 citas fueron comprobadas con `utilidades.errores_anotacion` y además como subcadenas exactas de su intervención original; máximo observado, 260 caracteres.
- El payload de alta confianza conserva íntegros los 18 textos y su SHA-256, no citas aisladas ni resúmenes.
- Se conserva un plan de 150 filas (30 casos × 5 folds), con exclusión por reunión/texto de validación. Para los 18 H/D altos, los números **potencialmente incorporables** por fold son 16/15/16/17/17. No se han añadido a ningún train.
- Los N, las dos decisiones direccionales de confianza media y la duda quedan documentados y separados. No se borran para aparentar una selección perfecta.
- No se modifica L0, etiquetas originales, adjudicaciones aceptadas, v2, A ni los folds. No se cambia el paquete BETO actual ni se reescriben sus métricas.
- El control semántico es la lectura del mismo agente: **no hay segunda anotación independiente ni aprobación humana por caso**. Las etiquetas son de entrenamiento propuesto, no gold ni test independiente.

## Archivos

Carpeta: `data/auditoria/ampliacion_hd_60_v1/anotacion_ia_v1/tanda_01/`.

- `decisiones.json`: decisiones nativas del agente, con cita y razón; fuente de la anotación.
- `anotaciones_ia.csv`: 30 filas vinculadas a IDs/textos, con origen IA, confianza y uso propuesto.
- `documentos_hd_alta.json`: 18 intervenciones completas de alta confianza; candidatos, no un paquete listo para el runner congelado.
- `plan_por_fold.csv`: restricciones de incorporación por fold; todas las filas tienen incorporación efectiva en cero.
- `resumen.json`: autorización, alcance de lectura, conteos y C31–C60 pendientes.
- `manifest.json`: hashes de entradas y salidas de la tanda.
- `verificacion.json`: comprobaciones de integridad efectuadas al cerrar.

Se guardan fuera de `data/etiquetas/*.csv` para impedir que un cargador histórico las absorba accidentalmente y cambie el control. En una nueva selección habrá que excluir también estos IDs ya anotados, no solo los 1.352 de la vista anterior.

## Próximos pasos

1. Continuar con G001–G020 de la cola nueva, en `data/auditoria/meta_hd_300_v1/anotacion_ia_v1/tanda_05/`, aún no creada. Leer cada texto íntegro desde L0 y verificar su hash antes de anotar. No esperar el Excel humano.
2. Revisar la calidad y variedad del conjunto ampliado sin forzar casos N o dudosos a H/D. No relajar la confianza para completar cuotas.
3. Preparar una nueva versión de los insumos de entrenamiento, respetando los folds y las purgas. No pasar estos JSON directamente a 38/39 ni mezclar paquetes.
4. Comparar contra el mismo control y validación de desarrollo, sin presentar esta ampliación como evaluación independiente. **No se ha realizado un nuevo entrenamiento en esta tanda.**
5. Mantener la limpieza extrema final pendiente y la idea sintética sin ejecutar.


## Control de cierre de la segunda tanda y acumulado

Las 30 citas de la segunda tanda se verificaron como subcadenas exactas (máximo 191 caracteres); los 17 textos H/D altos son idénticos a L0. Cero solapes de ID/texto/casi copia con la base, el marco humano y la primera tanda. El plan de 150 filas de esta tanda permitiría 16/15/13/15/16 nuevos casos por fold. Sumadas ambas tandas, serían **32/30/29/32/33**, no 35 en todos los folds. Las incorporaciones efectivas siguen en cero.

Los datos de `tanda_02/` usan el mismo esquema que `tanda_01/`, con decisiones, CSV, payload de textos, plan, resumen, manifiesto y verificación. Se cotejaron ambas tandas y el acumulado de 60 IDs únicos/35 H/D altos. El paquete f7aa1589… no cambia. No se ejecutó un nuevo modelo ni hubo segunda anotación semántica independiente.


## Cierre de tandas 03 y 04

Carpetas `data/auditoria/meta_hd_300_v1/anotacion_ia_v1/tanda_03/` y `tanda_04/`, con el mismo esquema verificable de decisiones, CSV, textos completos, planes, resumen y hashes. Las 29 citas son literales; no hay solapes de IDs/textos normalizados con originales o tandas previas. El control automático Jaccard ≥0,85 no encontró copias, pero la inspección manual sí apartó E009, demostrando el límite de ese filtro.

Los 59 nuevos altos permitirían **53/51/52/50/53** incorporaciones por fold después de purga; las efectivas siguen en cero. Los resultados BETO v1, el control TF-IDF, v2/folds/A y el paquete de entrada permanecen intactos. El contador anterior se conserva en `data/auditoria/meta_hd_300_v1/progreso_tras_tanda02.json`; el actual en `progreso.json`. Esta revisión es IA, no gold humano ni segunda revisión semántica independiente.
