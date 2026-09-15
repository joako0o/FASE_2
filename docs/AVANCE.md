# AVANCE — Proyecto D&H

> Memoria del proyecto entre sesiones. Actualización obligatoria al cierre de cada sesión de trabajo (REGLAS.md, regla de cierre).
> Última actualización: 2026-09-15 (sesión 1).

---

## Estado actual

- **Fase vigente**: Fase 2 (Codebook). Codebook v1 emitido; pendiente de revisión por el investigador.
- **PR abierta**: [#1](https://github.com/joako0o/FASE_2/pull/1) — contiene PLAN.md, docs/REGLAS.md, docs/AVANCE.md, docs/codebook_v1.md y README.

## Última sesión: 2026-09-15 (sesión 1)

### Completado

1. Planificación completa del proyecto (PLAN.md, versiones 1 a 4).
2. Verificación del contexto documental: WCB usa Minutas 2018–2024 en inglés; el corpus propio (Actas 2005–2015, español, intervenciones nombradas) es único y complementario.
3. Documentos de gobernanza: `docs/REGLAS.md` y `docs/AVANCE.md`.
4. `docs/codebook_v1.md`: definiciones operativas, reglas de decisión R1–R10, ejemplos semilla reales del corpus, formato de anotación, catálogo de casos borde y protocolo de control de calidad.
5. Decisiones de diseño registradas (PLAN.md §3) y arquitectura de datos por capas (PLAN.md §5) con set completo de variables macro.

### En curso

- Esperando revisión del investigador sobre `docs/codebook_v1.md` para producir la v2.

### Próximos pasos (en orden)

1. Investigador revisa `docs/codebook_v1.md`. Foco: §2 (definiciones), §3 (reglas R1–R10), §4 (ejemplos semilla) y veto o aceptación de la clase `irrelevante`.
2. Ajustar a codebook v2 con los cambios acordados.
3. Fase 3 — Preparación:
   - `scripts/01`: paso del Excel a capa L0 (CSV inmutable con `intervencion_id` y `meeting_id`) + EDA reproducible.
   - `scripts/02`: capa L2 — macro completa (TPM, IPC, desempleo, IMACEC, IPEC, situación país a 1 año, EEE inflación a 1 año) y metadata de actores (mandatos, nominación, background).
   - `scripts/03`: muestra piloto estratificada n=300 (año × tópico × actor), seed fija registrada.
4. Fase 4 — Piloto de etiquetado IA sobre la muestra, según codebook vigente.

### Bloqueos y pendientes

- PDFs fuente de las actas: sin resolver (campos `nombre_pdf`/`num_pagina` del esquema). Requiere respuesta del investigador.
- PR #1 pendiente de merge por el investigador.

## Decisiones clave (resumen; fuente completa: PLAN.md §3)

| # | Decisión |
|---|---|
| 1 | Unidad de análisis: intervención completa |
| 2 | Universo de etiquetado: las 9.725 intervenciones |
| 3 | Flujo: IA etiqueta en rondas; investigador valida a ciegas al final (gold n=300, Cohen's κ) |
| 4 | Modelo: fine-tune en español (BETO/RoBERTa-es), split por reunión |
| 5 | Entregables: score por intervención, serie temporal, perfiles de actores, evolución semántica |
| 6 | Operación: rondas en este chat; cada unidad de progreso cierra con PR y actualización de este documento |
| 7 | Votos: solo explícitos, extracción diferida a Fase 10, no alimenta el modelo |
| 8 | Estilo: lenguaje profesional, sin emojis en el repositorio |

## Cómo retomar el trabajo en una sesión nueva

1. Leer en este orden: `PLAN.md` → `docs/REGLAS.md` → este archivo → codebook vigente en `docs/`.
2. Verificar estar en la rama `arena/01a0a3a0-fase-2` y trabajar solo sobre ella.
3. El corpus es `consolidado_D&H.xlsx` (raíz del repo). Capa L0 inmutable: nunca editar a mano.
4. Continuar desde "Próximos pasos" de la última entrada del log.

## Log de sesiones

- **2026-09-15 (sesión 1)**: planificación inicial a v4; verificación de fuentes externas (WCB, calendario BCCh, APIs de macro); gobernanza del repo (PLAN, REGLAS, AVANCE); codebook v1 con ejemplos reales; PR #1 abierta.
