# Extensión preregistrada — tokenización, suavizamiento y embeddings v3

**Fijada:** 17-09-2026, después de la autorización explícita del investigador y antes de ejecutar resultados de esta extensión.

## Objetivo

Comparar cuatro representaciones viables en CPU para mejorar H/D, especialmente D, sin seleccionar retrospectivamente sobre los 793 casos de desarrollo ya abiertos.

## Conjunto exclusivo de selección

La selección metodológica usa únicamente las 559 filas con `fold_validacion=0` de IA-base v3. Estas filas nunca forman parte de los 793 casos externos (`fold=1..5`). La selección usa `GroupKFold(3)` por `meeting_id`, con purga adicional de copias textuales normalizadas entre train y validación interna.

Las 89 IA nuevas no participan en la elección de metodología. Se incorporan después, al ajustar el ganador dentro de cada outer train permitido, aplicando la purga histórica por reunión y texto.

## Métodos candidatos fijados

1. **token_monetario**: TF-IDF de palabras con tokenizador que preserva expresiones monetarias, negación, porcentajes, puntos base, UF y siglas, combinado con `char_wb` 3–5; regresión logística balanceada.
2. **nbsvm**: representación TF-IDF palabra+carácter reponderada mediante log-count ratio supervisado calculado solo dentro de cada train; clasificadores binarios one-vs-rest.
3. **lsa128**: TF-IDF de palabras 1–2, máximo 50.000 rasgos, `TruncatedSVD(128)` y normalización L2; regresión logística balanceada. Constituye el embedding latente sin red neuronal.
4. **suavizado_oraciones**: modelo palabra+carácter que combina probabilidades de la intervención completa y promedio de oraciones con peso fijo `0,75/0,25`.

Todos conservan la puerta de relevancia y la clasificación H/D/N entre textos relevantes. No se usan campos de anotación, cita, fundamento, estrato ni metadatos predictivos.

## Regla de selección interna

Para cada método se generan predicciones OOF internas. Se elige por la tupla, en este orden:

1. media de F1-HD de los tres folds;
2. recall D agregado;
3. macro-F1 agregado;
4. menor complejidad en el orden fijo `token_monetario`, `nbsvm`, `lsa128`, `suavizado_oraciones`.

No se modifica esta regla después de observar resultados.

## Evaluación externa única

Solo el ganador interno se ajusta en los cinco outer trains del candidato C y se compara una vez contra C sobre los 793 casos abiertos. La decisión de avance aplica íntegramente la regla multicriterio de `docs/PROTOCOLO_LOOP_MEJORA_V3.md`.

Un resultado en esta extensión sigue siendo desarrollo abierto y no confirma la meta oficial, que exige una evaluación real nueva, ciega y agrupada por reunión.
