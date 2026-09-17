# Revisión v3 — escalado r5

**Fecha:** 17-09-2026
**Archivo:** `data/etiquetas/etiquetas_escalado_r5.csv`
**Alcance:** 99/99 intervenciones, incluidas H, D, N y relevancia.

## Resultado frente a v2 vigente

| Resultado | Casos |
|---|---:|
| Compatibles | **97** |
| Cambios de etiqueta | **2** |
| Cambios de relevancia | 0 |
| Pendientes | 0 |

Transiciones: 1 N→H y 1 D→H. La distribución pasa de 22 H/1 D/76 N a 24 H/0 D/75 N.

## Correcciones

- `RPM-2005-01-11:30:1`, N→H: sostiene que “es el momento de empezar a reducir pausadamente este estímulo monetario”. La dirección restrictiva respaldada es explícita.
- `RPM-2005-02-10:127:1`, D→H: considera adecuada la normalización al alza, aunque podría avanzar más lentamente y tanto una pausa como un alza inmediata serían coherentes. Menor velocidad de endurecimiento no es D; la trayectoria que hace propia sigue siendo H.

También se confirmó la compatibilidad de los H vigentes `RPM-2005-01-11:5:1` y `:39:1`: el primero contiene una estimación institucional de continuar la normalización y una trayectoria de tasa ascendente; el segundo respalda iniciar la reducción gradual del estímulo. No se recodificaron como H los menús de opciones sin preferencia, expectativas ajenas ni diagnósticos sin orientación propia.

## Evidencia y límites

La revisión por ID está en `data/auditoria/revision_etiquetas_escalado_r5_v3/revision.csv`; las decisiones que cambian v2 están declaradas en `decisiones.json`. Se verificaron IDs, citas literales tras normalizar espacios y hashes contra L0. Las etiquetas eran visibles y la revisión fue realizada por el agente, no por un segundo anotador ciego. El lote queda cerrado, sin entrenamiento ni sobrescritura de originales.
