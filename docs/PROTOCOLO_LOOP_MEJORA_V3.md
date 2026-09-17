# Protocolo del loop de mejora hasta la meta aspiracional v3

**Fijado:** 17-09-2026, después de aprobar las metas y antes de nuevas variantes.  
**Meta aspiracional:** macro-F1 ≥0,80; F1-HD ≥0,75; F1 D ≥0,70; inversiones H↔D ≤3% de H+D reales.  
**Condición indispensable:** el cumplimiento definitivo se decide en evaluación real nueva, ciega y agrupada por reunión.

## 1. Qué significa «hacer loop»

El agente iterará de manera autónoma sobre datos, representaciones y modelos, conservará también resultados negativos y detendrá el ciclo cuando ocurra primero:

1. un candidato satisface las metas aspiracionales dentro del desarrollo bajo el protocolo fijado;
2. se completan ocho rondas predefinidas sin alcanzarlas;
3. falta un insumo imprescindible —por ejemplo, segunda anotación humana o pesos de un encoder—;
4. una ronda requeriría consultar repetidamente el test final o elegir casos según sus errores.

No se garantiza alcanzar una métrica determinada: una meta es criterio de éxito, no autorización para alterar etiquetas, contaminar particiones o continuar hasta obtener por azar una cifra favorable.

## 2. Separación de datos

- Los 793 OOF históricos quedan como **desarrollo abierto**: sirven para diagnóstico, nunca como prueba final.
- Las 306 respuestas humanas v3 son descriptivas y no vuelven a ser ciegas.
- Los 257 pre-2000 entrarán solo después de adjudicación v3 completa y únicamente como ampliación de train.
- Los sintéticos actuales permanecen fuera del candidato general; ninguna dosis cumplió criterios.
- Se preparará una evaluación nueva sin predicciones visibles y se abrirá una sola vez para el candidato congelado.

Durante el loop, la selección de hiperparámetros debe ocurrir mediante validación interna agrupada por reunión dentro del train permitido. No se seleccionará una variante por una mejora aislada en los 793 casos ya consultados.

## 3. Rondas predefinidas

### Ronda 0 — baseline congelado

- C sin sintéticos: 1.352 IA-base + 89 IA nuevas según purga por fold.
- Referencia comparativa, no modelo adoptado.

### Ronda 1 — ampliación real pre-2000

- Auditar 257/257 bajo v3, resolver pendientes, citas y duplicados.
- Comparar B/C con y sin pre-2000 mediante el mismo desarrollo agrupado.
- No modificar arquitectura.

### Ronda 2 — error y representación lineal

- Evaluar una única familia lineal prefijada que combine palabras y caracteres para robustez ortográfica.
- Mantener pesos, parámetros y selección dentro de CV interna.
- Medir si reduce D→H sin trasladar el error a D→N.

### Ronda 3 — jerarquía direccional

- Separar relevancia, presencia de dirección y signo H/D.
- La puerta direccional y el signo se entrenan solo dentro de cada train.
- Comparar contra arquitectura multiclase sin usar el test final.

### Ronda 4 — encoder contextual en español

- Evaluar BETO u otro encoder reproducible si existen pesos y cómputo.
- Mismos grupos y referencia; sin mezclar evaluación humana abierta.
- Registrar semillas, dispersión y costo.

### Ronda 5 — adaptación de dominio no supervisada

- Si hay recursos, adaptar representaciones con corpus BCCh sin etiquetas antes del ajuste supervisado.
- El corpus de validación no aporta etiquetas ni decisiones de selección.

### Ronda 6 — datos sintéticos rediseñados

- Solo una versión nueva con D indirectos, neutrales difíciles, familias/prompts/semillas y menor repetición.
- Dosis y peso se fijan antes de evaluar.
- Los sintéticos entran solo en train y nunca sustituyen referencia real.

### Ronda 7 — ensamblaje/calibración

- Combinar como máximo los dos candidatos previamente fijados.
- Umbrales, abstención y calibración se seleccionan dentro de CV interna.
- No optimizar directamente sobre el test final.

### Ronda 8 — congelación

- Elegir un único candidato con la regla multicriterio.
- Generar hash de código, datos, parámetros y predicciones esperadas.
- Prohibir nuevos cambios antes de abrir la evaluación ciega.

## 4. Regla multicriterio en desarrollo

Una ronda avanza como candidata solo si, frente al baseline de la ronda:

- mejora media de F1-HD agrupada y al menos tres folds;
- no reduce F1 D ni recall D;
- no aumenta inversiones H↔D;
- no logra la mejora simplemente enviando H/D a neutral;
- mantiene macro-F1 y F1 N;
- el efecto no depende de una sola reunión o periodo.

El objetivo aspiracional no reemplaza estos controles. Un modelo con accuracy alta pero recall D bajo queda rechazado.

## 5. Confirmación final

El cumplimiento oficial exige simultáneamente en el test nuevo:

- macro-F1 ≥0,80;
- F1-HD ≥0,75;
- F1 D ≥0,70;
- inversiones H↔D ≤3% de H+D;
- además de los mínimos de precisión/recall y calidad de referencia aprobados.

Si el candidato no los cumple, se informa el resultado. El test no se convierte en un nuevo conjunto de tuning; un segundo ciclo requerirá otra evaluación futura o un diseño explícito que preserve independencia.

## 6. Próxima acción

La siguiente acción del loop es la **ronda 1: adjudicación completa de los 257 registros pre-2000**, porque son datos reales y pueden aumentar cobertura histórica de D/H. No se ejecutará entrenamiento con ellos hasta cerrar 257/257, reparar evidencia y fijar grupos.
