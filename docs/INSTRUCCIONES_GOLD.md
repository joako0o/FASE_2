# Guía de etiquetado del gold ciego (test set final)

Archivo: `data/muestras/gold_ciego_300.csv` — **306 intervenciones** (no 300: la estratificación por fase obligó 34 × 9 fases). Es el **test puro** del proyecto: nada de este archivo fue usado para entrenar, y la IA no etiquetará estas intervenciones. Con tus etiquetas se calcula el **Cohen's κ** IA–humano y se evalúa el modelo fine-tuneado (Fases 7/8).

## Lo que tienes que hacer

Abre el CSV (Excel o editor de texto plano) y rellena **solo** estas columnas, una por intervención:

| Columna | Qué poner |
|---|---|
| `etiqueta` | `hawkish`, `dovish` o `neutral` (según el codebook v2; abajo un resumen) |
| `confianza` | `alta` o `media` (`baja` no se usa: si dudas, deja `media` y nota por qué) |
| `es_relevante` | `1` si la intervención tiene contenido de política monetaria; `0` si es pura logística (aprobar acta, agenda, saludos) |
| `nota` | Texto libre, obligatoria si `es_relevante=0` (ej.: "trámite: solicita presentación de opciones"). Si dudaste, anota por qué |
| `frase_justificante` | La frase del texto que más justifica tu etiqueta (copia y pega). Obligatoria si `es_relevante=1` |

**Ya vienen precargadas** y no debes tocarlas: `intervencion_id`, fecha, actor, texto, metadatos (`metodo=humano_gold`, `ronda=gold_ciego`, `version_codebook=v2`, `etiquetador=usuario`).

La columna `score_continuo` es opcional para ti: déjala vacía; el κ se calcula con la clase.

## Reglas de oro

1. **A ciegas**: no mires etiquetas de la IA ni el historial de TPM si es posible; el κ mide acuerdo, no consenso por contaminación.
2. **Etiqueta lo que está ahí**: la unidad es la **intervención completa**, no la frase ni el voto final del Consejo. Si un consejero explica pero no decide, etiqueta su argumento (hawkish/dovish/neutral por dirección del razonamiento).
3. **`neutral` se usa mucho y está bien**: descripciones de datos, metodología, preguntas sin dirección, y "mantener" cuando no hay sesgo, son neutral. El corpus es mayoritariamente descriptivo en realidad (eso lo muestra el training set: ~85% neutral).
4. **Carga de tiempo**: ~15-30 segundos por intervención de las cortas y 1-2 minutos por las largas; total estimado **2 a 3 horas** (no tiene que ser de una sentada; guarda y sigue).
5. Si un texto está dañado (cortado, ilegible), etiqueta best-effort y dilo en `nota`.

## Resumen del codebook v2 (recordatorio)

- **hawkish**: favorece endurecer la política monetaria relativo al status quo (subir TPM, retirar estímulo antes, reafirmar sesgo al alza, oponerse a recortes).
- **dovish**: favorece aflojar (bajar TPM, pausa prolongada en ciclo de alzas, eliminar sesgo al alza, apoyar estimulo).
- **neutral**: descriptivo/metodológico/preguntas, o balance explícito sin inclinación.

Convenciones que la IA viene usando (para el κ son comparables — no las tienes que memorizar):

- **Votos y acuerdos** con alza/baja claros: hawkish/dovish 0.85-0.95.
- **"Voto por mantener"** dentro de un ciclo de alzas activo (opción de subir viva en la mesa): dovish leve (se va contra la corriente de la fase), salvo que el propio comunicado reafirme alzas futuras → hawkish moderado.
- **Opciones del staff (Gerente de Estudios)**: si hay recomendación explícita ("se justifica solamente la opción X"), vale la clase de la opción X; si solo presenta pros y contras de dos opciones sin inclinarse → neutral.
- Reflexiones con sesgo claro pero sin voto: neutral media con el tilt en la `nota`.

## Qué pasa después

1. Me pasas el CSV rellenado (o un rango de filas, si prefieres hacerlo por bloques).
2. Calculo el **κ por clases y por sub-estrato** (general / enriquecido-por-señal), match rates, y te devuelvo los casos de desacuerdo reunión por reunión para discusión (así se resuelven las diferencias antes del fine-tune).
3. Con el gold acordado queda fijado el **test set** del fine-tune de BETO (Fase 7) y del scoring final (Fase 8).
