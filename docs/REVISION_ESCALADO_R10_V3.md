# Revisión v3 — escalado r10

**Fecha:** 17-09-2026
**Archivo:** `data/etiquetas/etiquetas_escalado_r10.csv`
**Alcance:** 120/120 intervenciones, incluidas H, D, N y relevancia.

## Resultado frente a v2 vigente

| Resultado | Casos |
|---|---:|
| Compatibles | **113** |
| Cambios de etiqueta | **7** |
| Cambios de relevancia | 0 |
| Pendientes | 0 |

Transiciones: 1 D→H, 4 D→N, 1 N→H y 1 N→D. La distribución pasa de 5 H/7 D/108 N a 7 H/3 D/110 N.

## Correcciones

- `RPM-2008-03-13:1731:1`, D→H: rechaza relajar por sus efectos inflacionarios; mantener frente a subir no lo hace D.
- `RPM-2008-04-10:1778:1`, `:1782:1` y `RPM-2008-11-13:2171:1`, D→N: mantienen y eliminan o rechazan un sesgo; no adoptan dirección futura.
- `RPM-2009-08-13:2681:1`, D→N: presenta mantener o ampliar estímulo como menú, sin preferencia.
- `RPM-2009-11-12:2791:1`, N→H: respalda retirar gradualmente la FLAP y señalizar normalización pausada.
- `RPM-2010-01-14:2870:1`, N→D: explicita como propósito propio de la política impulsar demanda y oferta.

Los 17 N/relevancia0 permanecen como formalidad o logística. La evidencia está en `data/auditoria/revision_etiquetas_escalado_r10_v3/`. Las etiquetas eran visibles; no fue una segunda anotación ciega. No hubo entrenamiento ni sobrescritura de originales.
