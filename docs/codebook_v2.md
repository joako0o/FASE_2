# CODEBOOK v2 — Codificación de Postura de Política Monetaria
**Proyecto D&H · Actas RPM Banco Central de Chile 2005–2015**

> **Estado histórico:** v2 fue aprobado el 2026-09-15 y permanece congelado para reproducir sus anotaciones, referencias y métricas. Fue sustituido para nuevas anotaciones y revisión por [`codebook_v3.md`](codebook_v3.md), aprobado el 2026-09-17. No reinterpretar resultados v2 como si hubieran usado v3.
> Cambios v1 → v2: la variable de postura queda en **3 clases** (hawkish/dovish/neutral); la clase `irrelevante` se reemplaza por el flag binario `es_relevante` + columna `nota` obligatoria. Fundamento: la relevancia es una propiedad del registro, no una postura (coherente con Shah et al. 2023, FOMC, 3 clases).
> Este documento conserva la fuente que rigió las rondas v2. Cualquier nueva corrección debe registrarse en la capa v3, sin sobrescribir este historial.

---

## 1. Unidad y variables

- **Unidad de codificación**: la intervención completa (un registro del corpus).
- **Variable principal (postura)**: inclinación de política monetaria expresada en el texto, en 3 categorías: `hawkish`, `dovish`, `neutral`.
- **Variable ortogonal (relevancia)**: `es_relevante` (1 por defecto; 0 si el registro es formalidad, logística o carece de contenido monetario evaluable). Cuando vale 0, la columna `nota` es **obligatoria** y registra el motivo.
- **Qué mide la postura**: la inclinación (contractiva ↔ expansiva) respecto de la TPM chilena que se desprende del texto.
- **Qué NO mide**: si la economía va bien o mal, ni si el actor comparte el diagnóstico del equipo técnico. Un diagnóstico pesimista no es `dovish` por sí solo (ver R2).

## 2. Definiciones operativas

### 2.1 `hawkish`
El texto favorece, justifica o anticipa una postura **más contractiva**: TPM más alta, subir antes/más, no bajar, o énfasis dominante en riesgos inflacionarios.

**Señales típicas**: inflación sobre el centro de la meta · expectativas desanclándose · holguras que se cierran · demanda sobrecalentada · riesgo de indexación · "adelantar la normalización" · "mi opción es subir N puntos base".

### 2.2 `dovish`
El texto favorece, justifica o anticipa una postura **más expansiva**: TPM más baja, bajar antes/más, no subir, o énfasis dominante en debilidad de actividad/empleo u holguras persistentes.

**Señales típicas**: desempleo elevado/creciente · brecha del producto negativa · riesgos a la baja del crecimiento · "espacio para mayor estímulo" · "mi opción es bajar N puntos base".

### 2.3 `neutral`
Cumple **al menos una** de:
- (a) diagnóstico descriptivo sin inclinación de política (dice *qué pasa*, no *qué hacer*);
- (b) argumentos balanceados en ambos sentidos sin resolución;
- (c) presenta escenarios/opciones sin revelar preferencia;
- (d) contenido no relacionado con la postura de política monetaria (definición coherente con el `neutral` de Shah et al. 2023).

### 2.4 El flag `es_relevante`
Vale **0** cuando el registro es formalidad o logística de sesión: encabezado del acta, declaración de quórum/asistencia, apertura o cierre de la sesión, aprobación del acta anterior, agradecimientos sin contenido. Vale **1** en todo otro caso.

**Dato del corpus**: el contenido de este tipo está concentrado en el actor `Consejo del Banco Central de Chile` con tópico `apertura_cierre` (137 registros) y en unos 67 registros del Presidente en el mismo tópico. No existe ningún actor "administrativo": son registros formales de actores reales.

**Regla de convivencia**: incluso con `es_relevante=0` se asigna una postura best-effort (casi siempre `neutral`), pero los análisis de postura se filtran por el flag. Así ningún registro se pierde y la distribución de postura no se contamina.

## 3. Reglas de decisión (aplicar en orden)

| # | Regla |
|---|---|
| **R1** | **La declaración explícita de opción domina todo** ("mi opción es subir 25 puntos" → `hawkish`, aunque el resto del párrafo sea balanceado). |
| **R2** | **Diagnóstico ≠ postura**: un diagnóstico positivo o negativo por sí solo es `neutral`. Importa si se conecta con la dirección de la política: "la actividad se desacelera" → `neutral`; "la actividad se desacelera, lo que da espacio para un estímulo adicional" → `dovish`. |
| **R3** | **Escenario internacional**: `neutral` por defecto, salvo vínculo explícito con la política doméstica ("…lo que obliga a ser más cautos en el retiro del estímulo"). |
| **R4** | **Énfasis dominante**: si hay argumentos en ambos sentidos, clasificar según el riesgo/preocupación que domina el texto. Si no hay dominancia → `neutral`. |
| **R5** | **Staff técnico** (gerentes): presunción de `neutral` (exposición informativa). Etiquetar `hawkish`/`dovish` solo si el texto **recomienda o evalúa** dirección de política. La presentación de opciones sin recomendación → `neutral`. |
| **R6** | **Consejo / acuerdo_comunicado**: etiquetar la postura del texto institucional (el acuerdo comunica una decisión y su justificación: sí tiene stance). No marcar `es_relevante=0` por ser institucional; el flag es solo para formalidad sin contenido. |
| **R7** | **Forward-looking cuenta igual que backward-looking**: "la inflación convergerá a la meta sin acción adicional" puede ser señal `dovish` según énfasis. |
| **R8** | **Flags `Cotejar_PDF`**: etiquetar igual si el texto es legible y registrar el flag en la nota. Si está dañado al punto de no ser evaluable → `es_relevante=0`, postura `neutral` y `nota="texto dañado, no evaluable"`. |
| **R9** | **Sesgo conservador**: ante la duda entre `hawkish`/`dovish` y `neutral` → `neutral`. Ante duda entre `hawkish` y `dovish` → aplicar R4; si persiste → `neutral`. Mejor perder señal que inventarla. |
| **R10** | **Frase justificante obligatoria**: registrar la cita textual (≤ 300 caracteres) que más pesa en la decisión, cuando `es_relevante=1`. Con `es_relevante=0` no se exige. |

## 4. Ejemplos semilla (reales del corpus; conjunto preliminar a validar/expandir en el piloto)

| Etiqueta | `es_relevante` | ID | Actor | Extracto | Justificación |
|---|---|---|---|---|---|
| `hawkish` | 1 | RPM-2005-02-10:136:1 | De Gregorio | "…la política monetaria es aún muy expansiva… habría que tomar la velocidad de normalización de la tasa de política monetaria" | Sesgo contractivo explícito (R1/R7) |
| `hawkish` | 1 | RPM-2005-04-07:218:1 | De Gregorio | "…los distintos indicadores de inflación subyacentes indican que la inflación estaría subiendo gradualmente…" en contexto de normalización | Preocupación inflacionaria dominante (R4) |
| `neutral` | 1 | RPM-2011-12-13:4464:1 | Lehmann (Ger. Análisis Internacional) | Exposición técnica sobre banca europea y primas de liquidez | Staff + escenario internacional sin vínculo con política doméstica (R3+R5) |
| `neutral` | 1 | RPM-2013-01-17:5322:1 | Vial | "…tono más positivo en los mercados financieros internacionales… mayor fortaleza en los datos de actividad en EE.UU." | Diagnóstico descriptivo sin inclinación (R2, caso (a)) |
| `neutral` | 0 | RPM-2015-04-16:6692:1 | Consejo | "ACTA DE LA SESIÓN DE POLÍTICA MONETARIA N° 221… se reúne el Consejo… con la asistencia de…" | Encabezado formal del acta (§2.4); nota="encabezado formal del acta" |

> **Pendiente:** Los ejemplos `dovish` definitivos se seleccionarán en el piloto (esperados con alta frecuencia en 2008–09 y 2013–14, ciclos de bajas de TPM). No se fuerzan aquí para no codificar sobre extractos truncados.

## 5. Formato de anotación (por intervención)

| Campo | Valores |
|---|---|
| `etiqueta` | `hawkish` / `dovish` / `neutral` |
| `es_relevante` | `1` (por defecto) / `0` |
| `nota` | Obligatoria si `es_relevante=0`; opcional en otro caso (caso borde, flag `Cotejar_PDF`, regla aplicada) |
| `confianza` | `alta` / `media` / `baja` |
| `frase_justificante` | Cita textual ≤ 300 caracteres (R10); vacía si `es_relevante=0` |

Salida persistida según formato largo del PLAN §4.2 (append-only, una fila por intervención × método).

## 6. Casos borde (catálogo vivo — se completa con el piloto)

| Caso | Tratamiento v2 |
|---|---|
| Ministro de Hacienda | Etiquetar el texto tal cual, sin asumir "postura de gobierno". El cargo está en L0 y se analiza por separado. |
| Lenguaje condicional ("si la inflación sigue alta, habría que subir") | Inclinación `hawkish` suave con `confianza=media` (la condición no elimina el sesgo revelado). |
| Intervención de una sola frase formal ("el Presidente declara cerrada la sesión") | `es_relevante=0`, postura `neutral`, nota explicativa. |
| Registro del Consejo de apertura/cierre (encabezado, asistencia, quórum) | `es_relevante=0`, postura `neutral`, nota explicativa. |
| Réplicas a otros consejeros ("comparto lo señalado por…") | Hereda la postura solo si el texto referenciado está en la misma intervención; si no, evaluar el contenido propio. |
| Correcciones del texto (flag de cotejo) | Ver R8. |
| Texto muy largo del staff con una recomendación final | La señal de la conclusión pesa más que el cuerpo descriptivo (R5 por el lado de la recomendación). |

## 7. Control de calidad

- **Test-retest**: 30 IDs fijos re-etiquetados por ronda → meta ≥ 90% de coincidencia en postura y en flag; divergencias se documentan en §6.
- **Gold humano**: 300 intervenciones etiquetadas a ciegas por el investigador al final del proceso → Cohen's κ vs etiquetas IA; meta κ ≥ 0.7 (ideal ≥ 0.8).
- **Toda divergencia gold–IA se analiza** y, si revela un problema del criterio, gatilla nueva versión del codebook + re-etiquetado del tramo afectado.

## 8. Versionado

| Versión | Fecha | Cambio |
|---|---|---|
| v1 | 2026-09-15 | Borrador inicial (IA), 4 clases con `irrelevante` propuesta. No se usó para etiquetar. |
| v2 | 2026-09-15 | Decisión del investigador: postura en 3 clases; `irrelevante` reemplazada por flag binario `es_relevante` + `nota` obligatoria. Neutral absorbe contenido no relacionado con postura (coherente con Shah et al. 2023). Ejemplo de encabezado reclasificado. Pendiente de revisión final. |
