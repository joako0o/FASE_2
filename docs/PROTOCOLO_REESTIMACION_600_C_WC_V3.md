# Prerregistro — reestimación única C versus W+C con dos tandas humanas (600)

**Fijado:** 17-09-2026, después de cerrar semánticamente la segunda tanda de 300 y antes de ejecutar o consultar resultados de esta ronda.

## Propósito

Medir una sola vez si añadir la segunda tanda dirigida —con mayor presencia dovish— corrige el déficit de recall D y omisiones observado con la primera tanda. Se comparan C y W+C con las mismas 600 referencias humanas cerradas. Los 793 casos históricos siguen siendo desarrollo abierto, no prueba independiente.

## Datos y purga

Para cada outer fold histórico se conserva su validación original y se entrena con:

1. train histórico permitido, purgando copias textuales de validación;
2. 89 referencias IA v3;
3. primera tanda humana cerrada de 300;
4. segunda tanda humana dirigida cerrada de 300.

Cada ampliación se excluye si su reunión aparece en validación o su texto normalizado coincide con validación. Ninguna de las 600 filas entra como validación. Se audita inclusión por fila, origen y fold.

## Modelos congelados

- **C+600:** puerta de relevancia y clasificador H/D/N TF-IDF de palabras, con los parámetros del candidato C.
- **W+C+600:** misma arquitectura con unión de palabras y `char_wb` 3–5.

No hay búsqueda nueva. Los pesos de caracteres permanecen congelados: fold 1=`1,0`; fold 2=`0,5`; folds 3–5=`1,0`. Primero deben reproducirse exactamente C+89 y C+primera300.

## Decisión

Se reportan las métricas y errores ya definidos. W+C+600 reemplaza C+600 solo si satisface simultáneamente los ocho controles congelados: mejora de media F1-HD y de al menos tres folds; F1 D y recall D no bajan; inversiones, omisiones no aumentan; macro-F1 y F1 N no bajan.

Si W+C falla algún control, se selecciona C+600. La representación seleccionada solo reemplaza el modelo de desarrollo vigente C+89 si satisface los mismos ocho controles frente al ancla. No se modificarán pesos, reglas ni etiquetas tras observar resultados.

## Límite

Esta es la única apertura histórica autorizada para la segunda tanda. Aunque mejore, no confirma la meta oficial: esa conclusión requiere evaluación nueva y ciega dentro del dominio 2005–2015, con exclusión por reunión.
