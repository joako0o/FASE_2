# Instrucciones para el etiquetado gold ciego (~300 intervenciones)

Este instrumento valida el etiquetado automático de la tesis: tú etiquetas
306 intervenciones **sin ver las etiquetas de la IA** y luego comparamos
(kappa de Cohen). Es un test puro: ninguna de estas intervenciones está en el
training set de 1.025.

## Archivo

`data/muestras/gold_ciego_300.csv` — una fila por intervención, en orden
aleatorio (no por fecha ni actor). Puedes abrirlo en Excel/LibreOffice.

## Columnas que debes llenar (una por fila)

| columna | qué anotar |
|---|---|
| `etiqueta` | `hawkish` / `dovish` / `neutral` (minúsculas, sin tilde) |
| `confianza` | `alta` o `media` (qué tan seguro estás de tu etiqueta) |
| `es_relevante` | `1` normalmente; `0` solo si es pura logística (suspensión, apertura de sesión, lista de asistentes, agradecimientos) |
| `nota` | breve, obligatoria si `es_relevante=0`; opcional en el resto |
| `frase_justificante` | **verbatim** del texto (copiar-pegar, máx. 300 caracteres) que justifica tu etiqueta; recomendada siempre, obligatoria en hawkish/dovish |

No modifiques las demás columnas (`orden`, `intervencion_id`, `metodo`,
`ronda`, etc.).

## Criterio (resumen del codebook v2)

- **hawkish**: favorece o justifica política **más restrictiva** de lo que está
  sobre la mesa: subir la TPM, subirla más o antes, restringir, o mantener una
  postura restrictiva cuando el menú dominante apunta a relajar. El ancla es
  **relativa**: lo relevante es la posición frente al menú de opciones del
  momento, no un umbral absoluto de TPM.
- **dovish**: lo simétrico hacia lo expansivo (bajar, pausar un ciclo de
  alzas, mantener en el mínimo, ampliar estímulo).
- **neutral**: análisis de datos sin posición de política monetaria, diagnóstico
  descriptivo, o intervenciones logísticas. Cuando dudes entre una clase y
  neutral, pregunta: ¿el texto argumenta *dirección* de política o solo
  *describe*? Describir ("la inflación subió") no es halcón; lo halcón es
  convertirlo en razón para restringir.
- Los votos explícitos mandan: "voto por subir 25 pb" es hawkish claro.
  Presentar un **menú de opciones sin recomendación** (staff) es neutral aunque
  las opciones sean hawkish.
- Si `es_relevante=0`, igual deja `etiqueta=neutral` y explica en `nota`.

## Reglas prácticas

- Cada intervención se evalúa **de forma autónoma**: no uses recuerdos de otras
  reuniones ni lo que creas que piensa ese consejero.
- La `frase_justificante` debe estar contenida literalmente en el texto (el
  validador la verificará).
- No busques las etiquetas de la IA: el ejercicio pierde valor si no es ciego.
- No hay apuro: conviene hacerlo en sesiones de ~30-40 intervenciones.

Al terminar, avísame y corro el kappa y las curvas de acuerdo por clase.
