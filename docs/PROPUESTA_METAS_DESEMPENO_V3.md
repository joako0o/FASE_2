# Propuesta de metas de desempeño para clasificación v3

**Estado:** propuesta para aprobación del investigador; no usada todavía para seleccionar modelos.  
**Objeto:** clasificación por intervención del BCCh en hawkish, dovish o neutral bajo dirección monetaria doméstica respaldada.

## 1. Por qué no usar una única cifra publicada

Las cifras de la literatura no son directamente intercambiables con este proyecto. Cambian el banco central, idioma, unidad textual, definición de H/D, proporción neutral, atribución a hablantes, forma de partición y grado de independencia del test.

Shah, Paturi y Chava (ACL 2023) introducen una referencia FOMC H/D/N y reportan para RoBERTa-large F1 aproximado de 0,715 en minutos, 0,552 en conferencias, 0,717 en discursos y 0,717 combinado. Su acuerdo entre dos anotadores va de 89,04% a 95,03%. Sin embargo, su definición admite señales macroeconómicas más amplias y no exige siempre la dirección respaldada por un actor como v3.

El BIS (2024) usa 1.243 oraciones FOMC, particiones aleatorias 80/20 y encuentra alrededor de 83% de accuracy para su mejor CB-RoBERTa, con algunos LLM afinados entre 80% y 88%. En una prueba más difícil de 237 noticias largas, los CB-LM logran alrededor de 65% y GPT-4/Llama-3 70B cerca de 80–81%. La diferencia entre tareas cortas/largas muestra que contexto y diseño del test importan tanto como la arquitectura.

Op-Fed (2025) es conceptualmente más cercano: exige atribuir postura monetaria a un hablante y conservar contexto. Estima menos de 8% de posturas no neutrales, señala que 65% de los casos requiere contexto más allá de la oración, reporta acuerdos moderados en etapas difíciles (aproximadamente 0,55–0,72) y un baseline humano de accuracy 0,89 frente a 0,61 para el mejor LLM evaluado en postura.

Trabajos recientes reportan macro-F1 cercanos a 0,73–0,74 en benchmarks FOMC, pero usan otros esquemas y modelos: Yao et al. (2026) obtiene macro-F1 0,7327; *Mind the Shift* (2026) llega aproximadamente a F1 0,7387 en su benchmark H/D. Son referencias de escala, no metas trasladables literalmente.

La literatura chilena encontrada construye principalmente índices de tono y valida contra tasas, swaps o precios de activos; no ofrece un benchmark supervisado por intervención con la definición v3. Por ello, la meta oficial debe combinar literatura, baseline interno y costo de cada confusión.

## 2. Situación interna que sirve de baseline

El candidato C sin sintéticos, aún no independiente, presenta sobre los 793 casos reutilizados:

- accuracy 0,9281;
- macro-F1 0,7730;
- F1-HD 0,6763;
- F1 H 0,7813;
- F1 D 0,5714;
- F1 N 0,9662;
- precisión D 0,5806 y recall D 0,5625;
- 12 inversiones H↔D;
- 15 omisiones H/D→N;
- 30 falsas señales N→H/D.

Estas cifras no deben convertirse en objetivo retrospectivo ni presentarse como generalización: el desarrollo fue abierto, corregido y consultado en múltiples comparaciones.

## 3. Meta propuesta en tres niveles

### 3.1 Calidad de la nueva referencia ciega

Antes de evaluar modelos:

| Control de anotación | Meta mínima |
|---|---:|
| Acuerdo bruto H/D/N entre dos anotadores independientes | ≥ 85% |
| Cohen κ o Krippendorff α global | ≥ 0,70 |
| Cobertura de adjudicación de desacuerdos | 100% |
| Citas literales verificadas en casos relevantes | 100% |
| Pendientes en test final | 0 |

El acuerdo bruto se calibra con el 89–95% de Shah et al.; κ/α reconoce que la atribución de postura contextual es más difícil, como muestra Op-Fed. Si no existe segundo anotador humano, debe declararse y no reemplazarse silenciosamente por acuerdo agente-investigador.

### 3.2 Umbral mínimo para considerar útil un modelo

Debe medirse en un test nuevo, real, ciego y agrupado por reunión:

| Métrica | Umbral mínimo propuesto |
|---|---:|
| Macro-F1 H/D/N | ≥ 0,75 |
| F1-HD | ≥ 0,70 |
| F1 H | ≥ 0,75 |
| F1 D | ≥ 0,65 |
| Precisión D | ≥ 0,65 |
| Recall D | ≥ 0,65 |
| F1 N | ≥ 0,94 |
| Accuracy | ≥ 0,90, secundaria |

No basta alcanzar el promedio: deben cumplirse simultáneamente los pisos de D. Esto evita aprobar un modelo que mejora accuracy prediciendo neutral o que logra alta precisión D omitiendo la mayoría de los D.

### 3.3 Metas de error operativo

Con denominadores explícitos:

| Error | Meta mínima propuesta |
|---|---:|
| Inversiones H↔D / H+D reales | ≤ 5% |
| Omisiones H/D→N / H+D reales | ≤ 10% |
| Error direccional total sobre H+D reales | ≤ 20% |
| Falsas señales N→H/D / N reales | ≤ 5% |

La inversión recibe el límite más estricto porque comunica la dirección opuesta. Las tasas deben publicarse junto con conteos y matriz, no solo porcentajes.

### 3.4 Meta aspiracional

Después de superar el mínimo en un test independiente:

- macro-F1 ≥ 0,80;
- F1-HD ≥ 0,75;
- F1 D ≥ 0,70;
- inversiones H↔D ≤ 3% de los H+D reales;
- intervalos de confianza y desempeño temporal sin deterioro severo.

## 4. Diseño necesario para medir la meta

Se propone una evaluación nueva con dos componentes bloqueados antes de predecir:

1. **Muestra representativa**, para estimar prevalencia y accuracy real.
2. **Estrato H/D enriquecido**, para estimar con precisión F1 H, F1 D e inversiones.

Ambos deben informar resultados por separado. No debe presentarse el estrato enriquecido como prevalencia poblacional. El test debe incluir idealmente al menos 60 H y 60 D adjudicados; con menos, pequeñas diferencias de conteo producen grandes oscilaciones de F1.

Controles obligatorios:

- ninguna reunión compartida con train;
- ningún texto/casi copia compartido;
- etiquetas y protocolo congelados antes de ejecutar;
- predicciones ocultas durante anotación;
- intervalos bootstrap agrupados por reunión;
- matriz y seis direcciones de confusión;
- resultados por periodo/regímenes;
- una única evaluación final del candidato congelado.

## 5. Regla de decisión propuesta

Un modelo se considera **candidato útil** solo si:

1. cumple todos los umbrales mínimos de 3.2 y 3.3 en el test nuevo;
2. no depende de un único periodo o reunión;
3. el límite inferior del intervalo de confianza de F1-HD no es incompatible con una mejora material sobre el baseline fijado;
4. supera baselines simples fijados: mayoría neutral, TF-IDF C y al menos un modelo contextual;
5. conserva trazabilidad por ID y abstención/revisión para casos de baja confianza.

No se adopta un modelo únicamente por superar una cifra de un paper, porque esos resultados no comparten exactamente nuestra tarea.

## 6. Siguiente decisión experimental

Antes de seguir entrenando, conviene que el investigador apruebe o modifique estas metas. Después:

1. cerrar la revisión pre-2000 como posible ampliación real;
2. congelar uno o dos candidatos sin volver a optimizar los 793 casos;
3. construir y anotar el test real nuevo;
4. ejecutar una única comparación final;
5. solo entonces decidir si una arquitectura contextual adicional está justificada.

## Referencias principales

- Shah, A., Paturi, S. y Chava, S. (2023). *Trillion Dollar Words: A New Financial Dataset, Task & Market Analysis*. ACL 2023. https://aclanthology.org/2023.acl-long.368/
- Gambacorta, L., Kwon, B., Park, T., Patelli, P. y Zhu, S. (2024). *CB-LMs: language models for central banking*. BIS Working Paper 1215. https://www.bis.org/publications/working-paper-1215-cb-lms-language-models-central-banking
- Keith, K. et al. (2025). *Op-Fed: Opinion, Stance, and Monetary Policy Annotations on FOMC Transcripts Using Active Learning*. https://arxiv.org/abs/2509.13539
- Yao, R. et al. (2026). *Interpreting Fedspeak with Confidence: A LLM-Based Uncertainty-Aware Framework Guided by Monetary Policy Transmission Paths*. https://arxiv.org/abs/2508.08001
- *Mind the Shift: Decoding Monetary Policy Stance from FOMC Statements with Large Language Models* (2026). https://arxiv.org/abs/2603.14313
- García-Herrero, A. et al. (2020). *Signaling and Financial Market Impact of Chile's Central Bank Communications*. https://economia.lse.ac.uk/articles/38
