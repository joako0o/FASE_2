# Por qué se deterioró TF-IDF al añadir 59 ejemplos

**17-09-2026. Diagnóstico de los mismos modelos ya evaluados; no nueva variante ni cambios de etiquetas.**

## Conclusión para decidir el siguiente paso

El problema observado **no se reduce a tener pocos H/D**. Hay evidencia de tres dificultades:

1. **Asociaciones léxicas que no distinguen el acto discursivo.** Una pregunta sobre un alza, una alternativa descartada y una decisión de alza comparten vocabulario, pero no la misma postura.
2. **La ampliación refuerza fórmulas y contexto que también aparecen en N.** Nombres, cargos, expresiones de votación, “mantener la TPM”, escenarios y sesgos ganan peso; una recomendación explícita puede quedar superada por el resto del texto.
3. **Fronteras de criterio entre referencias.** Algunos textos de mantención se clasifican por riesgo inflacionario o trayectoria implícita; otros por decisión presente/sesgo. Esto debe auditarse con un criterio uniforme, sin cambiar etiquetas retrospectivamente para recuperar la métrica.

La meta 300/300 sigue registrada, pero **sumar ejemplos del mismo tipo no asegura corregir esas distinciones**. Recomiendo priorizar coherencia y contrastes semánticos en la siguiente selección, no cambiar de modelo ni agregar neutros indiscriminadamente.

## Qué se revisó

- Los **16 textos completos** con predicciones diferentes: nueve errores nuevos, tres corregidos y cuatro errores que cambiaron de tipo. Total: **57.722 caracteres**.
- Reconstrucción de los cinco ajustes originales y ampliados con los mismos parámetros/cohorte; **A, B y predicción final reproducidos exactamente sobre los 793 casos de cada condición**.
- Descomposición del margen en **12.005 contribuciones léxicas**, con interceptos aparte y cierre algebraico comprobado.
- Tres vecinos entre los nuevos ejemplos **permitidos en train de ese fold** por cada caso: 48 relaciones de similitud. No se usan vecinos de la reunión validada.

La comparación de rendimiento sigue siendo la publicada: F1 H/D media **0,747060→0,713526**, errores **51→57**, inversiones **15→17**. No se volvió a puntuar con otras referencias ni se optimizó una variante para estos casos.

## 1. Preguntar no equivale a adherir: un error especialmente claro

**RPM-2008-07-10:1975:1**, N→H:

> “consulta al Consejero señor Sebastián Claro si se suma a la votación de la mayoría de los Consejeros”

La unidad pregunta si otro actor se suma a un alza de 50 pb; no contiene su respuesta. Entre los nuevos ejemplos del train de ese fold, el vecino más próximo es **RPM-2008-09-04:2098:1**, H, cuya cita dice:

> “se adhiere a la decisión de la mayoría de los Consejeros en cuanto a subir la Tasa de Política Monetaria en 50 puntos base”

Ese ejemplo nuevo tiene una etiqueta H justificable: es una adhesión efectiva. El problema es que **se parecen mucho en palabras, no en función**. Su coseno es 0,436; eso no demuestra que un único vecino haya causado el error.

El margen H−N pasa de **−0,031347 a +1,036279**. La señal de `consulta` sigue favoreciendo N, e incluso aumenta ligeramente en esa dirección (−0,07118→−0,07792). Sin embargo, las contribuciones positivas de las familias `subir`, `50 puntos base` y `los consejeros` crecen y dominan. No es correcto decir simplemente que “no vio la palabra consulta”.

## 2. Sí hay una recomendación de alza, pero otras asociaciones la superan

**RPM-2008-09-04:2088:1**, H→D:

> “se inclina por sugerir un alza de 50 puntos base en esta ocasión”

La resolución es clara: subir 50, no bajar. Discutir si conviene 50 o 75 no cambia el signo.

El margen D−H pasa de **−0,412760 a +0,039149**. El término `subir` continúa favoreciendo H y su contribución en ese margen se vuelve más negativa (−0,05877→−0,07372). Pero numerosas asociaciones cambian hacia D, incluidas `senor beltran de ramon`, `division operaciones` y `por las razones`.

Cada uno de varios n-gramas del nombre pasa aproximadamente de −0,00961 a +0,00336 en D−H. No se deben sumar esos ejemplos como evidencia independiente: son características solapadas. El vecino nuevo más próximo es un texto del mismo actor que **sí recomienda bajar** (RPM-2014-02-18:6043:1, coseno 0,2081).

**Hipótesis apoyada por los pesos:** se está aprovechando parcialmente el estilo/cargo/actor y el vocabulario de contexto, no solo el contenido de la decisión. Esto no prueba que los nombres sean la única causa ni autoriza eliminarlos sin un ensayo separado.

## 3. “Sesgo neutral” no puede clasificarse como palabra aislada

**RPM-2012-06-14:4897:1**, N→D, termina con:

> “mantener la TPM en su nivel actual del 5% anual, con un sesgo neutral para las próximas decisiones”

Describe riesgos europeos importantes, pero distingue ese escenario del equilibrio doméstico y sostiene neutralidad. El margen D−N pasa de **−0,011814 a +0,191010**.

Las contribuciones relativas a D de `mantener la tpm` aumentan de 0,01182 a 0,02350; las de `sesgo neutral`, de 0,00196 a 0,00907. Esto parece paradójico, pero en datos correctos puede haber **recorte actual + sesgo neutral futuro = D**. La misma frase de sesgo tiene sentido diferente si la acción actual es mantener.

La tarea necesita distinguir **acción actual, dirección futura respaldada y nivel de compromiso**. No bastaría con imponer una regla léxica “neutral significa N”.

**RPM-2012-02-14:4648:1**, también N→D, es una frontera distinta: mantiene en zona de normalidad y dice que no se descartan bajas futuras, pero sin oportunidad/magnitud claras. Su vecino nuevo más próximo (RPM-2011-12-13:4508:1, D, coseno 0,2190) sí vota **introducir un sesgo a la baja**. La posibilidad abierta y el compromiso explícito no son intercambiables.

## 4. Negación, retiro e historia: señales que el vocabulario pierde

Dos de los cuatro casos que siguieron errados ilustran el mecanismo:

- **RPM-2012-03-15:4721:1**, N de referencia, cambia H→D. Dice **“descartar la opción de recortar la TPM”**, no recomendarla. `recortar la tpm` aparece en dos documentos del train original y en dos nuevos: pasa de df=2 a df=4 y entra al vocabulario con min_df=3. Su nueva contribución D−H es +0,01741, aunque en este caso está dentro de una alternativa rechazada.
- **RPM-2007-05-10:1260:1**, N de referencia, cambia H→D. Dice **“haber quitado el sesgo a la baja”**. Los n-gramas de `sesgo la baja` ganan peso hacia D. En ese fold, `quitado` aparece en cero documentos originales y uno nuevo, por lo que no supera min_df=3; no está entre las características activas del modelo. `el sesgo la baja`, en cambio, pasa de df=1 a df=6 y sí entra.

El analizador estándar omite palabras de una letra, de ahí la forma técnica `sesgo la baja` de los n-gramas; el texto original no se modificó. **Leer el documento completo como entrada no garantiza que toda distinción relevante sobreviva al vectorizador.**

Esto no implica que deba repetirse la búsqueda de n-gramas 1–6: ya fue realizada. Tampoco demuestra que bajar min_df resolvería el problema sin ruido o sobreajuste. Se necesita una hipótesis y prueba nueva si se decide cambiar la representación.

## 5. Narrativa compartida con recortes, sin recorte doméstico

**RPM-2012-09-13:5084:2**, N→D, dedica gran parte del texto a Europa, China, liquidez y desaceleración. Su conclusión doméstica sugiere mantener y esperar información.

El margen D−N pasa de **−0,430260 a +0,068568**. Ganan peso `escenario economico`, `desaceleracion`, `2012` y otras expresiones descriptivas. Su nuevo vecino más próximo es **RPM-2011-12-13:4507:3**, D, coseno 0,2830: comparte narrativa, pero aquel sí concluye **recomendar rebajar 25 pb**.

La similitud no hace incorrecta la etiqueta del nuevo ejemplo; muestra por qué necesitamos aprender la distinción entre **describir el contexto y respaldar una acción**, y entre **política extranjera y doméstica**.

## 6. No todos los “errores nuevos” son igualmente inequívocos

La evaluación se mantiene fija, pero la lectura revela fronteras que conviene documentar:

| Caso | Cambio | Frontera observada, sin adjudicar otra etiqueta |
|---|---|---|
| 192:1, marzo 2005 | H→N | H es implícito: tasa neutral mayor y brechas cerrándose, sin voto de alza; también defiende prudencia |
| 197:1, marzo 2005 | N→H | Mantener hoy dentro de una reducción gradual del impulso, tras relatar dos alzas |
| 672:1, mayo 2006 | D→H | Pausa respaldada, pero trayectoria del escenario central con alzas futuras; menor velocidad no significa automáticamente D |
| 4648:1, febrero 2012 | N→D | Posibilidad de bajas futuras sin compromiso claro frente a sesgo explícito |
| 1607:2, diciembre 2007 | D→H | Recomienda esperar ante riesgos contrapuestos; la nueva H no sigue esa resolución, aunque el límite D/N de “esperar” también requiere coherencia |

**No se afirma que sus referencias estén erradas ni se cambian para mejorar F1.** Se señala que hay que aplicar de modo uniforme el criterio de dirección respaldada a toda la intervención, frente a tono macro, decisión puntual y trayectoria.

También importa revisar los aciertos nuevos:

- **1049:3**, enero 2007, N→D: recomienda recortar; corrección semánticamente clara.
- **5748:1**, agosto 2013, D→N: mantener y “mismo tenor” del comunicado anterior, sin describir su sesgo en esta unidad. No se debe heredar una dirección ajena. El margen final N−D es solo +0,011935.
- **1102:1**, febrero 2007, N→H: aumenta el score contra una referencia H, pero la resolución es mantener con lenguaje neutral y discusión futura diferida. La H parece depender del énfasis inflacionario. **Mejor score en ese caso no prueba mejor comprensión.**

Los otros cambios errados se documentaron: 1090:4 expone razones para recortar y mantener y acaba con sesgo neutral; 6965:1 cuestiona un alza por falta de desanclaje y pasa de H a N, que sigue sin acertar su referencia D.

## 7. Qué dicen los números del modelo, y qué no

Para cada caso se calculó el margen **clase ampliada menos clase control**. Todos eran negativos y pasan a positivos, con cierre numérico verificado.

Se usó la identidad simétrica:

`Δ(x·w) = media(x)·Δw + media(w)·Δx`, con el intercepto separado.

Entre los nueve errores nuevos, el componente de coeficientes tiene mayor magnitud absoluta que los otros dos componentes en **8/9**; el componente de representación apunta **en contra** del cambio de etiqueta en **7/9**. Por tanto, no respalda atribuirlo todo a que “el IDF se ensució”. Es una descomposición algebraica, no un porcentaje causal del problema; los coeficientes también responden a la representación y los términos nuevos usan una convención de ceros.

El vocabulario crece entre **3.268 y 3.544 términos** por fold; no se retiran términos anteriores. La ponderación balanced no quedó accidentalmente sin aplicar: por ejemplo, en fold 1 los pesos H/D/N cambian de **2,7661 / 3,8930 / 0,4199** a **2,3617 / 3,1121 / 0,4434**, como corresponde al nuevo train. No se puede explicar la mayor predicción D diciendo que se le aumentó manualmente su peso: no ocurrió.

A se reproduce y vale 1 en todos los 16 cambios. **El fallo estudiado está en B, no en que A haya cambiado o bloqueado esos textos.** No se detectó un error de alineación de IDs, folds, referencias o parámetros.

## 8. Recomendación concreta

1. **Mantener el control original.** No aprobar el ampliado ni reinterpretar el score negativo como éxito.
2. **Antes de continuar por cantidad, cerrar un criterio operacional uniforme** para pregunta/adhesión, historia, alternativa descartada, mantención con sesgo, posibilidades futuras y dirección implícita. Gran parte ya está acordada; corresponde detectar su aplicación inconsistente, no cambiarla silenciosamente.
3. **Buscar contraste, no más N al azar:** ejemplos reales de entrenamiento que compartan vocabulario pero difieran en quién respalda qué. Pregunta frente a adhesión, recorte frente a rechazo del recorte, mantener con sesgo frente a mantener sin dirección. Los N ya son abundantes; falta evidenciar estas distinciones, no igualar cuotas mecánicamente.
4. **No meter estos 16 casos en su propio train** ni generar variantes a medida de ellos. Son desarrollo conocido. Cualquier selección nueva debe preservar purga y trazabilidad.
5. Si luego se autoriza una prueba, fijar **una sola hipótesis**: por ejemplo, representación de acción/objeto/adhesión frente al texto completo, o control del atajo de nombres. No lanzar simultáneamente un modelo nuevo, más datos y nuevos parámetros, porque no sabremos qué cambió.

La meta 300/300 no queda cancelada, pero no debería dictar las etiquetas ni desplazar los controles de calidad. No se ejecutó ninguna de esas pruebas propuestas en este diagnóstico. La generación sintética continúa pendiente y no autorizada para ejecución.

## Artefactos y reproducción

Carpeta `data/auditoria/diagnostico_ampliacion_tfidf_59_v1/`:

- `lectura_casos.json`: lectura cualitativa de las 16 unidades, citas y límites de criterio; sin etiquetas corregidas.
- `margenes.csv`, `contribuciones.csv`: cierres algebraicos y todos los aportes, no solo una selección favorable.
- `vecinos_nuevos_train.csv`: relaciones de similitud restringidas al train permitido.
- `reajustes.json`, `frecuencias_auditadas.json`: tamaños, balanced y presencia de términos relevantes.
- `protocolo.json`, `resumen.json`, `manifest.json`, `verificacion.json`: procedimiento e integridad/replay.

El gestor ofrece `diagnosticar-ampliacion-tfidf --salida RUTA_NUEVA`; solo reconstruye las mismas condiciones para examinarlas, sin persistir modelos. Protocolo legible: [PROTOCOLO_DIAGNOSTICO_AMPLIACION_TFIDF](PROTOCOLO_DIAGNOSTICO_AMPLIACION_TFIDF.md).
