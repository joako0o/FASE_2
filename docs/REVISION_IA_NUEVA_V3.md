# Revisión v3 — cuatro tandas IA nuevas

**Fecha:** 17-09-2026
**Alcance:** 89/89 intervenciones de las cuatro tandas IA nuevas, incluidas H, D y N.

## Resultado frente a la anotación IA previa

| Tanda | Archivo | Revisadas | Compatibles | Cambios |
|---|---|---:|---:|---:|
| 01 | `ampliacion_hd_60_v1/.../tanda_01/anotaciones_ia.csv` | 30 | 29 | 1 |
| 02 | `ampliacion_hd_60_v1/.../tanda_02/anotaciones_ia.csv` | 30 | 30 | 0 |
| 03 | `meta_hd_300_v1/.../tanda_03/anotaciones_ia.csv` | 20 | 18 | 2 |
| 04 | `meta_hd_300_v1/.../tanda_04/anotaciones_ia.csv` | 9 | 9 | 0 |
| **Total** | | **89** | **86** | **3** |

Las tres transiciones son D→N. La distribución conjunta pasa de 30 H/37 D/22 N a 30 H/34 D/25 N. No hubo cambios de relevancia y todas las filas conservan relevancia 1.

## Correcciones

- `RPM-2011-10-13:4388:1`: propone mantener y cambiar el sesgo, pero no identifica la dirección del nuevo sesgo. El deterioro macroeconómico no permite inferir D.
- `RPM-2014-08-14:6375:1`: presenta mantener, recortar 25 o recortar 50 con argumentos para cada opción, sin conclusión propia. Un menú que incluye recortes sigue siendo N.
- `RPM-2011-12-13:4512:1`: vota mantener y únicamente señala que “no se opondría” a un sesgo a la baja. La no oposición atenuada no equivale a adoptar, recomendar o respaldar D.

Se conservaron las anotaciones direccionales cuando existía voto, recomendación, acuerdo, sesgo futuro o defensa sustantiva del estímulo/restricción. También se conservaron N los relatos históricos, expectativas ajenas, diagnósticos y casos con dirección no resuelta. Los casos que originalmente tenían confianza media o baja fueron abiertos y leídos completos; la revisión v3 no heredó automáticamente su incertidumbre.

## Cierre de todas las anotaciones IA

Con estas tandas quedan revisadas **1.441/1.441 anotaciones IA**: 1.352 de las rondas originales y 89 nuevas. Permanecen únicamente las 306 humanas.

La evidencia por ID está en `data/auditoria/revision_ia_nueva_tanda_01_v3/` a `revision_ia_nueva_tanda_04_v3/`. Se preservaron los archivos IA originales y sus etiquetas; las correcciones existen solo en la capa v3. Las etiquetas eran visibles y la revisión fue realizada por el agente, no por un segundo anotador ciego. No hubo entrenamiento.
