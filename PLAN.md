# PLAN — Proyecto D&H: Score Hawkish/Dovish por Intervención
**Actas de las Reuniones de Política Monetaria (RPM) del Banco Central de Chile, 2005–2015**

> Documento maestro de planificación. Estado: **planificación v2, ejecución pendiente de luz verde.**
> Última actualización: 2026-09-15 (v5: postura en 3 clases H/D/N + flag binario `es_relevante` con `nota`; `nombre_pdf`/`num_pagina` eliminados del esquema (los PDFs no se integran al flujo; el Excel ya contiene el contenido íntegro); codebook v2 emitido).

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

## 9. Roadmap

- [x] **Fase 0 histórica** — *(previa al repo)* consolidación del corpus y esquemas v0a/v0b
- [x] **Fase 1** — Planificación y documentación inicial (este archivo, v2)
- [x] **Fase 2** — Codebook v2 APROBADO y congelado (2026-09-15, `docs/codebook_v2.md`)
- [ ] **Fase 3** — Preparación: scripts 01–03 creados y ejecutados (L0 + muestra piloto n=300 con seed 20260915 listos). Pendiente: descarga macro (sandbox sin salida TLS; bootstrap progresivo con fetcher o ejecución local) y curado restante de metadata de actores
- [ ] **Fase 4** — Piloto de etiquetado IA + revisión → codebook v2
- [ ] **Fase 5** — Rondas de escalado **acotado a training set ~1.000** (cronológico 2005 + estratificado por fases 2006–2015; decisión 8 §3) + curva de aprendizaje (PR por ronda)
- [ ] **Fase 6** — Gold humano a ciegas (n=300) + Cohen's κ
- [ ] **Fase 7** — Fine-tune BETO + evaluación final vs gold
- [ ] **Fase 8** — Scoring de las 9.725 + serie temporal + validación vs ΔTPM
- [ ] **Fase 9** — Entregables de actores (radar, vocab, convergencia, afinidad, disenso) + evolución semántica + comparación humano-máquina de tópicos/keywords
- [ ] **Fase 10** — Extracción de **votos explícitos** por actor y de la decisión del Consejo en cada acta (diferida al final: no se usa en el modelo)
- [ ] **Fase 11 (fuera de alcance por ahora)** — Scrollytelling + paper

## 10. Referencias

1. Shah, A. et al. (2025). *Words That Unite The World: A Unified Framework for Deciphering Central Bank Communications Globally*. NeurIPS 2025 (Datasets & Benchmarks). Repo: `gtfintechlab/WorldCentralBanks`; dataset Chile: `gtfintechlab/central_bank_of_chile` (1.000 frases, 2018–2024, EN).
2. Shah, A., Paturi, S., Chava, S. (2023). *Trillion Dollar Words: A New Financial Dataset, Task & Market Analysis*. ACL 2023. Repo: `gtfintechlab/FOMC-Dataset` (FOMC-RoBERTa).
3. *Deciphering Fedspeak: Quantifying Dissent Among Hawks and Doves*. Findings of EMNLP 2023 (GPT-4 como clasificador).
4. Monroe, B., Colaresi, M., Quinn, K. (2008). *Fightin' Words: Lexical Feature Selection and Evaluation for Identifying the Content of Political Conflict*. Political Analysis. (vocabulario distintivo).
5. Acuerdo BCCh N°2763-01-260115 (2026): difusión de actas con rezago de 10 años; esquema de publicación vigente.
