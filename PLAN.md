# PLAN — Proyecto D&H: Score Hawkish/Dovish por Intervención

> Para ejecutar o trasladar ahora: [EMPEZAR_AQUI.md](EMPEZAR_AQUI.md). Para otra sesión: [CONTINUIDAD](docs/CONTINUIDAD.md). Este documento conserva el plan y la cronología; no es una receta para ejecutar todos los scripts.
**Actas de las Reuniones de Política Monetaria (RPM) del Banco Central de Chile, 2005–2015**

> Documento maestro de planificación. Estado: **TF-IDF evaluado; n-gramas e influencias diagnosticados; investigación externa e híbrido mínimo v1 completados sin mejora media; BETO y scoring completo pendientes.**
> Última actualización: 2026-09-16. Codebook v2 vigente; los cambios de evaluación se registran en §9.1–9.6.

---

## 1. Objetivo

Construir un **score de postura de política monetaria (hawkish ↔ dovish) por intervención** sobre las 9.725 intervenciones del corpus, y a partir de él:

1. **Serie de tiempo agregada** del stance del Consejo (mensual, 2005–2015), validada contra la decisión real de TPM.
2. **Perfiles por actor**: trayectoria de postura (estructural vs coyuntural), especialista temático (radar estilo FIFA), vocabulario distintivo, matriz de votos, convergencia intra-reunión, disenso y red de afinidad.

Estos productos serán insumo de un *scrollytelling* y un paper (fuera del alcance de este plan por ahora).

### Fase 0 histórica (previa a este repo)

Antes de orientar el proyecto se trabajó en la consolidación del corpus y en ideas de esquema final de datos. Se evaluaron dos propuestas de columnas:

- **v0a**: `speech_id, tpm, inflación, desempleo, imacec, ipec, sit país a 1 año, eee inflación a 1 año, word_count, hawk_dove_label, hawk_dove_score, razonamiento, participant_id, speech_id_fallback, prob_dovish, prob_hawkish, prob_neutral, hawk_dove_score_tfidf, hawk_dove_label_tfidf, hawk_dove_score_embeddings, hawk_dove_label_embeddings`
- **v0b (preferida)**: `meeting_id, nombre_pdf, num_pagina, year, participant, es_herencia, text, main_topic, topic_vector, keywords_flags, confidence_flag, policy_decision, doc_regime, speech_id, TPM`

La v0b gana por linaje documental (`nombre_pdf`, `num_pagina`, `doc_regime`), decisión de política junto al texto (`policy_decision`) y flag de confianza. La v0a aporta el contexto macro y la comparación multi-método. **Ambas se armonizan en la arquitectura por capas de la §5.**

Actualizaciones al 2026-09-15: ~~`es_herencia`~~ eliminada (obsoleta); ~~`nombre_pdf`/`num_pagina`~~ eliminados (los PDFs existen pero no se integran al flujo; el Excel ya contiene el contenido íntegro de las actas; el linaje queda a nivel `meeting_id`); clase `irrelevante` reemplazada por flag binario `es_relevante` + `nota`.

## 2. Datos

### 2.1 Corpus: `consolidado_D&H.xlsx`

| Dimensión | Valor |
|---|---|
| Filas | 9.725 intervenciones |
| Período | 2005-01-11 → 2015-12-17 |
| Reuniones | 132 (12/año × 11 años) |
| Actores | 55 únicos (top 5 concentran 46,6%) |
| Cargos | 46 (Presidente, Consejeros, Gerentes, Ministros de Hacienda, Consejo como entidad) |
| Largo texto | media ~1.282 car.; mediana 470 (máx ~32 mil) |
| Tópicos | 13 categorías (acuerdo_comunicado, debate, escenario_internacional, mercados_financieros, inflacion, actividad_interna, mercado_laboral, decision_tpm, opciones_tpm, riesgos, politica_fiscal, apertura_cierre, otros) |
| Flags de calidad | 312 registros con `Cotejar_PDF` (revisar antes de muestrear; 45 con texto dañado) |

Columnas: `Fecha, ID, ID_Intervencion, Actor, Cargo, Tópico, Keywords, Texto, Cotejar_PDF`.
Todos los IDs siguen el patrón `RPM-AAAA-MM-DD:N:M` → la reunión es la unidad natural de agrupación; la `N` es secuencial y reconstruye el **orden de habla** dentro de la sesión (base de la métrica de convergencia, §7).

### 2.2 Contexto documental (clave para defender la ventana de estudio)

- **Actas completas** (transcripción con intervenciones nombradas): publicadas hasta 2017; el BCCh las difunde **con rezago de 10 años** (cada marzo se liberan las del undécimo año anterior → en 2026 llegan hasta 2015).
- **Desde enero 2018**: esquema nuevo (8 reuniones/año) y la **Minuta** (síntesis anonimizada) reemplaza a la Acta como documento oportuno. Los votos se individualizan solo desde 2018.
- **Referencia externa WCB (NeurIPS 2025)**: 1.000 frases del BCCh etiquetadas (hawkish/dovish/neutral/irrelevant), pero construidas desde **Minutas 2018–2024 en inglés** → cero solape temporal, idiomático y documental con este corpus.
- **Consecuencia**: 2005–2015 es la única ventana del mundo con análisis de postura por intervención nombrada posible en el BCCh. El corpus es original y complementario a la literatura.

## 3. Decisiones de diseño (registradas con el investigador)

| # | Decisión | Acuerdo |
|---|---|---|
| 1 | Unidad de análisis | **Intervención completa** (no frase) |
| 2 | Universo de etiquetado | **Las 9.725** (todos los tópicos y actores) |
| 3 | Flujo de etiquetado | **IA primero, en rondas → validación humana al final (a ciegas)** |
| 4 | Modelo | **Fine-tune de modelo en español** (BETO / RoBERTa-es / alternativas) |
| 5 | Entregables | Score por intervención → serie temporal + data de actores (§7) + contexto macro (§5) |
| 6 | Operación | Etiquetado en este chat por rondas; **todo documentado + PR constante a GitHub** |
| 7 | Esquema final | Arquitectura por capas (§5), armonizando las propuestas v0a/v0b de la Fase 0 |
| 8 | Alcance del etiquetado chat (2026-09-15, decisión del investigador) | La IA **no** etiqueta las 9.725 a mano: el escalado en chat construye solo el **training set (~1.000 intervenciones)**, estratificado por fase de política monetaria; el **modelo fine-tuneado (BETO) etiqueta el resto del corpus** en la Fase 8. Universo de scoring sigue siendo las 9.725 (decisión 2); lo que se acota es el trabajo manual |
| 9 | Gold ciego y test set (2026-09-16, decisión del investigador) | **306 intervenciones** de test puro (`data/muestras/gold_ciego_300.csv`), con **exclusión dura** de todo lo etiquetado (assert en `scripts/09`). Estratificación: 34 por cada una de las 9 fases TPM posteriores a jul-2005 (residuo jul-2005, 50 int., excluido y documentado) × sub-estrato por señal de decisión: **2/3 del marco tiene vocabulario de decisión** (`PATRON_DECISION`), para que κ pueda medir acuerdo también en clases minoritarias — el sesgo del marco queda documentado en el script. Seed 20260916. La misma 306 será el **test set del fine-tune** (Fases 7/8): κ IA-humano y evaluación del modelo se refieren al mismo conjunto |
| 10 | Desbalance de clases del training set (2026-09-16, investigador: *"has lo mas recomendable"* → se ejecutan ambas mitigaciones) | El training set base (1.025) quedó con 88 % neutral (85/8,5/6,5 % sin contar flag-0; solo 122 ejemplos hawkish+dovish). Mitigación doble: **(1)** segunda ola de etiquetado chat con **estrato enriquecido** (`scripts/10`, seed 20260917): ~250 intervenciones priorizando Consejo con palabras de decisión (pool A, tope 20/fase) y Gerente de Div. Estudios con palabras de decisión (pool B), troceadas en tandas ≤20k palabras que continúan la numeración (tandas 9+); mismo codebook v2 y misma capa L1. **(2)** En Fases 7/8 el modelo se estructura **en dos etapas**: etapa A filtra lo sin-stance (procedural/descriptivo; insumos `es_relevante` y etiquetas actuales) y etapa B clasifica hawkish/dovish/neutral solo sobre lo filtrado. Recomendaciones técnicas asociadas: `class_weight='balanced'` en el fine-tune, variante de entrenamiento solo-relevantes, corrección de priors opcional tras etapa A (tipo King-Zeng/EM), y evaluación contra el gold por clase y por sub-estrato. **Convención hija registrada (sesión 10):** votar mantener cuando el staff ofrece `{disminuir 25, mantener}` y el sesgo previo era a la baja = **hawkish relativo (0,65-0,70)** — simétrica a la regla de pausas en ciclos de alzas |

### Clases de postura (decisión del investigador, 2026-09-15; detalle en `docs/codebook_v2.md`)

| Clase | Definición operativa |
|---|---|
| `hawkish` | Postura de política monetaria más contractiva: subir TPM o sesgo de alza; preocupación dominante por inflación/expectativas |
| `dovish` | Postura más expansiva: bajar TPM o sesgo de baja; preocupación dominante por actividad/empleo |
| `neutral` | Diagnóstico descriptivo sin inclinación, argumentos balanceados, o contenido no relacionado con postura de política monetaria |

**Variables ortogonales obligatorias en cada etiqueta**: `es_relevante` (binaria; 1 por defecto; 0 = formalidad, logística o contenido sin valor monetario) y `nota` (motivo breve, obligatoria cuando `es_relevante=0`). La clase `irrelevante` **no** forma parte de la variable de postura: la relevancia es una propiedad del registro, no una postura. Coherente con Shah et al. 2023 (FOMC, 3 clases); WCB (2025) usa 4ª clase por trabajar con frases crudas scrapeadas, mientras este corpus ya viene curado (los registros formales son pocos y concentrados: `apertura_cierre` del Consejo y del Presidente).

## 4. Protocolo de etiquetado

### 4.1 Flujo (IA-primero con validación humana final)

```
Codebook v1 → Piloto IA (300) → revisión investigador → rondas IA (curva de aprendizaje)
   → Gold humano (300 a ciegas) → Cohen's κ humano–IA
   → fine-tune final → scoring de las 9.725
```

1. **Codebook versionado** (`docs/codebook_vX.md`): definiciones + ≥3 ejemplos reales por clase + casos borde (escenario_internacional ≠ stance; ministros; textos institucionales; flags `Cotejar_PDF`).
2. **Piloto (n=300)**: muestra estratificada año × tópico × actor (seed fija). Cada etiqueta incluye `label + confianza + frase_justificante textual`. El investigador revisa una submuestra → ajuste del rubro (codebook v2).
3. **Rondas de escalado acotadas (decisión 8, §3)**: se etiqueta en chat hasta completar un training set de **~1.000 intervenciones**: (a) bloque cronológico inicial (cierre de 2005, fase de alzas 3→4,75% TPM, máxima densidad de cambios de decisión) y (b) bloque **estratificado por fase de política monetaria** 2006–2015 (alzas 2006, mantención 2007–08, alzas y bajas de crisis 2008–09, pausa 0,5% 2009–10, alzas 2010–11, mantención 2012–13, bajas 2013–14, quiebre 2015), con seed fija. Tras cada ronda se entrena un modelo rápido y se registra Macro-F1 → **curva de aprendizaje**; se detiene cuando se agote el presupuesto estratificado o la mejora marginal se estanque. **El resto del corpus (~8.600) lo etiqueta el modelo fine-tuneado en la Fase 8.**

4. **Gold ciego y test puro (decisión 9)**: validación humana con **306 intervenciones** (`scripts/09_muestra_gold_ciego.py`, seed 20260916) *excluyentes* del training set, estratificadas por las 9 fases de la decisión 8 y con sub-estrato 2/3 de vocabulario de decisión (regex documentado) para que el kappa Cohen y el test final sean informativos en las clases minoritarias (una muestra puramente aleatoria entregaría ~90% neutrales). Instrumento: `data/muestras/gold_ciego_300.csv` + `docs/INSTRUCCIONES_GOLD.md`. Uso dual: (a) κ IA-chat vs humano (el chat etiqueta esas mismas 306 a ciegas, sin ver las respuestas) y (b) test set final del modelo fine-tuneado (Fases 6–8). El sesgo de enriquecimiento se declara: las métricas poblacionales del corpus se reportan aparte (por sub-estrato).

5. **Mitigación del desbalance de clases (decisión 10)**: el training set inicial quedó 85% neutral / 15% H+D (n=122, excluyendo 213 ítems de logística con `es_relevante=0`), fiel a la composición real de las actas pero insuficiente para un fine-tune estable de las clases minoritarias. Mitigación doble: (a) **tanda 9 enriquecida** (`scripts/10_muestra_tanda9_stance.py`, seed 20260917): ~250 intervenciones nuevas muestreadas del universo sin etiquetar con sobre-representación de consejeros y de vocabulario de decisión, que el chat etiqueta en tandas por presupuesto (objetivo: H+D ≈ 20% del total ampliado ~1.275); (b) **arquitectura en dos etapas** (implementación en Fases 6–8): etapa A filtra relevancia/tipo de intervención (procedural vs descriptiva vs con stance, derivable de las etiquetas actuales y del flag `es_relevante`) y etapa B clasifica stance 3-clases solo sobre intervenciones filtradas; en el scoring se corrige el prior (las métricas se reportan por composición poblacional).
4. **Test-retest**: 30 IDs fijos re-etiquetados en cada ronda → consistencia interna (meta ≥ 90% de coincidencia).
5. **Gold humano (n=300)**: el investigador etiqueta **a ciegas** (sin ver etiquetas de la IA) una muestra estratificada. Si κ < 0.7 → revisión del rubro y re-etiquetado; meta κ ≥ 0.7 (ideal ≥ 0.8).

### 4.2 Formatos de registro

- **Etiquetas en formato largo** (append-only), `data/etiquetas/etiquetas_ronda_XX.csv`:
  `intervencion_id, metodo, etiqueta, prob_hawkish, prob_dovish, prob_neutral, score, frase_justificante, confianza, es_relevante, nota, ronda, version_codebook, fecha, etiquetador`
  donde `metodo ∈ {ia_ronda, humano_gold, tfidf, embeddings, beto_ft, llm_zeroshot}`. Formato largo (no columnas por método como en v0a): agregar métodos no rompe el esquema y habilita comparaciones limpias.
- Las frases justificantes quedan como activo de explicabilidad (y material para el scrollytelling).

## 5. Arquitectura de datos por capas (esquema objetivo)

| Capa | Tabla | Contenido |
|---|---|---|
| **L0** | `corpus` | Inmutable, desde el Excel: `intervencion_id, meeting_id, fecha, actor, cargo, topico, keywords, texto, flag_cotejo` |
| **L1** | `etiquetas` | Largo (§4.2): una fila por intervención × método |
| **L2** | `votos` | `meeting_id, actor, opcion (sube/mantiene/baja), magnitud_pb, fuente_textual, confianza` — **solo declaraciones explícitas** del actor; extracción diferida a Fase 10 (no alimenta el modelo) |
| **L2** | `macro` | Set completo (decisión del investigador, 2026-09-15): `meeting_id, TPM, dTPM, policy_decision, ipc, desempleo, imacec, ipec, sit_pais_1a, eee_inflacion_1a` (fuentes: mindicador, BDE, Adimark). Roles: `TPM, dTPM, policy_decision` → validación externa (obligatorios); `ipc, imacec` → variable de ciclo para la descomposición estructural-coyuntural (§7); el resto → contexto y análisis de robustez |
| **L2** | `actores_metadata` | `actor, inicio_mandato, fin_mandato, nominado_por, cargo_max, background, educacion` |
| **L3** | `master` (vista) | Esquema v0b materializado: intervención + etiqueta final + score + macro + provenance. Lista para análisis |

**Campos v0b resueltos así:** `speech_id=intervencion_id` · `main_topic/topic_vector` ← modelado temático complementario a los 13 tópicos oficiales (§8.2) · `keywords_flags` ← keywords + flags derivados · `confidence_flag` ← confianza de etiquetado · `policy_decision` + `TPM` ← capa macro · `doc_regime` = "acta" para 2005–2015 (queda definido para una eventual extensión con minutas) · ~~`es_herencia`~~ ← eliminada (obsoleta) · ~~`nombre_pdf`/`num_pagina`~~ ← eliminados (el Excel ya contiene el contenido íntegro; linaje a nivel `meeting_id`).

## 6. Validación externa

- **TPM real** mensual 2005–2015: `mindicador.cl/api/tpm` (gratuita, sin key) como fuente principal; API oficial BDE del BCCh como respaldo.
- Prueba de utilidad económica: correlación del índice de stance agregado con **ΔTPM** contemporáneo y lead/lag; eventos foco: crisis 2008–09 (bajas agresivas), normalización 2010–11, ciclo de bajas 2013–14.
- **Matriz de votos extraída del propio texto** (§7) como ground truth de comportamiento por actor.

## 7. Entregables de data por actor (y por reunión)

| Archivo | Contenido | Uso previsto |
|---|---|---|
| `actores/perfil_topico_actor.csv` | Distribución normalizada por actor en 7 ejes (internacional, financiero, inflación/precios, actividad/demanda, laboral, fiscal, decisión-TPM) | **Radar FIFA** por actor |
| `actores/vocabulario_distintivo_actor.csv` | Palabras más distintivas por actor (log-odds con prior Dirichlet informativa, Monroe et al. 2008) | Etiquetas de ejes, listas de palabras |
| `actores/scores_intervencion.csv` | `s_i = P(hawkish) − P(dovish) ∈ [−1,1]` + probabilidades por intervención con actor | Series individuales |
| `actores/serie_stance_actor.csv` | Rolling 12m por actor vs media total; descomposición `s_it = α_i + β_i·ciclo_t + ε` | **Hawk estructural (α) vs coyuntural (β)** |
| `actores/matriz_votos.csv` | Por reunión × actor: **solo votos explícitos** (el actor declara textualmente su opción, + magnitud), fuente y confianza. Extracción diferida a Fase 10; no entra al modelo. **Única base de votos individualizados 2005–2015 que existe** | Comportamiento de voto; GT de validación |
| `actores/convergencia_actor.csv` | Por reunión: brecha inicial (`s_primera − decisión`), brecha final (`s_última − decisión`), convergencia = \|inicial\| − \|final\|; promedio por actor | ¿Quién converge al consenso y quién marca posición? |
| `actores/red_afinidad.csv` | Matriz actor × actor de coincidencia (votos exactos o correlación de scores) | **Red de afinidad**: coaliciones, posición del Presidente |
| `actores/disenso_actor.csv` | Distancia entre stance del actor y consenso de la reunión | Ranking de disenso |
| `actores/actores_metadata.csv` | Mandatos, nominación, background, educación | Perfiles, controles |
| `actores/tpm_real.csv` | TPM efectiva por reunión | Validación externa |

### 7.1 Convergencia intra-reunión (definición)

Por actor con voto en la reunión *t*: `s_primera` = score de su primera intervención con stance; `s_última` = última intervención pre-decisión; `d_t` = decisión final. `convergencia_it = |s_primera − d_t| − |s_última − d_t|`. Promedio por actor → índice de convergencia/persuasión. El orden de habla se reconstruye con la `N` secuencial del `ID_Intervencion`.

**Nota:** se calcula con **scores** (no requiere votos explícitos) → no depende de la extracción de la Fase 10.

### 7.2 Red de afinidad (explicación simple)

Con la matriz de votos (o, antes de ella, los scores) calculo para cada **par de consejeros** en qué porcentaje de reuniones coinciden en postura. Eso es una red: cada nodo es un consejero y entre dos nodos va una arista tanto más gruesa cuanto más coinciden. Ejemplo: si en 2009–2010 dos consejeros coinciden en el 85% de las reuniones, su arista es gruesa y aparecen juntos en el grafo; quien coincide poco con ambos queda alejado → **emergen visualmente los "clanes" o coaliciones**, y se ve si el Presidente lidera un bloque único o negocia entre dos bandos. Se calcula con acuerdo exacto de votos o, en su defecto, correlación de scores en el tiempo.

### 7.3 Evolución semántica en el tiempo (entregable de data)

- `semantica/mix_topico_anio.csv`: participación de cada tópico por año (gráfico base: área apilada / heatmap).
- `semantica/palabras_distintivas_era.csv`: fightin' words por período (bursts de vocabulario: "subprime", "normalización"…).
- `semantica/deriva_anio.csv`: centroide de embeddings por año + distancia coseno año-a-año (trayectoria 2D para gráfico de impacto).
- Recomendación scrolly: mix + palabras como base narrativa; deriva como gráfico central.

### 7.4 Tópicos y keywords: clasificación humana vs máquina

El corpus ya trae `Tópico` y `Keywords` catalogados **manualmente por el investigador**. Diseño de separación: ambas variables existen en dos versiones —

- `topico_humano` / `keywords_humano` (capa L0, inmutables, verdad de referencia)
- `topico_maquina` / `keywords_maquina` (detectados por el modelo: clasificador supervisado que aprende la taxonomía humana + extracción no supervisada tipo BERTopic/KeyBERT como contraste)

Entregable `semantica/comparacion_topico_humano_maquina.csv` con: matriz de acuerdo, % de coincidencia por actor/tópico/año y los casos divergentes con su texto (¿error de la máquina, caso genuinamente ambiguo, o algo que la catalogación humana no capturó?). **Valor metodológico**: audita la consistencia de la catalogación humana y agrega una capa de validación a la tesis.

## 8. Flujo de trabajo en GitHub

- Rama de trabajo: `arena/01a0a3a0-fase-2` (PRs frecuentes hacia `main`).
- Reglas de trabajo permanentes: `docs/REGLAS.md` (incluye estilo: lenguaje profesional, sin emojis).
- Memoria entre sesiones: `docs/AVANCE.md` (actualización obligatoria al cierre de cada sesión).
- **Un PR por unidad de progreso**: docs, codebook, cada ronda de etiquetado, cada entregable.
- Datos etiquetados en CSV append-only bajo `data/etiquetas/`; codebook y decisiones bajo `docs/`.
- Muestras con seed fija y registrada (reproducibilidad).
- No commitear artefactos grandes (checkpoints de modelos van fuera de git o con LFS si hiciera falta).

## 9. Roadmap (actualizado 2026-09-16)

- [x] **Fase 0 histórica** — Consolidación del corpus y esquemas v0a/v0b.
- [x] **Fase 1** — Planificación y documentación.
- [x] **Fase 2** — Codebook v2 aprobado y congelado; convenciones del entrenamiento preservadas en `docs/CONVENCIONES_ETIQUETADO.md`.
- [x] **Fase 3** — L0, metadata inicial, marco piloto y macro local. Auditados contra fuentes; completar campos pendientes según `data/L2/pendientes_manifest.csv`.
- [x] **Fase 4** — Piloto IA 300/300 completado.
- [x] **Fase 5** — Training cerrado: 19 CSV, 1.352 etiquetas IA (H=116, D=89, N=1.147; relevancia 0=269). Cobertura exacta de tandas verificada. Curva de aprendizaje y test-retest 30 aún pendientes.
- [ ] **Fase 6** — **Evaluación TF-IDF vs humano completada; cierre documental pendiente.** Selección sobre 1.352 IA: 12 candidatos, cinco folds por reunión; elegido unigramas/min_df=3/C=2, media CV 0,7264. Reajuste con 1.352 y test humano 306: accuracy 0,8497, macro-F1 0,6775, κ 0,6458. Persisten 86 citas pendientes; no se forzó importación gold. Este κ es modelo–humano, no IA-chat–humano (control opcional). Ver `docs/EVALUACION_TFIDF_GOLD.md`.
- [ ] **Fase 7** — Experimento BETO dos etapas. Revisar metas con el baseline correcto; seleccionar hiperparámetros sin usar el test final.
- [ ] **Fase 8** — Scoring completo y validación de serie. Hay 8.373 IDs sin etiqueta IA (8.016 sanos fuera de training/gold). Sanidad descriptiva existente: Spearman 0,6639 vs ΔTPM en 131 reuniones con etiquetas relevantes.
- [ ] **Fase 9** — Entregables de actores, vocabulario, convergencia, afinidad y disenso; evolución semántica y comparación de tópicos/keywords.
- [ ] **Fase 10** — Extracción de votos explícitos y decisión del Consejo, diferida; no convertirla sin acuerdo en variable de entrada del clasificador.
- [ ] **Fase 11** — Scrollytelling + paper (fuera de alcance actual).

### 9.1 Punto de retoma

**Fuentes inmutables:** los dos consolidados Excel, L0, 19 corridas de etiquetas, marco gold canónico, libro devuelto y codebook v2. Los generadores rechazan sobrescrituras. La auditoría reconstruye selecciones históricas en temporales con las exclusiones de cada etapa, no con el training final.

**Corrección técnica que cambia la interpretación del baseline:** el 0,3511 publicado anteriormente comparaba predicciones con filas equivocadas. No usarlo como piso ni como evidencia de incapacidad bag-of-words; se retiraron de la retoma las metas BETO derivadas de él. Los artefactos actuales registran hashes y `version_evaluacion=oof_por_indice_v2`.

**Decisión de evaluación acordada (2026-09-16):** separar entrenamiento, validación y test por función, no forzar 80/10/10 sobre cantidades ya fijadas. Dentro de las 1.352 IA se usa GroupKFold(5), ~80 % train/~20 % validación en cada vuelta. El gold humano de 306 no participa en selección. Se elige la mayor media de macro-F1 de validación, se reajusta con las 1.352 y se evalúa una sola configuración humana. Las citas son un requisito documental separado de la evaluación de clases completas. Una segunda anotación IA-chat no es prerrequisito para evaluar TF-IDF.

**Resultado congelado:** `data/evaluacion/tfidf_gold_v1/` contiene protocolo previo, candidatos, folds, elección, predicciones y métricas. Scripts 18 y 19 se ejecutan en procesos separados; el 18 no abre el Excel humano. Reproducción completa verificada sin cambiar parámetros tras conocer el test. El mejor CV es una cifra de selección, no una prueba independiente.

**Hacer a continuación:**
1. Corregir las 86 citas en una nueva versión sin alterar etiquetas; conservar original, fecha confirmada y procedimiento humano con revisión posterior IA sin cambios declarados. No afirmar protocolo completamente ciego.
2. Decidir siguiente experimento/scoring. Para BETO, ajustar solo dentro de training/validación y definir la evaluación antes de ejecutar. Las dos etapas son relevancia y postura; no eliminar todo diagnóstico económico como irrelevante.
3. El gold comparte 115 reuniones y 12 textos con training; sensibilidad sin textos repetidos ya reportada (macro-F1 0,6859). **Los resultados humanos ya son conocidos**: si guían cambios, reservar otra evaluación independiente; no presentar una nueva evaluación en estos 306 como test intacto.
4. Mantener el análisis IA-chat/humano como control adicional si se necesita evaluar el proceso de anotación, distinto de la prueba del clasificador ya realizada.

**Documentos de continuidad:** `docs/AVANCE.md` (estado conciso), `docs/EVALUACION_TFIDF_GOLD.md` (examen humano), `docs/REVISION_2026-09-16.md` (auditoría), `docs/CONVENCIONES_ETIQUETADO.md` (decisiones históricas preservadas), `docs/REGLAS.md` (operación).

**Infraestructura:** Python 3.11, `python3 -m venv ~/venvs/fase2` y `~/venvs/fase2/bin/pip install -r requirements.txt`. Pruebas: `python -m unittest discover -s tests -v`; auditoría: `python scripts/17_auditar_estado_gold.py --reproducir-baseline`. No hay servicio web ni GPU necesarios para estos controles. Trabajar solo en la rama de sesión `arena/01a0a81b-fase-2`; no restaurar ramas anteriores con `reset --hard`.

### 9.2 Experimento léxico autorizado y completado (2026-09-16)

**Solicitud:** extraer expresiones de 1–4 palabras frecuentes en el corpus, revisar su dirección en contexto y comparar TF-IDF solo frente a características de diccionario. No convertir frases aisladas en etiquetas automáticas de intervenciones.

**Separación para construir características:** GroupShuffleSplit por reunión, 40 % para descubrimiento, semilla maestra +20: 559 intervenciones/52 reuniones. La reserva de 793/80 reuniones aporta cinco folds GroupKFold; descubrimiento se añade solo al entrenamiento de cada fold. Evita que la revisión vea sus propios ejemplos de validación. No es evaluación final nueva: la selección previa del baseline ya usó las 1.352 IA y el resultado humano agregado ya se conocía.

**Protocolo previo:** umbral ≥5 intervenciones y ≥3 reuniones; 6 candidatos por longitud y criterio (frecuencia/asociación H/D), más 6 monetarios por dirección, deduplicados. Catálogo de descubrimiento de 9.247; 73 candidatos revisados por el agente IA con 219 extractos. Diccionario congelado: 3 restrictivos, 2 expansivos, 36 contextuales y 32 sin dirección. Señales binarias afirmadas/negadas, negación izquierda de tres tokens y coincidencia más larga. No resuelve atribución, menús ni negación posterior; `recorte` también puede referirse a otros objetos.

**Comparación prefijada:** A fija en unigramas; B cruza unigramas o n-gramas 1–4 con/sin cuatro indicadores léxicos. min_df=3, C=2 y balanced, sin búsqueda extra. Todos los vocabularios y modelos se ajustan dentro de train. Media macro-F1: 0,7500 / 0,7562 / **0,7803** / 0,7124, respectivamente. Ampliar n-gramas resulta más prometedor; el diccionario no aporta una mejora consistente. No se reemplazó TF-IDF v1 ni se volvió a predecir el test humano.

**Catálogo total posterior:** 23.252 n-gramas de las 1.352 IA, únicamente descriptivo, generado después de congelar/evaluar; no se usó para modificar esta versión. Los no revisados quedan explícitamente marcados. Reextracción y comparación repetidas en temporales con resultados idénticos. Ver [informe léxico](docs/LEXICO_NGRAMAS.md) y `data/evaluacion/lexico_ngramas_v1/reproducibilidad.json`.

**Control de solape textual:** aunque las reuniones de train/validación son disjuntas, 34/793 filas validadas tienen texto idéntico a algún texto de su train (normalización de espacios). Se declara en `integridad_cierre.json`; no se retocó la partición tras evaluar. Una confirmación estricta con textos inéditos debe controlar también estas duplicaciones.

**Siguiente decisión:** no adoptar por máximo observado sin discutir confirmación. Si este experimento o el catálogo completo guían nuevas características, registrar una nueva versión y no presentar la reserva o los 306 humanos conocidos como un test intacto. Las citas gold pendientes son un trabajo documental separado, no un prerrequisito para esta comparación IA.

### 9.3 Búsqueda de longitud autorizada y completada (2026-09-16)

**Alcance acordado:** comparar `(1,1)` a `(1,6)` sin diccionario, manteniendo A en unigramas, min_df=3, C=2 y los mismos cinco folds del experimento léxico. No es una nueva optimización conjunta de hiperparámetros. Se congela un protocolo nuevo antes de entrenar y se conserva intacta la versión anterior. Selección por mayor media macro-F1 no redondeada; empate exacto: menor longitud. Detener esta búsqueda en seis alternativas.

**Resultados medios en orden n=1…6:** 0,7500 / 0,7617 / 0,7673 / **0,7803** / 0,7730 / 0,7753. Se selecciona `(1,4)` como candidato interno. Diferencia con unigramas +0,0303 (mejora en 4/5 folds); con el segundo, `(1,6)`, solo +0,0050. La dispersión y cinco folds no permiten proclamar superioridad estadística. Vocabulario B medio: 36.702 frente a 42.846 de `(1,6)`.

**Controles:** vocabularios/IDF/clasificadores ajustados solo dentro de train; A compartida entre las seis B de cada fold. Límites 1 y 4 reproducen exactamente las predicciones anteriores. Reejecución completa idéntica; métricas por clase, matrices, dispersión y vocabularios guardados en `data/evaluacion/longitud_ngramas_v1/`. Ver [informe](docs/LONGITUD_NGRAMAS.md).

**Interpretación:** mejor límite observado entre los seis, no óptimo universal. Es selección interna adaptativa sobre una reserva ya consultada; persisten 34 textos repetidos con train. No se vuelve a usar el test humano, no se construye léxico nuevo, no se reajusta con las 1.352 ni se reemplaza el modelo vigente. Antes de adopción/scoring se debe acordar confirmación; una evaluación independiente necesita otro conjunto y control del solape textual. No se prolonga esta búsqueda tras ver los resultados.

### 9.4 Diagnóstico de influencias autorizado y completado (2026-09-16)

**Objeto:** explicar el candidato (1,4) en cinco folds IA ya seleccionados, sin nuevas longitudes, etiquetas o modelos híbridos. Coeficientes globales contrastivos: clase B frente al promedio de otras y H−D; margen binario en A. Aporte local TF-IDF × diferencia de pesos, incluyendo intercepto y residuo; verifica exactamente los márgenes. No interpretación causal ni probabilidades calibradas. B queda marcada como inactiva si A fuerza neutral.

**Resultados:** 793 predicciones idénticas a la selección; 62 errores de postura, de los cuales 17 H↔D. Revisión del agente IA de los 17 casos completos, más seis aciertos y cuatro errores con neutral (fragmentos para aciertos largos). No se cambian etiquetas ni se reabre gold. Unión de top 25: 261 pares término–contraste / 199 términos, sin cambios de signo donde aparecen; 12 pares ausentes en algún fold. Los folds comparten training y esa estabilidad no prueba significado ni generalización.

**Hipótesis para un híbrido:** vincular acción/objeto, apoyo/rechazo, actor y horizonte; distinguir mantener con sesgo o frente a un menú, y reducir estímulo frente a reducir TPM. Revisar normalización numérica: `5,25%` deja `25`, y magnitudes como `25 puntos base` favorecen H aunque no definan dirección. Separar diagnóstico general de recomendación, preservando sesgo futuro. Evaluar normalización y enmascaramiento de nombres como ablaciones separadas. Un modelo de texto completo y una vista contextual de decisión podrían combinarse y derivar contradicciones a revisión; no implementar reglas deterministas a partir de estos errores.

**Siguiente decisión pendiente:** autorizar y prefijar una comparación acotada del híbrido, todavía no entrenado. Los ejemplos inspeccionados pasan a desarrollo; una confirmación independiente requiere otra evaluación y control de duplicaciones. No cambiar el codebook ni presentar nuevamente los 306 humanos conocidos como test intacto. Ver [informe de influencias](docs/INFLUENCIAS_NGRAMAS.md), tablas, revisión y manifiestos en `data/evaluacion/influencias_ngramas_v1/`.

### 9.5 Investigación externa previa al híbrido (2026-09-16)

**Pedido autorizado:** revisar en profundidad trabajos y foros antes de implementar. Revisión dirigida completada en [INVESTIGACION_HIBRIDO.md](docs/INVESTIGACION_HIBRIDO.md), con 20 fuentes y alcance de lectura/versiones registrado. No es revisión sistemática exhaustiva ni reproducción de resultados externos.

**Conclusión:** aprender dirección desde palabras aisladas no resuelve objeto, respaldo, negación, emisor ni temporalidad. Los trabajos justifican comparar representaciones contextualizadas, no dictar una mejora local ni invertir H/D por una negación. La tokenización numérica es un problema verificable y debe aislarse del aporte del contexto. WCB trabaja con documentos disponibles en inglés; su guía de Chile contiene inconsistencias en la tabla 98 del HTML v2. Esto exige aclaración antes de importar, no demuestra inversión global de las etiquetas externas.

**Recomendación pendiente de autorización, no nuevo diseño ejecutado:** primera comparación de cuatro B: referencia (1,4), representación numérica corregida, vista contextual y combinación de ambas. A y parámetros base fijos; sin más búsqueda de longitudes, diccionarios direccionales ni reemplazo de modelo. Prefijar extracción, escalado, pruebas conductuales y criterio de selección antes de entrenar. Pasado y futuro cuentan conforme a R7; conservar condiciones, texto completo y atribución dentro de la intervención. Neutral no equivale a abstención.

**Evaluación:** los 793 y sus errores son desarrollo conocido. Ajustes, combinadores o calibración deben quedar dentro de train; una confirmación futura necesita control prefijado de reuniones y duplicados, otra evaluación y autorización. No reabrir los 306 humanos, modificar el codebook, reajustar las 1.352 ni puntuar el corpus en esta unidad. Transformer/LLM serían una comparación posterior autorizada, no una búsqueda abierta.

**Cierre documental:** no se entrenaron modelos ni se ejecutaron tests de ajuste. Se conservan los resultados y controles experimentales anteriores; se verifican integridad de archivos y enlaces del nuevo informe.

### 9.6 Cuatro representaciones del híbrido: autorizadas y comparadas (2026-09-16)

**Autorización posterior a la investigación:** «vamos con tu recomendación». [Protocolo previo](docs/PROTOCOLO_HIBRIDO_V1.md), módulo `representaciones_contextuales.py` y evaluador `24_evaluar_hibrido_contextual.py`. Preparación sin ajuste registra hashes; la ejecución exige protocolo intacto. No se modificaron scripts previos.

**Diseño ejecutado:** B0 texto completo (1,4); B1 tokenizador con decimales/dígitos aislados/%; B2 texto completo + ventanas candidatas de decisión y una frase vecina a cada lado; B3 ambas modificaciones. A compartida fija; C=2/min_df=3; cuatro variantes y cinco folds históricos. Vista contextual no cruza huecos ni intervenciones, no impone etiquetas por palabras y conserva pasado/condiciones. Es una selección léxica de contexto, **no resolución semántica completa** de emisor, objeto, negación o preferencia. Bloques L2 de peso 1 sin renormalización global.

**Resultado:** macro-F1 medio B0/B1/B2/B3 = **0,780282 / 0,779266 / 0,776352 / 0,776365**. Ninguna modificación gana en media ni cumple las tolerancias prácticas prefijadas. Errores totales = **62/61/62/63**, H↔D = **17/18/17/16**. B1 reduce un error total, pero no mejora la métrica principal; B3 mejora ligeramente el macro-F1 conjunto, pero no el promedio por fold que decide. No cambiar de métrica después del resultado.

**Diagnóstico:** contexto en 345/793 intervenciones, 41,0 % de caracteres totales; ocho textos con formatos numéricos ambiguos. La batería prefijada de 14 ejemplos inventados da 25/70 aciertos por variante (cinco folds, no observaciones independientes); la invariancia por pares no garantiza corrección. Estos tests no son estimación representativa del corpus. No se retocó el modelo para pasarlos.

**Cierre:** no adoptar el híbrido v1 ni ampliar la rejilla. Conservar B0 (1,4) como referencia, no confundirlo con el modelo unigramas guardado del examen anterior, que permanece intacto. Cualquier extractor semántico/transformer es otra propuesta, no queda ejecutado por esta ronda. Confirmación futura separada con control de reuniones y duplicados; 793 reutilizados y 34 copias siguen siendo desarrollo. Sin abrir/predicir 306 humanos ni reajuste final/scoring completo.

**Verificación:** B0 reproduce exactamente las predicciones de (1,4). Repetición completa en temporal: nueve CSV, métricas e informe idénticos; 91 pruebas superadas y una antigua omitida para no reabrir referencias humanas. 136 archivos previos intactos, incluidas fuentes/etiquetas/modelo; cinco CSV del examen anterior verificados solo por hash. [Informe](docs/EVALUACION_HIBRIDO_V1.md) y artefactos en `data/evaluacion/hibrido_contextual_v1/`.

### 9.7 Piloto WCB Chile: autorizado, ejecutado y cerrado (2026-09-16)

**Autorización:** «ok si puedes probarla bien mientras pensare otra forma». Se verificó acceso público, licencia, idioma y esquema antes de probar. Alcance comunicado y protocolo congelado antes de los resultados: [PROTOCOLO_WCB_PILOTO_V1.md](docs/PROTOCOLO_WCB_PILOTO_V1.md).

**Adquisición y traducción:** primeros 100 train de la semilla 5768, no 700 ni 1.000; captura de columnas desde la respuesta completa de API mediante herramienta web (la descarga directa por Python falló por TLS). Traducción al español del agente, no texto oficial alineado, no ciega ni revisión humana. Datos originales y traducción bajo CC BY-NC-SA 4.0 con atribución, separados en `data/externos/wcb_chile_piloto_v1/`. No se inspeccionó val/test externo ni se auditó el solape completo entre las tres semillas. No equiparar traducción guardada con traducción validada independientemente.

**Diseño:** mismo train/validación IA histórico, A unigramas compartida, B (1,4)/C2/min_df3. Base, +99 inglés, +99 español. Se excluye únicamente la frase irrelevant de B sin mapearla a neutral ni entrenar A con externos. Se preservan H/D/N de origen, incluso donde no equivalen a nuestro criterio. Peso externo individual 1; balanced cambia con los nuevos conteos. Sin búsqueda adicional ni actualización del codebook. Texto externo reciente en evaluación retrospectiva, no predicción temporal sin información futura.

**Resultado:** media macro-F1 **0,780282 / 0,728468 / 0,725897**. Español pierde **0,054385**, gana 1/5 folds y eleva errores **62 → 74** (4 corregidos/16 nuevos). Inglés también empeora (69 errores). No cumple criterio de confirmación. **No adoptar esta importación**, sin concluir que todo el corpus WCB sea inútil. Las diferencias de tarea/unidad, la traducción no oficial y el pequeño tamaño limitan cualquier generalización.

**Cierre:** script 25 y once tests nuevos, B0 idéntica, A compartida, cuatro CSV + auditoría/métricas/informe reproducidos. **102 tests superados y uno omitido** para no abrir referencias humanas. **160 archivos previos intactos**, sin cambio del modelo ni anotaciones canónicas; sin acceder/predicir 306 humanos, refit final o scoring completo. [Informe](docs/EVALUACION_WCB_PILOTO_V1.md); artefactos en `data/evaluacion/wcb_chile_piloto_v1/`. Quedan conocidas las 34 repeticiones IA históricas; no confirmación independiente.

### 9.8 Ronda H/D con control de copias: autorizada y cerrada (2026-09-16)

**Autorización:** «has todas las pruebas que quieras pero manten todo limpio», después de discutir recursos financieros españoles y la debilidad H/D del examen humano conocido. Se fijó una ronda acotada, sin utilizar las 306 respuestas para ajustar.

**Bloqueo contextual:** no hay checkpoint BETO local o GPU; dos CPU/~3,8 GiB RAM. La petición de configuración a HF falló con TLS EOF. Se consultó README oficial y no se obtuvo ningún peso. BETO y entrenamiento auxiliar financiero **no ejecutados**, no clasificados como experimentos que perdieron. Sin instalación de paquetes grandes o scripts de entrenamiento sin probar.

**Diseño:** [protocolo previo](docs/PROTOCOLO_CLASIFICADORES_HD_V1.md), script 26 y 14 tests. Cinco candidatos B con A compartida: LR palabras, SVM palabras, LR mixta, SVM mixta y LR jerárquica neutral/direccional→H/D. C fijos 2/1, palabras 1–4; char_wb 3–5/50.000 máximo y L2 global para mixtas. Sin externos, calibración o ajuste de umbrales. Ancla histórica separada. Principal: media por fold del F1 H/D, calculado sobre todas las clases para penalizar falsas alarmas sobre neutral.

**Nueva higiene de evaluación:** conservar las mismas 793 validaciones; retirar de cada train sus copias normalizadas sin mirar etiquetas de validación. Exclusiones por fold 16/15/15/10/11, train final 1178/1178/1178/1183/1183. Afecta a parte de los 559 originalmente fijos. Cero copias exactas normalizadas train/val; siguen presentes limitaciones de desarrollo reutilizado, repetición interna y similitud semántica. No modificar L0, etiquetas ni resultados previos.

**Resultado:** F1 H/D medio **0,691477 / 0,628481 / 0,649631 / 0,641184 / 0,647029**. Macro-F1 H/D/N medio **0,783501 / 0,740357 / 0,754841 / 0,749707 / 0,752287**. Ninguna alternativa supera B0 limpia ni cumple los umbrales previos. La SVM mixta mejora accuracy global a 0,9256 (59 errores), pero recall D cae a 0,4490: no seleccionarla por ese indicador. Referencia limpia: 60 errores y 90/118 H/D IA correctos; retirar copias solo corrigió dos neutrales frente al ancla, no mejoró recall H/D. No se midió una mejora humana.

**Cierre y limpieza:** nueve CSV, métricas e informe idénticos al repetir en temporal eliminado. **116 tests aprobados y uno omitido** por acceso al gold; **177 archivos previos intactos**. Nuevos: un evaluador, un archivo de tests, protocolo, informe y artefactos de reproducción. Sin nuevos datasets, checkpoints, dependencias o modelos persistidos. No se entrenó con las 1.352 completas ni se puntuó el corpus. [Informe](docs/EVALUACION_CLASIFICADORES_HD_V1.md).

**Siguiente:** no extender esta rejilla tras sus resultados. BETO necesita adquisición de pesos y recursos adecuados; su comparación queda pendiente bajo la autorización amplia, no fingir ejecución. Cualquier futura confirmación necesita una referencia humana nueva y reservada.

### 9.9 Revisión humana acotada de entrenamiento: preparación histórica (devolución en §9.11)

**Autorización:** «ok hazlo», después de proponer revisar 10 H/10 D/10 N antes de BETO. Esta fase no inventa decisiones humanas ni mide acuerdo todavía. [Protocolo](docs/PROTOCOLO_REVISION_ENTRENAMIENTO_30_V1.md).

**Selección reproducible:** grupo de 559 de descubrimiento. Excluir los 306 IDs humanos (solo marco), sus copias por texto L0 y copias de las 793 validaciones. Deduplicar pool por normalización espacios/minúsculas/acentos; quedan 541 (47 H/40 D/454 N). Rangos SHA256 con semilla 20260916 para elegir 10 de cada etiqueta IA y otro rango para mezclar orden. 30 casos/15 reuniones, sin priorizar errores/longitud/confianza. Textos íntegros (81.439 caracteres), 195–6.760 por caso. No estimación poblacional ni nuevo test independiente.

**Interfaz y custodia:** script 27 + plantilla HTML + once tests; formulario con códigos, texto completo y metadatos, sin clave IA ni feedback. H/D/N, duda no entrenable, relevancia, cita y nota según guía. Registrar ayuda y acceso previo a etiquetas sin afirmar ciego estricto. Guardado local, exportación y recuperación JSON de la misma muestra; no respuestas guardadas por servidor. Clave reservada fuera de carpeta pública, pero accesible al dueño del repositorio. No abrirla antes de decidir.

**Verificación:** generación repetida con clave y HTML idénticos. **127 tests pasados y uno omitido** por lectura humana; interfaz probada en DOM simulado jsdom 26.1.0, no inspección visual. HTTP protege las rutas del padre con 404. **195 archivos anteriores intactos**. Sin nuevo Excel, modelo, dataset externo, corrección o entrenamiento BETO. jsdom solo en caché de tests fuera del repo.

**Paso pendiente al cerrar la preparación (ya devuelto, ver §9.11):** el investigador completa [formulario](data/auditoria/revision_entrenamiento_30_v1/formulario/index.html), descarga y adjunta JSON. Preservar primera devolución antes de comparar, no sobrescribir anotaciones antiguas ni convertir desacuerdos automáticamente en errores IA. BETO permanece pendiente de adquisición de pesos; no se preparó una nueva comparación supervisada antes de resolver esta revisión.

### 9.10 Revisión mediante XLSX: cambio de interfaz autorizado

El investigador informó que el formulario no guardó su avance y solicitó descargar un Excel ordenado para rellenarlo. Se mantiene la misma muestra de 30, sin selección nueva, etiquetas IA visibles u ocultas ni respuestas inventadas. [Libro](data/auditoria/revision_entrenamiento_30_v1/revision_entrenamiento_30.xlsx).

Cuatro hojas: Inicio, Respuestas, Textos y Guía. Decisiones C–F vacías/editables en amarillo, desplegables, cita ≤300, motivo, enlaces internos y estado de campos (no evaluación de corrección ni literalidad). Texto completo dividido en bloques para visualización; 81.439 caracteres reconstruidos idénticamente. Guardar copia local y devolver XLSX; no depende del almacenamiento del navegador.

Script 29 añade enlace HTTP de descarga y servidor de dos rutas públicas, sin exponer la clave o archivos archivados. Generadores 27/28 y muestras intactos; interfaz/manifiesto anterior archivados explícitamente, manifiesto activo v1.2. XLSX entregado también como archivo en chat.

18 pruebas específicas pasaron; descarga attachment con bytes idénticos, enlaces/validaciones/protecciones y reproducción semántica comprobados. 208 archivos previos protegidos sin cambios. Sin ejecución en Excel real ni suite ML completa (checkpoint histórico ausente del entorno restaurado); sin modelos, etiquetas corregidas o nueva evaluación humana. Estado al entregar: pendiente recibir el libro rellenado; devolución posterior en §9.11.

### 9.11 Devolución de los 30: recibida y comparada, adjudicación pendiente

El investigador devolvió `30 anotaciones humanas.xlsx` mediante enlace a GitHub. Se descargó del commit fijado `2667e7d7eaa16ba9dcc67d4288515f31b0500456`, se verificó el blob y se preservó intacto con recibo/hash. La hoja simplificada tiene las 30 posturas; ID y texto completo corresponden a la muestra: 29 textos exactos y R03 igual tras normalizar espacios. No se infiere fecha de anotación del recibo.

**Resultado:** 24/30 acuerdos. Filas IA / columnas humano, H,D,N: `[[10,0,0],[0,5,5],[1,0,9]]`. Cinco D de IA son N humanos y un N de IA es H humano. Son dos anotaciones de entrenamiento, no predicciones ni un nuevo test. No extrapolar a todo el corpus porque la muestra tiene diez por clase IA.

**Interpretación separada:** leídos los seis textos completos. Aclarar mantener hoy frente a trayectoria futura, crítica al ritmo de alzas y menú frente a preferencia; R1/R7 y la neutralidad conservadora R9 requieren discusión en esos casos. [Lectura cualitativa](docs/LECTURA_DISCREPANCIAS_REVISION_30.md), atribuida al agente después de recibir/abrir la comparación, no adjudicación independiente. Ninguna decisión ni codebook cambiado.

**Documentación:** 18 citas literales de hasta 300 caracteres y 12 marcadores de ausencia; relevancia y procedencia de revisión no declaradas. Se comparan posturas sin rellenar esos campos con IA. No importación canónica, no correcciones automáticas, no reentrenamiento y ningún acceso nuevo a las 306 respuestas.

**Verificación:** script 30 valida la identidad antes de unir la clave privada. Nueve pruebas aprobadas; reproducción exacta de tres CSV, resumen e informe en temporal, 216 archivos previos intactos y siete citas adicionales del análisis verificadas. [Informe numérico](docs/REVISION_HUMANA_ENTRENAMIENTO_30_V1.md). Mantener entregas originales y resultados de experimentos congelados. No hace falta repetir las 30 anotaciones; acordar criterio/adjudicación antes de cambiar etiquetas o avanzar a desarrollo BETO, aún sin pesos.

**Continuación autorizada:** el investigador aclaró que el futuro también expresa postura y pidió seis propuestas concretas, no cambios automáticos. [Propuesta pendiente de confirmación](docs/PROPUESTA_SEIS_DISCREPANCIAS_30_V1.md): R01 H / R03 N / R08 D / R12 H / R17 D / R21 D. Siete extractos verificados, originales intactos, sin alterar v2 ni métricas originales. Son lecturas del agente después de ver ambas anotaciones; R03/R12 ambiguos. Basta discutir/confirmar por chat; no repetir el Excel ni dar por adjudicadas las etiquetas.

**Aceptación posterior: revisión de los seis cerrada.** El investigador respondió «acepto todas». [Adjudicación aprobada](docs/ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md): las seis etiquetas se registraron en una capa separada, con referencia exacta a la propuesta, mensaje de confirmación y hashes. Originales, comparación 24/30 y v2 intactos. No son etiquetas humanas independientes: hubo propuesta/explicación IA y aceptación posterior. No se requiere otro Excel ni otra confirmación de estos seis casos. Siguiente: preparación del experimento de modelo; BETO sigue pendiente de pesos, sin importación canónica o entrenamiento realizado en esta adjudicación.

### 9.12 Referencia con adjudicaciones: ejecutada; BETO aún bloqueado

El investigador pidió continuar. [Protocolo previo](docs/PROTOCOLO_MODELO_ADJUDICADO_V1.md) congelado antes del fit. Script 31 aplica en memoria las seis adjudicaciones aceptadas, solo tres cambios respecto de IA (R01/R03/R12), sin cambiar las corridas canónicas ni imputar relevancia humana. Los seis casos permanecen fuera de validación, en todos los train purgados de las mismas cinco particiones.

Dos condiciones de la misma LR TF-IDF sin nuevos hiperparámetros: original y adjudicada. La original reproduce las 793 predicciones A/B/finales de B0 limpia de 26. Parámetros, textos, validación, A y vocabularios/IDF constantes; cambia supervisión de B y sus pesos balanced derivados de train.

**Resultado contra IA reutilizada:** F1 H/D medio **0,691477 → 0,648822**, macro-F1 **0,783501 → 0,754311**, errores **60 → 66**. Nueve predicciones finales distintas, un error corregido y siete nuevos; mejora en 1/5 folds. No revertir decisiones aceptadas por esta caída ni presentarla como medición de calidad humana. [Informe reproducible](docs/EVALUACION_MODELO_ADJUDICADO_V1.md).

10 tests nuevos + 9 de recepción aprobados; cuatro CSV, métricas e informe reproducidos exactamente en temporal; 233 archivos previos intactos. No respuestas antiguas, refit final, scoring global o modelo persistido. Venv reconstruida con requirements; no instalación transformer grande.

**Bloqueo y siguiente paso:** chequeo HTTPS config/API BETO falla TLS EOF; sin GPU detectada. No ejecutar más búsquedas léxicas ni pedir anotaciones otra vez. Obtener pesos de revisión/hash verificables en un entorno con acceso, preferiblemente GPU. El protocolo define entrenamiento por intervención con cobertura completa por segmentos; es diseño previo, no runner implementado/probado. BETO debe compararse con TF-IDF adjudicado bajo las mismas etiquetas/particiones y confirmar solo después con referencia humana realmente nueva si pasa los umbrales.

### 9.13 Revisión de etiquetas de los errores: primera tanda completada

A petición del investigador se inspeccionaron los siete casos que pasan de coincidir con IA a diferir tras el cambio de tres etiquetas. Lectura de textos completos y anotaciones IA, posterior a conocer predicciones: diagnóstico del agente, no nuevo anotador ciego. [Informe](docs/REVISION_ERRORES_NUEVOS_ADJUDICADA_V1.md).

**Resultado cualitativo:** cuatro referencias D respaldadas (recomendación de bajar o rechazo/cambio explícito de trayectoria alcista) y tres casos ambiguos. No se concluye que los siete estén mal anotados. En dos se contraponen pausa táctica y normalización; en otro es necesario aclarar dirección y, posiblemente, cotejar la fuente. Ninguna nueva corrección aceptada/aplicada, ningún reentrenamiento ni sustitución de métricas originales.

Script 32 reconstruye la selección e inventario de 66; lecturas del agente separadas en JSON. Ocho tests, diez extractos propios literales y reproducción de tres archivos más informe; 245 archivos previos intactos. **59 casos restantes pendientes**, no revisión completa de los 66. Mantener las 793 como desarrollo conocido; no ajustar/reanotar sus errores y después presentarlas como evaluación independiente. Las 306 respuestas antiguas no se abren.

### 9.14 Segunda tanda de errores: todos los intercambios H/D revisados

El usuario pidió seguir. Se leyeron los 16 intercambios directos H↔D pendientes, 65.147 caracteres completos, con sus anotaciones IA originales. Selección reproducible desde el inventario de la primera tanda, sin volver a revisar sus siete casos. [Informe](docs/REVISION_INTERCAMBIOS_HD_TANDA_2_V1.md).

Juicios del agente: 10 referencias respaldadas, tres cuestionables y tres ambiguas. Propuestas pendientes (confianza media): Corbo mayo-2006 D→H, De Gregorio febrero-2008 D→H y comunicado agosto-2011 D→N. No aprobación humana nueva, corrección canónica ni reinterpretación de la aceptación de las seis adjudicaciones anteriores. En los casos ambiguos no se asigna una nueva etiqueta definitiva.

Cobertura acumulada: 23 de 66, incluidos los 20 intercambios H/D. Quedan 43 discrepancias de neutralidad. Acumulado de lecturas: 14 referencias respaldadas, tres cuestionables y seis ambiguas; no proporciones representativas de errores del corpus. No cambiar etiquetas de validación para mejorar métricas ni presentar las 793 como test intacto.

Script 33 y lecturas JSON separados; 25 citas adicionales verificadas. Ocho pruebas de cada tanda aprobadas, reproducción exacta de inventario acumulado, casos, resumen e informe. 254 archivos previos intactos; scripts/resultados anteriores congelados. No entrenamiento ni apertura del examen de 306.

### 9.15 Tercera tanda: ampliar cobertura de neutralidad

El investigador pidió abarcar lo más posible. Para maximizar el número de intervenciones leídas íntegramente en esta tanda se informó y aplicó orden ascendente por longitud original, desempate por ID, a los 43 pendientes. Se revisaron 30 textos completos (72.911 caracteres); quedan 13 largos, 105.621 caracteres. Selección por presupuesto, no muestra aleatoria ni estimación representativa.

[Informe](docs/REVISION_NEUTRALIDAD_TANDA_3_V1.md): 19 referencias respaldadas, cinco cuestionables y seis ambiguas. Nuevas propuestas pendientes: N→H en Valdés enero-2005, Ovalle marzo-2005, Corbo mayo-2007 y García enero-2005; N→D en De Ramón agosto-2015. No se cambia validación hacia las predicciones: esta última propuesta contradice también H del modelo. Ocho propuestas cuestionables acumuladas sin aceptación humana nueva.

Cobertura acumulada: **53/66; 33 respaldadas, 8 cuestionables, 12 ambiguas**. Los 20 intercambios directos H/D ya estaban cubiertos; la revisión restante es neutralidad. Se verificó A=1 y final=B en los 30 nuevos: no es fallo de filtrado de relevancia. No se explican causalmente coeficientes ni se entrena otra variante.

Script 34, lecturas manuales en JSON y validadores congelados reutilizados. 35 extractos propios literales; 24 pruebas entre las tres tandas aprobadas; reproducción exacta de cuatro archivos más informe; 263 archivos anteriores intactos. No etiquetas canónicas, métricas o modelos modificados ni respuestas del examen de 306 leídas. Continuar por los 13 pendientes explícitos; no interpretar los campos de propuesta del agente como decisiones humanas finales.

### 9.16 Cierre de la revisión de los 66 desacuerdos

Se leyeron íntegros los 13 textos restantes (105.621 caracteres), sin omitir casos ni cambiar la selección congelada. Última tanda: 8 referencias neutrales respaldadas y 5 cuestionables. Nuevas propuestas: Naudon junio-2015 N→D por prolongación del estímulo, Valdés marzo-2005 N→H por respaldo a continuar normalización, Marfán junio-2013 N→D por preferencia futura por reducción de tasas, García diciembre-2008 N→D por respaldo explícito a la conveniencia del relajamiento y García agosto-2009 N→D por defensa del estímulo y la tasa mínima prolongada. Confianza alta en Marfán y García diciembre; media en las otras tres. Ninguna aceptada/aplicada todavía.

[Informe de cierre](docs/REVISION_ERRORES_CIERRE_66_V1.md): **66/66; 41 respaldadas, 13 cuestionables y 12 ambiguas**. No queda lectura pendiente en esta lista; sí adjudicación de propuestas y resolución de ambigüedades. Las 13 propuestas acumuladas no heredan aceptación de las seis adjudicaciones Rxx. Las 12 ambiguas mantienen propuesta nula. Se conserva separada la referencia IA y la opinión del agente, posterior a conocer predicciones. No reetiquetar la validación para demostrar una mejora artificial.

Script 35, 13 lecturas manuales y resultados nuevos en `tanda_4_largos_v1/`; `revision_consolidada.csv` reúne las 66 opiniones sin reescribir las anteriores y apunta a los textos íntegros. 22 extractos nuevos verificados; A=1 y final=B en los 13. 34 pruebas específicas aprobadas, cinco archivos de datos e informe reproducidos exactamente y 273 archivos previos intactos. No entrenamiento, nuevas métricas, etiquetas canónicas modificadas, cambios a v2 o apertura de respuestas de 306. Siguiente decisión: adjudicar propuestas concretas y tratar las dudas por separado; no repetir las 30 anotaciones ni la aceptación anterior.

### 9.17 Correcciones aceptadas y ejecución local del modelo

El investigador pidió «corrige las referencias, e ittenta mandar el modelo en tu entorno» y luego «sigue». Las 13 propuestas concretas del cierre pasan de pendientes a **aceptadas**, con registro separado por ID/hash/procedencia. Los 12 ambiguos no se alteran. Las seis decisiones anteriores siguen vigentes: 19 aceptaciones, 16 cambios efectivos frente a IA. Las citas/confianza son del agente; no adjudicación ciega independiente.

La vista activa para el nuevo experimento es `data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv`: 1.352 IDs, relevancia IA y referencias original/con seis/con seis más trece. No sobrescribe corridas históricas ni cambia automáticamente sus cargadores. Script 36 preparado antes del fit, con mismos cinco folds purgados/parámetros/puerta A/vocabularios/IDF. El control reproduce exactamente la variante adjudicada de 31.

[Informe](docs/EVALUACION_REFERENCIAS_CORREGIDAS_V2.md): comparación 2×2. F1 H/D medio del control contra IA **0,648822**, contra referencias corregidas **0,711084**; este incremento de **0,062262** no cambia el modelo. Reentrenado contra IA **0,684035**, contra corregidas **0,747060**. Comparando ambas supervisiones contra la misma referencia corregida: **+0,035976**, mejora en 4/5 folds, errores **55→51**, 9 predicciones distintas, 6 errores corregidos y 2 nuevos. Sigue siendo desarrollo reutilizado después de revisar desacuerdos, no evidencia independiente de generalización. No refit final ni scoring del corpus.

Diez ajustes por fold ejecutados aquí y reproducidos en rutas temporales. **56 pruebas específicas aprobadas, 0 omitidas**, cinco archivos de datos e informe idénticos; protocolo igual salvo fecha y 284 archivos previos intactos. Los manifiestos temporales cambian por sus fechas/hash del protocolo. No apertura de respuestas de 306. [Protocolo previo](docs/PROTOCOLO_REFERENCIAS_CORREGIDAS_V2.md).

BETO: nuevo intento oficial API/config con urllib y curl; TLS EOF y SSL_ERROR_SYSCALL (35), respectivamente. Dos CPU, sin nvidia-smi; sin pesos descargados ni entrenamiento BETO. Registro técnico en `adjudicacion_cierre_66_v1/beto_disponibilidad.json`. No desactivar TLS ni presentar diseño como ejecución. El siguiente bloqueo es acceso a pesos/recursos para BETO; no pedir reaceptar estas 13 ni las seis anteriores.

### 9.18 Diagnóstico de las diez inversiones H/D más claras

El usuario expresó preocupación por invertir D y H y autorizó el diagnóstico propuesto. Sobre las predicciones corregidas de 36 se separan 15 inversiones: diez con referencia más clara (nueve respaldadas y una corrección aceptada) y cinco ambiguas. No adjudicar estas últimas ni tratar las quince como errores semánticos indiscutibles. Relectura completa de 40.937 caracteres, sin truncar fuentes.

Script 37 reconstruye cinco modelos con supervisión seis_mas_trece, sin buscar parámetros; reproduce las 793 predicciones A/B/finales. Las diez inversiones tienen A=1. Descomposición exacta del margen predicción−referencia en intercepto y aportes TF-IDF, con 8.558 features activos exportados, seis mayores por signo y residuo. No confundir coeficiente con contribución ni contribución con efecto causal de borrar texto.

[Lectura final](docs/LECTURA_DIAGNOSTICO_INVERSIONES_HD_V1.md) e [informe técnico](docs/DIAGNOSTICO_INVERSIONES_HD_V1.md): señales correctas como reducir la tasa/subir sí aportan a la referencia, pero pueden ser superadas. Reducir estímulo y una condición negada de subir requieren resolver objeto y postura. En dos alzas, la suma textual favorece ligeramente H, pero el intercepto aprendido lleva a D. No toda explicación se reduce a palabras dominantes, longitud o política fiscal.

Sonda de primera cita literal fijada antes de coeficientes: B coincide con la referencia completa en 4/10, da N en cuatro y conserva inversión en dos. Citas elegidas manualmente con conocimiento de referencia; no son extractor ni score independiente. Algunas pierden contexto legítimamente necesario (duración del estímulo en De Gregorio 2009), por lo que N en esos fragmentos no se cuenta como error semántico nuevo.

[Protocolo](docs/PROTOCOLO_DIAGNOSTICO_INVERSIONES_HD_V1.md): comparación posterior de B contextual con misma referencia/folds/A, texto íntegro y sin citas oracle. Mantener umbrales previos F1 H/D/macro/recall y exigir menos inversiones sin aumentar H/D→N, con denominadores fijos. BETO no ejecutado; acceso a pesos sigue bloqueado según 36. Estos diez casos son diagnóstico conocido, no test ni ejemplos extra de entrenamiento.

64 pruebas específicas aprobadas sin omisiones, replay exacto de seis datos e informe técnico; protocolo igual salvo UTC; 298 archivos anteriores intactos. Registro `data/auditoria/inversiones_hd_v1/verificacion.json`, con hash separado de la síntesis manual posterior. Sin etiquetas, métricas históricas o checkpoints modificados y sin apertura de respuestas de 306. Actualización en la misma rama y PR #4.

## 10. Referencias

1. Shah, A. et al. (2025). *Words That Unite The World: A Unified Framework for Deciphering Central Bank Communications Globally*. NeurIPS 2025 (Datasets & Benchmarks). Repo: `gtfintechlab/WorldCentralBanks`; dataset Chile: `gtfintechlab/central_bank_of_chile` (1.000 frases, 2018–2024, EN).
2. Shah, A., Paturi, S., Chava, S. (2023). *Trillion Dollar Words: A New Financial Dataset, Task & Market Analysis*. ACL 2023. Repo: `gtfintechlab/FOMC-Dataset` (FOMC-RoBERTa).
3. *Deciphering Fedspeak: Quantifying Dissent Among Hawks and Doves*. Findings of EMNLP 2023 (GPT-4 como clasificador).
4. Monroe, B., Colaresi, M., Quinn, K. (2008). *Fightin' Words: Lexical Feature Selection and Evaluation for Identifying the Content of Political Conflict*. Political Analysis. (vocabulario distintivo).
5. Acuerdo BCCh N°2763-01-260115 (2026): difusión de actas con rezago de 10 años; esquema de publicación vigente.


### 9.19 Preparación verificable del ensayo BETO y salida a Colab

El usuario autorizó continuar y consultar trabajos/web. Investigación dirigida de Bundesbank/MILA, Bernoth/DIW, BERT para documentos largos y documentación oficial BETO; alcance y límites de lectura en [protocolo](docs/INVESTIGACION_Y_PROTOCOLO_BETO_V1.md). No importar datasets ni adoptar métricas externas. Texto completo, no citas seleccionadas ni solo los primeros 512 tokens; la agregación simple propuesta todavía puede diluir la conclusión.

Intentos reales de HF, descarga histórica de autores y wheels CPU: TLS EOF. GitHub API/PyPI accesibles; 2 CPU, ~4 GB RAM, sin NVIDIA. Metadatos HF leídos por navegador, no pesos descargados al cómputo. Vocabulario histórico de autores distinto al checkpoint HF: rechazado, fuera de Git. Instalados transformers/tokenizers para controles, no torch ni encoder.

Scripts 38/39: paquete de **1.352 textos / 1.997.823 caracteres**, mismos cinco train/validación purgados, **793 filas de control**, referencias corregidas v2/A fijos. BETO cased con revisión/hash fijados; ventanas completas de 510+2 y solapamiento 64, media de logits por documento, CE ponderada train-only, acumulación 8 con último grupo real. Tres épocas predefinidas, sin escoger con validación. Prueba real de dos textos de train con forward/backward y actualización de encoder/cabeza antes de cinco folds; nueva instancia inicial por fold. Detener ante OOM/hash/NaN, no truncar silenciosamente.

**78 pruebas aprobadas, 0 omitidas**: 14 nuevas sin encoder y 64 de etapas 31–37. Reproducción exacta de los cinco archivos del paquete, incluido manifest; **313 archivos anteriores intactos**. El comparador se comprobó con fixtures sintéticas temporales idénticas al control, no predicciones BETO. Verificación en `data/auditoria/preparacion_beto_v1/`. No respuestas de 306 abiertas, cambios de etiquetas ni reentrenamiento TF-IDF en esta preparación.

[Notebook](notebooks/BETO_comparacion_v1.ipynb) y [guía](docs/GUIA_EJECUTAR_BETO_COLAB_V1.md): código desde commit fijo, entorno aislado, pesos públicos verificados, recuperación de folds completos mediante ZIP; no reanudación a mitad de fold. El usuario debe iniciar una GPU gratuita disponible; no hay cuenta/servicio de pago configurado ni Colab ejecutado por este agente. Pesos/paquetes/resultados/dependencias fuera de Git.

**Pendiente real:** descarga de pesos, prueba GPU y comparación BETO. Menos H↔D sin aumentar H/D→N, F1 H/D +0,02 y ≥3/5 folds favorables, guardas macro/recall; cinco ambiguos conocidos desglosados, criterio principal sobre 793. No declarar mejora, generalización, adopción o entrenamiento global antes de ejecutar y revisar. Mantener PR #4, sin nuevas anotaciones ni otra búsqueda de n-gramas.

### 9.20 Organización para traslado y nueva sesión

El investigador solicita limpieza, código/datos identificados para otro PC y continuidad antes de cambiar de sesión. **Punto de entrada actual: [EMPEZAR_AQUI.md](EMPEZAR_AQUI.md)**; para agentes, [CONTINUIDAD](docs/CONTINUIDAD.md). No requiere volver a ejecutar las etapas numeradas desde 01 ni completar formularios antiguos.

Se conserva la estructura `scripts/`, `data/`, `docs/`: no renombrar rutas sujetas a hashes. README/AVANCE pasan a ser breves, con índices por carpeta; el detalle histórico se consulta en este plan y los informes congelados. Se retiran caches regenerables y recetas duplicadas de la portada; se conservan corpus, etiquetas originales, devoluciones y resultados necesarios para procedencia/reproducción. Los blancos obsoletos ya fueron eliminados en la limpieza inicial.

Gestor 40: instalación `.venv` en el PC destino (Python 3.11 recomendado), requisitos CPU separados de los GPU, preparación que verifica si ya existe, pruebas limitadas a módulos seguros y delegación a 38/39 sin cambiar el protocolo. Entrenamiento con respaldo por grupo, sin prometer recuperación de optimizador a mitad de fold. Exportación ZIP por inventario explícito, sin `.git`, entornos, pesos, caches o archivos personales no declarados; sí datos originales, referencia v2 y paquete listo. El ZIP lleva manifiesto de bytes verificable con biblioteca estándar y no requiere Git en el PC destino.

No se cierran/fusionan PR automáticamente. Descargar un ZIP desde GitHub no requiere cerrar el PR; integrar a `main` requiere Merge, no simplemente Close. La próxima sesión debe revisar qué rama/base recibe y seguir las restricciones del nuevo entorno, no cambiar a la rama anterior de manera automática.

La organización no aporta métricas nuevas ni ejecución BETO: pesos, prueba real GPU y comparación siguen pendientes. No más anotaciones, cambios de referencias/folds/A, datasets externos, refit final o scoring global. Evidencia de limpieza/instalación/portabilidad y límites en `data/auditoria/entrega_portable_v1/`.

Cierre verificado de 9.20: **90 pruebas aprobadas, 0 omitidas**, instalación limpia desde ZIP sin Git en ruta con espacios, paquete idéntico y reexportación comprobada; **330 archivos anteriores protegidos intactos**. Retirados 29 caches (631.950 bytes). Solo Linux/Python 3.11, sin encoder/GPU ni ejecución Windows/macOS/Colab.
