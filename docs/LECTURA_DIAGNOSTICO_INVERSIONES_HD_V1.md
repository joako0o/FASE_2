# Qué está fallando al distinguir H de D

## Conclusión

**La preocupación por las inversiones de dirección está justificada. El TF-IDF reconoce algunas expresiones de alza/recorte, pero puede perder la decisión al agregar el resto del texto y no resuelve de forma fiable el objeto, la condición o el horizonte de esa expresión. No es solo un problema de longitud ni de predecir neutral.**

Esta conclusión combina la relectura completa de diez intervenciones con la descomposición exacta de sus decisiones lineales. Las asociaciones medidas no equivalen a una explicación causal del lenguaje; el siguiente modelo todavía debe probarse.

## Qué hicimos y qué no

- Releímos **10 textos completos, 40.937 caracteres**: cinco D→H y cinco H→D de la referencia corregida.
- Reconstruimos los cinco modelos por fold y comprobamos **las 793 predicciones A/B/finales** contra el experimento 36. No cambiaron.
- En los diez casos A=1. El fallo de dirección ocurre en **B**, no porque la puerta de relevancia fuerce neutralidad.
- Descompusimos cada margen error−referencia en intercepto y todos sus aportes TF-IDF: **8.558 features activos** en total.
- Dejamos aparte **cinco inversiones con referencias ambiguas**. Nueve de las diez seleccionadas tenían referencia respaldada por el agente; la restante es la corrección N→D de De Ramón aceptada por el investigador. Ninguna es una nueva anotación ciega.
- No cambiamos etiquetas, no entrenamos un candidato distinto, no abrimos las 306 respuestas y no ejecutamos BETO.

## Tres hallazgos concretos

### 1. La señal correcta existe, pero puede perder frente al resto

**Consejo, enero de 2007 — `RPM-2007-01-11:1057:1`.** El acuerdo dice explícitamente que reduce la TPM desde 5,25% a 5%. Los n-gramas «reducir la tasa» y «reducir la tasa de» aportan cada uno **−0,0621** al margen H−D, es decir, favorecen correctamente D. Sin embargo, la suma de los demás términos termina inclinando la clasificación a H.

El término «25» aporta **+0,0510** hacia H y aparece dentro de **5,25%**, no como una instrucción de subir 25 puntos. También aportan H fórmulas como «de política monetaria» y «mensual». No hay una única palabra culpable: el margen completo es **+1,0152** tras combinar todos los aportes y el intercepto.

Cuando B recibe solo el recorte explícito, predice D. Esto demuestra que el contexto completo cambia la decisión, **no** que ya tengamos un extractor automático de la frase correcta. Además, el híbrido numérico anterior no mejoró consistentemente: este ejemplo no justifica adoptarlo retrospectivamente.

### 2. Mencionar una acción no es respaldarla; el objeto también importa

**De Ramón, agosto de 2015 — `RPM-2015-08-13:6965:1`.** El autor argumenta que subir solo se justificaría bajo un desanclaje que **no está presente**. En el texto completo, «subir la», «subir la tasa» y «subir» aportan respectivamente **+0,0447**, **+0,0373** y **+0,0364** hacia H frente a D. Son n-gramas solapados, no tres evidencias semánticas independientes. La cita aislada da N, no D: acortar tampoco resuelve plenamente la condición rechazada.

**Consejo, septiembre de 2015 — `RPM-2015-09-15:7045:1`.** Anuncia que habrá que **reducir el elevado estímulo monetario**, comenzando pronto. La dirección es contractiva aunque mantenga hoy la TPM. «Reducir» aporta **+0,0296** al margen D−H equivocado, junto con expresiones de mantener. La primera cita aislada da N: no basta con entregar una frase que contenga la señal.

**Schmidt-Hebbel, febrero de 2008 — `RPM-2008-02-07:1672:1`.** Recomienda una política menos restrictiva y suprimir el sesgo. «Un alza», «alza» e «inflacionaria» aportan hacia H en el texto completo, cuyo cuerpo discute primas y expectativas. B incluso predice H con la recomendación aislada. Aquí no se puede atribuir todo el problema a los párrafos previos.

### 3. No todos los fallos se explican por una palabra dominante

**García, diciembre de 2015 — `RPM-2015-12-17:7212:1`.** Vota por subir 25 puntos. La suma de los aportes del texto al margen D−H es **−0,0165**, ligeramente favorable a H, pero el intercepto aprendido es **+0,2300** y el margen final queda en **+0,2134**, favorable a D.

**De Gregorio, octubre de 2010 — `RPM-2010-10-14:3491:1`.** Vota subir 25 en lugar de 50 y continuar retirando estímulo. La suma textual es **−0,0326** a favor de H; el intercepto **+0,1395** produce un margen D−H de **+0,1069**.

En ambos, B reconoce H al recibir solo el voto. El intercepto es un parámetro ajustado del clasificador, **no** prueba automática de desbalance de clases ni una probabilidad de error. Estos resultados desaconsejan explicar todos los fallos contando palabras como «baja» o «estímulo».

## La sonda de citas: resultado completo

La primera cita de cada caso se fijó después de leerlo completo y **antes** de reconstruir los coeficientes. Se introdujo solo esa cita en B, sin cambiar el modelo y sin elegir luego una cita mejor.

| Caso | Referencia | B texto completo | B primera cita |
|---|---|---|---|
| De Gregorio, oct-2009 (`2758:1`) | D | H | N |
| Larraín, ago-2011 (`4272:1`) | D | H | N |
| Consejo, ene-2007 (`1057:1`) | D | H | D |
| Schmidt-Hebbel, feb-2008 (`1672:1`) | D | H | H |
| Naudon, dic-2015 (`7210:1`) | H | D | H |
| Marfán, mar-2008 (`1731:2`) | H | D | D |
| García, dic-2015 (`7212:1`) | H | D | H |
| Consejo, sep-2015 (`7045:1`) | H | D | N |
| De Gregorio, oct-2010 (`3491:1`) | H | D | H |
| De Ramón, ago-2015 (`6965:1`) | D | H | N |

**Cuatro coincidencias, cuatro N y dos inversiones persistentes.** Es una sonda informada por etiquetas, no accuracy de validación ni prueba de una mejora. Las cuatro coincidencias contienen votos/recomendaciones de alza o recorte explícitos. En otros casos la dirección depende de duración, sesgo, condiciones o interpretación del objeto.

**La referencia pertenece a la intervención completa, no necesariamente a su primera cita aislada.** Al aislarla también podemos quitar contexto legítimamente necesario: en De Gregorio 2009 la primera cita conserva el voto y las medidas, pero no la duración que aparece en la segunda. Por ello, las cuatro salidas N no se cuentan como cuatro errores semánticos nuevos sobre fragmentos ni prueban por sí solas incapacidad contextual. La inversión de la recomendación explícita «menos restrictiva» sí ofrece evidencia más directa de que no todo se explica por un cuerpo demasiado largo.

Marfán merece una cautela adicional: vota mantener hoy, conserva el sesgo alcista y prefiere una combinación de alza e intervención cambiaria. La referencia H no significa que vote subir hoy. Su clasificación es más defendible que la de los cinco ambiguos excluidos, pero no es tan simple como un voto inmediato de alza.

Tampoco quedó demostrada la hipótesis de que la normalización fiscal causara el fallo de Larraín: entre sus mayores aportes locales positivos aparecen términos genéricos, y «ministro de Hacienda» favorece D. No se convierte una hipótesis plausible sobre el texto en causalidad demostrada por el mero hecho de haberla planteado.

## Qué recomiendo hacer ahora

**Probar un candidato contextual con la referencia ya corregida**, no seguir cambiando etiquetas para que coincidan con el TF-IDF. BETO sigue siendo un candidato razonable, no una mejora garantizada. Su descarga permanece bloqueada según la comprobación de la etapa 36; esta etapa no repitió solicitudes ni fingió un ajuste transformer.

La comparación queda diseñada con:

1. **Mismos datos, cinco folds purgados y puerta A.** Solo cambia B; no se mezclan nuevos cambios de etiquetas con arquitectura.
2. **Texto completo**, segmentado cuando exceda 512 tokens, incluyendo su final. Sin citas manuales como entradas ni ventanas elegidas con la referencia. La agregación por media también puede diluir una conclusión: habrá que comprobarlo, no asumir que segmentar resuelve el problema.
3. **H→D y D→H por separado, sobre soportes fijos**, junto con H/D→N y N→H/D. Un modelo no debe parecer mejor por esconder toda dirección en N.
4. **Criterios previos de desarrollo:** +0,02 de F1 H/D medio y mejora en ≥3/5 folds; pérdida macro ≤0,005 y recall H/D ≤0,02; menos inversiones sin aumentar H/D→N. No modificar repetidamente estos criterios después de ver resultados.
5. **Límites claros:** los diez casos son diagnóstico conocido, no un test nuevo ni diez ejemplos adicionales para entrenar. Una afirmación de generalización exige confirmación realmente nueva; no reutilizar el examen antiguo como si fuera intacto.

No recomiendo una regla que convierta cualquier «subir» en H o cualquier «reducir» en D, ni otra ronda general de n-gramas. Tampoco pedir que el investigador vuelva a anotar lo que ya revisó.

## Evidencia y reproducción

- [Informe técnico de los diez casos](DIAGNOSTICO_INVERSIONES_HD_V1.md): textos/citas, mayores aportes de ambos signos, interceptos, residuos y cinco ambiguos separados.
- [Protocolo fijado antes de reconstruir](PROTOCOLO_DIAGNOSTICO_INVERSIONES_HD_V1.md).
- `data/auditoria/inversiones_hd_v1/resultados/`: todos los aportes, textos completos, scores, sondas y predicciones reconstruidas.
- `data/auditoria/inversiones_hd_v1/verificacion.json`: pruebas, replay, hashes previos y huella de esta interpretación final del agente. Este documento es síntesis manual posterior al diagnóstico, no salida de un modelo nuevo.
