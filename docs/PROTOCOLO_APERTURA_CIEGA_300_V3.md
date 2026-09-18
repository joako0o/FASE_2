# Protocolo de apertura única — evaluación ciega agrupada v3

**Fijado:** 17-09-2026, después del cierre humano de etiquetas y antes de generar o consultar predicciones sobre estas 300 filas.

## Datos

Se evalúan las 299 filas decidibles del instrumento de 300. Una fila cerrada como `no_puedo_decidir` queda documentada y excluida de métricas. Las 33 reuniones seleccionadas se excluyen por completo de todo ajuste, junto con cualquier duplicado textual del instrumento.

## Modelos congelados

1. **C+89 formal:** ensamble por voto mayoritario de los cinco estimadores outer originales, reentrenados con el train histórico de cada fold y las 89 referencias permitidas, tras la cuarentena.
2. **W+C+600 challenger:** el mismo ensamble, incorporando ambas tandas de 300 y usando los pesos de caracteres congelados por miembro: `1,0; 0,5; 1,0; 1,0; 1,0`.

El desempate del voto, si existe, se resuelve en orden fijo H, D, N. No habrá búsqueda, calibración, cambio de etiquetas ni consulta iterativa.

## Reporte y decisión

Se reportan accuracy, macro-F1, F1-HD, precision/recall/F1 por clase, matriz H/D/N, errores, inversiones H↔D, omisiones H/D→N y falsas direcciones N→H/D, tanto globalmente como por subconjunto oculto de recuperación.

W+C+600 solo desplaza al modelo formal si no reduce macro-F1, F1-HD, F1/recall D ni F1 N, y no aumenta errores, inversiones u omisiones. La evaluación es agrupada y prospectivamente purgada, pero las reuniones tuvieron exposición histórica de desarrollo y el muestreo está enriquecido como desafío: no estima prevalencia natural.

## Transparencia

La arquitectura, datos y pesos ya estaban congelados antes de recibir etiquetas. La regla explícita de agregación de los cinco modelos se documentó después de cerrar etiquetas, pero antes de generar predicciones o observar desempeño ciego.
