# Revisión humana del entrenamiento: 30 casos

**24/30 decisiones coinciden con la etiqueta IA; 6 difieren.**

**Esto compara anotaciones, no predicciones de un clasificador.** No es un nuevo test humano ni permite extrapolar una tasa de errores al corpus.

## Recepción y vinculación

- Original recibido desde el enlace GitHub proporcionado por el investigador, fijado al commit de `recepcion.json`, con Git blob SHA1 y SHA256 verificados. Se conserva sin cambios en `data/auditoria/revision_entrenamiento_30_v1/devolucion_humana_v1/`.
- La devolución usa una hoja simplificada de cinco columnas: ID_30, texto, decisión, cita y motivo. No es el libro de cuatro hojas, pero la identidad se verifica por ID y texto completo, no por el orden supuesto de las filas.
- 29 textos idénticos y 1 iguales tras normalizar únicamente espacios. No se aceptan recortes, cambios léxicos o casos sustituidos.
- No trae relevancia, fecha de anotación, ayuda recibida o declaración de acceso previo a etiquetas IA. Quedan **no declaradas**. El recibo UTC no se usa como fecha de anotación. No se afirma revisión ciega independiente.

## Resultado de la comparación de postura

| Etiqueta IA de origen | Humano H | Humano D | Humano N |
|---|---:|---:|---:|
| hawkish | 10 | 0 | 0 |
| dovish | 0 | 5 | 5 |
| neutral | 1 | 0 | 9 |

Muestra seleccionada con 10 casos por clase **IA**, no humana. Una proporción global de acuerdo aquí está ponderada por ese diseño, no por la distribución real del corpus.

| Estrato IA | Coincidencias / decisiones comparables |
|---|---:|
| hawkish | 10/10 |
| dovish | 5/10 |
| neutral | 9/10 |

## Casos que requieren revisión conjunta

Se conserva tu decisión tal como la enviaste. Un desacuerdo no demuestra automáticamente que tú o la IA estén equivocados. Las citas se muestran sin sustituirlas por una elección del agente.

| Caso | ID original | IA | Humano | Motivo del investigador |
|---|---|---|---|---|
| R01 | RPM-2005-06-09:288:4 | neutral | hawkish | Observacion: Simpre tienden a usar neutral como comodin , es raro que se guien directamente por H&D, neutral es siempre una opcion plusible |
| R03 | RPM-2006-11-16:976:1 | dovish | neutral | Solo es descriptivo y abre a debatir ciertos asuntos relacionado a la expectativa que se proyecta a futuro  |
| R08 | RPM-2005-05-12:262:1 | dovish | neutral | Solo da un analisis descriptivo |
| R12 | RPM-2005-06-09:291:1 | dovish | neutral | Dice textualmente mantener la tasa |
| R17 | RPM-2011-10-13:4392:1 | dovish | neutral | Dice textualmente mantener la tasa |
| R21 | RPM-2010-01-14:2887:1 | dovish | neutral | Se acordo mantener Tasa |

## Citas y alcance documental

| Control de cita | Casos |
|---|---:|
| literal_hasta_300 | 18 |
| ausente_o_marcador | 12 |

Los marcadores «-» o «.» se registran como ausencia de cita, no como evidencia literal válida. La normalización para literalidad solo ajusta espacios; no corrige palabras o puntuación. Una cita literal tampoco garantiza que fundamente la postura.
Estas incidencias **no invalidan ni cambian las decisiones de postura para esta comparación**. Sí impiden declarar completa una importación canónica bajo la guía v2, junto con la relevancia no declarada. No se rellenan los campos con las etiquetas/citas IA.

## Próximo paso y límites

Revisar las discrepancias con el texto completo y R1–R5: opción respaldada frente a menú, diagnóstico frente a postura, escenario extranjero y mantenimiento frente a sesgo. Documentar una decisión conjunta antes de proponer cualquier corrección, en una versión separada.
No se entrenó BETO, no se modificaron las 1.352 etiquetas IA y no se abrió el examen de 306. La muestra procede de desarrollo, fue balanceada por IA y excluye los IDs/copias del examen y de la validación reutilizada según el protocolo original. Es una auditoría acotada, no una demostración de calidad global.

## Reproducción

`scripts/30_comparar_revision_humana.py` valida primero identidad y después une la clave IA. Rechaza sobrescribir. Guarda decisiones originales, citas y texto completo, incidencias, matriz y hashes de fuentes/salidas.

```bash
python scripts/30_comparar_revision_humana.py --salida /ruta/nueva --informe /ruta/informe_nuevo.md
```
Los detalles de recepción, comparación y posterior repetición se conservan junto al original. La revisión cualitativa del agente, si se realiza, se documenta aparte y no sobrescribe las decisiones.
