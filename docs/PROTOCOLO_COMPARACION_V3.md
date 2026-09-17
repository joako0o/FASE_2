# Protocolo de consolidación y comparación v3

**Fijado:** 17-09-2026, después de cerrar 1.747/1.747 revisiones.  
**Estado:** referencia consolidada; comparación y entrenamiento todavía no ejecutados.

## 1. Objetivo

Separar tres efectos que no deben mezclarse:

1. **Recodificación de la referencia:** cambia qué se considera H/D/N sin cambiar predicciones ni entrenamiento.
2. **Cambio de supervisión:** reentrenar el mismo modelo con etiquetas/relevancia v3.
3. **Ampliación de datos:** añadir las 89 IA nuevas o, posteriormente, el set pre-2000.

La vista canónica está en `data/evaluacion/referencia_v3/referencia_v3.csv`. Contiene los 1.747 IDs con origen, revisión, etiquetas previa/v3, relevancia, resultado, confianza, cita, fundamento, estado, hash y rol recomendado. Su generación reproducible es `python scripts/consolidar_referencia_v3.py`.

## 2. Cohortes y roles

| Cohorte | IDs | Uso inicial |
|---|---:|---|
| IA base v2 revisada | 1.352 | Control primario v3, mismos folds y configuración histórica |
| IA nueva revisada | 89 | Ampliación separada, nunca mezclada en el primer control |
| Humana v3 | 306 | Evaluación descriptiva no independiente; no test ciego |
| Pre-2000 preparado | 257 | Excluido hasta revisión v3 y trazabilidad propias |

Distribución consolidada de los 1.747: **H218 / D115 / N1.414**; relevancia **1.439/308**. En el control IA base: **H149 / D54 / N1.149**, con 1.084 relevantes y 268 irrelevantes.

## 3. Fase A — efecto de recodificación, sin reentrenar

1. Congelar y hashear las predicciones históricas del control TF-IDF sobre los mismos 793 IDs OOF.
2. Puntuar exactamente esas predicciones contra la referencia v2 histórica y contra v3.
3. Publicar matrices, F1 H/D, macro-F1, recall por clase y errores H↔D, H/D→N y N→H/D para ambas referencias.
4. Informar cuántos cambios provienen exclusivamente de la nueva referencia. No presentarlos como mejora o deterioro del modelo.

## 4. Fase B — efecto de supervisión v3

1. Reutilizar los mismos 1.352 IDs IA base, cinco folds por reunión, textos, purgas, configuración TF-IDF, semilla y regla de selección histórica.
2. Sustituir únicamente etiqueta/relevancia por la capa v3. No añadir las 89 IA nuevas.
3. Reentrenar desde cero dentro de cada fold y evaluar sobre los mismos IDs OOF usando v3.
4. Comparar:
   - predicción histórica contra v3 (fase A);
   - predicción reentrenada v3 contra v3 (fase B).
5. Descomponer cambios por fold y familia de transición. Conservar todas las salidas aunque la métrica baje.

Esta fase mide el efecto de cambiar supervisión dentro del desarrollo reutilizado. No prueba generalización externa.

## 5. Fase C — ampliación IA de 89

Solo después de cerrar A/B:

- añadir las 89 IA nuevas al train permitido de cada fold;
- excluir por reunión y texto/casi copia respecto de la validación;
- conservar exactamente la validación y los parámetros de B;
- comparar B frente a B+89 sin búsqueda de hiperparámetros;
- reportar efecto agregado y por fold, sin retirar ejemplos por perjudicar el score.

## 6. Referencia humana

Las 306 humanas v3 fueron abiertas y revisadas por el agente. Pueden utilizarse para diagnóstico descriptivo, cobertura temporal y análisis de familias, pero no para afirmar desempeño ciego o independiente. No se usarán simultáneamente como train y evaluación. Para medir generalización será necesaria una muestra humana nueva, ciega y fijada antes de observar predicciones.

## 7. Set pre-2000

`Set_Entrenamiento_Pre_2000.xlsx` permanece fuera de A/B/C. La [revisión inicial](REVISION_INICIAL_SET_PRE_2000_V1.md) encontró pendientes en la columna de etiqueta, citas no literales, duplicados y casos incompatibles con el criterio doméstico respaldado. Su incorporación exige:

- capa de revisión separada y sin sobrescribir el XLSX;
- procedencia, acta/reunión, actor, offsets o unidad fuente y hash;
- estado `pendiente` separado de H/D/N;
- citas continuas reparadas;
- agrupación de duplicados y reuniones;
- revisión completa H/D/N bajo v3.

Si se incorpora después, será una **fase D de ampliación temporal**, nunca parte retroactiva del control primario.

## 8. Controles de cierre para cada fase

- entradas y código con SHA-256 antes de ejecutar;
- IDs únicos y cobertura exacta;
- agrupación por reunión y texto normalizado;
- ningún acceso a etiquetas de validación para ajustar parámetros;
- replay determinista de CSV/métricas;
- matrices y métricas recalculadas independientemente;
- manifiesto de salidas;
- declaración expresa de que no existe test ciego humano v3.

No se adopta un modelo por una única métrica. Primero se informa la separación recodificación/supervisión/ampliación y luego el investigador decide si avanzar a una evaluación humana realmente nueva.
