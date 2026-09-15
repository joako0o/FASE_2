# AVANCE — Proyecto D&H

> Memoria del proyecto entre sesiones. Actualización obligatoria al cierre de cada sesión de trabajo (REGLAS.md, regla de cierre).
> Última actualización: 2026-09-15 (sesión 6).

---

## Estado actual

- **Fase vigente**: Fase 4 (Piloto de etiquetado) EN CURSO. Rondas 1, 2 y 3 = tandas 1 a 3 de 4 completadas y validadas (283/300 intervenciones). Queda la tanda 4 (17 intervenciones).
- **PR abierta**: [#1](https://github.com/joako0o/FASE_2/pull/1) — acumula todos los commits del proyecto.

## Última sesión: 2026-09-15 (sesión 6)

### Completado en esta sesión

1. **Ronda 3 del piloto etiquetada y validada** (tanda 3, 85 intervenciones, 19.858 palabras, 2011-12 a 2015-05, 37 reuniones): `data/etiquetas/etiquetas_piloto_r3.csv`. Distribución: 77 neutral, 0 hawkish, 8 dovish; 29 registros `es_relevante=0`; confianza 75 alta / 10 media. Cobertura exacta contra la tanda 3 verificada.
   - Dovish (8): Larraín 2013-05-16 ("condiciones para comenzar un nuevo ciclo de reducción de la TPM"), Marshall 2013-06-13 (mantención con sesgo a la baja: "un recorte facilitará el necesario ajuste"), comunicado 2013-07-11 ("podría requerir de ajustes en la TPM en los próximos meses", confianza media — caso límite del eufemismo "ajustes"), comunicado 2014-01-16 ("podría ser necesario agregar un mayor estímulo monetario", sesgo explícito), Claro 2014-02-18 (voto -25 pb a 4,25 %), Arenas 2014-06-12 ("seguir aumentando el estímulo monetario... evitar costos cíclicos innecesarios"), Vergara 2014-08-14 (constancia del recorte unánime a 3,5 %), Arenas 2015-03-19 ("es fundamental que la política monetaria continúe contribuyendo a esta recuperación", confianza media — mantención avalada con énfasis acomodaticio).
   - Hawkish: ninguno en esta tanda (rasgo de época: pausa de normalización y ciclo de recortes 2012-2015).
2. **Incidencia de generación**: atajo en el generador temporal (filas flag-0 heredaron es_relevante=1); el validador 05 lo detectó inmediatamente (frase obligatoria si flag 1) y se corrigió. Refuerza el valor del control automático.
3. **Cobertura y verbatim**: los 85 registros pasan íntegros el validador endurecido (dominios, coherencia prob/score/argmax, nota obligatoria si flag 0, frase verbatim de L0, largo ≤300).

### Hallazgos analíticos de la ronda 3

- La tanda cubre la pausa larga de 5 % (2012), la apertura al sesgo expansivo (2013) y el ciclo de recortes hasta 3 % (oct-2013 a mar-2014). **El piloto completa así el arco 2005-2015**: alzas 2005-2008, colapso y piso 2009-2010, normalización 2010-2011, recortes 2013-2014.
- Casos límite acumulados para revisión al cierre del piloto: (a) comunicados con el eufemismo "ajustes" (5699:3, dovish media); (b) preocupación por inflación BAJA sin implicancia explícita de postura (Vergara 2013-01-17, neutral media, probs 0.20 dovish); (c) aval de mantención con retórica acomodaticia sin pedir cambios (Arenas 2015-03-19, dovish media); (d) la convención ya establecida "mantención + sesgo explícito se etiqueta según el sesgo".
- Confirmado una vez más: el 80 % del habla es diagnóstico o logística; la postura se concentra en votos, sesgos comunicacionales y recomendaciones (staff/ministerio).

### Próximos pasos (en orden)

1. **Tanda 4** (17 intervenciones, 4.372 palabras, 2015): leer, etiquetar, validar → **piloto 300/300**.
2. Al cierre del piloto: revisión de casos límite (lista acumulada rondas 1-3) + decisiones de codebook v3 si aplica + test-retest 30 (≥90 % de estabilidad).
3. Infraestructura pendiente (no bloqueante): ejecutar `scripts/02...py` con internet (macro) + curado restante de `actores_metadata.csv`.

### Bloqueos y pendientes

- Sin bloqueos para etiquetar. Macro y metadata: pendientes no bloqueantes (manifiesto `data/L2/pendientes_manifest.csv`).

---

## Sesiones anteriores

### 2026-09-15 (sesión 5)

#### Completado en esta sesión

1. **Ronda 2 del piloto etiquetada y validada** (tanda 2, 88 intervenciones, 19.490 palabras, 2009-07 a 2011-12, 28 reuniones): `data/etiquetas/etiquetas_piloto_r2.csv`. Distribución: 78 neutral, 5 hawkish, 5 dovish; 24 registros `es_relevante=0`; confianza 79 alta / 9 media. Cobertura exacta contra la tanda 2 verificada.
   - Hawkish: Marfán 2010-05-13 (mantención con "sesgo al alza explícito"), De Gregorio 2010-05-13 ("ventana de oportunidad" para normalizar, confianza media), Vergara 2010-06-15 (voto +50 pb a 1 %), Larraín 2011-05-12 (recomendación ministerial +25 pb), Herrera 2011-06-14 (recomendación del staff +25 pb a 5,25 %, R5-excepción).
   - Dovish: Céspedes 2009-07-09 (staff: "impulso monetario adicional", TPM negativa en regla de Taylor), De Gregorio 2009-09-08 (mantención + riesgo de inflación bajo meta), Marshall 2010-01-14 (mantención + "riesgo de retirar el estímulo prematuramente"), Larraín 2011-08-18 (pausa + "quitar el sesgo restrictivo"), Claro 2011-10-13 (mantención + "próximo movimiento debiera ser a la baja").
2. **Validador (script 05) endurecido**: control de que `frase_justificante` sea cita verbatim del texto L0 (R10), con espacios en blanco normalizados en ambos lados (el corpus conserva quiebres de línea tipográficos; la exigencia palabra a palabra se mantiene) y control de largo máximo de 300 caracteres.
3. **Control de calidad retroactivo en ronda 1**: el validador endurecido detectó 23 frases de ronda 1 no verbatim (uso de elipsis "..." uniendo fragmentos y paráfrasis menores); todas fueron reemplazadas por citas textuales contiguas tras revisar cada texto original. Caso documentado: el corpus traía OCR con palabra cortada ("afecta ría") y la cita verbatim lo respetó. Ambas rondas pasan ahora íntegramente el validador endurecido.
4. **Infraestructura sandbox**: pandas se pierde al reiniciar el contenedor (venv ~/.local no persiste en el snapshot); reinstalado con `pip install --user --break-system-packages -r requirements.txt` si aparece ModuleNotFoundError.

#### Hallazgos analíticos de la ronda 2

- La tanda 2 cubre el tramo 2009-2011: salida de la crisis, normalización (primer alza junio 2010) y ciclo al alza hasta 5,25 %, luego pausa con sesgo a la baja a fines de 2011. El piloto ya contiene un ciclo completo de endurecimiento con votos explícitos.
- Confirma el patrón dominante: la postura vive en los **bloques de votación/justificación** y en las **recomendaciones ministeriales y del staff**; el resto es diagnóstico (R2).
- Patrón registrado para revisión al cierre del piloto: **mantención + sesgo comunicacional explícito se etiqueta según el sesgo** (Marfán 2010-05-13 hawkish con voto a mantener; Claro 2011-10-13 dovish con voto a mantener), consistente con R4 (énfasis dominante) y con el precedente Marshall de la ronda 1.
- Los votos de mantención sin sesgo articulado siguen siendo neutral (Larraín 2010-03-18 post-terremoto: endoso de mantención con shock transitorio).

#### Próximos pasos (en orden)

1. **Tanda 3** (85 intervenciones, 19.858 palabras, 2011-2015): leer, etiquetar, validar, commit.
2. Tanda 4 (17 intervenciones, remanente 2015) y cierre del piloto (300/300).
3. Al cierre del piloto: revisión de casos límite (mantención + sesgo; votos silenciosos), codebook v3 si aplica, test-retest 30 (≥90 %).
4. Infraestructura pendiente (no bloqueante): ejecutar `scripts/02...py` con internet; curado restante de `actores_metadata.csv`.

#### Bloqueos y pendientes

- Sin bloqueos para etiquetar. Macro y metadata: pendientes no bloqueantes (manifiesto).

---

### 2026-09-15 (sesión 4)

#### Completado

1. **Regla operativa de tandas por presupuesto de palabras** (acuerdo con el investigador): el etiquetado ya no se mide en número fijo de intervenciones por turno, sino en presupuesto de palabras (20.000 por tanda; escalable a 30–40 mil si el flujo va bien). Implementada en `scripts/04_tandas_por_presupuesto.py` + parámetro `PRESUPUESTO_PALABRAS_TANDA` en `config.py`. Salida: `data/muestras/piloto_300_tandas.csv` (orden cronológico dentro de cada tanda) y `tandas_resumen.csv`: T1 = 110 intervenciones / 19.935 palabras (2005–2009), T2 = 88 / 19.490 (2009–2011), T3 = 85 / 19.858 (2011–2015), T4 = 17 / 4.372 (2015, remanente).
2. **Ronda 1 de etiquetado ejecutada** (tanda 1 completa): `data/etiquetas/etiquetas_piloto_r1.csv` con 110 registros (metodo=`ia_ronda`, ronda=`piloto_t1_r1`, codebook v2). Distribución: 98 neutral, 6 hawkish, 6 dovish; 24 registros con `es_relevante=0` (fórmulas de ofrecimiento de palabra, reanudaciones, acuerdos formales, encabezados); confianza 87 alta / 23 media.
3. **`scripts/05_validar_etiquetas.py`**: validador paramétrico obligatorio para toda corrida de etiquetado (columnas del formato largo, dominios, coherencia prob/score/argmax, nota obligatoria si flag 0, frase obligatoria si flag 1, cobertura contra L0, no-nulidad estructural). La corrida 1 lo supera íntegro.
4. **Descarga macro derivada al investigador**: el sandbox no tiene salida TLS (verificado); `scripts/02_capa_l2_macro_y_actores.py` está listo para ejecutarse en cualquier máquina con internet normal y deposita los JSONs en `data/L2/raw/` automáticamente.

#### Hallazgos analíticos de la ronda 1 (preliminar, muestra piloto)

- Casi todo el habla de actas 2005–2009 es descriptiva o procedural (diagnóstico ≠ postura, regla R2).
- El contenido postural real se concentra en **propuestas de votación** (De Ramón, Desormeaux) y en la **justificación de la decisión** (comunicado institucional, regla R6).
- Hawkers tanda 1 (6): Valdés 2005-02-10:121 (staff con recomendación explícita, caso R5-excepción), Desormeaux x2, De Ramón x2 (propuestas +50 pb), comunicado 2008-11-06 (alza a 7,75 %).
- Dovish tanda 1 (6): Marshall 2006-09-07:873 (voto a mantención + "TPM cerca de su nivel neutral", confianza media — caso límite registrado), De Ramón 2007-09-06:1049 (recorte −25), Schmidt-Hebbel 2008-02-07:1672 ("menos restrictiva"), Velasco 2008-10-23:2167 ("preferiría recorte"), Desormeaux 2009-01-15:2377 (adhesión −250), Consejo 2009-04-16:2500 (−50 pb).
- Caso límite que conviene revisar al cierre del piloto (posible v3 o nota interpretativa): votos silenciosos denominados "mantención" cuando el sesgo era claramente restrictivo o expansivo.

#### Próximos pasos (en orden)

1. **Tanda 2** (88 intervenciones, 19.490 palabras, 2009–2011): leer y etiquetar en esta sesión si hay margen, si no, en la siguiente.
2. Tandas 3 y 4 para completar el piloto (300 intervenciones).
3. Al cierre del piloto: revisión de casos límite + decisiones de codebook v3 (si aplica) + test-retest 30 (control ≥90 % de estabilidad).
4. Infraestructura pendiente (no bloqueante): ejecutar `scripts/02...py` con internet; curado restante de `actores_metadata.csv` (manifiesto `data/L2/pendientes_manifest.csv`).

#### Bloqueos y pendientes

- Sin bloqueos para etiquetar. Macro y metadata: pendientes no bloqueantes (manifiesto).

---

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
- **2026-09-15 (sesión 5)**: ronda 2 etiquetada y validada (tanda 2, 88 intervenciones, `etiquetas_piloto_r2.csv`); validador endurecido con control verbatim R10; 23 frases de ronda 1 corregidas retroactivamente; piloto al 66 % (198/300).
- **2026-09-15 (sesión 6)**: ronda 3 etiquetada y validada (tanda 3, 85 intervenciones, `etiquetas_piloto_r3.csv`; 77 neutral, 8 dovish, 0 hawkish); arco histórico 2005-2015 completo en el piloto; queda la tanda 4 (17); piloto al 94 % (283/300).

---

## Sesión 7 (2026-09-15) — Piloto completo 300/300 + inicio del escalado

**Qué se hizo**

1. **Ronda 4 — el piloto quedó completo**: 17 intervenciones de 2015 (jun–dic), archivo `data/etiquetas/etiquetas_piloto_r4.csv`. Incluye el sesgo al alza del comunicado de sep-2015 y la primera alza del ciclo (dic-2015, recomendación formal de la Gerencia). Cifras del piloto completo: **300 etiquetas únicas, cobertura exacta** contra `piloto_300.csv`; 266 neutral / 20 dovish / 14 hawkish; 84 no relevantes (28%).
2. **`scripts/06_tandas_escalado.py`**: arma el universo de Fase 5 (corpus L0 sano menos el piloto): 9.374 intervenciones, 1,96 M palabras, en **101 tandas cronológicas de 20.000 palabras** (`data/muestras/escalado_tandas.csv` + resumen).
3. **Escalado tanda 1 etiquetada**: 99 intervenciones (ene–feb 2005: sesión del IPoM de enero y RPM de febrero, ambas con alza de 25 pb), archivo `data/etiquetas/etiquetas_escalado_r5.csv`. Distribución: 78 neutral / 20 hawkish / 1 dovish; 19 no relevantes; 90 alta / 9 media confianza.

**Aprendizajes de la tanda 1**

- El formato de actas 2005 es más verboso que el de 2015: los votos son intervenciones largas (300–700 palabras) que mezclan diagnóstico y voto; la frase justificante se toma de la oración explícita del voto.
- La Gerencia de División Estudios presenta "Opciones de Política Monetaria" con recomendación explícita: eso se captura como hawkish/dovish (convención ya usada en el piloto con la recomendación de dic-2015).
- El Ministro de Hacienda (sin voto) sí registra postura: Mario Marcel en feb-2005 fue la única intervención dovish de la tanda ("la normalización podría ir a un ritmo más lento").
- Tramos puramente logísticos de las actas antiguas (suspensión/reanudación, fijación de fecha, apertura de votación) son el grueso del flag `es_relevante=0` (19 casos).

**Pendiente**

- Casos límite acumulados para revisión conjunta al cierre del gold: los ya listados en sesión 6 más el balance de riesgos "sesgo al alza para la inflación" en presentaciones del staff (etiquetado neutral con tilt 0,20).
- Tanda 2 del escalado (93 intervenciones, feb–abr 2005) queda lista para el próximo turno.
- Al final: gold ciego del usuario (~300), kappa, fine-tune BETO.

---

## Sesión 7b (2026-09-15) — Llega el macro consolidado y recuperación del repo

**Incidente y recuperación (sin pérdida de trabajo)**

El repo de GitHub fue recreado y el usuario subió por web dos archivos (`consolidado_D&H.xlsx`, el corpus fuente de 9.725 intervenciones, y `consolidado_macro.xlsx`, la descarga macro ejecutada localmente). Eso dejó el historial remoto sin relación con el local y sin la rama de trabajo ni el PR #1. Todos los archivos de trabajo estaban intactos en el sandbox; se reconstruyó la rama `arena/01a0a3a0-fase-2` sobre el nuevo `main` y se re-subió todo en un solo commit.

**Qué hizo el usuario**

Ejecutó la descarga macro en su máquina y entregó `consolidado_macro.xlsx` con: TPM, IPC, IMACEC y dólar diarios/mensuales 2000-2025; desempleo mensual (desde 2010-03, límite del API); cobre mensual; `Macro_por_Reunion` con TPM, TPM_post, dTPM y policy_decision para **las 132 reuniones del corpus, sin faltantes**; `Actores_Metadata` (465 actores, historia larga) y catálogo de variables.

**Qué se hizo en esta sesión**

1. `scripts/07_macro_desde_excel.py`: materializa la capa L2 macro desde el libro, con cortes y asserts (una fila por reunión, cobertura total, dTPM coherente en signo con la decisión).
2. Generados `data/L2/macro_por_reunion.csv` (132 reuniones: 80 mantiene / 35 sube / 17 baja) y `data/L2/macro_mensual.csv` (312 meses, 2000-2025).
3. `data/L2/pendientes_manifest.csv` depurado: quedan solo eee_inflacion_1a, ipec, sit_pais_1a, pib, exportaciones, importaciones y el hueco desempleo 2005-2009.

**Desbloqueo**

La Fase de validación del score contra dTPM ya tiene su insumo completo. El PR de trabajo se reabre con todo el acumulado.
