# Protocolo preregistrado — ensamble calibrado v3

**Fijado:** 17-09-2026, tras autorización expresa del investigador y antes de ejecutar resultados de esta ronda.

## Propósito

Combinar los dos componentes lineales más útiles y complementarios:

- **C**: TF-IDF histórico de palabras, más estable para neutral;
- **W+C**: TF-IDF de palabras y caracteres, con mejor F1-HD, F1 D e inversiones en la comparación previa.

No se incorporan pre-2000, sintéticos, NB-SVM ni arquitectura jerárquica.

## Separación de selección y evaluación

La selección completa usa únicamente las 559 filas IA-base con `fold_validacion=0`, mediante `GroupKFold(3)` por reunión y purga de copias textuales. Los 793 casos con folds 1–5 no intervienen en la selección de representación, mezcla, multiplicador D ni margen.

Primero se elige el peso global de caracteres W+C entre `{0,5; 1,0}` por media interna de F1-HD; desempates: recall D, macro-F1 y menor peso. Después se generan, en los mismos splits internos, probabilidades OOF de C, W+C y W+C con evidencia oracional máxima.

Las probabilidades respetan la puerta histórica: si la probabilidad de relevancia es inferior a 0,5, el componente entrega neutral; si no, conserva las probabilidades multiclase H/D/N.

## Políticas candidatas fijadas

`alpha_wc` es el peso de W+C; el resto corresponde a C.

| Política | alpha_wc | multiplicador D | margen H–D | Evidencia oracional |
|---|---:|---:|---:|---|
| blend_50 | 0,50 | 1,00 | 0 | no |
| blend_50_d115 | 0,50 | 1,15 | 0 | no |
| blend_75wc_d115 | 0,75 | 1,15 | 0 | no |
| blend_75wc_d115_margin05 | 0,75 | 1,15 | 0,05 | no |
| blend_50_maxsent_d115 | 0,50 | 1,15 | 0 | sí |

En la variante oracional, W+C combina `0,75` de la intervención completa con `0,25` del máximo por clase entre sus oraciones; después se normaliza y mezcla con C.

El multiplicador D se aplica antes de renormalizar. El margen envía a N una predicción H/D cuando la diferencia absoluta entre sus probabilidades H y D es inferior a 0,05.

## Selección interna

Cada política se compara contra C interno con los ocho controles multicriterio del protocolo principal. Se selecciona:

1. mayor número de controles satisfechos;
2. mayor media F1-HD de tres folds;
3. mayor recall D agregado;
4. orden de políticas de la tabla.

No se modifican políticas ni regla tras observar resultados.

## Apertura externa única

Solo la política ganadora se ajustará en cada outer train permitido, incorporando las 89 IA nuevas con purga por reunión/texto, y se abrirá una vez sobre los 793 casos de desarrollo. Para avanzar debe satisfacer íntegramente la regla multicriterio frente a C.

Esta ronda no constituye prueba final. El cumplimiento oficial sigue requiriendo datos reales nuevos, ciegos y agrupados por reunión.
