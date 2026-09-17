# N-gramas y diccionario de señales: revisión y validación IA

## Qué se hizo

- De las 1.352 intervenciones IA, 559 de 52 reuniones se reservaron para construir y revisar el léxico.
- Las otras 793 intervenciones aportaron cinco folds de validación por reunión. Descubrimiento se agrega solo al train de cada fold.
- Umbral prefijado: n-gramas de 1–4 palabras en al menos 5 intervenciones y 3 reuniones distintas.
- Catálogo de descubrimiento: 9247 n-gramas. Revisados por IA: 73 candidatos, con hasta 3 contextos cada uno; no revisión humana ni lectura de todas las ocurrencias.
- Priorización por frecuencia y asociación relativa H/D, sin asignar la dirección automáticamente por esa asociación.
- No se leyó el Excel humano, no se volvió a predecir gold y no se reemplazó TF-IDF v1.

## Diccionario revisado

| Categoría | Cantidad |
|---|---:|
| contextual | 36 |
| sin_direccion | 32 |
| restrictiva | 3 |
| expansiva | 2 |

### Señales direccionales

| Expresión | Señal | Precaución / razón |
|---|---|---|
| recorte | expansiva | En los contextos revisados nombra un recorte de TPM, incluso como opción o expectativa; señal léxica expansiva, no voto automático. |
| aumentar la tasa | restrictiva | Describe una opción o acción de alza. Puede aparecer en menús o antecedentes sin respaldo del hablante: es señal adicional, no etiqueta automática. |
| bajar la tasa | expansiva | Acción de reducción de tasa; aparece en acuerdos de baja y también al considerar prematura esa opción. Requiere contexto para postura final. |
| subir la tpm | restrictiva | Alza explícita de TPM. Hay votos favorables y un ejemplo que la rechaza con negación posterior; por eso no es clasificador determinista. |
| acordo aumentar la tasa | restrictiva | Acuerdo explícito de alza en los ejemplos. Puede narrarse una decisión pasada: señal restrictiva textual, no necesariamente nueva recomendación. |

**Asociación no es significado:** `impulso monetario` es contextual (puede retirarse o ampliarse); `vota por mantener` depende del menú/ciclo; `Marfán agradece` es cortesía, aunque aparezca asociado a dovish.

Las características son cuatro indicadores binarios (restrictiva/expansiva afirmada/negada) añadidos a B. Negación izquierda de hasta tres tokens; no invierte etiquetas. La coincidencia más larga evita solapamientos. No resuelve negación posterior, atribución, pasado, menú o condicionales.

## Comparación sobre la misma reserva IA

A (relevancia) queda fijo; B usa unigramas o n-gramas 1–4, sin/con diccionario. C=2, min_df=3, balanced, sin nueva búsqueda. TF-IDF usa el tokenizador estándar del baseline; el léxico conserva tokens de una letra y límites de oración.

| Variante | Macro-F1 medio folds | Macro-F1 OOF conjunto | F1 H | F1 D | Recall H | Recall D |
|---|---:|---:|---:|---:|---:|---:|
| unigramas | 0.7500 | 0.7497 | 0.6974 | 0.5872 | 0.7681 | 0.6531 |
| unigramas_lexico | 0.7562 | 0.7586 | 0.7237 | 0.5905 | 0.7971 | 0.6327 |
| ngramas_1_4 | 0.7803 | 0.7810 | 0.7397 | 0.6372 | 0.7826 | 0.7347 |
| ngramas_1_4_lexico | 0.7124 | 0.7243 | 0.7347 | 0.4808 | 0.7826 | 0.5102 |

### Diferencia de añadir el diccionario (media de folds)

- unigramas: **+0.0061**; mejora en 3/5 folds, empeora en 2/5.
- ngramas_1_4: **-0.0679**; mejora en 1/5 folds, empeora en 4/5.

## Interpretación y límites

Soporte de validación: hawkish: 69, dovish: 49, neutral: 675.
Esta es una comparación exploratoria interna, no un nuevo test humano. La reserva no se usó para extraer/revisar el léxico, pero pertenece al training IA sobre el que ya se eligió el baseline anterior. No interpretar pequeñas diferencias como significativas con solo cinco folds.
No comparar directamente estos números con 0,7264 de la búsqueda previa (otra composición de train/validación) ni con el recall humano 55,1 % / 53,1 %. No se midió una mejora humana en esta sesión.
Los umbrales de frecuencia dejan fuera expresiones poco comunes, aunque puedan ser importantes. Los candidatos no revisados NO reciben automáticamente una etiqueta semántica.
- Cobertura de señales en reserva: 56/793 intervenciones.
- El catálogo completo de las 1.352, generado solo después de congelar y validar, tiene 23252 n-gramas que superan los mismos umbrales. Es descriptivo: no se usó para modificar esta versión.
- Los datos, etiquetas, codebook y examen humano anteriores permanecen intactos. No hay adopción automática de la variante con mayor puntuación.

## Archivos útiles

- `data/lexico/ngramas_v1/diccionario_v1.csv`: 73 decisiones con categoría y justificación.
- `contextos_revision.csv`: ejemplos y sus IDs de descubrimiento.
- `catalogo_descubrimiento.csv` / `candidatos_revision.csv`: frecuencias, reuniones, TF-IDF medio y asociaciones usadas en revisión.
- `data/evaluacion/lexico_ngramas_v1/catalogo_training_completo.csv`: catálogo completo descriptivo.
- `catalogo_revisado.csv` en esa carpeta: catálogo completo enlazado con categorías revisadas; el resto queda `no_revisado`.
- `comparacion_variantes.csv`, `resultados_folds.csv`, `predicciones_validacion.csv`, `metricas.json`: evaluación y cobertura.
- Los manifiestos registran hashes de diccionario, partición, entradas y salidas. No se sobrescriben versiones anteriores.

Para repetir: script 20 hacia una carpeta nueva; conservar la revisión v1 y sus hashes; script 21 con `--lexico` y `--salida` nuevos. Las decisiones de revisión son un artefacto manual del agente, no una etiqueta que el script vuelva a generar.
