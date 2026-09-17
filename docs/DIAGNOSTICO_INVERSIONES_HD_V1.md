# Diagnóstico de diez inversiones H/D

**Se reconstruyó el TF-IDF corregido y se explicaron sus diez inversiones con referencias más claras. No se cambiaron etiquetas ni se probó un candidato nuevo.**

## Qué se comprobó

- Las 793 predicciones A/B/final coinciden exactamente con el experimento 36. Los errores siguen siendo 15 inversiones H↔D, 12 H/D→N y 24 N→H/D.
- De las 15 inversiones, cinco conservan referencia ambigua y quedan aparte. Las diez examinadas son nueve respaldadas por el agente y una corrección aceptada: no son diez nuevos ejemplos humanos independientes.
- Se releyeron **40.937 caracteres íntegros**. En los diez casos A=1: la inversión ocurre en el clasificador de postura B, no por forzar N desde relevancia.
- Cada margen predicción−referencia se reconstruye exactamente como intercepto más aportes TF-IDF. Se guardan todos los términos activos; las tablas breves no ocultan su residuo.
- **Sonda de evidencia:** B coincide con la referencia en 4/10 primeras citas aisladas, fijadas antes de obtener los coeficientes. En 6/10 no coincide. No es una mejora de precisión: las citas fueron seleccionadas manualmente con conocimiento de la referencia.

Si la cita aislada se reconoce, el contexto completo cambia la decisión del modelo, pero esto no demuestra que exista un extractor capaz de encontrarla. Si también falla aislada, no basta culpar a la longitud. Las frecuencias y pesos son asociaciones del train, no comprensión del objeto, tiempo o negación.

## Resumen de casos

| ID | Referencia → B texto completo | B primera cita | Margen error−referencia |
|---|---|---|---:|
| RPM-2009-10-13:2758:1 | D → H | N | 0.395456 |
| RPM-2011-08-18:4272:1 | D → H | N | 0.431276 |
| RPM-2007-01-11:1057:1 | D → H | D | 1.015190 |
| RPM-2008-02-07:1672:1 | D → H | H | 0.586304 |
| RPM-2015-12-17:7210:1 | H → D | H | 0.253693 |
| RPM-2008-03-13:1731:2 | H → D | D | 0.242439 |
| RPM-2015-12-17:7212:1 | H → D | H | 0.213449 |
| RPM-2015-09-15:7045:1 | H → D | N | 0.408783 |
| RPM-2010-10-14:3491:1 | H → D | H | 0.106880 |
| RPM-2015-08-13:6965:1 | D → H | N | 0.139190 |

## Evidencia y contribuciones por caso

Un aporte positivo favorece la predicción errónea frente a la referencia; uno negativo favorece la referencia. No es una probabilidad ni el efecto causal de borrar esa palabra. Los n-gramas se solapan y el TF-IDF está normalizado. La sonda usa solo B, no la puerta A.

### RPM-2009-10-13:2758:1 — José De Gregorio Rebeco

**Referencia D; modelo H; fold 2; 2179 caracteres completos.**

> vota por mantener la TPM en 0,5% y las medidas de política monetaria excepcionales adoptadas en julio.

> cuyo propósito ha sido fortalecer el compromiso de mantener la tasa de interés baja por varios trimestres

D por sostener tasa mínima y medidas excepcionales. La retirada futura de facilidades queda como tema de revisión, no como una decisión de elevar ahora la TPM. El riesgo de inflación demasiado baja refuerza la acomodación.

**Hipótesis previa:** El vocabulario de recuperación y de una salida futura podría contrapesar el compromiso expansivo; verificar cuáles términos aportan realmente al margen H−D.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| la evolucion | +0.033082 | 39 / 21 / 81 |
| un aumento | +0.032017 | 43 / 10 / 68 |
| tener | +0.031766 | 37 / 13 / 85 |
| un aumento de | +0.029843 | 30 / 7 / 31 |
| pausado | +0.029825 | 16 / 4 / 5 |
| la evolucion de | +0.027626 | 30 / 16 / 47 |
| mantener | -0.043947 | 51 / 49 / 75 |
| baja | -0.035302 | 24 / 39 / 155 |
| mantener la | -0.033083 | 42 / 41 / 59 |
| cual se | -0.028743 | 1 / 10 / 14 |
| mantener la tasa | -0.024338 | 30 / 34 / 47 |
| por varios | -0.023577 | 1 / 8 / 5 |

Intercepto: **-0.091971**; suma de todos los aportes: **+0.487428**; residuo de términos no mostrados: **+0.492260**. Margen final: **+0.395456**.

Primera cita aislada: B predice **N**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** No confundir instrumentos de liquidez con una variación de TPM. La frase sobre un deterioro de la recuperación presenta redacción extraña y se conserva, sin reconstruirla.

### RPM-2011-08-18:4272:1 — Felipe Larraín Bascuñán

**Referencia D; modelo H; fold 3; 8090 caracteres completos.**

> es necesario quitar el sesgo restrictivo a la política monetaria de los Comunicados anteriores

La recomendación doméstica es pausar y retirar el sesgo restrictivo: D. La normalización fiscal del Ministerio y las políticas extranjeras no se convierten en su recomendación sobre la TPM chilena.

**Hipótesis previa:** Una exposición extensa incluye normalización fiscal, actividad dinámica y tasas extranjeras; comprobar si señales genéricas de ese cuerpo dominan sobre la recomendación final.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| puntos | +0.027691 | 77 / 31 / 91 |
| base en | +0.026329 | 36 / 8 / 21 |
| puntos base en | +0.025664 | 34 / 7 / 20 |
| el crecimiento | +0.020919 | 40 / 14 / 85 |
| de inflacion | +0.020820 | 73 / 36 / 125 |
| escenario internacional | +0.018977 | 16 / 2 / 20 |
| de hacienda | -0.023988 | 8 / 13 / 56 |
| hacienda | -0.023988 | 8 / 13 / 56 |
| forma | -0.023230 | 23 / 23 / 51 |
| ministro de | -0.021144 | 7 / 12 / 49 |
| ministro de hacienda | -0.021144 | 7 / 12 / 49 |
| senor ministro de | -0.020648 | 5 / 10 / 26 |

Intercepto: **-0.283078**; suma de todos los aportes: **+0.714354**; residuo de términos no mostrados: **+0.708094**. Margen final: **+0.431276**.

Primera cita aislada: B predice **N**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** No atribuir causalmente el error al párrafo fiscal solo porque existe. Los coeficientes pueden mostrar asociaciones distintas. La postura no se hereda al comunicado separado de la misma reunión.

### RPM-2007-01-11:1057:1 — Consejo del Banco Central de Chile

**Referencia D; modelo H; fold 3; 2503 caracteres completos.**

> acordó reducir la tasa de interés de política monetaria desde 5,25% a 5% anual.

D por recorte explícito, repetido en el acuerdo y comunicado. La fortaleza de la demanda y la mejora de la actividad no revierten esa decisión.

**Hipótesis previa:** Comprobar si las fórmulas del comunicado y el diagnóstico desplazan la instrucción de reducir; no basta suponer que el modelo no conoce reducir.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| 25 | +0.051042 | 75 / 26 / 50 |
| de politica monetaria | +0.026998 | 93 / 54 / 152 |
| mensual | +0.022877 | 27 / 7 / 38 |
| politica monetaria | +0.022059 | 104 / 66 / 182 |
| brechas de | +0.021154 | 23 / 4 / 8 |
| anos | +0.021144 | 24 / 4 / 112 |
| reducir la tasa | -0.062136 | 0 / 4 / 1 |
| reducir la tasa de | -0.062136 | 0 / 4 / 1 |
| reducir la | -0.039422 | 6 / 8 / 6 |
| reducir | -0.034711 | 13 / 12 / 16 |
| trimestres | -0.023554 | 17 / 15 / 39 |
| en la tpm | -0.019805 | 2 / 7 / 4 |

Intercepto: **-0.283078**; suma de todos los aportes: **+1.298268**; residuo de términos no mostrados: **+1.374759**. Margen final: **+1.015190**.

Primera cita aislada: B predice **D**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** Caso especialmente claro. Se conserva la repetición del acuerdo/comunicado: no se deduplica internamente para obtener una predicción mejor.

### RPM-2008-02-07:1672:1 — Klaus Schmidt-Hebbel Dunker

**Referencia D; modelo H; fold 4; 4212 caracteres completos.**

> se sugiere adoptar una política levemente menos restrictiva en esta ocasión, manteniendo la Tasa de Política Monetaria en 6,25%, pero suprimiendo todo sesgo a dicha decisión.

D por recomendación final de menor restricción y supresión del sesgo. La larga discusión de expectativas inflacionarias considera el argumento opuesto, pero no es la conclusión elegida.

**Hipótesis previa:** Verificar si las menciones repetidas a alzas, premios y expectativas aportan hacia H pese a la recomendación final D; menos restrictiva exige resolver una comparación.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| un alza | +0.059164 | 38 / 10 / 31 |
| alza | +0.055213 | 61 / 24 / 160 |
| inflacionaria | +0.050364 | 42 / 9 / 50 |
| un aumento | +0.036499 | 46 / 10 / 72 |
| puntos base | +0.033273 | 75 / 32 / 67 |
| puntos | +0.029375 | 77 / 34 / 96 |
| en un | -0.026686 | 41 / 37 / 95 |
| reduccion | -0.025750 | 21 / 18 / 43 |
| mes | -0.019367 | 39 / 38 / 176 |
| de investigacion | -0.018692 | 5 / 4 / 2 |
| de investigacion economica | -0.018692 | 5 / 4 / 2 |
| gerente de investigacion | -0.018692 | 5 / 4 / 2 |

Intercepto: **-0.229990**; suma de todos los aportes: **+0.816294**; residuo de términos no mostrados: **+0.680284**. Margen final: **+0.586304**.

Primera cita aislada: B predice **H**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** No inferir D del recorte de la Fed: la evidencia decisiva es la recomendación doméstica. No se borra el riesgo inflacionario para convertir el texto en un caso simple.

### RPM-2015-12-17:7210:1 — Alberto Naudon Dell'Oro

**Referencia H; modelo D; fold 4; 6083 caracteres completos.**

> se inclina por recomendar un aumento de 25 puntos base en esta Reunión, para llevar la tasa de política a 3,5%.

> la sugerencia de la Gerencia de División Estudios es la de mantener el sesgo al alza

H por recomendar subir 25 puntos y conservar un sesgo al alza, aunque el nivel posterior siga siendo expansivo y las alzas futuras se espacien. El texto sí expresa la dirección; no hay que importar una tasa de partida desde otra intervención.

**Hipótesis previa:** Comprobar si la debilidad de actividad y las palabras sobre expansividad empujan a D, y si la recomendación aislada se reconoce como H.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| baja | +0.036968 | 21 / 41 / 149 |
| sesgo | +0.034164 | 18 / 23 / 20 |
| mantener | +0.024742 | 47 / 49 / 65 |
| tiempo | +0.021858 | 20 / 26 / 85 |
| contexto | +0.021729 | 17 / 22 / 49 |
| bajos | +0.020080 | 5 / 11 / 30 |
| un aumento | -0.039852 | 46 / 10 / 72 |
| alza | -0.036562 | 61 / 24 / 160 |
| un aumento de | -0.029368 | 31 / 6 / 30 |
| 25 puntos base | -0.027063 | 68 / 18 / 34 |
| 25 puntos | -0.026975 | 68 / 18 / 35 |
| de 25 puntos base | -0.023557 | 40 / 5 / 22 |

Intercepto: **+0.229990**; suma de todos los aportes: **+0.023703**; residuo de términos no mostrados: **+0.047536**. Margen final: **+0.253693**.

Primera cita aislada: B predice **H**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** Mantener la política en terreno expansivo describe nivel; reducir su expansividad describe dirección. Una media de segmentos en BETO también podría diluir esta distinción; no basta cambiar arquitectura.

### RPM-2008-03-13:1731:2 — Manuel Marfán Lewis

**Referencia H; modelo D; fold 4; 4752 caracteres completos.**

> vota por mantener la tasa de política monetaria en su nivel actual, manteniendo el sesgo al alza en el Comunicado.

H por conservar explícitamente el sesgo al alza y preferir una combinación de alza e intervención cambiaria. Sin el segundo instrumento rechaza subir hoy. La referencia es más defendible que en los cinco ambiguos, pero no tiene la simplicidad de un voto de alza inmediata.

**Hipótesis previa:** Comprobar si los argumentos contra subir sin intervención dominan frente al sesgo y a la combinación preferida.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| estacionario | +0.049287 | 0 / 4 / 3 |
| sesgo | +0.038070 | 18 / 23 / 20 |
| votacion | +0.037369 | 1 / 11 / 7 |
| equilibrio estacionario | +0.032056 | 0 / 2 / 1 |
| consecuencia el | +0.026426 | 2 / 7 / 2 |
| en consecuencia el | +0.026426 | 2 / 7 / 2 |
| elevar | -0.054265 | 19 / 2 / 4 |
| elevar la | -0.053941 | 15 / 1 / 2 |
| elevar la tasa de | -0.049723 | 11 / 0 / 1 |
| elevar la tasa | -0.038959 | 12 / 1 / 2 |
| compensaciones | -0.022788 | 11 / 1 / 9 |
| compensaciones inflacionarias | -0.021691 | 10 / 1 / 6 |

Intercepto: **+0.229990**; suma de todos los aportes: **+0.012449**; residuo de términos no mostrados: **+0.044182**. Margen final: **+0.242439**.

Primera cita aislada: B predice **D**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** No traducir H como voto de alza hoy: vota mantener. La condición de intervención cambiaria es sustantiva. Conservar la cautela de horizonte y paquete; no afirmar error indiscutible por el solo estado respaldada.

### RPM-2015-12-17:7212:1 — Pablo García Silva

**Referencia H; modelo D; fold 4; 4178 caracteres completos.**

> su voto es por aumentar la TPM en 25 puntos base, a 3,5%.

H por voto explícito de alza. La comunicación neutral y el carácter aún expansivo del nivel de tasa no convierten la decisión en D ni en N. El menú inicial acaba en una preferencia elegida.

**Hipótesis previa:** Examinar si las asociaciones con mantener, expansividad y sesgo neutral superan la evidencia de subir; probar el voto aislado sin llamarlo un clasificador nuevo.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| sesgo | +0.052959 | 18 / 23 / 20 |
| tpm | +0.036668 | 22 / 31 / 44 |
| la tpm | +0.033144 | 22 / 30 / 36 |
| de opciones | +0.032628 | 7 / 14 / 9 |
| mantener | +0.031068 | 47 / 49 / 65 |
| la minuta | +0.028175 | 10 / 14 / 26 |
| 25 puntos base | -0.057536 | 68 / 18 / 34 |
| 25 | -0.057446 | 79 / 29 / 53 |
| 25 puntos | -0.057348 | 68 / 18 / 35 |
| aumentar la | -0.050819 | 31 / 3 / 10 |
| un alza | -0.040836 | 38 / 10 / 31 |
| alza | -0.040375 | 61 / 24 / 160 |

Intercepto: **+0.229990**; suma de todos los aportes: **-0.016541**; residuo de términos no mostrados: **+0.073179**. Margen final: **+0.213449**.

Primera cita aislada: B predice **H**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** Una preferencia marginal sigue siendo una preferencia, no certeza sobre toda la trayectoria futura. No heredar automáticamente el sesgo de otro consejero.

### RPM-2015-09-15:7045:1 — Consejo del Banco Central de Chile

**Referencia H; modelo D; fold 5; 1982 caracteres completos.**

> el Consejo considera que la convergencia de la inflación a 3% en el horizonte de política requerirá reducir el elevado estímulo monetario actual. Dados los antecedentes recientes, se prevé que este proceso comenzará en el corto plazo.

H por anunciar retiro de estímulo próximo, aunque mantenga hoy la TPM. Reducir estímulo es dirección contractiva, no reducir la tasa.

**Hipótesis previa:** Verificar si estímulo, debilidad y mantener aportan D y si los n-gramas disponibles distinguen el objeto de reducir.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| mantener la tasa | +0.037868 | 29 / 33 / 44 |
| mantener | +0.034827 | 50 / 47 / 73 |
| mantener la | +0.031608 | 39 / 39 / 57 |
| reducir | +0.029567 | 13 / 14 / 14 |
| votacion | +0.025200 | 3 / 9 / 7 |
| la votacion | +0.024461 | 2 / 6 / 7 |
| de politica monetaria | -0.032622 | 97 / 55 / 152 |
| de politica | -0.024533 | 104 / 68 / 174 |
| siguen | -0.022429 | 43 / 15 / 57 |
| de inflacion | -0.021770 | 71 / 38 / 121 |
| del banco | -0.021621 | 45 / 22 / 64 |
| alza | -0.020440 | 62 / 22 / 155 |

Intercepto: **+0.139484**; suma de todos los aportes: **+0.269299**; residuo de términos no mostrados: **+0.229183**. Margen final: **+0.408783**.

Primera cita aislada: B predice **N**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** El texto no fija una magnitud de alza. No inventar una decisión inmediata ni identificar una palabra como causa suficiente sin medir sus contribuciones.

### RPM-2010-10-14:3491:1 — José De Gregorio Rebeco

**Referencia H; modelo D; fold 5; 4127 caracteres completos.**

> su voto es por subir la TPM en 25 puntos base hasta 2,75%.

> el proceso de retiro del estímulo monetario debe continuar

H: sube 25 en lugar de los 50 que habría preferido sin nuevas noticias y respalda continuar retirando estímulo. La moderación del ritmo y los relajamientos extranjeros no invierten la dirección doméstica.

**Hipótesis previa:** Comprobar si el vocabulario de moderar, inflación contenida o relajamiento domina; un menor endurecimiento no es automáticamente una reducción de la TPM.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| estimulo | +0.027396 | 21 / 20 / 20 |
| economias | +0.025993 | 25 / 26 / 81 |
| del peso | +0.025474 | 5 / 13 / 29 |
| las economias | +0.024955 | 16 / 20 / 58 |
| estimulo monetario | +0.022531 | 19 / 18 / 15 |
| emergentes | +0.021198 | 14 / 21 / 63 |
| subir la | -0.068385 | 25 / 3 / 11 |
| subir | -0.055757 | 30 / 7 / 26 |
| 25 puntos base | -0.046174 | 69 / 20 / 31 |
| subir la tasa | -0.046019 | 19 / 3 / 9 |
| 25 puntos | -0.046009 | 69 / 20 / 32 |
| 25 | -0.043724 | 81 / 29 / 51 |

Intercepto: **+0.139484**; suma de todos los aportes: **-0.032604**; residuo de términos no mostrados: **+0.125917**. Margen final: **+0.106880**.

Primera cita aislada: B predice **H**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** El escenario alternativo de subir 50 es contrafactual; la decisión efectivamente respaldada es subir 25. No tratar ambos como dos recomendaciones independientes.

### RPM-2015-08-13:6965:1 — Beltrán de Ramón Acevedo

**Referencia D; modelo H; fold 5; 2831 caracteres completos.**

> la opción de subir la tasa es confusa y se justificaría únicamente en un contexto de desanclaje, que hoy no está presente.

D, conforme a la corrección N→D aceptada: argumenta contra el alza porque la condición que la justificaría no está presente. El relato de inflación y desanclaje de 2008 contrasta con el escenario actual, no respalda subir ahora.

**Hipótesis previa:** Medir si inflación, desanclaje y subir aportan H aun dentro de una condición rechazada; comprobar también la lectura del fragmento aislado.

| Término activo | Aporte al margen error−referencia | df train H / D / N |
|---|---:|---|
| subir la | +0.044688 | 25 / 3 / 11 |
| subir la tasa | +0.037274 | 19 / 3 / 9 |
| subir | +0.036436 | 30 / 7 / 26 |
| precios | +0.034246 | 73 / 37 / 158 |
| un alza de | +0.033157 | 33 / 5 / 5 |
| que es | +0.031134 | 47 / 24 / 118 |
| tiempo | -0.030755 | 20 / 26 / 77 |
| forma | -0.026030 | 26 / 25 / 49 |
| antecedentes de | -0.022536 | 1 / 7 / 4 |
| es por ello | -0.020714 | 2 / 6 / 2 |
| de esta | -0.020686 | 20 / 16 / 61 |
| lo que | -0.018814 | 64 / 54 / 313 |

Intercepto: **-0.139484**; suma de todos los aportes: **+0.278674**; residuo de términos no mostrados: **+0.201276**. Margen final: **+0.139190**.

Primera cita aislada: B predice **N**. No se eligió retrospectivamente otra cita para mejorar esta respuesta.

**Límite:** No propone explícitamente un recorte. La corrección sigue siendo adjudicación asistida post-predicción; no se convierte su confianza del agente en certeza humana independiente.

## Cinco inversiones ambiguas excluidas

No se modifican estas referencias ni se convierten en neutral automáticamente. Son parte de las 15 inversiones numéricas, no errores semánticos inequívocos.

| ID | Referencia → predicción |
|---|---|
| RPM-2006-05-11:671:1 | D → H |
| RPM-2005-04-07:215:1 | D → H |
| RPM-2006-09-07:867:1 | D → H |
| RPM-2006-12-14:1019:1 | H → D |
| RPM-2006-03-16:621:1 | D → H |

## Qué exigir al siguiente modelo

1. Separar decisión respaldada de diagnóstico, pasado, alternativas y condiciones rechazadas.
2. Resolver el objeto de reducir: tasa frente a estímulo; distinguir fiscal/extranjero de política monetaria chilena.
3. Separar nivel y dirección: seguir expansivo no impide subir; subir menos no es recortar; mantener hoy no elimina un sesgo futuro explícito.
4. Leer toda la intervención, sin tomar solo sus primeros 512 tokens ni entregar al modelo las citas elegidas por el agente.
5. Medir H→D y D→H sobre soportes fijos, sin esconder inversiones en N; conservar matriz completa y guardas F1/recall.

El siguiente ensayo contextual está diseñado, no ejecutado. Mantendría referencia v2, folds purgados y puerta A, comparando B TF-IDF con B BETO. El acceso a pesos sigue siendo el bloqueo documentado en 36; no se simula entrenamiento. La media de segmentos también puede diluir una conclusión, por lo que cambiar arquitectura no garantiza resolver estos diez ejemplos.

Criterios de desarrollo previos a un nuevo candidato: +0,02 F1 H/D medio y mejora en ≥3/5 folds, pérdida macro ≤0,005 y recall H/D ≤0,02, además de menos inversiones sin aumentar H/D→N. Estos casos son diagnóstico conocido, no test nuevo. Una afirmación de generalización requerirá confirmación independiente posterior.

## Reproducción y trazabilidad

Artefactos en `data/auditoria/inversiones_hd_v1/`: lecturas manuales, selección, cinco excluidos, textos completos, aportes activos, scores/sondas, 793 predicciones reconstruidas, protocolo, hashes y verificación. Se preservan las opiniones previas y las referencias corregidas. No se abre el examen de 306 ni se cambia un checkpoint.

```bash
python scripts/37_diagnosticar_inversiones_hd.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/37_diagnosticar_inversiones_hd.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
```

[Protocolo previo](PROTOCOLO_DIAGNOSTICO_INVERSIONES_HD_V1.md) · [Referencia/modelo congelados](EVALUACION_REFERENCIAS_CORREGIDAS_V2.md)
