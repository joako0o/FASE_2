# AVANCE — Proyecto D&H

> Memoria del proyecto entre sesiones. Actualización obligatoria al cierre de cada sesión de trabajo (REGLAS.md, regla de cierre).
> Última actualización: 2026-09-15 (sesión 2).

---

## Estado actual

- **Fase vigente**: Fase 2 (Codebook). Codebook v2 emitido; pendiente de revisión final del investigador.
- **PR abierta**: [#1](https://github.com/joako0o/FASE_2/pull/1) — acumula todos los commits de planificación y documentación.

## Última sesión: 2026-09-15 (sesión 2)

### Completado

1. Investigación sobre la clase `irrelevante`: WCB la usa como 4ª clase porque etiqueta frases crudas scrapeadas; FOMC (Shah et al. 2023, ACL) usa solo 3 clases y su `neutral` absorbe el contenido no relacionado. Conclusión aplicada: postura en 3 clases + relevancia como dimensión ortogonal.
2. Decisión implementada: **3 clases de postura (hawkish/dovish/neutral) + flag binario `es_relevante` + `nota` obligatoria cuando vale 0**.
3. Verificación del corpus: no existe actor "administrativo"; el contenido formal está concentrado en `Consejo del Banco Central de Chile` × `apertura_cierre` (137 registros) y Presidente × `apertura_cierre` (67).
4. PDFs fuente: existen pero no se integran al flujo (el Excel ya contiene el contenido íntegro) → campos `nombre_pdf`/`num_pagina` eliminados del esquema; linaje a nivel `meeting_id`.
5. `docs/codebook_v2.md` emitido (sustituye a v1 como vigente; v1 conservada como registro histórico).
6. PLAN.md actualizado a v5; README apunta al codebook v2.

### En curso

- Esperando revisión final del investigador sobre `docs/codebook_v2.md`.

### Próximos pasos (en orden)

1. Investigador revisa `docs/codebook_v2.md`. Foco: §2 (definiciones y flag), §3 (R1–R10), §4 (ejemplos semilla).
2. Con la aprobación, el codebook vigente queda congelado para el piloto.
3. Fase 3 — Preparación:
   - `scripts/01`: paso del Excel a capa L0 (CSV inmutable con `intervencion_id` y `meeting_id`) + EDA reproducible.
   - `scripts/02`: capa L2 — macro completa (TPM, IPC, desempleo, IMACEC, IPEC, situación país a 1 año, EEE inflación a 1 año) y metadata de actores (mandatos, nominación, background).
   - `scripts/03`: muestra piloto estratificada n=300 (año × tópico × actor), seed fija registrada.
4. Fase 4 — Piloto de etiquetado IA sobre la muestra, según codebook vigente.

### Bloqueos y pendientes

- PR #1 pendiente de merge por el investigador. (Tras el merge, el trabajo continúa en PRs sucesivas.)

## Decisiones clave (resumen; fuente completa: PLAN.md §3 y docs/codebook_v2.md)

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
| 9 | Postura en 3 clases; relevancia como flag ortogonal `es_relevante` + `nota` |
| 10 | PDFs fuera del flujo; linaje documental a nivel `meeting_id` |

## Cómo retomar el trabajo en una sesión nueva

1. Leer en este orden: `PLAN.md` → `docs/REGLAS.md` → este archivo → codebook vigente en `docs/` (actualmente `codebook_v2.md`).
2. Verificar estar en la rama `arena/01a0a3a0-fase-2` y trabajar solo sobre ella.
3. El corpus es `consolidado_D&H.xlsx` (raíz del repo). Capa L0 inmutable: nunca editar a mano.
4. Continuar desde "Próximos pasos" de la última entrada del log.

## Log de sesiones

- **2026-09-15 (sesión 1)**: planificación inicial a v4; verificación de fuentes externas (WCB, calendario BCCh, APIs de macro); gobernanza del repo (PLAN, REGLAS, AVANCE); codebook v1 con ejemplos reales; PR #1 abierta.
- **2026-09-15 (sesión 2)**: decisión de 3 clases + flag `es_relevante`; investigación WCB/FOMC; PDFs eliminados del esquema; codebook v2; PLAN v5.
