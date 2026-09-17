# Ampliación H/D: anotación de IA para entrenamiento

## Cambio de encargo

El investigador aclaró que **el agente debe buscar y puntuar los ejemplos de entrenamiento**, no delegarle otra ronda de anotación humana. Desde esta aclaración no se espera que complete el Excel de 60 candidatos. El libro vacío se conserva como artefacto de selección, no se rellena ni se presenta como respuesta humana.

Se utilizan intervenciones reales completas de L0. La cita es evidencia de la decisión, **no el texto que reemplaza a la intervención al entrenar**. No se generan ejemplos ficticios ni se fuerza una cuota H/D.

## Primera tanda terminada: C01–C30

Se leyeron **30 intervenciones íntegras, 107.796 caracteres y 17.674 palabras**, dentro del presupuesto vigente de 20.000 palabras por tanda. Se registra etiqueta, confianza, cita literal, explicación y procedencia IA por caso.

| Resultado de la lectura IA | Cantidad |
|---|---:|
| Hawkish | 7 |
| Dovish | 13 |
| Neutral | 10 |
| Total revisado | 30 |

**Núcleo propuesto de alta confianza para ampliar H/D: 18 casos (6 H + 12 D).** Se prepararon sus textos completos, sin añadirlos todavía al train activo. Las otras dos decisiones direccionales —C13 H y C15 D— tienen confianza media y quedan en reserva. Los diez N no se fuerzan a H/D; C03 se marca además como duda y se excluye de incorporación. Confianza es el juicio del agente, no una probabilidad calibrada ni validación humana.

Esta primera tanda no agota los 60: **C31–C60 siguen pendientes de lectura/anotación IA**. No deben incorporarse por su canal de búsqueda. No hace falta esperar respuestas del investigador para continuar con ellos.

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

1. Continuar la lectura y anotación IA de C31–C60 en una segunda tanda separada; no esperar el Excel humano.
2. Revisar la calidad y variedad del conjunto ampliado sin forzar casos N o dudosos a H/D. No relajar la confianza para completar cuotas.
3. Preparar una nueva versión de los insumos de entrenamiento, respetando los folds y las purgas. No pasar estos JSON directamente a 38/39 ni mezclar paquetes.
4. Comparar contra el mismo control y validación de desarrollo, sin presentar esta ampliación como evaluación independiente. **No se ha realizado un nuevo entrenamiento en esta tanda.**
5. Mantener la limpieza extrema final pendiente y la idea sintética sin ejecutar.
