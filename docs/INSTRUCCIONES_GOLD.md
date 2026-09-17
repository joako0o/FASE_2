# Gold recibido: validación y correcciones pendientes

## Archivos vigentes

- **Original devuelto:** `gold_ciego_300_listo.xlsx`. Se conserva intacto.
- **Marco canónico congelado:** `data/muestras/gold_ciego_300.csv` (306 IDs y textos). Sus respuestas vacías son intencionales; no se rellena ni regenera a mano.
- **Citas pendientes:** `data/auditoria/2026-09-16/incidencias_gold.csv` (86 filas, incluye orden y fila Excel).
- **Control actual de citas y fechas:** `data/auditoria/2026-09-16/incidencias_gold_actual.csv` (una fila por incidencia; puede haber varias por intervención).

Las plantillas vacías XLSX/CSV alternativo y sus generadores fueron eliminados tras recibir las respuestas. No hay que volver a rellenar el instrumento desde cero.

## Evaluación de clases ya realizada

TF-IDF ya se evaluó contra estas 306 decisiones, después de seleccionar hiperparámetros solo con IA y guardar las predicciones en un proceso sin abrir las respuestas humanas: 260 coincidencias, accuracy 0,8497, macro-F1 0,6775 y κ 0,6458. Ver [informe](EVALUACION_TFIDF_GOLD.md).

La evaluación de clases no fuerza la importación documental ni modifica citas: estas siguen pendientes. No corregir etiquetas para concordar con el modelo. Si las respuestas se revisan sustantivamente, preservar esta versión y reportar el cambio; el test ya se examinó.

## Estado de la devolución

Las 306 filas tienen etiqueta, confianza, relevancia, nota y frase. La importación sigue bloqueada por 85 citas no literales y una cita de 334 caracteres. La columna `fecha` recorre diariamente desde 2026-09-15 hasta 2027-07-17, compatible con autorrelleno. **El usuario confirmó posteriormente que todas las anotaciones fueron el 2026-09-16**; usar esa fecha explícita al importar, sin sobrescribir el libro original. `fecha_reunion` está intacta.

## Procedencia confirmada por el anotador

El usuario declaró que decidió las etiquetas y luego consultó a una IA si estaba de acuerdo y por qué. Confirmó que **mantuvo todas sus etiquetas**. Reportar: «Etiquetado humano inicial con revisión posterior de IA, sin cambios en las etiquetas según declaración del anotador».

Esto permite conservar sus decisiones como referencia humana con esa salvedad; no acredita un protocolo completamente ciego ni autoría humana independiente de notas/citas/confianza. No se han auditado registros de las decisiones previas. Declaración y hash del original: [procedencia_gold.json](../data/auditoria/2026-09-16/procedencia_gold.json).

## Reglas para corregir sin alterar la referencia humana

1. Guardar una **nueva versión** del libro, sin reemplazar el original recibido.
2. Reemplazar las citas afectadas por fragmentos contiguos **copiados literalmente** del texto, hasta 300 caracteres. No unir fragmentos con `...`; preservar incluso errores OCR. La comparación solo normaliza espacios.
3. No cambiar silenciosamente etiquetas ni confianza para hacerlas coincidir con IA. Si una decisión humana cambia, registrar la revisión del anotador por separado.
4. Mantener IDs, orden, textos, actores, cargos y demás metadatos originales. Se permite reordenar filas, no modificar su campo `orden`.
5. Registrar fecha real de anotación en formato `AAAA-MM-DD`. Si el anotador confirma una única fecha para todas las respuestas, puede proporcionarse explícitamente al importador; no se infiere del autorrelleno.
6. Incluir la procedencia declarada arriba al reportar κ; la contraparte IA de evaluación sí debe generarse sin acceso a las respuestas humanas.

## Dominios vigentes

| Campo | Regla |
|---|---|
| `etiqueta` | hawkish / dovish / neutral |
| `confianza` | alta / media en el instrumento humano |
| `es_relevante` | 0 / 1 |
| `nota` | Obligatoria si relevancia 0 |
| `frase_justificante` | Obligatoria en **todos los relevantes**, incluidos neutral (R10); si se aporta en irrelevantes también debe ser literal |
| `fecha` | Fecha real, válida y no futura |

Relevancia 0 implica neutral; diagnóstico económico puede ser relevante 1 y neutral. El criterio de postura está en el [codebook v2](codebook_v2.md). Las [convenciones históricas](CONVENCIONES_ETIQUETADO.md) documentan cómo se produjo el training, no autorizan cambiar el gold retrospectivamente.

## Comandos

```bash
# Solo valida: no escribe ni altera fuentes.
~/venvs/fase2/bin/python scripts/fusionar_gold_llenado.py gold_ciego_300_listo.xlsx --validar --fecha-anotacion 2026-09-16

# Después de corregir las citas: salida NUEVA con la fecha confirmada.
~/venvs/fase2/bin/python scripts/fusionar_gold_llenado.py ruta/al/gold_corregido.xlsx \
  --fecha-anotacion 2026-09-16 --salida data/muestras/gold_ciego_300_llenado.csv
```

`--fecha-anotacion AAAA-MM-DD` solo se usa con una fecha confirmada por el anotador. `--permitir-parcial` permite una devolución incompleta sin errores en las filas llenadas. No existe `--forzar`; el importador rechaza sobrescrituras y genera un manifiesto `.provenance.json` con hashes y fecha de importación.

La salida es un **instrumento validado**, no el esquema L1 con probabilidades. Para κ basta emparejar clases por ID; no inventar probabilidades humanas. La contraparte TF-IDF ya se obtuvo en un proceso sin acceso a respuestas humanas. Una anotación adicional de IA conversacional sería un control opcional diferente, no un requisito pendiente de este examen.
