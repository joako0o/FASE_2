# PLAN — Proyecto D&H: Score Hawkish/Dovish por Intervención
**Actas de las Reuniones de Política Monetaria (RPM) del Banco Central de Chile, 2005–2015**

> Documento maestro de planificación. Estado: **planificación cerrada, ejecución pendiente de luz verde.**
> Última actualización: 2026-09-15.

---

## 1. Objetivo

Construir un **score de postura de política monetaria (hawkish ↔ dovish) por intervención** sobre las 9.725 intervenciones del corpus, y a partir de él:

1. **Serie de tiempo agregada** del stance del Consejo (mensual, 2005–2015), validada contra la decisión real de TPM.
2. **Perfiles por actor**: trayectoria de postura, especialista temático (radar estilo FIFA), vocabulario distintivo, matriz de votos e índice de disenso.

Estos productos serán insumo de un *scrollytelling* y un paper (fuera del alcance de este plan por ahora).

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
Todos los IDs siguen el patrón `RPM-AAAA-MM-DD:N:M` → la reunión es la unidad natural de agrupación.

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
| 5 | Entregables | Score por intervención → serie temporal + data de actores (§7) |
| 6 | Operación | Etiquetado en este chat por rondas; **todo documentado + PR constante a GitHub** |

### Clases propuestas (pendiente de validación en el codebook)

| Clase | Definición operativa |
|---|---|
| `hawkish` | Postura de política monetaria más contractiva: subir TPM o sesgo de alza; preocupación dominante por inflación/expectativas |
| `dovish` | Postura más expansiva: bajar TPM o sesgo de baja; preocupación dominante por actividad/empleo |
| `neutral` | Diagnóstico descriptivo sin inclinación, o argumentos en ambos sentidos balanceados |
| `irrelevante` | Logística de sesión, formalidades, contenido no evaluable (propuesta sujeta a veto del investigador) |

## 4. Protocolo de etiquetado

### 4.1 Flujo (IA-primero con validación humana final)

```
Codebook v1 → Piloto IA (300) → revisión investigador → rondas IA (curva de aprendizaje)
   → Gold humano (300 a ciegas) → Cohen's κ humano–IA
   → fine-tune final → scoring de las 9.725
```

1. **Codebook versionado** (`docs/codebook_vX.md`): definiciones + ≥3 ejemplos reales por clase + casos borde (escenario_internacional ≠ stance; ministros; textos institucionales; flags `Cotejar_PDF`).
2. **Piloto (n=300)**: muestra estratificada año × tópico × actor (seed fija). Cada etiqueta incluye `label + confianza + frase_justificante textual`. El investigador revisa una submuestra → ajuste del rubro (codebook v2).
3. **Rondas de escalado** (~150–300 por ronda): tras cada ronda se entrena un modelo rápido y se registra Macro-F1 → **curva de aprendizaje**; se detiene cuando la mejora marginal se estanque (justificación empírica del n final, defendible en tesis).
4. **Test-retest**: 30 IDs fijos re-etiquetados en cada ronda → consistencia interna (meta ≥ 90% de coincidencia).
5. **Gold humano (n=300)**: el investigador etiqueta **a ciegas** (sin ver etiquetas de la IA) una muestra estratificada. Si κ < 0.7 → revisión del rubro y re-etiquetado; meta κ ≥ 0.7 (ideal ≥ 0.8).

### 4.2 Formato de registro (append-only)

`data/etiquetas/etiquetas_ronda_XX.csv` con columnas:

`ID_Intervencion, etiqueta, confianza, frase_justificante, ronda, version_codebook, fecha, etiquetador`

Las frases justificantes quedan como activo de explicabilidad (y material para el scrollytelling).

## 5. Modelamiento

| Componente | Diseño |
|---|---|
| Modelo base | `dccuchile/bert-base-spanish-wwm-cased` (BETO); alternativas: `PlanTL-GOB-ES/roberta-base-bne`, `xlm-roberta-base` |
| Split | **Por reunión completa** (group split 70/15/15, estratificado por año) para evitar leakage entre intervenciones de la misma sesión; holdout temporal opcional (test = 2013–2015) como robustez |
| Entrenamiento | Fine-tune sobre etiquetas IA aceptadas; validación contra gold humano |
| Métricas | Macro-F1 (principal), accuracy, matriz de confusión, κ humano-modelo |
| **Score** | `s_i = P(hawkish) − P(dovish) ∈ [−1, +1]` por intervención (clasificador calibrado) |
| Agregación | Media/mediana por reunión → serie mensual; ponderadores (largo de texto, cargo) como análisis de sensibilidad |
| Benchmarks opcionales | LLM zero-shot en submuestra; modelo WCB-Chile sobre texto traducido (referencia externa, con cautelas de dominio) |

## 6. Validación externa

- **TPM real** mensual 2005–2015: `mindicador.cl/api/tpm` (gratuita, sin key) como fuente principal; API oficial BDE del BCCh como respaldo.
- Prueba de utilidad económica: correlación del índice de stance agregado con **ΔTPM** contemporáneo y lead/lag; eventos foco: crisis 2008–09 (bajas agresivas), normalización 2010–11, ciclo de bajas 2013–14.
- **Matriz de votos extraída del propio texto** (§7) como ground truth de comportamiento por actor.

## 7. Entregables de data por actor

| Archivo | Contenido | Uso previsto |
|---|---|---|
| `actores/perfil_topico_actor.csv` | Distribución normalizada de tópicos por actor (ejes de radar: internacional, financiero, inflación/precios, actividad/demanda, laboral, fiscal, decisión-TPM) | **Radar FIFA** por actor |
| `actores/vocabulario_distintivo_actor.csv` | Palabras más distintivas por actor (log-odds con prior Dirichlet informativa, Monroe et al. 2008) | Etiquetas de ejes, nube/lista de palabras |
| `actores/scores_intervencion.csv` | `s_i` + probabilidades por intervención con actor | Series individuales |
| `actores/matriz_votos.csv` | Por reunión × actor con voto: opción declarada (sube/mantiene/baja + magnitud), fuente textual, confianza. Extraído de intervenciones `decision_tpm`/`opciones_tpm` y del párrafo de acuerdo | Comportamiento de voto; **GT de validación** |
| `actores/disenso_actor.csv` | Distancia entre stance del actor y consenso de la reunión | Ranking de disenso, coaliciones |
| `actores/actores_metadata.csv` | Inicio/fin de mandato, nominado por, máximo cargo, background (academia/público/privado), educación | Perfiles, controles |
| `actores/tpm_real.csv` | TPM efectiva por reunión | Validación externa |

**Análisis adicionales propuestos (opcionales):** coaliciones (quién coincide con quién → red), pivotes en turning points (quién gira primero de postura), stance estructural vs coyuntural por actor, volumen/timing de partición (apertura vs decisión), % forward-looking e incertidumbre por actor.

## 8. Flujo de trabajo en GitHub

- Rama de trabajo: `arena/01a0a3a0-fase-2` (PRs frecuentes hacia `main`).
- **Un PR por unidad de progreso**: docs, codebook, cada ronda de etiquetado, cada entregable de actores.
- Datos etiquetados en CSV append-only bajo `data/etiquetas/`; codebook y decisiones bajo `docs/`.
- Muestras con seed fija y registrada (reproducibilidad).
- No commitear artefactos grandes (checkpoints de modelos van fuera de git o con LFS si hiciera falta).

## 9. Roadmap

- [x] **Fase 0** — Planificación y documentación inicial (este archivo)
- [ ] **Fase 1** — Codebook v1 (propuesta IA → revisión investigador)
- [ ] **Fase 2** — Preparación: EDA reproducible, limpieza de flags `Cotejar_PDF`, muestra piloto estratificada (n=300) con seed
- [ ] **Fase 3** — Piloto de etiquetado IA + revisión → codebook v2
- [ ] **Fase 4** — Rondas de escalado + curva de aprendizaje (PR por ronda)
- [ ] **Fase 5** — Gold humano a ciegas (n=300) + Cohen's κ
- [ ] **Fase 6** — Fine-tune BETO + evaluación final vs gold
- [ ] **Fase 7** — Scoring de las 9.725 + serie temporal + validación vs ΔTPM
- [ ] **Fase 8** — Entregables de actores (radar, vocab, votos, disenso, metadata)
- [ ] **Fase 9 (fuera de alcance por ahora)** — Scrollytelling + paper

## 10. Referencias

1. Shah, A. et al. (2025). *Words That Unite The World: A Unified Framework for Deciphering Central Bank Communications Globally*. NeurIPS 2025 (Datasets & Benchmarks). Repo: `gtfintechlab/WorldCentralBanks`; dataset Chile: `gtfintechlab/central_bank_of_chile` (1.000 frases, 2018–2024, EN).
2. Shah, A., Paturi, S., Chava, S. (2023). *Trillion Dollar Words: A New Financial Dataset, Task & Market Analysis*. ACL 2023. Repo: `gtfintechlab/FOMC-Dataset` (FOMC-RoBERTa).
3. *Deciphering Fedspeak: Quantifying Dissent Among Hawks and Doves*. Findings of EMNLP 2023 (GPT-4 como clasificador).
4. Monroe, B., Colaresi, M., Quinn, K. (2008). *Fightin' Words: Lexical Feature Selection and Evaluation for Identifying the Content of Political Conflict*. Political Analysis. (vocabulario distintivo).
5. Acuerdo BCCh N°2763-01-260115 (2026): difusión de actas con rezago de 10 años; esquema de publicación vigente.
