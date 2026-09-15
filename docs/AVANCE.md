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

---

## Sesión 8 (2026-09-15) — Escalado: tandas 2 y 3 etiquetadas y validadas

**Qué se hizo**

1. **Tanda 2 escalada** (`data/etiquetas/etiquetas_escalado_r6.csv`): 93 intervenciones, feb–abr 2005. 89 neutral / 3 hawkish / 1 dovish; 12 `es_relevante=0`; 7 confianza media. Incluye la respuesta completa del Consejo a la crisis energética (gas/petróleo) y la subida de marzo. Caso actor-céntrico: Eyzaguirre (Hacienda) nuevamente dovish — "estamos mucho más en tinieblas" — continuidad del patrón iniciado con Marcel en la tanda 1.
2. **Tanda 3 escalada** (`data/etiquetas/etiquetas_escalado_r7.csv`): 103 intervenciones (19.953 palabras), sesiones RPM 76 (07-abr: **alza unánime a 3,0 %**) y 77 (12-may: diagnóstico y opciones; la votación de mayo cae en la tanda 4). 94 neutral / 7 hawkish / 2 dovish; 17 `es_relevante=0`; 2 confianza media.
   - Hawkish de abril: los 5 votos de consejeros +25 pb, el acuerdo/comunicado (`2005-04-07:219:2`) y las opciones del staff con recomendación explícita de 25 pb (`214:4`).
   - Dovish: la Ministra Wagner (`215:1`, prefería mantener aunque "podemos vivir" con el alza) y Eyzaguirre en mayo (`262:1`, 378 palabras contra "una estrategia tan marcadamente front low").
   - Tandas 1–3 van 295 intervenciones del escalado; escalado + piloto = 595/9.725 (6,1 % del corpus).

**Aprendizajes operativos**

- Trampas de verbatim del validador ya documentadas: el acta contiene typos propios que deben copiarse tal cual (`sucesa`, `Rabio García`, `instancia monetaria`) y toda frase que empiece en mayúscula de oración debe coincidir exactamente; recortar subcadenas a media oración.
- Convención de tandas: una sesión larga puede partirse entre tandas (los votos de mayo 2005 abren la tanda 4); la cobertura se valida contra `escalado_tandas.csv`, no contra la sesión completa.

**Pendiente**

- Tanda 4 del escalado (comienza con la votación de mayo-2005 y avanza jun–jul 2005).
- Casos límite acumulados para revisión conjunta al cierre del gold; test-retest de 30; codebook v3 al final.
- Al final: gold ciego del usuario (~300), kappa, fine-tune BETO.

---

## Sesión 8b (2026-09-15) — Decisión de alcance: training set ~1.000 y muestreo estratificado por fases

**Decisión del investigador (consolidada como decisión 8 del PLAN)**

El etiquetado en chat NO cubre el corpus completo: construye solo el training set de ~1.000 intervenciones para el fine-tune de BETO; el modelo etiqueta las ~8.600 restantes en la Fase 8. El universo de *scoring* sigue siendo las 9.725. Justificación: un fine-tune de 3 clases converge bien en ese rango y la clase minoritaria importa más que el total; el trabajo manual se acota al mínimo defendible.

**Diseño del training set**

- Ya etiquetado: 595 (piloto 300 estratificado por año×tópico×actor + tandas cronológicas 1-3 de 2005-fa alzas).
- **Tanda 4** (pendiente, cronológica): 52 intervenciones; cierra 2005 (votación de mayo + jun-jul).
- **Tandas 5-8 estratificadas** (`scripts/08_muestra_estrato_fases.py`): 378 intervenciones / 67.740 palabras, 9 fases del ciclo TPM derivadas de las transiciones reales en `data/L2/macro_por_reunion.csv` (42 por fase, seed 20260915): alza_fin 2006, mixto 2007, crisis_alza 2008, bajas 2009, alza_emergencia 2010, alza 2011, mantiene 2012-13, bajas 2013-14, quiebre 2015.
- **Proyección total: 1.025** etiquetas de entrenamiento + gold ciego del usuario (~300, test puro, sin tocar).
- Archivos: `data/muestras/estrato_fases.csv` y `estrato_fases_resumen.csv`.

**Pendiente**

- Tanda 4 (cierre 2005) en el próximo turno; luego tandas 5-8 estratificadas.
- Después: curva de aprendizaje con modelos rápidos (TF-IDF/embeddings), kappa vs gold, fine-tune BETO y scoring del corpus.
- Diferido: casos límite, test-retest 30, codebook v3, votos explícitos (Fase 10).

---

## Sesión 8c (2026-09-15) — Tanda 4: cierre cronológico de 2005

**Tanda 4 etiquetada y validada** (`data/etiquetas/etiquetas_escalado_r8.csv`): 52 intervenciones, 16.167 palabras (mayo-jul 2005). 34 neutral / 10 hawkish / 8 dovish; 12 `es_relevante=0`; 4 confianza media.

Contenido clave:
- **12-may (sesión 77), alza unánime a 3,25 %**: 5 votos +25 pb hawkish; comunicado hawkish. Matiz: Carrasco abogó por pausa (dovish) y Schmidt-Hebbel declaró que el alza "domina inambiguamente" (hawkish explícito). Eyzaguirre sigue escéptico (tasa neutral, expectativas ancladas).
- **09-jun (sesión 79), mantención unánime**: los 5 consejeros votan mantener por razones tácticas (evitar señal de tercera alza consecutiva) → 5 votos dovish del propio Consejo; comunicado mantención + reafirmación de retiro pausado = hawkish media (convención ya establecida). Eyzaguirre de nuevo dovish (duda de la tendencia del IPCX1).
- Acumulado training set: **647 etiquetas**. Quedan las tandas 5-8 estratificadas (378) para completar ~1.025.

---

## Sesión 8d (2026-09-15) — Tanda 5 estratificada: alza fin 2006, mixto 2007, crisis 2008 (inicio)

**Tanda 5 etiquetada y validada** (`data/etiquetas/etiquetas_escalado_r9.csv`): 94 intervenciones / ~19,7 mil palabras de las fases 2006_alza_fin (42), 2007_mixto (42) y 2008_crisis_alza (10). 82 neutral / 7 hawkish / 5 dovish; 24 `es_relevante=0`; 5 confianza media.

Hitos para los entregables actor-céntricos:
- **jul-2006**: reunión partida (De Gregorio ya venía recomendando pausa en mayo → dovish; Desormeaux y Corbo votan +25 pb → hawkish). Velasco: "normalización más corta o más lenta" (dovish).
- **ene-2007**: la única baja del periodo (a 5,0 %): García la recomienda explícitamente (dovish). mar-2007: Desormeaux vota mantener *contra* la opción de bajar por riesgo inflacionario → hawkish media (posición relativa al menú de opciones).
- **dic-2007**: alza a 6,0 % por anclaje de expectativas (Marfán y De Gregorio, votos hawkish con justificación explícita). Jadresic "ante la duda abstente" (dovish).
- **ago-2008**: Marfán vota +50 pb (única ronda de alzas de 50; hawkish). nov-2008: exposición de Soto ya describe desinflación acelerada (transición a la fase de bajas).
- Acumulado training set: **741/1.025**. Quedan tandas 6 (120), 7 (110) y 8 (54).

---

## Sesión 8e (2026-09-15) — Tanda 6 estratificada: crisis 2008 (cierre), bajas 2009, alza de emergencia 2010

**Tanda 6 etiquetada y validada** (`data/etiquetas/etiquetas_escalado_r10.csv`): 120 intervenciones / ~19,4 mil palabras de las fases 2008_crisis_alza (32 restantes), 2009_bajas (42), 2010_alza_emergencia (42) y 2011_alza (4 de 42). 109 neutral / 5 hawkish / 6 dovish; 17 `es_relevante=0`; 3 confianza media. Cobertura exacta contra `estrato_fases.csv[tanda==6]` (120/120).

Contenido clave del periodo (útil para entregables actor-céntricos y validación vs TPM):

- **mar-2008, disenso en plena crisis de inflación**: Marshall vota mantener 6,25 % descartando bajar pero posponiendo el alza por riesgo externo (dovish 0,70); Marfán vota mantener *manteniendo el sesgo al alza* y condiciona la subida a intervención cambiaria (hawkish media 0,55: "en ausencia de esta última, no corresponde elevar").
- **abr-2008, fin del sesgo**: Velasco y Marfán votan mantener y eliminar el sesgo de alza por el escenario que se configuraba (dovish 0,65 ambos).
- **sep-2008, última alza del ciclo (a 7,75 %)**: García (staff) descarta +75 pb y la recomendación efectiva es +50 (hawkish 0,80, escenario convergente suave a tasas 8,75–9,25 %); Desormeaux declara preferencia explícita por +75 pb aunque se suma a la mayoría (hawkish 0,90). Caso canónico de "posición respecto del menú de opciones".
- **nov-2008, pausa pre-mega-baja**: De Gregorio vota mantener a la espera de que las noticias confirmen la caída de la inflación, con "política menos restrictiva de lo previsto" (dovish 0,75).
- **feb-2009, baja récord**: Claro vota rebajar *solo* 200 pb (dovish 0,90; el Consejo bajó 250 pb). Velasco (Hacienda, abr-2009) registra el "update demoledor" de proyecciones (neutral media con sesgo dovish 0,35).
- **ago-oct-2009, piso 0,5 % y FLAP**: opciones del staff entre mantener la instancia o ampliar estímulo (neutral: presentación de menú sin recomendación); De Gregorio vota mantener TPM 0,5 % + FLAP por riesgo de inflación bajo rango de tolerancia (dovish 0,80).
- **oct-2010, alza +25 a 2,75 %**: De Gregorio vota subir 25 pb pese a declarar que, sin apreciación del peso ni menores registros de inflación, "la opción más adecuada hubiera sido subir la tasa en 50 puntos base" (hawkish 0,95 por voto efectivo; nota de calibre registrada como matiz de intensidad). Comunicado unánime hawkish 0,95.
- **oct-2011**: Marfán duda que la desaceleración prevista sea solo ajuste de inventarios y prevé moderación del gasto (neutral media, sesgo dovish 0,30) — antecedente del quiebre de ciclo de fines de 2011.

**Acumulado training set: 861/1.025** (84 %). Pendiente verificado contra el estrato: tanda 7 (110: 2011_alza resto 38, 2012_13_mantiene 42, 2013_14_bajas 30) y tanda 8 (54: 2013_14_bajas resto 12, 2015_quiebre 42) → cierre exacto en 1.025.

**Nota operativa**: el sandbox se reinició entre sesiones y `pandas` desapareció del Python de sistema (PEP 668 bloquea el pip global). Se creó un entorno virtual en `/home/user/venvs/fase2` (pandas 3.0.5 + openpyxl); todos los scripts se ejecutan con `/home/user/venvs/fase2/bin/python`. `05_validar_etiquetas.py` quedó verificado compatible con pandas 3.0.5.

---

## Sesión 8f (2026-09-15) — Tandas 7 y 8: cierre del training set en 1.025 etiquetas

**Tanda 7 etiquetada y validada** (`data/etiquetas/etiquetas_escalado_r11.csv`): 110 intervenciones / ~19,7 mil palabras (2011_alza resto 38, 2012_13_mantiene 42, 2013_14_bajas 30). 101 neutral / 8 dovish / 1 hawkish; 14 `es_relevante=0`; 6 confianza media. Cobertura exacta contra `estrato_fases.csv[tanda==7]`.

**Tanda 8 etiquetada y validada** (`data/etiquetas/etiquetas_escalado_r12.csv`): 54 intervenciones / ~8,8 mil palabras (cierre 2013_14_bajas, 12; 2015_quiebre, 42). 50 neutral / 2 hawkish / 2 dovish; 14 `es_relevante=0`; 1 confianza media. Cobertura exacta contra `estrato_fases.csv[tanda==8]` y control global: `estrato_fases` 378/378, sin duplicados entre archivos.

**TRAINING SET COMPLETO: 1.025/1.025** (piloto r1-r4: 300; escalado tandas 1-8: 725). Se cierra la Fase de etiquetado IA por rondas de chat prevista en la decisión 8 del PLAN.

Hitos del periodo 2011-2015 para los entregables:

- **jun-2011**: Marshall vota +25 pb a 5,25 % con sesgo matizado (hawkish 0,95; último tramo del ciclo de alzas post-emergencia).
- **sep-2011, pausa del ciclo**: Marshall vota mantener (dovish 0,75) con monitoreo cercano del frente externo; Marcel (Marfán) en oct-11 ya dudaba del ajuste por inventarios (sesgo dovish 0,30) → anticipa el quiebre hacia la mantención larga.
- **2012-13, mantención en 5 %**: opciones del staff (Herrera) descartan *ambas* direcciones (subir por dudas externas, bajar por riesgos inflacionarios) → recomendaciones de mantener = neutral pura; señales hawkish latentes: Marfán (recalentamiento construcción/comercio, feb y ago-2012), Vergara (cuenta corriente/TCR, sep-2012) y Vial (mar-2013: "habría que plantearse con bastante más urgencia una política que la sustituya").
- **oct-2013, retorno a las bajas**: Vial vota -25 pb a 4,75 % (dovish 0,90); acuerdo unánime consistente. nov-2013: Marfán adelanta la segunda baja por la revisión de Cuentas Nacionales (dovish 0,90).
- **feb-ago 2014, ciclo de recortes**: Vergara deja de ser Consejero y preside los recortes: "la opción de bajar la TPM se impone claramente sobre la de mantenerla" (dovish 0,90); Claro vota -25 pb a 3,5 % en ago-14 (dovish 0,95) aunque pide no sobredimensionar el dato de inflación (hawkish-latente, media).
- **dic-2014, pausa en 3 %**: Vergara vota mantener con sesgo neutral, descartando explícitamente ambas direcciones (neutral pura).
- **ago-2015**: de Ramón (staff) argumenta que subir la tasa "es confusa y se justificaría únicamente en un contexto de desanclaje, que hoy no está presente" (neutral media, sesgo dovish 0,35) — dos meses antes del inicio de las alzas.
- **oct-2015, primera alza del quiebre (a 3,25 %)**: acuerdo hawkish 0,95 ("la trayectoria futura de la TPM contempla ajustes adicionales").
- **dic-2015**: García vota +25 pb a 3,5 % con sesgo neutral (hawkish 0,95, decisión "finamente balanceada"); el Ministro Micco declara que "la política monetaria tiene amplio espacio para mantenerse acomodativa" (dovish 0,85) el día después de la primera alza de la Fed en casi una década.

**Distribución global del training set** (1.025 etiquetas `ia_ronda`, codebook v2): ver `scripts/05_validar_etiquetas.py` por archivo; el consolidado queda para la Fase 6 (baselines y curva de aprendizaje).

**Pendiente (secuencia de cierre del PLAN)**

- Gold ciego del usuario (~300, test puro) → kappa Cohen IA vs humano.
- Fase 6: baselines TF-IDF/embeddings con split por tiempo; curva de aprendizaje.
- Fase 7: fine-tune BETO sobre las 1.025; Fase 8: scoring del corpus completo (9.725); validación vs ΔTPM.
- Diferido: casos límite acumulados, test-retest 30, codebook v3, votos explícitos (Fase 10).

## Sesión 9 (2026-09-16) — Gold ciego (decisión 9) y mitigación del desbalance (decisión 10)

### Completado en esta sesión

1. **Gold ciego cerrado y commiteado** (decisión 9 del PLAN): `scripts/09_muestra_gold_ciego.py` (seed 20260916) extrae **306 intervenciones** test-puro, con exclusión dura vía assert contra todo `data/etiquetas/`. Estratificación: 34 por cada una de las 9 fases TPM posteriores a jul-2005 (las 50 intervenciones del residuo jul-2005 quedan fuera y documentadas) × sub-estrato de señal de decisión (2/3 del marco con vocabulario de decisión vía `PATRON_DECISION`, para que κ pueda medir clases minoritarias). Instrumento: `data/muestras/gold_ciego_300.csv` (306 int / 99.660 palabras) + `_resumen.csv`. Las mismas 306 serán el test set del fine-tune (Fases 7/8). Instrucciones para el usuario: `docs/INSTRUCCIONES_GOLD.md`.
2. **Diagnóstico del desbalance** del training set base (1.025): 88 % neutral (903/69/53); sin flag-0, 85/8,5/6,5 % sobre 812 relevantes; solo 122 H+D puros. Concluido que es en parte real (el corpus es mayoritariamente descriptivo; hawks=0 en bajas es sustantivo) con dos problemas genuinos: 213 flag-0 asentados como clase y F1 inestable de minoritarias.
3. **Decisión 10 (mitigación doble)**: ante "haz lo más recomendable" se ejecutan ambas: (a) segunda ola enriquecida (`scripts/10_muestra_enriquecida.py`, seed 20260917) de 252 intervenciones en tandas 9-14 (~109 mil palabras): pool A = Consejo con señal de decisión (tope 20/fase) + pool B = Gerente de Div. Estudios con señal; exclusión dura contra etiquetadas y gold; (b) modelo en dos etapas para Fases 7/8 (A filtra sin-stance; B clasifica H/D/N). Registrado en PLAN.md §3.
4. **Refactor config.py como fuente única**: `FASES_TPM`, `PATRON_DECISION` (regex no-capturante), `CARGOS_CONSEJO`, `CARGOS_OPCIONES`; script 09 refactorizado a importarlos y re-verificado reproducible (diff vacío sobre el CSV del gold).
5. **Tanda 9 etiquetada (`data/etiquetas/etiquetas_r13_tanda09.csv`, ronda `enriquecido_t09_r13`)**: 41 intervenciones / 19.734 palabras (2006_alza_fin + inicio 2007_mixto). Relevantes: 18 neutral / 9 hawkish / 8 dovish (42 % H+D vs ~9 % en el estrato general — el enriquecimiento funciona como diseñado) + 6 flag-0; 3 confianza media. Validaciones: cobertura exacta contra el corte oficial `tanda==9`, frases verbatim contra el corpus (con normalización de espacios por saltos de línea del acta), sin duplicados, archivos previos intactos (append-only por hash), y pasa `scripts/05_validar_etiquetas.py`. Script `13_ronda_tanda09.py` idempotente y en formato L1 canónico (PLAN §4.2).
6. **Incidencia documentada**: una primera extracción de lectura en un directorio efímero se perdió y resultó no corresponder al corte oficial del archivo (170/171 de sus ítems no estaban en la muestra: contenía material ya etiquetado y no-muestra). Se descartó íntegramente **antes** de etiquetar y se re-extrajo/verificó por (id, palabras) contra `estrato_enriquecido.csv`. Sin impacto en la capa L1.

### Estado del training set tras la tanda 9

**1.066 etiquetas** (`ia_ronda`, codebook v2): relevantes 847 = 708 neutral (83,6 %) / 78 hawkish (9,2 %) / 61 dovish (7,2 %); flag-0: 219. H+D puros: 139 (era 122). Restan ~210 del estrato enriquecido (tandas 10-14) — tras ellas el training set proyectado ronda **~1.280 con ~16-18 % H+D**.

### Hallazgos analíticos de la tanda 9 (SEP-2005 a DIC-2007)

- **sep-2005-nov-2005**: staff (Valdés) recomienda +25 cuatro veces seguidas ("difícil justificar otra opción"); Marfán y Corbo votan la quinta alza por desanclaje (hawkish 0,90).
- **dic-2005, primera pausa**: De Gregorio vota mantener tras 5 alzas (dovish 0,70) — pausa a la espera de información, riesgo de sobrepasar.
- **mayo-jun-2006**: Desormeaux y Marfán votan pausa: dos alzas seguidas romperían la "normalización pausada" y cálculo de error de tipo 2 (dovish 0,70-0,75).
- **jul-2006, alza a 5,25 % y fin del ciclo**: acuerdo hawkish 0,85 con matiz de pausas "menos frecuentes"; desde sep-2006 el staff solo justifica mantención (dovish 0,70-0,75) y Velasco pide cambiar el sesgo del comunicado (oct-2006).
- **2007_mixto**: opciones del staff sin recomendación (abr: -25 vs mantener → neutral pura); **ago-2007** Marfán/Consejo: alza +25 a 5,5 % por shock alimentario (hawkish 0,85-0,95) aunque Marfán propone eliminar el sesgo comunicacional; **dic-2007** (Magendzo ya de Gerente subrogante): opciones sin inclinación con sesgo neutro — preludio del fin del ciclo de alzas.

### Próximos pasos (en orden)

1. Entregar `docs/INSTRUCCIONES_GOLD.md` al usuario y recibir el gold etiquetado → κ por clase y sub-estrato.
2. Tandas 10-14 del enriquecido (unas ~210 intervenciones; ~1-2 tandas por turno de trabajo).
3. Fase 6 (baselines TF-IDF/embeddings, split por tiempo): instalar scikit-learn en el venv (pendiente).
4. Fase 7 (fine-tune BETO, modelo de dos etapas, class_weight='balanced') → Fase 8 (scoring 9.725) → validación vs ΔTPM.

### Bloqueos y pendientes

- Sin cambios de fondo: scikit-learn pendiente de instalación; test-retest 30 y codebook v3 diferidos; votos explícitos en Fase 10.

## Sesión 10 (2026-09-16) — Tanda 10 del enriquecido (2007_mixto cierre + 2008_crisis_alza)

**Tanda 10 etiquetada y validada** (`data/etiquetas/etiquetas_r14_tanda10.csv`, ronda `enriquecido_t10_r14`): 36 intervenciones / 19.361 palabras. Relevantes: 20 neutral / 9 hawkish / 3 dovish + 4 flag-0 (2 confianza media). Cobertura exacta contra `estrato_enriquecido.csv[tanda==10]`, validación 05 OK, append-only verificado.

### Convención nueva registrada

- **Votar mantener cuando las opciones del staff son {disminuir 25, mantener} y el sesgo previo es a la baja = hawkish relativo** (0,65-0,70): espejo exacto de la convención de pausas dentro de ciclos de alzas. Casos: Desormeaux (ene-2007 y abr-2007) y Corbo (feb-2007) votan contra el recorte.

### Hallazgos analíticos de la tanda 10

- **feb-may 2007, la pausa dividida**: el Consejo se resquebraja — Velasco (MinHacienda) respalda con fuerza la baja (dovish 0,85, "abrumadores"), mientras Desormeaux y Corbo ganan la mantención por mayoría (hawkish 0,65-0,70). El staff deja ambas opciones sin inclinarse.
- **ago-sep 2007, retorno duro a las alzas**: Velasco recomienda +25 moderado evitando sobrerreacción; el comunicado de sep-07 (+25 a 5,75%, hawkish 0,95) abre el ciclo que durará hasta jul-2008. Marfán vota la alza pero pide eliminar el sesgo.
- **ene-mar 2008, el timing de la crisis**: el staff descarta mantener (García ene-08: incongruente con la meta, hawkish 0,85); en mar-08 la división es total — Claro insiste en subir a 6,50 % contra la mantención mayoritaria (hawkish 0,85), y Marfán negocia laredacción de la Minuta sobre la posible "intervención" cambiaria.
- **jun-ago 2008, el pico inflacionario**: García descarta mantener (jun-08) y De Gregorio vota **+50 pb** en ago-08 con sesgo al alza (hawkish 0,95) — cúspide restrictiva del ciclo.
- **nov-dic 2008, el quiebre hacia la crisis**: el staff ya solo justifica mantener a 8,25 % en plena crisis (had-hoc del trade-off), Marfán descarta ambas direcciones (TC desalineado) pero declara que "lo estándar apuntaría a bajas rápidas y bruscas de 50 pb o más" (dovish 0,60, anticipando el recorte de ene-09).

### Estado del training set

**1.102 etiquetas** (rondas `ia_ronda`, codebook v2): relevantes 879 = 728 neutral (82,8 %) / 87 hawkish (9,9 %) / 64 dovish (7,3 %); flag-0: 223. H+D puros: 151. Restan ~175 del estrato enriquecido (tandas 11-14).

### Próximos pasos

1. Tandas 11-14 del enriquecido (~175 int).
2. Recibir gold etiquetado por el usuario → κ por clase y sub-estrato.
3. Fase 6 (baselines; instalar scikit-learn), Fase 7 (BETO dos etapas), Fase 8 (scoring 9.725).

## Sesión 11 (2026-09-15) — Tanda 9 del estrato_tanda9 + reconciliación de plan enriquecido

**Tanda 9 etiquetada y validada** (`data/etiquetas/etiquetas_escalado_r13.csv`, ronda `escalado_t09_r13`): 58 intervenciones / 19.996 palabras sobre `estrato_tanda9.csv[tanda==9]`. Relevantes: 44 neutral / 5 hawkish / 4 dovish + 13 flag-0. Validación 05 OK: codebook v2, sin duplicados, conferencia literal de frase_justificante 58/58 (2 corregidas tras detección de paráfrasis), cobertura exacta de la tanda.

### Reconciliación de estratos de enriquecimiento (IMPORTANTE)

Existen dos estratos: `estrato_enriquecido.csv` (252 int, tandas 9-14, sesión 9a/10: tetiquetadas tandas 9 y 10 = 77 filas, rondas `enriquecido_t09_r13`/`enriquecido_t10_r14`) y `estrato_tanda9.csv` (250 int, tandas 9-13, seed 20260917, cuotas stance-signal 150/62/38, decision 10 final). El segundo **reemplaza** al primero para el trabajo pendiente: se dibujó excluyendo gold + todas las etiquetas existentes (por eso las 77 etiquetas `enriquecido_*` quedan intactas y sin duplicados en el training set). Las tandas 11-14 del `estrato_enriquecido` (~175 int) quedan **obsoletas/abandonadas**: 11 de esas intervenciones vuelven a entrar por `estrato_tanda9` (solape verificado: 11 ids, ninguno ya etiquetado), el resto simplemente no se muestrea.

### Estado del training set

**1.160 etiquetas** (codebook v2, `ia_ronda`): 1.000 neutral / 92 hawkish / 68 dovish (H+D puros: 160; flag-0 incluidas en el conteo por clase). Pendiente de `estrato_tanda9`: 192 intervenciones en 4 tandas → r14 = tanda 10 (56 int / 19.507 p.), r15 = tanda 11 (71 / 19.726), r16 = tanda 12 (58 / 19.848), r17 = tanda 13 (7 / 2.064). Total tras enriquecido: ~1.352.

### Hallazgos de la tanda 9

- Acuerdos/comunicados con señal explícita: voto +25 pb (feb-2011 x2, jun-2011) → hawkish 0,95; ago-2011 mantención de 5,25 % sin sesgo forward en fase de alzas → dovish relativo 0,60 (convención pausa); oct-2009 De Gregorio "mantención prolongada + no convencionales" contra retiro anticipado → dovish 0,75.
- Nov-2014 García: "única opción razonable es mantener 3,0 % (votación con implicancias)" → neutral (sesgo ya a la baja desde oct-14).
- Feb-2014 staff recomienda "mantener un sesgo explícito a la baja en el párrafo final del Comunicado" → dovish 0,60.
- Mar-2006 comunicado: mantiene 4,75 % pero "incrementos futuros siguen siendo necesarios" → hawkish 0,55 (mantención con reafirmación explícita de retiro).
- Oct-2013 menú staff {mantener 5 % vs recortar 4,75 %} sin recomendación → neutral pura; dic-2013 Herrera recomienda mantener 4,5 % descartando tercer recorte sucesivo por "señal de urgencia" → ligeramente hawkish respecto al menú pero dentro de neutral (ya etiquetado neutral por menú balanceado con recomendación de mantener sin descarte agresivo).

### Próximos pasos

1. r14: tanda 10 de `estrato_tanda9` (56 int / 19.507 p.).
2. r15-r17: tandas 11-13 (136 int / ~41,6k p.).
3. Recibir gold etiquetado por el usuario → κ por clase y sub-estrato.
4. Fase 6 (baselines; instalar scikit-learn), Fase 7 (BETO dos etapas), Fase 8 (scoring 9.725).

### Sesión 11 (cont., ~20k palabras extra) — Tanda 10 del estrato_tanda9 (r14)

**Tanda 10 etiquetada y validada** (`data/etiquetas/etiquetas_escalado_r14.csv`, ronda `escalado_t10_r14`): 56 intervenciones / 19.507 palabras. Relevantes: 37 neutral / 7 hawkish / 5 dovish + 14 flag-0 (las 12 micro-intervenciones logísticas habituales: fijación de fechas, tránsitos a votación, aprobaciones de comunicado, cierres; más 1 institucional de presupuesto). Validación completa: codebook v2, sin duplicados, conferencia literal 56/56, cobertura exacta `estrato_tanda9.csv[tanda==10]`.

**Hallazgos**: sep-2007 Valdés (staff) recomienda +25 pb ("difícil argumentar opción diferente") → hawkish 0,95; ago-sep-2008 el clímax restrictivo: Marshall, Marfán y el Consejo votan +50 pb a 7,75 %/8,25 % con "trayectoria futura contempla ajustes adicionales" (3 x hawkish 0,95); feb-2008 De Gregorio pausa en ciclo de alzas por apreciación cambiaria → dovish relativo 0,65; abr-2010 De Gregorio mantiene 0,5 % pero anuncia "comenzar a normalizar en los meses venideros" → hawkish 0,70 (convención mantención con reafirmación de retiro); abr-2009 recortes de 50 pb de Marfán y Céspedes con sesgo de continuación → dovish 0,95/0,85; jul-2014 Vergara defiende "sesgo negativo" → dovish 0,70.

**Training set: 1.216 etiquetas** (H=99, D=73, N=1.044). Restan tandas 11 (71 int), 12 (58) y 13 (7) = 136 intervenciones (~41,6k palabras) → r15-r17. Ventana de costo: completo el enriquecido quedaría ~1.352 etiquetas.

---

## Sesión 11 (cont.): tandas 11-13 del estrato — DECISIÓN 10 CUMPLIDA (2026-09-15)

**Rondas r15-r17 completadas.** Las 3 tandas restantes del `estrato_tanda9` (136 int / 41,6k p.) quedaron etiquetadas y validadas:

| Ronda | Tanda | Int. | Distribución | Notas texto-perdurable |
|---|---|---|---|---|
| `escalado_t11_r15` | 11 | 71 | 55 N / 8 H / 8 D (8 flag-0) | Ciclo 2008-2011 + 2014-2015; convención "mantener=única opción relevante" (García/Vial) = neutral; retiro explícito de sesgo al alza (De Gregorio sep-2011) = dovish relativo p_d=0,65 |
| `escalado_t12_r16` | 12 | 58 | 41 N / 9 H / 8 D (10 flag-0) | Clímax de crisis 2009: Marshall/Velasco abr-2009 (-50pb) = D 0,95/0,85; Marfán abr-2013 "pedir gráfico" = neutral (peticiones de datos no son postura); cycle-ender Corbo oct-2007 (mantener + esperar) con balance al alza = hawkish relativo 0,55 media |
| `escalado_t13_r17` | 13 | 7 | 6 N / 0 H / 0 D (1 flag-0) | Tanda residual corta; Soto deja constancia de expectativa de alza (market pricing, no postura propia) |

**VALIDACIÓN IGUAL QUE RONDAS ANTERIORES:** código del conjunto: prob sum=1, frase ≤300, conferencia literal contra `escalado_tandas.csv` (normalización NFD+minúsculas+cosas), sin duplicados `intervencion_id` entre los 19 CSV de `data/etiquetas/`, codebook v2, asserts del generador.

### Estado final del training set (DECISIÓN 10 cerrada)

- **Archivos en `data/etiquetas/`:** 19 CSV (`base` r1-r4, `escalado` r5-r17, `enriquecido`, gold-r0 placeholder) = **1.352 etiquetas IA**.
- Distribución: **H=116 (8,6%) / D=89 (6,6%) / N=1.147 (84,8%)**; H+D = **205 (15,2%)**; flag-0 = 269 (19,9% de las intervenciones, mayoría logística de sesión).
- **Rendimiento del enriquecimiento por señal-TPM decisión 10:** +163 intervenciones H/D adicionales sobre las 42 originales del diseño previo (rondas 5-10 puras daban ~5% de prevalence). Las 250 etiquetas del estrato aportaron 110 H/D (44% de rendimiento), consistente con el ataque dirigido al cuello de botella.
- El código generador del estrato (`scripts/10_muestra_enriquecida.py`, seed 20260917) quedó congelado; la muestra está **agotada** por diseño: usar el conjunto remanente de alto-TPM-churn requeriría duplicar tandas. Cualquier expansión futura del training set debe venir de otra fuente (p.ej., segundo estrato por confianza-baja del modelo BETO en Fase 8, active learning).

### Cobertura de fases TPM (training)

Con 1.352 etiquetas: F1 alza-2005 108, F2 mantención 335, F3 alza-2007 152, F4 piso-crisis 232, F5 normalización 116, F6 alza-2011 81, F7 mantención-2012 180, F8 baja-2013-14 118, F9 post-2014 30. Las fases 5-9 (era De Gregorio tardío / Vergara) tienen 6-30 etiquetas cada una; es el precio de haber seguido el plan "cronológico + estratificado" con recursos finitos. El fine-tuning compensará con **arquitectura de dos etapas** (Fase 6-8): etapa A clasifica `es_relevante`/PM-adjacency, etapa B (sobre relevantes) elige hawkish/dovish/neutral con `class_weight` inverso a frecuencia y semantic-matching de negaciones. Se documenta en `config.py` (`FASES_TPM` + `PATRON_DECISION`).

### Hallazgos textuales perdurable (r15-r17)

1. Un consejero evita votar "sesgo" explícito en el acta; la frase de state es "concordar con la recomendación de la Gerencia de División Estudios" (muy frecuente en 2012-2014). Mapeada a **neutral** salvo contexto de ruptura.
2. Existe un micro-género propio: el Presidente De Gregorio/Vergara abriendo y cerrando sesiones ("ofrece la palabra", "ha resuelto que la Reunión de mayo se celebre el 14"). ~19,9% de las intervenciones son esto; Fase 8 las filtrará con el flag `es_relevante=0` ya etiquetado, no con heurística de longitud.
3. Ministros de Hacienda 2010-2011 (Larraín) difieren del tono 2006-2009 (Velasco): Velasco argüía con posiciones propias (dovish 2009), Larraín reporta datos macro sin juicio de TPM (neutral best-effort).
4. La frase spoiler "el mercado espera unánimemente una mantención" es constatación, no postura; nunca vale como justificante de etiqueta direccional.

### Próximos pasos

- **Pendiente usuario:** etiquetado gold ciego 306 (instrumento `data/muestras/gold_ciego_300.csv`, `docs/INSTRUCCIONES_GOLD_v2.md`). Sin esto no hay κ ni test-set para el fine-tune.
- Tras recibir gold: script de conciliación (Cohen's κ, matriz de confusión por ronda), luego Fase 6-8 (BETO + 2 etapas) con los 1.352 training + 306 gold-test.
- Riesgo conocido: confianza "media" concentra ~11% de las etiquetas; si el gold muestra que "media" es ruido, se elevará a "alta" iterando el codebook v2→v3.

*Sesión 11 cerrada. Repositorio sincronizado (`git push origin arena/01a0a3a0-fase-2`).*
