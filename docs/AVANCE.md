# AVANCE — Proyecto D&H

> Memoria del proyecto entre sesiones. Actualización obligatoria al cierre de cada sesión de trabajo (REGLAS.md, regla de cierre).
> Última actualización: 2026-09-15 (sesión 3).

---

## Estado actual

- **Fase vigente**: Fase 4 (Piloto de etiquetado) lista para comenzar. Codebook v2 aprobado y congelado; muestra piloto generada.
- **PR abierta**: [#1](https://github.com/joako0o/FASE_2/pull/1) — acumula todos los commits del proyecto.

## Última sesión: 2026-09-15 (sesión 3)

### Completado

1. **Codebook v2 aprobado y congelado** por el investigador (`docs/codebook_v2.md`): 3 clases de postura + flag `es_relevante` + `nota`.
2. **Fase 3 ejecutada** (pipeline reproducible, `scripts/`, numerados en orden de ejecución):
   - `config.py`: parámetros centrales (semilla maestra 20260915, rutas, años, tamaños).
   - `01_excel_a_capa_l0.py`: Excel → `data/L0/corpus.csv` (9.725 filas, 132 reuniones, `meeting_id`, `orden_habla`, flags de cotejo) + 3 tablas EDA. Validado con asserts.
   - `02_capa_l2_macro_y_actores.py`: descarga macro tolerante a fallos + metadata de actores. En sandbox las 44 descargas fallaron (TLS) y quedaron registradas en `data/L2/pendientes_manifest.csv`; `actores_metadata.csv` quedó generada (55 actores: derivados del corpus + 3 mandatos curados y verificados con fuente: De Gregorio, Marfán, Desormeaux).
   - `03_muestra_piloto.py`: `data/muestras/piloto_300.csv` (estratificada año × grupo de actor; 148 votantes, 101 staff, 26 consejo-entidad, 25 ministros), `test_retest_30.csv` y `piloto_300_estratos.csv`. Excluidos 51 registros con texto dañado (R8).
3. `requirements.txt` y `.gitignore` creados.

### En curso

- Nada bloqueante: el piloto puede etiquetarse ya.

### Próximos pasos (en orden)

1. **Fase 4 — Ronda 1 del piloto**: etiquetar intervenciones de `data/muestras/piloto_300.csv` según codebook v2, en tandas. Salida: `data/etiquetas/etiquetas_piloto_r1.csv` (formato PLAN §4.2, metodo=`ia_ronda`).
2. Al terminar y revisar el piloto: codebook v3 si hace falta + rondas de escalado con curva de aprendizaje.
3. Pendiente de infraestructura (no bloquea el piloto):
   - Descarga macro: ejecutar `scripts/02...py` en una máquina con internet normal, o bootstrap progresivo de JSONs con el fetcher del agente (TPM prioritaria).
   - Curado restante de `actores_metadata.csv` (ver manifiesto).
4. Merge de PR #1 por el investigador cuando esté conforme.

### Bloqueos y pendientes

- Ninguno para etiquetar. Macro y metadata completa: pendientes no bloqueantes (manifiesto en `data/L2/`).

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
| 11 | Semilla maestra única: 20260915 (toda aleatoriedad se deriva de ella) |

## Cómo retomar el trabajo en una sesión nueva

1. Leer en este orden: `PLAN.md` → `docs/REGLAS.md` → este archivo → `docs/codebook_v2.md`.
2. Verificar estar en la rama `arena/01a0a3a0-fase-2` y trabajar solo sobre ella.
3. Corpus: `consolidado_D&H.xlsx` (raíz) → regenerar L0 con `python scripts/01_excel_a_capa_l0.py`.
4. Continuar desde "Próximos pasos" de la última entrada del log.

## Log de sesiones

- **2026-09-15 (sesión 1)**: planificación inicial a v4; verificación de fuentes externas (WCB, calendario BCCh, APIs de macro); gobernanza del repo (PLAN, REGLAS, AVANCE); codebook v1; PR #1 abierta.
- **2026-09-15 (sesión 2)**: decisión de 3 clases + flag `es_relevante`; investigación WCB/FOMC; PDFs eliminados del esquema; codebook v2; PLAN v5.
- **2026-09-15 (sesión 3)**: codebook v2 aprobado; Fase 3 ejecutada (scripts 01–03, L0, muestra piloto 300, metadata parcial, manifiesto de pendientes).
