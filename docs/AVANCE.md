# AVANCE — Proyecto D&H

> Memoria del proyecto entre sesiones. Actualización obligatoria al cierre de cada sesión de trabajo (REGLAS.md, regla de cierre).
> Última actualización: 2026-09-15 (sesión 4).

---

## Estado actual

- **Fase vigente**: Fase 4 (Piloto de etiquetado) EN CURSO. Ronda 1 = tanda 1 de 4 completada y validada (110/300 intervenciones).
- **PR abierta**: [#1](https://github.com/joako0o/FASE_2/pull/1) — acumula todos los commits del proyecto.

## Última sesión: 2026-09-15 (sesión 4)

### Completado en esta sesión

1. **Regla operativa de tandas por presupuesto de palabras** (acuerdo con el investigador): el etiquetado ya no se mide en número fijo de intervenciones por turno, sino en presupuesto de palabras (20.000 por tanda; escalable a 30–40 mil si el flujo va bien). Implementada en `scripts/04_tandas_por_presupuesto.py` + parámetro `PRESUPUESTO_PALABRAS_TANDA` en `config.py`. Salida: `data/muestras/piloto_300_tandas.csv` (orden cronológico dentro de cada tanda) y `tandas_resumen.csv`: T1 = 110 intervenciones / 19.935 palabras (2005–2009), T2 = 88 / 19.490 (2009–2011), T3 = 85 / 19.858 (2011–2015), T4 = 17 / 4.372 (2015, remanente).
2. **Ronda 1 de etiquetado ejecutada** (tanda 1 completa): `data/etiquetas/etiquetas_piloto_r1.csv` con 110 registros (metodo=`ia_ronda`, ronda=`piloto_t1_r1`, codebook v2). Distribución: 98 neutral, 6 hawkish, 6 dovish; 24 registros con `es_relevante=0` (fórmulas de ofrecimiento de palabra, reanudaciones, acuerdos formales, encabezados); confianza 87 alta / 23 media.
3. **`scripts/05_validar_etiquetas.py`**: validador paramétrico obligatorio para toda corrida de etiquetado (columnas del formato largo, dominios, coherencia prob/score/argmax, nota obligatoria si flag 0, frase obligatoria si flag 1, cobertura contra L0, no-nulidad estructural). La corrida 1 lo supera íntegro.
4. **Descarga macro derivada al investigador**: el sandbox no tiene salida TLS (verificado); `scripts/02_capa_l2_macro_y_actores.py` está listo para ejecutarse en cualquier máquina con internet normal y deposita los JSONs en `data/L2/raw/` automáticamente.

### Hallazgos analíticos de la ronda 1 (preliminar, muestra piloto)

- Casi todo el habla de actas 2005–2009 es descriptiva o procedural (diagnóstico ≠ postura, regla R2).
- El contenido postural real se concentra en **propuestas de votación** (De Ramón, Desormeaux) y en la **justificación de la decisión** (comunicado institucional, regla R6).
- Hawkers tanda 1 (6): Valdés 2005-02-10:121 (staff con recomendación explícita, caso R5-excepción), Desormeaux x2, De Ramón x2 (propuestas +50 pb), comunicado 2008-11-06 (alza a 7,75 %).
- Dovish tanda 1 (6): Marshall 2006-09-07:873 (voto a mantención + "TPM cerca de su nivel neutral", confianza media — caso límite registrado), De Ramón 2007-09-06:1049 (recorte −25), Schmidt-Hebbel 2008-02-07:1672 ("menos restrictiva"), Velasco 2008-10-23:2167 ("preferiría recorte"), Desormeaux 2009-01-15:2377 (adhesión −250), Consejo 2009-04-16:2500 (−50 pb).
- Caso límite que conviene revisar al cierre del piloto (posible v3 o nota interpretativa): votos silenciosos denominados "mantención" cuando el sesgo era claramente restrictivo o expansivo.

### Próximos pasos (en orden)

1. **Tanda 2** (88 intervenciones, 19.490 palabras, 2009–2011): leer y etiquetar en esta sesión si hay margen, si no, en la siguiente.
2. Tandas 3 y 4 para completar el piloto (300 intervenciones).
3. Al cierre del piloto: revisión de casos límite + decisiones de codebook v3 (si aplica) + test-retest 30 (control ≥90 % de estabilidad).
4. Infraestructura pendiente (no bloqueante): ejecutar `scripts/02...py` con internet; curado restante de `actores_metadata.csv` (manifiesto `data/L2/pendientes_manifest.csv`).

### Bloqueos y pendientes

- Sin bloqueos para etiquetar. Macro y metadata: pendientes no bloqueantes (manifiesto).

---

## Sesiones anteriores

### 2026-09-15 (sesión 3)

#### Completado

1. **Codebook v2 aprobado y congelado** por el investigador (`docs/codebook_v2.md`): 3 clases de postura + flag `es_relevante` + `nota`.
2. **Fase 3 ejecutada** (pipeline reproducible, `scripts/`, numerados en orden de ejecución):
   - `config.py`: parámetros centrales (semilla maestra 20260915, rutas, años, tamaños).
   - `01_excel_a_capa_l0.py`: Excel → `data/L0/corpus.csv` (9.725 filas, 132 reuniones, `meeting_id`, `orden_habla`, flags de cotejo) + 3 tablas EDA. Validado con asserts.
   - `02_capa_l2_macro_y_actores.py`: descarga macro tolerante a fallos + metadata de actores. En sandbox las 44 descargas fallaron (TLS) y quedaron registradas en `data/L2/pendientes_manifest.csv`; `actores_metadata.csv` quedó generada (55 actores: derivados del corpus + 3 mandatos curados y verificados con fuente: De Gregorio, Marfán, Desormeaux).
   - `03_muestra_piloto.py`: `data/muestras/piloto_300.csv` (estratificada año × grupo de actor; 148 votantes, 101 staff, 26 consejo-entidad, 25 ministros), `test_retest_30.csv` y `piloto_300_estratos.csv`. Excluidos 51 registros con texto dañado (R8).
3. `requirements.txt` y `.gitignore` creados.

#### En curso

- Nada bloqueante: el piloto puede etiquetarse ya.

#### Próximos pasos (en orden)

1. **Fase 4 — Ronda 1 del piloto**: etiquetar intervenciones de `data/muestras/piloto_300.csv` según codebook v2, en tandas. Salida: `data/etiquetas/etiquetas_piloto_r1.csv` (formato PLAN §4.2, metodo=`ia_ronda`).
2. Al terminar y revisar el piloto: codebook v3 si hace falta + rondas de escalado con curva de aprendizaje.
3. Pendiente de infraestructura (no bloquea el piloto):
   - Descarga macro: ejecutar `scripts/02...py` en una máquina con internet normal, o bootstrap progresivo de JSONs con el fetcher del agente (TPM prioritaria).
   - Curado restante de `actores_metadata.csv` (ver manifiesto).
4. Merge de PR #1 por el investigador cuando esté conforme.

#### Bloqueos y pendientes

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
| 12 | Las tandas de etiquetado se definen por presupuesto de palabras (20.000), no por número fijo de intervenciones |

## Cómo retomar el trabajo en una sesión nueva

1. Leer en este orden: `PLAN.md` → `docs/REGLAS.md` → este archivo → `docs/codebook_v2.md`.
2. Verificar estar en la rama `arena/01a0a3a0-fase-2` y trabajar solo sobre ella.
3. Corpus: `consolidado_D&H.xlsx` (raíz) → regenerar L0 con `python scripts/01_excel_a_capa_l0.py`.
4. Continuar desde "Próximos pasos" de la última entrada del log.

## Log de sesiones

- **2026-09-15 (sesión 1)**: planificación inicial a v4; verificación de fuentes externas (WCB, calendario BCCh, APIs de macro); gobernanza del repo (PLAN, REGLAS, AVANCE); codebook v1; PR #1 abierta.
- **2026-09-15 (sesión 2)**: decisión de 3 clases + flag `es_relevante`; investigación WCB/FOMC; PDFs eliminados del esquema; codebook v2; PLAN v5.
- **2026-09-15 (sesión 3)**: codebook v2 aprobado; Fase 3 ejecutada (scripts 01–03, L0, muestra piloto 300, metadata parcial, manifiesto de pendientes).
- **2026-09-15 (sesión 4)**: regla de tandas por presupuesto de palabras (script 04); ronda 1 del piloto etiquetada y validada (tanda 1 de 4, 110 intervenciones, `etiquetas_piloto_r1.csv`); validador obligatorio de corridas (script 05).
