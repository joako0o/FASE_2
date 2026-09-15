# CODEBOOK v1 — Codificación de Postura de Política Monetaria
**Proyecto D&H · Actas RPM Banco Central de Chile 2005–2015**

> **Estado: borrador v1 (propuesta IA), pendiente de revisión del investigador → v2.**
> Este documento es la única fuente válida para etiquetar. Cualquier cambio de criterio implica nueva versión y queda registrado aquí.

---

## 1. Unidad y variable

- **Unidad de codificación**: la intervención completa (un registro del corpus).
- **Variable**: postura de política monetaria expresada en el texto, en 4 categorías: `hawkish`, `dovish`, `neutral`, `irrelevante`.
- **Qué mide**: la inclinación de política (contractiva ↔ expansiva) que se desprende del texto, refiriéndose a la TPM chilena.
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
- (d) contenido monetario sin dirección clara.

### 2.4 `irrelevante` *(propuesta, vetable por el investigador)*
Sin contenido evaluable de política monetaria: formalidades de sesión (apertura/cierre, asistencia, aprobación del acta anterior), agradecimientos, logística.
**Nota**: el `acuerdo_comunicado` **NO** es irrelevante — es la decisión institucional y tiene postura propia (R6).

## 3. Reglas de decisión (aplicar en orden)

| # | Regla |
|---|---|
| **R1** | **La declaración explícita de opción domina todo** ("mi opción es subir 25 puntos" → `hawkish`, aunque el resto del párrafo sea balanceado). |
| **R2** | **Diagnóstico ≠ postura**: un diagnóstico positivo o negativo por sí solo es `neutral`. Importa si se conecta con la dirección de la política: "la actividad se desacelera" → `neutral`; "la actividad se desacelera, lo que da espacio para un estímulo adicional" → `dovish`. |
| **R3** | **Escenario internacional**: `neutral` por defecto, salvo vínculo explícito con la política doméstica ("…lo que obliga a ser más cautos en el retiro del estímulo"). |
| **R4** | **Énfasis dominante**: si hay argumentos en ambos sentidos, clasificar según el riesgo/preocupación que domina el texto. Si no hay dominancia → `neutral`. |
| **R5** | **Staff técnico** (gerentes): presunción de `neutral` (exposición informativa). Etiquetar `hawkish`/`dovish` solo si el texto **recomienda o evalúa** dirección de política. La presentación de opciones sin recomendación → `neutral`. |
| **R6** | **Consejo / acuerdo_comunicado**: etiquetar la postura del texto institucional (el acuerdo comunica una decisión y su justificación: sí tiene stance). |
| **R7** | **Forward-looking cuenta igual que backward-looking**: "la inflación convergerá a la meta sin acción adicional" puede ser señal `dovish` según énfasis. |
| **R8** | **Flags `Cotejar_PDF`**: etiquetar igual si el texto es legible y registrar el flag en la nota. Si está dañado al punto de no ser evaluable → `irrelevante` con nota explicativa. |
| **R9** | **Sesgo conservador**: ante la duda entre `hawkish`/`dovish` y `neutral` → `neutral`. Ante duda entre `hawkish` y `dovish` → aplicar R4; si persiste → `neutral`. Mejor perder señal que inventarla. |
| **R10** | **Frase justificante obligatoria**: registrar la cita textual (≤ 300 caracteres) que más pesa en la decisión. Sin excepciones. |

## 4. Ejemplos semilla (reales del corpus; conjunto preliminar a validar/expandir en el piloto)

| Clase | ID | Actor | Extracto | Justificación |
|---|---|---|---|---|
| `hawkish` | RPM-2005-02-10:136:1 | De Gregorio | "…la política monetaria es aún muy expansiva… habría que tomar la velocidad de normalización de la tasa de política monetaria" | Sesgo contractivo explícito (R1/R7) |
| `hawkish` | RPM-2005-04-07:218:1 | De Gregorio | "…los distintos indicadores de inflación subyacentes indican que la inflación estaría subiendo gradualmente…" en contexto de normalización | Preocupación inflacionaria dominante (R4) |
| `neutral` | RPM-2011-12-13:4464:1 | Lehmann (Ger. Análisis Internacional) | Exposición técnica sobre banca europea y primas de liquidez | Staff + escenario internacional sin vínculo con política doméstica (R3+R5) |
| `neutral` | RPM-2013-01-17:5322:1 | Vial | "…tono más positivo en los mercados financieros internacionales… mayor fortaleza en los datos de actividad en EE.UU." | Diagnóstico descriptivo sin inclinación (R2, caso (a)) |
| `irrelevante` | RPM-2015-04-16:6692:1 | Consejo | "ACTA DE LA SESIÓN DE POLÍTICA MONETARIA N° 221… se reúne el Consejo… con la asistencia de…" | Formalidad de apertura (§2.4) |

> **Pendiente:** Los ejemplos `dovish` definitivos se seleccionarán en el piloto (esperados con alta frecuencia en 2008–09 y 2013–14, ciclos de bajas de TPM). No se fuerzan aquí para no codificar sobre extractos truncados.

## 5. Formato de anotación (por intervención)

| Campo | Valores |
|---|---|
| `etiqueta` | `hawkish` / `dovish` / `neutral` / `irrelevante` |
| `confianza` | `alta` / `media` / `baja` |
| `frase_justificante` | Cita textual ≤ 300 caracteres (R10) |
| `nota` | Opcional: caso borde, flag `Cotejar_PDF`, regla aplicada |

Salida persistida según formato largo del PLAN §4.2 (append-only, una fila por intervención × método).

## 6. Casos borde (catálogo vivo — se completa con el piloto)

| Caso | Tratamiento v1 |
|---|---|
| Ministro de Hacienda | Etiquetar el texto tal cual, sin asumir "postura de gobierno". El cargo está en L0 y se analiza por separado. |
| Lenguaje condicional ("si la inflación sigue alta, habría que subir") | Inclinación `hawkish` suave con `confianza=media` (la condición no elimina el sesgo revelado). |
| Intervención de una sola frase formal ("el Presidente declara cerrada la sesión") | `irrelevante`. |
| Réplicas a otros consejeros ("comparto lo señalado por…") | Hereda la postura solo si el texto referenciado está en la misma intervención; si no, evaluar el contenido propio. |
| Correcciones del texto (flag de cotejo) | Ver R8. |
| Texto muy largo del staff con una recomendación final | La señal de la conclusión pesa más que el cuerpo descriptivo (R5 por el lado de la recomendación). |

## 7. Control de calidad

- **Test-retest**: 30 IDs fijos re-etiquetados por ronda → meta ≥ 90% de coincidencia; divergencias se documentan en §6.
- **Gold humano**: 300 intervenciones etiquetadas a ciegas por el investigador al final del proceso → Cohen's κ vs etiquetas IA; meta κ ≥ 0.7 (ideal ≥ 0.8).
- **Toda divergencia gold–IA se analiza** y, si revela un problema del criterio, gatilla nueva versión del codebook + re-etiquetado del tramo afectado.

## 8. Versionado

| Versión | Fecha | Cambio |
|---|---|---|
| v1 | 2026-09-15 | Borrador inicial (IA). Pendiente de revisión del investigador. |
