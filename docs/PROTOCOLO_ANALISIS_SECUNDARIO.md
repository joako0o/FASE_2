# Protocolo — análisis secundario congelado del test ciego v3

**Fijado:** 17-09-2026, después de la apertura primaria y antes de generar las dos condiciones factoriales faltantes.

## Estatuto

Este análisis usa un test ya abierto. Es explicativo y no constituye una nueva confirmación independiente, no autoriza búsqueda de hiperparámetros y no modifica retrospectivamente la regla ni la decisión primaria.

## Factorial 2×2

Se completan cuatro sistemas sobre las mismas 299 filas decidibles y con idéntica cuarentena de 33 reuniones y duplicados:

- C+89 y W+C+600: predicciones primarias inmutables;
- C+600: palabras con ambas tandas de 300;
- W+C+89: palabras y caracteres con solo las 89 referencias.

Cada condición usa voto de los cinco miembros outer y pesos de caracteres congelados `1,0; 0,5; 1,0; 1,0; 1,0`. No se ajustan umbrales, pesos, vocabularios ni parámetros.

## Incertidumbre y robustez

Se realiza bootstrap agrupado por `meeting_id`, con 10.000 remuestras y semilla 20260917. La unidad de remuestreo es la reunión completa. Se informan percentiles 2,5/50/97,5 de las diferencias W+C+600 menos C+89 en accuracy, macro-F1 y F1-HD, además de la proporción de diferencias positivas.

También se reportan resultados por reunión, año, estrato de recuperación, longitud y desacuerdo del ensamble. Los estratos son mecanismos de recuperación, no clases verdaderas. Se genera un inventario descriptivo de errores sin recodificar etiquetas ni reentrenar.
