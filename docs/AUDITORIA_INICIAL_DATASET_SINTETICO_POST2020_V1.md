# Auditoría inicial del dataset sintético post-2020

**Archivo:** `Dataset_Sintetico_Post2020.csv`  
**SHA-256:** `f961845e4494b0237f5991fe4a36208213d91513865a9460927ab93382754ff6`  
**Alcance:** estructura, duplicación, citas, trazabilidad, artefactos de generación y muestra semántica inicial. No se entrenó ningún modelo.

## Resultado estructural

| Control | Resultado |
|---|---:|
| Filas / IDs únicos | 1.018 / 1.018 |
| H / D / N | 357 / 364 / 297 |
| Textos normalizados únicos | 801 |
| Grupos con texto duplicado | 161 |
| Filas dentro de grupos duplicados | 378 |
| Copias excedentes | 217 |
| Duplicados con etiquetas contradictorias | 0 |
| Temas únicos | 513 |
| Fechas ficticias únicas | 38 |

Después de conservar un representante por texto normalizado quedarían **801 candidatos: H274/D285/N242**. Esta es la población máxima razonable antes de analizar paráfrasis y familias; no deben entrenarse las 1.018 filas como observaciones independientes.

No existe coincidencia exacta de texto normalizado ni de oraciones largas entre los sintéticos y `data/L0/corpus.csv`. Esto descarta copia literal directa, pero no demuestra independencia semántica.

## Citas

- 542 citas son subcadenas literales exactas tras normalizar espacios.
- 124 coinciden solamente ignorando mayúsculas/minúsculas.
- 352 no son una subcadena continua: frecuentemente agregan punto final donde el texto continúa, recortan una oración o alteran parte de la redacción.

Las citas no intervienen directamente si el entrenamiento consume solo `texto`, pero deben corregirse si se conservarán como evidencia auditada. No corresponde declarar las 1.018 citas verificadas.

## Repetición y familias

- 908 filas contienen al menos una oración larga reutilizada.
- Hay 614 oraciones largas distintas que aparecen más de una vez, con 2.489 apariciones dentro de esos grupos.
- Ninguno de los 513 valores de `tema` aparece asociado a más de una clase.
- Tampoco hay citas ni justificaciones compartidas entre clases.

`tema` y `justificacion` revelan la clase y **no pueden usarse como variables predictoras**. El modelo debe consumir únicamente `texto`. El tema puede servir provisionalmente como grupo de generación para repartir una curva de dosis, pero no reemplaza una familia de plantilla real.

Se distinguen dos lotes técnicos: en las filas 1–517, 514 textos contienen caracteres no ASCII/tildes; en las filas 518–1.018 solo 20. El segundo bloque tiene además mucha más reutilización de plantillas. Este cambio de estilo puede convertirse en una señal artificial y debe registrarse como lote.

## Muestra semántica inicial

Se inspeccionaron sistemáticamente 30 textos únicos distribuidos a lo largo del archivo: diez H, diez D y diez N, cubriendo ambos lotes. En esa muestra, **30/30 son compatibles provisionalmente con la definición de dirección respaldada v3**:

- H contiene alzas, intensificación/retiro de estímulo, sesgo contractivo u oposición sustantiva a recortes;
- D contiene recortes, relajamiento o sesgo futuro a la baja respaldado;
- N contiene mantención sin sesgo, menú abierto, postergación o balance sin dirección resuelta.

Esto es una señal favorable, no una adjudicación de los 801 textos únicos. La redacción es deliberadamente explícita y puede hacer que el entrenamiento aprenda atajos lexicales que no se repiten en actas reales.

## Metadatos ausentes

El archivo no incluye:

- generador;
- versión de prompt;
- semilla;
- familia de plantilla explícita;
- identificador de escenario independiente de `tema`.

Si esa información existe fuera del CSV, conviene agregarla antes del experimento. Si no existe, se inferirán grupos conservadores combinando lote, tema y similitud textual.

## Decisión

**La base es prometedora, pero todavía no está autorizada para entrenamiento.** Antes de ejecutar la curva de dosis se requiere:

1. conservar solo un representante de cada texto normalizado;
2. agrupar paráfrasis y oraciones reutilizadas, no solo duplicados exactos;
3. separar los dos lotes técnicos;
4. ampliar la revisión semántica estratificada, especialmente neutrales difíciles y H basados en “frenar recortes”;
5. definir una selección determinista y balanceada para 250, 500, 750 y hasta 801 textos únicos;
6. usar exclusivamente `texto` como predictor;
7. mantener los 793 reales como única validación;
8. reportar B+sintético y C+sintético por separado.

Con la deduplicación actual, una dosis de 1.018 no es válida: el máximo provisional son 801 textos únicos. Una futura curva puede usar 250/500/750/801.

## Relación con el set pre-2000

El archivo `Set_Entrenamiento_Pre_2000.xlsx` recibido coincide byte a byte con el ya auditado: SHA-256 `662ec786e234a8bd8824214c81cf8139ad0955a8f139a596ba9bbf18859ad3fb`. Sigue siendo una colección real distinta y permanece excluida hasta resolver sus seis pendientes, ocho citas problemáticas, duplicados y revisión semántica v3. No se mezclará con el sintético en el primer experimento.

## Artefactos

`data/auditoria/dataset_sintetico_post2020_v1/` contiene:

- `inventario.csv`: controles por fila;
- `incidencias.csv`: duplicados, citas y reutilización de oraciones;
- `candidatos_texto_unico.csv`: 801 representantes provisionales, aún no autorizados;
- `muestra_semantica_inicial.csv`: los 30 casos inspeccionados y su decisión provisional;
- `resumen.json`, `protocolo.json` y `manifest.json`.
