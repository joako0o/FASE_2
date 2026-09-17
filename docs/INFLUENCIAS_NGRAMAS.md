# Qué palabras y frases influyen en el modelo

## Conclusión

**Sí hay fundamento para investigar un híbrido contextual, pero no para asignar clases mediante otra lista de palabras.** El modelo aprende señales útiles y también asociaciones de números, fórmulas y nombres que no tienen dirección monetaria propia. La estabilidad entre folds no garantiza que una señal sea semánticamente correcta.

Esta revisión corresponde al candidato **TF-IDF (1,4), sin diccionario, en las cinco particiones IA**; no a seis modelos de longitudes distintas ni al examen humano. Se reconstruyeron las 793 predicciones exactamente, sin modificar parámetros.

## 1. Qué significa «relevante» en este informe

- **Coeficiente global:** para B se compara cada clase con el promedio de las otras dos, y también H frente a D. Para A se usa el margen binario relevante–irrelevante. No son etiquetas de frases.
- **Aporte local:** valor TF-IDF × diferencia de coeficientes. La suma de todos los aportes más el intercepto reproduce el margen lineal. Se guardan los cinco mayores aportes de cada signo y el residuo que no se muestra.
- El margen no es una probabilidad ni el efecto causal de borrar una palabra: al borrar texto cambiarían la normalización y otros n-gramas. Las frases solapadas son características correlacionadas, no evidencias independientes.
- B solo determina la clase final si A permite relevancia; sus explicaciones se marcan inactivas cuando A fuerza neutral.

## 2. Términos principales por partición

Primeros cinco por coeficiente contrastivo positivo de clase frente al resto. Los 25 completos, frecuencias y reuniones de entrenamiento están en `top_global.csv`. Los tokens se muestran tal como los utiliza el modelo, sin acentos.

| Fold | Favorecen H | Favorecen D | Favorecen N |
|---|---|---|---|
| 1 | `25 puntos base`; `25 puntos`; `25`; `puntos base`; `puntos` | `bajar la`; `mantener`; `bajar la tasa`; `bajar`; `la tasa` | `consulta`; `en anual`; `monetaria en anual`; `politica monetaria en anual`; `gerente de division estudios` |
| 2 | `25 puntos base`; `25 puntos`; `25`; `de politica monetaria`; `puntos base` | `bajar la`; `bajar la tasa`; `bajar`; `mantener`; `reducir la tasa` | `consulta`; `en anual`; `gerente`; `monetaria en anual`; `politica monetaria en anual` |
| 3 | `25 puntos`; `25 puntos base`; `25`; `puntos base`; `puntos` | `bajar la`; `bajar la tasa`; `bajar`; `mantener`; `la tasa` | `consulta`; `gerente`; `el gerente`; `gerente de`; `gerente de division estudios` |
| 4 | `25 puntos base`; `25 puntos`; `25`; `puntos base`; `puntos` | `bajar la`; `bajar la tasa`; `bajar`; `mantener`; `la tasa` | `consulta`; `gerente`; `en anual`; `monetaria en anual`; `politica monetaria en anual` |
| 5 | `25 puntos base`; `25 puntos`; `25`; `puntos base`; `puntos` | `bajar la`; `bajar la tasa`; `bajar`; `reducir la tasa`; `reducir la tasa de` | `consulta`; `en anual`; `monetaria en anual`; `politica monetaria en anual`; `gerente` |

### Frecuencia y estabilidad: ejemplos interpretables

Coeficientes medios dentro del contraste indicado; df es el rango de intervenciones del **train relevante de B** que contienen el término, no apariciones totales. No se debe comparar la magnitud entre contrastes como si fuera una escala de importancia universal.

| Término | Contraste | Coeficiente medio | df train | Folds con signo positivo / presente |
|---|---|---:|---:|---:|
| `25 puntos base` | hawkish_vs_dovish | 1.7939 | 113–124 | 5/5 |
| `subir la` | hawkish_vs_dovish | 1.2719 | 39–48 | 5/5 |
| `bajar la tasa` | dovish_vs_hawkish | 1.3082 | 16–18 | 5/5 |
| `mantener la tasa` | dovish_vs_hawkish | 1.0295 | 102–111 | 5/5 |
| `reducir la tasa` | dovish_vs_hawkish | 0.9688 | 5–9 | 5/5 |
| `rebajar` | dovish_vs_hawkish | 0.9005 | 3–3 | 4/4 |
| `consulta` | neutral_vs_resto | 0.7831 | 84–88 | 5/5 |
| `gerente` | neutral_vs_resto | 0.5892 | 257–278 | 5/5 |

- Se analizó la unión de los top 25: **261 pares término–contraste / 199 términos únicos**. Ninguno de esos pares cambia de signo donde está presente. Doce pares están ausentes en algún fold; ausencia no significa coeficiente cero.
- Esto NO demuestra estabilidad de todo el vocabulario. Los modelos comparten gran parte del entrenamiento y siempre incluyen las mismas 559 intervenciones; los cinco ajustes no son independientes.
- `rebajar` tiene peso alto pero solo tres intervenciones de train donde existe. Es una señal escasa, distinta de una señal frecuente.

## 3. Lo que muestran los errores y los aciertos

En esta validación IA hay **62 errores de postura**: **17 H↔D**, 34 neutrales predichos H/D y 11 H/D predichos neutrales. No confundir estos números con el examen humano anterior.

La revisión contextual del agente IA cubrió los **17 errores H/D completos**, más seis aciertos (dos por clase) y cuatro errores con neutral. En los aciertos largos se leyeron fragmentos iniciales/finales; no se revisaron todos los textos de validación ni todas las ocurrencias. Las etiquetas IA se conservan, no se adjudican como nuevas verdades.

### A. Números sin acción, y decimales fragmentados

`25 puntos base` favorece H de manera estable, pero una magnitud no define dirección. El tokenizador estándar también descarta tokens de un carácter y fragmenta números:

| Texto | Tokens resultantes antes de generar n-gramas |
|---|---|
| `desde 5,25% a 5% anual` | `desde`, `25`, `anual` |
| `en 3% anual` | `en`, `anual` |

Así aparecen fragmentos como `en anual`, asociados a neutral, que no son expresiones lingüísticas completas.

**Caso `RPM-2007-01-11:1057:1` (fold 3, IA D → modelo H):** el Consejo «acordó reducir la tasa de interés de política monetaria desde 5,25% a 5% anual». El token `25` aporta **+0,0478** al margen H−D; `reducir la tasa` aporta **−0,0626**. El margen completo es **+0,8562**: hay muchas otras contribuciones, no se atribuye todo el error al decimal.

### B. Mantener no equivale siempre a dovish

**`RPM-2007-06-14:1305:1` (fold 1, IA H → D):** mantiene la tasa, pero pide «introducir claramente un sesgo al alza». `mantener` aporta **−0,0449** a H−D. Hay que conservar la orientación futura.

**`RPM-2006-12-14:1019:1` (fold 3, IA H → D):** se discute bajar, pero se considera prematuro. `bajar la tasa` aporta **−0,0522** a H−D, pese al rechazo de esa opción. Una regla de negación de tres palabras no resuelve por sí sola el argumento completo.

El contraste también aparece frente a neutral: **`RPM-2012-08-16:5039:2` (IA N → D)** es una mantención por unanimidad. No modificar su etiqueta ni convertir todas las mantenciones en una sola clase.

### C. Acción respaldada frente a menú, pasado, otros países o condiciones

**`RPM-2008-02-07:1684:1` (fold 4, IA D → H):** «hubiera sido partidario de subir» es contrafactual; el voto actual es mantener. `subir la` aporta **+0,0421** a H−D.

**`RPM-2011-08-18:4272:1` (fold 3, IA D → H):** hay CDS y tasas extranjeras, normalización fiscal y muchos números; la recomendación monetaria local es mantener y quitar el sesgo restrictivo. `puntos` y `puntos base en` figuran entre los aportes H: no toda tasa/cifra describe una acción local de TPM.

### D. El objeto de «reducir» cambia el significado

**`RPM-2015-09-15:7045:1` (fold 5, IA H → D):** se mantiene la tasa y se anuncia «reducir el elevado estímulo monetario actual». `reducir` aporta **−0,0261** a H−D. Reducir estímulo no es reducir TPM.

**`RPM-2015-12-17:7210:1` (fold 4, IA H → D):** recomienda aumentar 25 puntos base aunque la política siga en terreno expansivo. Distinguir el nivel de expansividad del cambio propuesto; también distinguir baja del crecimiento de baja de TPM.

### E. El modelo a veces reconoce el voto, pero no le da suficiente peso

**`RPM-2010-10-14:3491:1` (fold 5, IA H → D):** vota subir la TPM en 25 puntos base. `subir la` aporta **+0,0695** y `25 puntos base` **+0,0517** a H−D. Pero el aporte textual total es **+0,0863** y el intercepto **−0,2067**: margen final **−0,1204**. La combinación completa, no una palabra aislada, decide.

El caso correcto **`RPM-2005-11-10:500:1` (IA H → H)** también contiene un voto de alza; allí `25 puntos base` aporta **+0,0852**. La misma señal puede participar tanto en aciertos como en errores.

### F. Fórmulas y nombres no son postura

**`RPM-2005-11-10:503:2` (IA N → H)** contiene solamente un encabezado de acuerdo sin indicar la acción. `politica monetaria` aporta **+0,1270** al margen H−N. En neutral aparecen `gerente`, `lehmann`, `soto`; son candidatos a un control de dependencia de nombres/cargos, no palabras a convertir en reglas semánticas.

## 4. Relevancia: analizar A aparte

- A fuerza neutral en **160** casos, todos con referencia IA neutral: no introduce errores finales de postura entre esos 160. En dos evita una predicción H/D que B habría hecho sin la máscara.
- Sin embargo, A tiene **26 errores de relevancia**: 17 irrelevantes pasan como relevantes y 9 relevantes se bloquean. Esos nueve tienen postura IA neutral, por eso no empeoran la métrica de postura. No afirmar que A funciona perfectamente.
- Entre los principales términos que favorecen irrelevancia están `presidente`, `sesion`, `palabra`, `horas`, `corbo`; para relevancia aparecen `tasa`, `inflacion` y también palabras gramaticales. Las fórmulas de sesión son plausibles para A; los nombres son asociaciones que conviene auditar, no reglas seguras.

## 5. Híbrido que propondría estudiar — todavía no entrenado

**Candidato principal: texto completo + evidencia de decisión contextual + alerta de contradicción.**

1. Mantener TF-IDF (1,4) como referencia de texto completo.
2. Añadir una representación separada de los fragmentos de postura: acción y objeto (TPM/estímulo/otra variable), quién la respalda, si es voto o alternativa rechazada/condicionada, y si es actual, pasada o futura. No limitarse a la última oración: un sesgo futuro puede determinar la postura.
3. Tratar números sin confundir nivel, magnitud y dirección; comparar una normalización estructurada con el tokenizador actual. No eliminar todos los números ni imponer una dirección a `25`.
4. Como ablación separada, evaluar si enmascarar nombres personales en B reduce dependencia de autor/fórmula. No borrar ciegamente cargos o texto útil de A.
5. Si la lectura de decisión y el modelo completo discrepan, derivar a revisión o a una segunda etapa contextual, en lugar de sobrescribir automáticamente con una regla. El umbral debe definirse con training/validación y medirse con cobertura y errores por clase; los márgenes actuales no son probabilidades calibradas.

**No se promete mejora.** Primero habría que prefijar una comparación pequeña, separar aportes de cada cambio y conservar el baseline. Estos ejemplos ya son datos de desarrollo del híbrido. Una confirmación independiente requiere otro conjunto y control de textos repetidos; los 306 humanos conocidos no se vuelven a presentar como test intacto.

## 6. Entregables y controles

- [Términos principales por fold](../data/evaluacion/influencias_ngramas_v1/top_global.csv).
- [Estabilidad y frecuencia](../data/evaluacion/influencias_ngramas_v1/estabilidad.csv); los coeficientes de todos los folds para esos términos están en `coeficientes_seleccionados.csv`.
- [Revisión de las 17 confusiones H/D](../data/evaluacion/influencias_ngramas_v1/revision_17_confusiones_hd.csv), con extractos verificados y razones, sin cambiar etiquetas.
- [Contribuciones por intervención](../data/evaluacion/influencias_ngramas_v1/aportes_locales.csv), [márgenes completos](../data/evaluacion/influencias_ngramas_v1/margenes.csv) y [casos IA](../data/evaluacion/influencias_ngramas_v1/casos_validacion.csv).
- `scripts/23_diagnosticar_influencias.py --salida /ruta/nueva` reproduce las tablas; requiere las mismas dependencias fijadas. Las interpretaciones de este informe y del CSV revisado son revisión del agente IA, no etiquetas regeneradas por el script.
- Todas las sumas se verificaron contra los márgenes originales. Protocolos/manifiestos conservan hashes; no se sobrescriben experimentos. Permanecen 34 textos de validación repetidos respecto de train. No se entrenó un híbrido, no se reemplazó el modelo y no se abrieron respuestas humanas.
