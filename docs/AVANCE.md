# AVANCE — Proyecto D&H

Última actualización: **diagnóstico de diez inversiones H/D completado: 40.937 caracteres íntegros, contribuciones exactas y 793 predicciones reproducidas. No se cambiaron referencias ni se ejecutó un candidato nuevo.**

## Estado activo: diagnóstico H/D y siguiente comparación contextual

- Usuario autorizó («pk adeñamte») revisar las diez inversiones más claras, apartar cinco ambiguas y diseñar la comparación contextual. [Síntesis para el investigador](LECTURA_DIAGNOSTICO_INVERSIONES_HD_V1.md) y [detalle técnico](DIAGNOSTICO_INVERSIONES_HD_V1.md).
- Selección exhaustiva de 15 H↔D de `seis_mas_trece`/referencia v2: diez seleccionadas (9 referencias respaldadas + De Ramón 6965 N→D aceptada), cinco ambiguas excluidas (671, 215, 867, 1019, 621). Las quince siguen siendo errores numéricos contra la referencia actual, no quince errores semánticos probados.
- Diez fuentes releídas íntegras: 40.937 caracteres. Script 37 reconstruyó cinco folds del mismo modelo; las **793 predicciones A/B/finales coinciden** con 36. A=1 en los diez. No nuevo candidato, ajustes de parámetros, etiquetas ni métricas sustituidas.
- Descomposición de margen error−referencia con **8.558 features activos**; se guardan todos y se muestran seis principales por signo con residuo. Intercepto + suma de aportes coincide con decision_function (tolerancia 1e-9). Coeficientes/aportes no equivalen a causalidad lingüística o efecto de borrar palabras.
- Hallazgos: en Consejo 1057 reducir la tasa aporta correctamente D, pero 25 (dentro de 5,25%) y fórmulas contribuyen H. En De Ramón 6965 subir favorece H pese a condición negada; en Consejo 7045 reducir favorece D pese a referirse a estímulo. Schmidt-Hebbel 1672 sigue H incluso con recomendación menos restrictiva aislada. No basta culpar a longitud.
- García 7212 y De Gregorio 3491: suma textual favorece ligeramente H, pero intercepto aprendido da margen D−H positivo. No describir todos los casos como dominancia de palabras D ni atribuir intercepto automáticamente a desbalance de clases. La hipótesis fiscal de Larraín no se confirmó por los mayores aportes observados.
- **Sonda primera cita preseleccionada:** 4 coincidencias (1057 D; 7210/7212/3491 H), 4 N (2758/4272/7045/6965), 2 inversiones (1672 H y 1731 D). No score de un extractor: selección manual informada por referencia. La primera cita puede perder contexto legítimo, como duración en 2758; no contar los cuatro N como nuevos errores semánticos de fragmentos.
- Marfán 1731 conserva matiz: vota mantener con sesgo al alza y prefiere alza junto a intervención cambiaria; H no significa voto de alza inmediata. Ninguna nueva adjudicación.
- [Protocolo previo](PROTOCOLO_DIAGNOSTICO_INVERSIONES_HD_V1.md): futura comparación de B TF-IDF/BETO con referencia v2, mismos folds/A y cobertura de todo el texto; no usar citas manuales como entradas. Contar inversiones por sentido con soportes fijos, H/D→N y N→H/D, F1 H/D y guardas macro/recall. Menos inversiones sin aumentar H/D→N, sin optimizar repetidamente sobre estos diez conocidos. BETO sigue sin ejecutar; no se repitió el chequeo TLS de 36.
- **Verificación:** 64 pruebas específicas aprobadas, 0 omitidas; seis salidas e informe técnico exactamente reproducidos; protocolo igual salvo UTC; **298 archivos previos intactos**. `data/auditoria/inversiones_hd_v1/verificacion.json` incluye hash de la síntesis manual final. No apertura de 306, refit global ni pesos persistidos.
- Rama fija `arena/01a0a81b-fase-2`; PR existente **#4** abierto. Esta continuación se añade al mismo PR. Siguiente bloqueo: acceso a pesos/recursos para candidato contextual; no volver a solicitar las 13 correcciones ni las seis aceptaciones anteriores.

## Historial: referencias corregidas v2 y modelo ejecutado

- Usuario: «corrige las referencias, e ittenta mandar el modelo en tu entorno», después «sigue». Se interpretó y anunció aplicación de las 13 propuestas y comprobación TF-IDF/BETO. Las 13 ya no requieren aceptación; los 12 ambiguos permanecen sin cambio. No repetir las seis decisiones Rxx anteriores.
- Aceptación por ID/etiqueta/hash en `data/auditoria/revision_errores_adjudicada_v1/adjudicacion_cierre_66_v1/aceptacion.json`. Asistida y posterior a predicciones, no humana ciega. 19 decisiones aceptadas entre ambas rondas, 16 cambios efectivos frente a IA. Confianza/citas del agente conservadas como tales.
- Vista activa: `data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv`, 1.352 IDs con etiquetas IA, seis previas, seis más trece, fold y relevancia IA. Se usa efectivamente en el experimento 36. Corridas canónicas y documentos históricos congelados intactos; su estado de propuestas pendientes queda superado por la aceptación nueva, no reescrito.
- [Protocolo previo](PROTOCOLO_REFERENCIAS_CORREGIDAS_V2.md) y [resultado](EVALUACION_REFERENCIAS_CORREGIDAS_V2.md). Dos supervisiones, mismos parámetros y cinco folds purgados; A/vocabularios/IDF idénticos. Control reproduce A/B/final de adjudicada en 31. Correcciones en validación por fold: **4/0/4/4/1**; en train de otros folds: **9/13/9/9/12**. No propio texto/reunión en train de su fold, pero sigue habiendo revisión post-predicción.
- **Comparación 2×2:** control frente a IA F1 H/D **0,648822**, macro **0,754311**, 66 errores; control frente a corregida **0,711084**, macro **0,798013**, 55 errores. Reentrenado frente a IA **0,684035**, macro **0,778042**, 62 errores; frente a corregida **0,747060**, macro **0,822250**, 51 errores.
- **Separación de efectos:** referencia sola +0,062262 no es mejora de modelo. Entrenamiento contra referencia corregida fija **+0,035976**, mejora en 4/5 folds; 9 predicciones distintas, 6 errores corregidos y 2 nuevos. No afirmar generalización ni test independiente sobre estas 793. No nuevas búsquedas/306 respuestas/refit global/modelo persistido.
- Python 3.11 y dependencias fijadas restaurados fuera del repo. **56 pruebas aprobadas, 0 omitidas**, replay de diez ajustes: cinco datos e informe exactamente iguales; protocolo igual salvo UTC; **284 archivos previos intactos**. Registro `referencias_corregidas_v2/verificacion.json`. Integridad y reproducción, no prueba semántica.
- **BETO:** urllib API/config falla TLS EOF; curl config exit 35 SSL_ERROR_SYSCALL. Dos CPU, sin nvidia-smi. Registro real en `adjudicacion_cierre_66_v1/beto_disponibilidad.json`; no pesos, no entrenamiento transformer ni TLS desactivado. No atribuir al modelo una limitación de acceso.
- El usuario también pidió abrir PR con los cambios acumulados de esta rama. No incluir venv, pesos ni temporales; no cambiar de rama. Los experimentos y revisiones anteriores se incluyen porque aún no se habían publicado desde esta sesión.

## Historial: cierre de cobertura y propuestas consolidadas

- El usuario pidió «continua». Se revisaron todos los 13 pendientes largos: **105.621 caracteres**, sin truncar. Magendzo diciembre-2007 (14.172 caracteres) se leyó en dos partes consecutivas, sin decidir antes de completar la segunda. Acumulado de cuatro tandas: **265.245 caracteres originales / 66 intervenciones**.
- [Informe consolidado](REVISION_ERRORES_CIERRE_66_V1.md): tabla única de 13 propuestas, 12 ambiguos y las 13 nuevas lecturas con citas. Última tanda: **8 N respaldadas, 5 cuestionables, 0 ambiguas nuevas**; acumulado **41/13/12**. Es cobertura completa de estos desacuerdos, no revisión de todas las 793 referencias ni estimación representativa del corpus.
- **Cinco propuestas nuevas NO aceptadas:** L02 Naudon 2015-06-11:6854 N→D (prolongar estímulo, media); L04 Valdés 2005-03-10:178 N→H (continuar normalización, media); L05 Marfán 2013-06-13:5632 N→D (reducción futura preferida, alta); L10 García 2008-12-11:2238 N→D (conveniencia del relajamiento respaldada, alta); L11 García 2009-08-13:2681 N→D (defensa de estímulo/tasa mínima prolongada, media). Confianza del agente, no certeza ni adjudicación humana.
- Conservar N en Corbo octubre-2007; Marshall diciembre-2008 y diciembre-2006; Naudon enero-2015; Herrera marzo-2012; Valdés febrero-2007; García marzo-2008; Magendzo diciembre-2007. Se distingue prolongar el estímulo respecto de lo previsto de meramente juzgar adecuado el actual; menús y riesgos condicionales no equivalen a preferencia adoptada.
- Script 35 y `tests/test_revision_cierre_66.py` nuevos; 32–34 congelados. `tanda_4_largos_v1/resultados/` guarda 13 textos completos/anotaciones IA/A-B-final, inventario de 66 y cola vacía, resumen, manifest y **`revision_consolidada.csv` con las 66 opiniones/citas/límites y rutas de evidencia**. No es archivo de importación canónica.
- **Controles:** 22 citas propias literales ≤300 caracteres; 13 citas IA literales conservadas. A=1 y final=B en los 13. **34 pruebas aprobadas, 0 omitidas**, cinco salidas e informe reproducidos exactamente; manifest igual salvo fecha UTC de generación; **273 archivos anteriores intactos**. Registro persistente `tanda_4_largos_v1/verificacion.json`. Estas pruebas no verifican verdad semántica.
- No cambios canónicos, entrenamiento, métricas recalculadas ni acceso a respuestas de 306. La validación sigue siendo desarrollo reutilizado. La aceptación anterior de seis casos no se extiende a las 13 propuestas actuales; los 12 ambiguos no reciben una etiqueta inventada.
- **Siguiente decisión:** resolver las 13 propuestas concretas y tratar los 12 ambiguos por separado, sin pedir repetir las 30 anotaciones ni reaceptar las seis ya cerradas. No hay más pendientes de lectura dentro de estos 66. BETO sigue bloqueado; no se ejecutó nuevo experimento.

## Historial: tercera tanda de revisión, neutralidad

- El usuario pidió «sigue intenta abarcar lo que mas puedas». Se informó y aplicó orden por longitud original ascendente, desempate por ID, sobre los 43 pendientes. Revisados los 30 más cortos, todos íntegros: **72.911 caracteres**. No es muestreo representativo; los 13 largos restantes suman **105.621 caracteres** y no se revisaron cualitativamente todavía.
- [Informe con 30 lecturas y lista de los pendientes](REVISION_NEUTRALIDAD_TANDA_3_V1.md). Esta tanda: **19 referencias respaldadas, 5 cuestionables, 6 ambiguas**. Acumulado de tres tandas: **53 revisados / 13 pendientes; 33 respaldadas, 8 cuestionables, 12 ambiguas**. Opiniones del agente posteriores a conocer IA/predicciones, no test ni adjudicación humana independiente.
- **Cinco propuestas nuevas NO aceptadas:** N07 Valdés 2005-01-11:39 N→H; N16 Ovalle 2005-03-10:198 N→H; N19 De Ramón 2015-08-13:6965 N→D; N21 Corbo 2007-05-10:1261:1 N→H; N27 García 2005-01-11:5 N→H. La propuesta D de De Ramón contradice también el H del modelo. Las cuatro H tienen confianza media; D, alta según el agente, sin convertirse en certeza/adjudicación humana.
- **Ambiguos:** Herrera 2005-01-11:46 (ajuste sin dirección explícita), Naudon 2015-12-17:7207 (nivel 3,5 sin tasa de partida en la unidad), Corbo 2007-02-08:1102 (riesgo inflacionario/mantención sin recorte explicitado), De Gregorio 2006-10-12:941 (mantención/posible eliminación futura del sesgo), Corbo 2007-03-15:1167 (sesgo de inflación frente a curso de política no especificado) y Jadresic 2006-07-13:774 (fundamentos para pausar/táctica para subir con redacción difícil). Propuesta nula, no cuarta clase ni N automáticamente aplicada.
- **Control A/B:** las 30 predicciones guardadas tienen A=1 y final=B. Estas discrepancias no se deben a filtrado de irrelevancia. Hay dos textos de 132/195 caracteres con alzas explícitas que B clasifica N; no todo puede atribuirse a longitud o anotaciones defectuosas. No se midieron contribuciones léxicas ni causas de vocabulario.
- Nuevos script 34 y tests; reutilizan validadores de 32/33 sin editarlos. Datos en `data/auditoria/revision_errores_adjudicada_v1/tanda_3_neutralidad_v1/`: lecturas manuales del agente y resultados separados. 35 citas propias verificadas (≤300, normalización de espacios); las 30 citas IA son literales, sin que eso pruebe su suficiencia semántica.
- **Verificación:** 8 pruebas de cada una de las tres tandas aprobadas (24 total, ninguna omitida); cuatro archivos e informe reproducidos exactamente; 263 archivos previos intactos. Registro `tanda_3_neutralidad_v1/verificacion.json`. Ningún entrenamiento, cambio de etiqueta/métrica o apertura de respuestas de 306. Guía v2 y seis adjudicaciones aceptadas siguen intactas.
- **Siguiente:** revisar los 13 pendientes largos desde `resultados/pendientes.json`; no declararlos ya revisados por haber medido su longitud. Las 8 propuestas cuestionables de tandas 2/3 no heredan aceptación humana anterior. Conservar validación como desarrollo reutilizado y no recalcular scores para presentar mejora artificial. BETO sigue bloqueado; no más petición de las 30 anotaciones.

## Historial: segunda tanda de revisión de etiquetas

- El usuario pidió seguir. Se eligieron los 16 intercambios H↔D pendientes tras la primera tanda, todos leídos completos: **65.147 caracteres** más anotaciones IA originales. No selección por conveniencia ni apertura de las 306 respuestas antiguas.
- [Informe con los 16 casos y citas](REVISION_INTERCAMBIOS_HD_TANDA_2_V1.md). Resultado del agente: **10 referencias respaldadas (5 H/5 D), 3 cuestionables, 3 ambiguas**. Con la tanda anterior: 23 revisados, 14 respaldadas / 3 cuestionables / 6 ambiguas. Los 43 restantes involucran neutralidad. No equivale a estimar error de todo el corpus.
- **Propuestas nuevas NO aprobadas:** H02, Corbo 2006-05-11:674, D→H por respaldo a continuar la normalización; H08, De Gregorio 2008-02-07:1684, D→H por conservación del sesgo alcista aunque suavizado; H13, comunicado 2011-08-18:4280, D→N por ausencia de dirección expresada. Confianza media en las tres. La propuesta N discrepa tanto de la IA como del modelo; no usar el output del modelo como oráculo.
- **Ambiguos:** Wagner 2005-04-07:215 (normalización adecuada pero pausa), Valdés 2006-09-07:867 (pausa prolongada y alzas lejanas como supuesto) y De Gregorio 2006-12-14:1019 (no bajar aún/posible recorte futuro con final de frase defectuoso). No se reconstruyeron fragmentos ni se cotejó PDF. No heredar automáticamente la aceptación del R12 humano a otros casos de pausa.
- **Hallazgos:** errores de modelo ante votos explícitos de subir o reducir; mantener con sesgo alcista puede ser H; subir menos sigue siendo subir; reducir estímulo no es reducir TPM; consolidación fiscal no es endurecimiento monetario. Son distinciones semánticas de los textos, no causas de predicción verificadas por contribuciones léxicas.
- Script 33 reutiliza selección/validación de 32 sin modificarlo. JSON de lecturas del agente separado, 25 citas verificadas (≤300; normalización de espacios) y 16 citas IA literales. Inventario acumulado en `data/auditoria/revision_errores_adjudicada_v1/tanda_2_hd_v1/resultados/`, manteniendo el inventario histórico de la tanda 1.
- **Controles:** 8 pruebas de tanda 2 + 8 de tanda 1 aprobadas; tres salidas e informe reproducidos exactamente; 254 archivos previos intactos. Evidencia en `tanda_2_hd_v1/verificacion.json`. No cambios de etiquetas, métricas o modelos. Las opiniones son posteriores a conocer IA/predicción y no un test independiente.
- **Siguiente:** continuar con los 43 desacuerdos de neutralidad pendientes. Cualquier corrección nueva requiere adjudicación por caso; el usuario no ha aceptado las tres propuestas de esta tanda. Mantener la validación como desarrollo reutilizado; no elevar artificialmente el score corrigiendo referencias hacia el modelo. BETO sigue bloqueado; no pedir otra vez las 30 anotaciones.

## Historial: primera tanda de revisión de etiquetas

- El usuario pidió «hace revision de las anotaciones erroneas». Se explicitó comenzar por los siete errores nuevos tras adjudicación, no asumir que cada desacuerdo demuestra etiqueta IA mala. Se leyeron las siete intervenciones completas (21.566 caracteres) y sus etiquetas/citas/notas IA originales.
- Selección reproducible: modelo original acertaba contra IA y modelo adjudicado difiere, sobre la misma validación. **No se revisaron cualitativamente los otros 59**. Inventario de 66 en `data/auditoria/revision_errores_adjudicada_v1/resultados/inventario_errores.csv`, con estados por cobertura.
- [Informe](REVISION_ERRORES_NUEVOS_ADJUDICADA_V1.md): D respaldada en 2006-10-12:936, 2013-11-19:5900, 2007-01-11:1050 y 2015-08-13:6969. Mi lectura atribuye esas discrepancias al modelo, no a etiquetas defectuosas. Son juicios del agente después de conocer predicciones, no verdad humana independiente.
- Ambiguos: 2006-05-11:671 y 2006-03-16:621 (normalización frente a pausa táctica), y 2005-01-11:42 (crítica al ritmo/comunicación con dirección poco clara; fuente dice literalmente «bajar O, 25, 50»). No sustituir bajar por subir sin cotejo; posible problema textual no demostrado. No se consultó PDF ni se reconstruyeron palabras. No se adjudicaron nuevas etiquetas en estos tres.
- Nuevos script 32, ocho tests y `lecturas_agente.json`: selección/controles automáticos separados de la lectura semántica manual del agente. Diez extractos propios verificados (≤300, normalización solo de espacios); siete citas IA originales literales, sin que eso certifique su suficiencia. No se midieron contribuciones léxicas ni se atribuyó causalmente el fallo a palabras específicas.
- **Verificación:** ocho pruebas aprobadas; inventario, casos JSON, resumen e informe reproducidos exactamente en temporal. 245 archivos anteriores intactos. No entrenamiento, modificación canónica, reapertura de respuestas de 306 ni recálculo de métricas con etiquetas del agente. Evidencia en `data/auditoria/revision_errores_adjudicada_v1/verificacion.json`.
- **Siguiente:** continuar la revisión del resto si se requiere; no extrapolar 4/3 a los 66. Cualquier corrección necesita decisión documentada por caso. La validación es desarrollo reutilizado y esta inspección refuerza esa condición: no corregirla para elevar artificialmente el score. BETO sigue bloqueado; no implica pedir otra vez las 30 anotaciones.

## Estado anterior: modelo tras adjudicación

- El usuario pidió continuar. Se aplicaron en memoria las seis adjudicaciones aceptadas a una vista experimental del train: tres cambios reales respecto de IA, R01 N→H / R03 D→N / R12 D→H. R08/R17/R21 ya eran D. No modificar L0, corridas IA, devolución original, guía ni aceptación. Relevancia conservada explícitamente de IA; no es relevancia humana imputada ni importación canónica de los 30.
- Nuevo `scripts/31_evaluar_adjudicacion.py`: preparación antes del fit, dos condiciones TF-IDF sin rejilla, mismos cinco folds purgados y 793 validaciones. Las seis adjudicaciones solo están en train; validación/puerta A/vocabularios/IDF intactos. Baseline original reproduce exactamente A/B/finales de B0 limpia de 26. No se ejecutaron las otras variantes históricas.
- **Resultado:** F1 H/D medio original/adjudicado **0,691477 / 0,648822**; macro-F1 **0,783501 / 0,754311**; errores **60 / 66**. Recall H **0,782609 / 0,797101**; D **0,734694 / 0,612245**. Nueve predicciones finales cambian: un error corregido, siete nuevos y un error que sigue siendo error. Mejora F1 H/D solo en 1/5 folds. [Informe](EVALUACION_MODELO_ADJUDICADO_V1.md).
- No demuestra deterioro o mejora frente a personas: mide acuerdo con las mismas referencias IA reutilizadas. No revertir las adjudicaciones para maximizar ese score ni declarar que el modelo entiende el futuro. No más tuning léxico; referencia adjudicada disponible de forma reproducible para comparar arquitecturas con la misma supervisión.
- **BETO:** dos peticiones directas config/API de Hugging Face volvieron a fallar TLS EOF; dos CPU, sin GPU detectada. No pesos ni instalaciones transformer grandes. [Protocolo previo](PROTOCOLO_MODELO_ADJUDICADO_V1.md) fija comparación y diseño de segmentos completos/solapamiento/agregación por intervención; el runner BETO aún no está implementado ni validado con pesos reales. Esto es bloqueo técnico, no resultado de BETO.
- **Verificación:** 10 tests nuevos y 9 de devolución aprobados, ninguno omitido en esas unidades. Repetición temporal completa: cuatro CSV + métricas + informe idénticos; 233 archivos previos intactos. Registro en `data/evaluacion/adjudicacion_modelo_v1/reproducibilidad.json`. Protocolo/manifiestos con hashes, sin modelos persistidos. No suite general ni respuestas humanas antiguas; del marco de 306 solo IDs para exclusión.
- **Siguiente:** resolver acceso a pesos y disponer de entorno adecuado, preferiblemente GPU, para implementar y ejecutar el ensayo BETO fijado. No repetir el Excel ni solicitar confirmación otra vez. No presentar el diseño pendiente como código transformer probado. Si el entorno actual sigue bloqueado, trasladar esa ejecución a uno con acceso (p. ej., GPU en Colab), sin exportar el examen antiguo.

## Historial reciente: revisión humana del entrenamiento

- El investigador envió por GitHub `30 anotaciones humanas.xlsx`, preservado sin cambios en `data/auditoria/revision_entrenamiento_30_v1/devolucion_humana_v1/`. Fuente fijada al commit `2667e7d7eaa16ba9dcc67d4288515f31b0500456`; recibo con Git blob SHA1/SHA256. No se hizo merge de main.
- Una hoja simplificada de cinco columnas, no el libro de cuatro hojas. IDs completos y texto íntegro verificados: 29 exactos y R03 igual tras espacios. Las 30 posturas están presentes: 11 H / 5 D / 14 N. No son respuestas recuperadas del navegador.
- Comparación: matriz filas IA / columnas humano, orden H,D,N: `[[10,0,0],[0,5,5],[1,0,9]]`. 24/30 acuerdos; discrepancias R01, R03, R08, R12, R17 y R21. No es evaluación de predicciones ni estimación de calidad poblacional.
- 18 citas literales ≤300 y 12 marcadores de ausencia; relevancia, fecha de anotación, ayuda y acceso previo a IA no declarados. No se imputan a partir del recibo o etiquetas IA. Comparación de postura válida, importación canónica no realizada ni declarada completa.
- [Informe numérico](REVISION_HUMANA_ENTRENAMIENTO_30_V1.md) y [lectura cualitativa de los seis textos completos](LECTURA_DISCREPANCIAS_REVISION_30.md). La lectura es del agente después de ver ambas anotaciones: no es adjudicación ni segundo anotador ciego. Detecta tensión entre mantener hoy y sesgo futuro, opciones y trayectoria; R12 tiene una unión aparentemente defectuosa que no se reconstruyó.
- **Aclaración posterior y propuesta autorizada:** el investigador indicó que una postura de subir cuenta aunque sea futura y autorizó revisar solo las seis discrepancias. Releídos los textos completos: propuestas del agente R01 H / R03 N / R08 D / R12 H / R17 D / R21 D, inicialmente pendientes y ahora aceptadas (ver registro siguiente). [Documento con siete citas verificadas y límites](PROPUESTA_SEIS_DISCREPANCIAS_30_V1.md); JSON/manifest en `devolucion_humana_v1/propuesta_adjudicacion_v1/`. R03 se propone N por tensión no resuelta, no por ser solo descriptivo; R12 H por respaldo a alzas graduales, con límite de fuente defectuosa y alternativa N si persiste duda. R17 es el caso más directo.
- **Aceptación explícita posterior:** el usuario respondió «acepto todas». [Seis adjudicaciones aprobadas](ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md), registradas en `devolucion_humana_v1/adjudicacion_aprobada_v1/`: aceptación literal, CSV de seis etiquetas y manifiesto de hashes. Se verificó correspondencia exacta con las propuestas/IDs/textos, sin sobrescribir insumos. Cuatro decisiones cambian respecto de la primera respuesta humana; tres difieren de la IA de origen. La adjudicación es asistida y posterior al feedback; no cambia la procedencia desconocida de la primera anotación ni elimina cautelas de R03/R12.
- **Cierre de adjudicación:** no repetir confirmación ni Excel. La ejecución TF-IDF posterior está documentada en el estado activo al inicio. BETO sigue sin evaluación. Guía/training canónico y comparación inicial 24/30 intactos; sin reapertura de 306 respuestas.
- Script 30 y `tests/test_revision_humana_30.py`: **9 pruebas aprobadas, ninguna omitida**, incluida integridad del original y matriz independiente. Reproducción temporal idéntica de tres CSV, resumen e informe; 216 archivos previos protegidos intactos y siete citas adicionales del agente verificadas. Evidencia en `devolucion_humana_v1/verificacion_comparacion_v1.json`. No se abrió el examen de 306 ni se ejecutó la suite ML completa.
- La interfaz/plantillas originales se conservan como entrega histórica. El servidor 29 solo sirve formulario y XLSX vacío: no publicar desde el directorio de auditoría ni exponer la devolución o clave.

Las secciones siguientes conservan la historia de las etapas anteriores; sus pendientes de devolución quedaron resueltos por el estado activo de arriba.

## Historial: entrega en Excel solicitada por el investigador

Después de informar que el avance no se guardó, el investigador pidió descargar un XLSX ordenado y completarlo allí. Esta petición autoriza un libro nuevo útil para la revisión, no restaurar los antiguos Excel descartados ni inventar las respuestas perdidas.

- **Archivo:** [revision_entrenamiento_30.xlsx](../data/auditoria/revision_entrenamiento_30_v1/revision_entrenamiento_30.xlsx). Las mismas 30 intervenciones/códigos/hash de la muestra, extraídas solo del payload público; no se leyó la clave IA. Decisiones vacías de forma deliberada.
- **Hojas visibles:** Inicio (instrucciones y declaración de ayuda), Respuestas (desplegables, celdas amarillas y enlaces), Textos (bloques consecutivos completos con retorno por código) y Guía (v2 secciones 1–3). No se ocultan etiquetas en hojas/columnas. Se conservan los 81.439 caracteres originales; se segmentan solo para evitar el límite visual de altura de Excel. Ningún resumen.
- **Uso:** descargar y guardar copia local, completar C–F en Respuestas, guardar regularmente y adjuntar XLSX al chat, incluso parcial. No requiere JSON o devolver datos por la web. Estado solo verifica presencia de campos/relevancia/longitud de cita; no es acuerdo IA ni certificación de cita literal. Las fórmulas se recalculan al abrir en Excel/LibreOffice, no se inspeccionaron en Excel real.
- **Descarga:** interfaz v1.2 añade enlace HTTP normal, sin Blob, a `/revision_entrenamiento_30.xlsx`. Servidor del script 29 solo permite formulario y ese archivo, con Content-Disposition attachment y MIME XLSX. La clave y archivos archivados nunca son rutas servidas. El fichero también se entrega directamente por el visor de archivos del chat; un bloqueo del iframe no obliga a usarlo.
- **Versionado:** script 29 y tests específicos nuevos. HTML/manifiesto v1.1 guardados en `archivo_interfaz_v1_1/`; el manifiesto activo incorpora XLSX e interfaz v1.2. No modificar generadores 27/28, su plantilla ni protocolos originales. Usar ahora `29_preparar_excel_revision.py --servir` en lugar del servidor genérico de carpeta, que no puede servir el XLSX situado en el directorio padre.
- **Controles:** 18 pruebas de Excel/exportación/interfaz pasaron, incluyendo descarga real con bytes idénticos y rutas privadas 404. Reproducción semántica de libro (celdas, fórmulas, validaciones, protección y enlaces), sin exigir identidad ZIP de timestamps. 120 celdas C–F sin decisiones; cuatro hojas; 208 archivos previos protegidos intactos. No se ejecutó toda la suite ML: el checkpoint histórico ignorado por Git no está disponible en este entorno restaurado. Ningún entrenamiento o examen humano.
- **Pendiente:** recibir y preservar el libro rellenado antes de comparar; no dar por revisados los 30 casos. El XLSX no recupera ni incluye respuestas del navegador. Las protecciones sin contraseña evitan cambios accidentales, no son un mecanismo de seguridad fuerte.

## Incidencia de descarga del formulario — interfaz v1.1

El investigador informó que no podía descargar JSON. Una pregunta de la interfaz cerró su visor; todavía no se sabe si el navegador conservó el avance. No afirmar pérdida ni recuperación y no abrir más diálogos para averiguarlo. Los datos del navegador no están en el servidor.

- Se conserva la misma ruta `formulario/index.html`, payload, códigos y clave localStorage. Nueva salida **Mostrar / copiar JSON**, textarea readonly con selección manual y copia con alternativa cuando clipboard no está permitido. El respaldo se prepara antes de intentar la descarga, también si el visor la bloquea silenciosamente. No se declara que una descarga se completó.
- Al abrir, se informa si se recuperó contenido; ya no se escribe automáticamente un estado vacío, para no pisar respaldos. Si no aparece el avance, pedir al investigador que avise por chat sin rellenar todo de nuevo. No puede garantizarse recuperación entre orígenes o si solo existía en memoria.
- Reparador `28_reparar_exportacion_revision.py` y `tests/test_exportacion_revision.py`: tres pruebas aprobadas, con escenarios DOM jsdom 26.1.0 de bloqueo de descarga, permisos de copia/almacenamiento y recuperación de estado v1 inventado. No se accedió a respuestas reales.
- HTML/manifiesto v1 conservados en `archivo_interfaz_v1/`, fuera del directorio público. El manifiesto activo describe v1.1; `reparacion_exportacion_v1_1.json` registra ambos hashes. Script 27, plantilla, protocolo y clave de selección siguen intactos. La reproducción anterior corresponde al HTML v1 archivado; aplicar el reparador para producir v1.1. No regenerar v1 sobre el formulario activo.
- Solo se sirve `formulario/` por HTTP, sin endpoint de subida. La revisión permanece pendiente de devolución. No se ejecutó entrenamiento, comparación de etiquetas o examen humano.

## El paso a paso y dónde estamos

1. **Training IA:** 1.352 intervenciones etiquetadas en 19 CSV, sin duplicados.
2. **Validación IA:** búsqueda de 12 configuraciones TF-IDF con cinco particiones por reunión. En cada vuelta: 1.081–1.083 para entrenar y 269–271 para validar. No se leyeron respuestas humanas.
3. **Selección:** unigramas, min_df=3, C=2; media de macro-F1 de validación **0,7264**. Se congeló la configuración y se reajustó con las 1.352 completas.
4. **Test humano:** predicciones de los 306 textos guardadas antes de abrir el libro de respuestas, y comparación en un proceso posterior. **260/306 coincidencias (84,97 %)**, 46 errores frente a la referencia; **macro-F1 0,6775**, **κ 0,6458**.
5. **Estado:** esta primera evaluación del clasificador ya está hecha. No se ajustó nada al resultado humano; no se entrenó BETO ni se puntuó el corpus restante.

6. **Nuevo experimento solicitado:** n-gramas 1–4, revisión contextual y comparación de cuatro variantes, sin reabrir ni predecir el gold humano. Detalle abajo.

7. **Búsqueda de longitud autorizada y completada:** se compararon seis límites sin diccionario. Ganó (1,4), sin reajuste final ni nuevo test humano.

8. **Diagnóstico autorizado:** coeficientes y contribuciones del candidato (1,4), revisión de errores IA e hipótesis de híbrido. No se cambiaron modelos ni etiquetas.

9. **Investigación externa solicitada y completada:** revisión de métodos monetarios y foros antes de implementar; propuesta acotada, sin nuevos entrenamientos ni etiquetas.

10. **Comparación autorizada y completada:** cuatro variantes B, misma validación IA y A fija. Ninguna mejora la media de macro-F1. Sin cambio del modelo guardado ni test humano.

11. **Piloto WCB autorizado y completado:** 100 frases train externas, 99 usadas para B; la importación traducida no mejora. Sin test externo/humano ni incorporación a etiquetas canónicas.

12. **Nueva autorización amplia con limpieza:** comparación acotada de clasificadores y purga de copias en train; ninguna alternativa supera la referencia H/D. No confundir validación IA con mejora humana.

13. **Revisión humana acotada recibida y comparada:** 30 textos de entrenamiento sin IDs/copias del examen o validación. 24 acuerdos y seis discrepancias; pendientes de adjudicación, sin cambios canónicos. Ver estado activo al inicio.

Formulario actual: [Revisión de entrenamiento](../data/auditoria/revision_entrenamiento_30_v1/formulario/index.html). Protocolo: [revisión 30 v1](PROTOCOLO_REVISION_ENTRENAMIENTO_30_V1.md). Comparación anterior: [EVALUACION_CLASIFICADORES_HD_V1.md](EVALUACION_CLASIFICADORES_HD_V1.md). WCB cerrado: [EVALUACION_WCB_PILOTO_V1.md](EVALUACION_WCB_PILOTO_V1.md). Híbrido cerrado: [EVALUACION_HIBRIDO_V1.md](EVALUACION_HIBRIDO_V1.md). Investigación: [INVESTIGACION_HIBRIDO.md](INVESTIGACION_HIBRIDO.md). Diagnóstico: [INFLUENCIAS_NGRAMAS.md](INFLUENCIAS_NGRAMAS.md). Informe de longitud: [LONGITUD_NGRAMAS.md](LONGITUD_NGRAMAS.md). Informe léxico: [LEXICO_NGRAMAS.md](LEXICO_NGRAMAS.md). Examen anterior: [EVALUACION_TFIDF_GOLD.md](EVALUACION_TFIDF_GOLD.md).

## Unidad activa: revisión humana del entrenamiento (preparada, esperando devolución)

- **Autorización:** «ok hazlo», al recomendar una revisión pequeña (10 H/10 D/10 N) antes de BETO y sin datos financieros auxiliares. Se anunció que el investigador decidiría antes de mostrar etiquetas IA. El agente no sustituye esas decisiones ni declara errores sin la devolución.
- **Selección prefijada:** semilla 20260916, rangos SHA256 independientes para selección y orden. Pool inicial 559 de descubrimiento; excluir IDs humanos y copias normalizadas de humanos/validación; 543 elegibles y 541 tras deduplicar (47 H/40 D/454 N). Selección 30 en 15 reuniones, 10 por etiqueta IA. Sin elegir por predicción, confianza, actor o longitud. No representa la distribución poblacional.
- **Aislamiento:** los 306 IDs se leen solo del marco de selección. Los textos L0 asociados se usan solo para vetar copias, sin leer respuestas humanas ni predecirlos. Cero ID/copia normalizada humana o de las 793 validaciones en la muestra. Fuente y etiquetas canónicas intactas. Desarrollo, no nuevo test humano.
- **Material:** `27_preparar_revision_entrenamiento.py`, plantilla HTML usada y once tests. [Protocolo](PROTOCOLO_REVISION_ENTRENAMIENTO_30_V1.md); `data/auditoria/revision_entrenamiento_30_v1/`. Texto íntegro: 81.439 caracteres entre los 30, máximo 6.760/mínimo 195 por intervención. No se recortan conclusiones ni se reemplazan casos largos; puede responderse por partes.
- **Formulario público:** solo texto/fecha/actor/cargo y código R01–R30; guía v2 secciones 1–3. Sin etiquetas, confianza, citas IA, predicciones o feedback de acuerdo. H/D/N + opción de duda no entrenable; relevancia y cita literal ≤300 caracteres según guía, motivo para duda/no evaluable. No completar cuotas. Declarar ayuda y si vio etiquetas; no afirmar ciego estricto o independencia.
- **Respuestas:** guardado exclusivamente en localStorage del navegador con aviso si falla. Descarga JSON parcial/completo y restauración desde JSON de la misma muestra (verificación de versión/hash/códigos, validez recalculada). **Adjuntar la devolución al chat**: no hay subida automática al servidor. No se importan etiquetas al entrenamiento en esta etapa.
- **Vista previa:** servidor estático puerto 8080, enlazado a 0.0.0.0, sirve únicamente `formulario/`. `NO_ABRIR_hasta_finalizar_clave.csv`, protocolo y manifiestos están fuera del directorio servido. La clave existe en el repositorio; el dueño podría abrirla, por lo que debe evitar hacerlo antes de decidir. No cifrado ni secreto fuerte.
- **Verificación:** clave reservada y HTML idénticos al regenerar en temporal eliminado; textos originales completos y 10/10/10 comprobados sin mostrar correspondencias. HTTP 200 para formulario y 404 para cuatro intentos de acceder a archivos fuera de su carpeta. **127 pruebas superadas**, una antigua omitida por apertura del gold. Incluye flujo en DOM simulado con jsdom 26.1.0, no inspección visual en navegador real. **195 archivos anteriores intactos**.
- **Limpieza:** sin Excel vacío, copia completa de corpus, nuevas etiquetas o modelos. jsdom se instaló solo en caché fuera del repositorio para los tests; no cambia requisitos Python. Se conserva el formulario usado y su clave para comparación futura, no material descartable.
- **Pendiente real:** recibir JSON del investigador, preservar la primera devolución y después analizar acuerdos/desacuerdos. No corregir automáticamente diferencias ni llamarlas test independiente. BETO sigue sin pesos disponibles; no se reintentó una búsqueda de modelos léxicos ni se presenta entrenamiento contextual inexistente.

## Unidad anterior: clasificadores H/D con control de copias (completada)

- **Autorización:** después de consultar sets financieros españoles y expresar preocupación por resultados H/D cercanos al 50%, el usuario indicó «ok has todas las pruebas que quieras pero manten todo limpio». Se mantuvo una ronda acotada y prefijada, sin búsqueda interminable.
- **Contextuales pendientes por infraestructura:** se verificó BETO en el README oficial `dccuchile/beto`. No hay GPU, solo dos CPU/~3,8 GiB RAM y ningún checkpoint local. Python no pudo obtener siquiera `config.json` de Hugging Face (TLS EOF), aunque PyPI respondió. No se adquirieron pesos ni instalaron paquetes grandes; no se entrenó BETO ni se generó código vacío para simularlo. Su calidad queda sin medir, no rechazada.
- **Financieros auxiliares:** FinancES, MultiFin y Financial PhraseBank multilingüe se discutieron como recursos, no se importaron ni entrenaron. Sentimiento/tema no equivale a H/D; no convertir positivo/negativo en postura. La ruta de entrenamiento auxiliar de BETO queda pendiente, no probada.
- **Diseño previo:** [protocolo](PROTOCOLO_CLASIFICADORES_HD_V1.md), script 26 y 14 tests nuevos (12 pasaron antes del fit, 2 de artefactos se activaron al ejecutar). Cinco candidatos: LR palabras, SVM palabras, LR palabras+caracteres, SVM palabras+caracteres y LR jerárquica neutral/direccional→H/D. A compartida; parámetros fijados, sin externos ni nuevos umbrales. Ancla histórica aparte.
- **Purga nueva y explícita:** mismas 793 validaciones por reunión; retirar solo de train sus copias normalizadas (espacios/minúsculas/acentos). Retirados por fold **16/15/15/10/11**, incluidos **7/6/6/4/5** del grupo inicialmente fijo. Train queda **1178/1178/1178/1183/1183**. Las 34 validaciones con copias pasan a cero copias entre train/val. No borrar L0 ni etiquetas; no afirmar independencia semántica, ausencia de copias internas o reserva nueva.
- **Principal prefijada:** media de (F1_H+F1_D)/2 sobre todas las filas, penaliza falsas alarmas sobre N. No es accuracy ni confianza. **B0/B1/B2/B3/B4 = 0,691477 / 0,628481 / 0,649631 / 0,641184 / 0,647029**. Ninguna alternativa gana. Macro-F1 H/D/N medio **0,783501 / 0,740357 / 0,754841 / 0,749707 / 0,752287**.
- **Señal de cautela:** SVM mixta da mayor accuracy global (**0,9256**, 59 errores frente a 60 de B0), pero recall D de solo **0,4490** frente a **0,7347**. No seleccionarla por el porcentaje global. B0 recupera **90/118 H/D IA (0,7627)**; no es el resultado humano anterior ni demuestra haberlo mejorado. La regla constante H da **0,5847** sobre H/D, pero falla en todos los neutrales; neutral constante da **0,8512** global y cero H/D.
- **Efecto de purga:** ancla histórica idéntica (0,780282 macro-F1 medio, 62 errores). B0 limpia (0,783501, 60 errores) corrige únicamente dos neutrales; no cambia recall H/D ni las 17 confusiones H↔D. No presentar esta limpieza como solución del problema direccional.
- **Conducta conocida:** 14 casos por cinco folds por seis variantes = 420 filas, no independientes. Aciertos por variante histórica/B0/B1/B2/B3/B4 **25/25/26/10/20/25 de 70**. Invariancia no es corrección. Ningún retoque por resultados.
- **Cierre:** ninguna alternativa cumple el criterio de confirmación. [Informe](EVALUACION_CLASIFICADORES_HD_V1.md), artefactos en `data/evaluacion/clasificadores_hd_v1/`. Repetición de **nueve CSV, métricas e informe idénticos**; **116 tests superados**, una prueba omitida expresamente para no abrir gold. **177 archivos previos intactos**, modelo y cinco CSV humanos comprobados por hash. Sin predicciones humanas, refit completo o modelo persistido.
- **Limpieza:** un evaluador nuevo, un archivo de tests, protocolo/informe y resultados trazables; repetición en temporal eliminado. Sin nuevos datasets, checkpoints, dependencias ni scripts sin ejecutar. Se conservan resultados negativos porque son evidencia utilizada, no archivos sobrantes.
- **Siguiente límite:** no extender C/longitudes/pesos de esta ronda después de verla. Para BETO hace falta un entorno que permita adquirir pesos, preferentemente con GPU. Una mejora futura debe confirmarse con humanos nuevos y reservados; los 306 conocidos no vuelven a ser test intacto.

## Unidad anterior: piloto WCB Chile autorizado y completado (2026-09-16)

- **Autorización:** tras consultar disponibilidad, el usuario indicó «ok si puedes probarla bien mientras pensare otra forma». Se comunicó el alcance acotado de 100 frases antes de entrenar. Esta autorización sustituye la nota anterior que dejaba pendiente importar/entrenar.
- **Fuente:** WCB Chile público en Hugging Face/GitHub, 1.000 frases en inglés; 700/150/150 por configuración, tres semillas que no se suman como 3.000 ejemplos independientes. Licencia CC BY-NC-SA 4.0. [Atribución y datos](../data/externos/wcb_chile_piloto_v1/README.md).
- **Adquisición limitada:** primeros 100 registros de train 5768, respuesta completa de API consultada por páginas y columnas capturadas a TSV. No descarga Parquet verificada por hash remoto. No se adquirieron ni inspeccionaron val/test externos ni otras semillas. La descarga directa por Python falló por TLS en los endpoints HF; la herramienta de páginas sí accedió. No se instalaron dependencias ni modelos de traducción.
- **Idioma:** no se estableció correspondencia por frase con originales españoles. Se guardó una traducción del agente de las 100 frases, no oficial ni ciega a etiquetas, con controles de cifras/signos/porcentajes pero sin revisión humana independiente. Selección de conveniencia y posible riesgo de transcripción. Original inglés y etiqueta se conservan al lado.
- **Etiquetas:** 28 H/30 D/41 N/1 irrelevant. El único irrelevant queda fuera de B, sin convertirlo en neutral. A se ajusta solo con IA. No armonizar ni corregir WCB según v2: se prueba transferencia tal como viene, con incompatibilidades de diagnóstico/escenario extranjero explicitadas. Nada se añade a las etiquetas canónicas.
- **Diseño congelado antes del fit:** [protocolo](PROTOCOLO_WCB_PILOTO_V1.md), `25_evaluar_wcb_piloto.py` y once nuevos tests. Diez tests pasaron antes del entrenamiento; el de artefactos se omitió hasta que existieran. Tres variantes, cinco folds históricos (559 fijos train/793 validación reutilizada), A compartida, B (1,4)/C2/min_df3, mismo peso y sin búsqueda. 99 externos adicionales en los train enriquecidos; balanced se recalcula, no es un control lingüístico puro.
- **Resultado macro-F1 medio:** B0 **0,780282**, +inglés **0,728468**, +español **0,725897**. Español delta **−0,054385**, mejora en **1/5** folds. Errores **62 → 74**, corrige **4** e introduce **16**; recall D **0,7347 → 0,5714**. El inglés también empeora (69 errores). No adoptar ni ampliar tamaño/pesos tras resultados. No descarta todo WCB, otras traducciones ni etiquetas armonizadas.
- **Verificación:** B0 idéntica a las 793 predicciones anteriores; A idéntica entre variantes. Cero duplicados exactos normalizados externos/IA (sin afirmar ausencia de duplicados semánticos); 34 duplicados IA históricos permanecen. Repetición completa: cuatro CSV, auditoría, métricas e informe idénticos. **102 pruebas superadas y una omitida** por acceso a referencias humanas. **160 archivos previos intactos**, modelo y cinco CSV del examen anterior verificados por hash.
- **Cierre:** [informe](EVALUACION_WCB_PILOTO_V1.md), fuentes/traducción separadas en `data/externos/wcb_chile_piloto_v1/`, evaluación en `data/evaluacion/wcb_chile_piloto_v1/`. Sin reabrir/predicir 306 humanos, sin refit de las 1.352, sin persistir clasificadores ni puntuar corpus. Comparación retrospectiva (externos 2018–2024 contra IA 2005–2015), no simulación histórica sin información futura.

## Unidad anterior: comparación del híbrido mínimo v1 (completada)

- **Autorización:** el usuario pidió avanzar con la recomendación tras la investigación. Protocolo y código fijados por hash antes del ajuste al corpus, doce nuevos tests, ninguna modificación del código experimental anterior.
- **Métodos:** B0 texto completo (1,4); B1 tokenizador numérico; B2 vista completa + ventanas candidatas y vecinas; B3 números + contexto. Mismos parámetros y cinco folds históricos. A única por fold. No reglas que impongan H/D, ni filtro temporal o internacional. Este contexto es una selección de fragmentos, no un extractor semántico completo.
- **Resultados de macro-F1 medio:** **B0 0,780282; B1 0,779266; B2 0,776352; B3 0,776365**. DE: 0,0640/0,0618/0,0699/0,0747. Ninguna supera B0 ni satisface el criterio práctico prefijado de avance a confirmación. No seleccionar otra métrica a posteriori: B3 mejora ligeramente macro-F1 conjunto, pero no media por fold.
- **Errores:** totales 62/61/62/63; H↔D 17/18/17/16. B1 corrige dos errores e introduce uno; B2 corrige ocho e introduce ocho; B3 corrige nueve e introduce diez. No basta mostrar solo los corregidos.
- **Extracción:** 345/793 con contexto, 448 sin candidato (bloque cero, texto completo conservado), 41,0 % de caracteres seleccionados; ocho textos con formato numérico ambiguo. Ventanas con posiciones verificadas; no precisión semántica adjudicada.
- **Conducta:** 14 ejemplos inventados por cinco folds, 25/70 aciertos en todas las variantes. La frase sintética de bajar TPM 25 puntos se predice H en los cinco folds de las cuatro variantes; A la considera relevante. No inferir rendimiento poblacional de esta batería, pero tampoco dar por resuelta dirección/negación. No se ajustaron reglas ni modelos tras ver esos fallos.
- **Controles:** B0 reproduce 793 predicciones antiguas; A idéntica entre variantes. Reejecución completa en temporal: nueve CSV, métricas e informe idénticos. **92 tests: 91 pasados y uno antiguo omitido** para no reabrir respuestas humanas. Los doce nuevos pasaron; 136 archivos previos intactos, 42 fuentes históricas protegidas y cinco CSV del examen anterior comprobados solo por hash.
- **Archivos:** `scripts/representaciones_contextuales.py`, `scripts/24_evaluar_hibrido_contextual.py`, `tests/test_hibrido_contextual.py`, [protocolo](PROTOCOLO_HIBRIDO_V1.md), [informe](EVALUACION_HIBRIDO_V1.md), `data/evaluacion/hibrido_contextual_v1/`. `reproducibilidad.json` documenta el cierre; tiempos separados de CSV deterministas. Sin nuevas dependencias ni clasificadores persistidos.
- **Decisión:** cerrar esta comparación **sin adoptar el híbrido**; B0 (1,4) permanece referencia de desarrollo, no un reemplazo del modelo unigramas guardado. No extender longitudes ni variantes para perseguir mejora. Confirmación separada o extractor semántico/transformer requieren otro acuerdo.
- **Límites vigentes:** 793 reutilizados, 34 textos repetidos con train, no confirmación independiente. No se examinaron/predijeron los 306 humanos ni se cambió codebook/etiquetas. Sin refit de 1.352 ni scoring completo. Las 86 citas siguen pendientes por separado.

## Unidad anterior: investigación externa previa al híbrido (completada)

- **Alcance:** revisión dirigida de 20 fuentes: trabajos monetarios, opinión estructurada, vinculación de números, CheckList, cobertura–riesgo, supervisión débil, documentación oficial y foros. Se registra qué se leyó y qué no; no revisión sistemática exhaustiva ni reproducción de benchmarks externos.
- **Hallazgo central:** separar expresión de opción respaldada; representar acción/objeto, negación, emisor, condiciones y tiempo, sin borrar el texto completo ni descartar pasado/futuro. Las mejoras externas no son evidencia de mejora en nuestro corpus.
- **Advertencia WCB:** usa documentos disponibles en inglés. Tabla 98 de Chile en HTML v2 con columnas/contenido y meta de inflación inconsistentes. No auditoría del dataset, no prueba de inversión global, no importación. Cotejo PDF/autores pendiente si se considera reutilización.
- **Foros contrastados:** patrón numérico de TF-IDF y diferencia tokenizer/analyzer corroborados con scikit-learn 1.9.1; truncar puede perder la recomendación; stacking requiere predicciones fuera de muestra y evaluación externa. Dos consultas al mismo LLM no son validación independiente; disentir de un alza no implica necesariamente querer una tasa menor.
- **Propuesta, no autorización de ejecución:** comparar B0 base (1,4), B1 números, B2 contexto y B3 ambos, con A y parámetros base fijos. Primero congelar las representaciones y protocolo; transformer/LLM solo en una eventual segunda comparación autorizada.
- **Límites:** los 793 ya son desarrollo; no reabrir los 306 humanos ni llamar independiente a una nueva partición de ejemplos conocidos. Confirmación futura con control de reuniones/duplicados. Sin etiquetas nuevas, cambio de codebook, full refit, sustitución de modelo ni scoring.
- **Entregable:** [INVESTIGACION_HIBRIDO.md](INVESTIGACION_HIBRIDO.md), con evidencia, limitaciones, ejemplos didácticos y registro de fuentes/versiones. Solo se actualizan documentación e índices; no código ni dependencias nuevas.
- **Controles de esta unidad:** integridad por hash de 136 archivos bajo data/modelos/scripts/tests y documentos congelados, más comprobación de enlaces locales y `git diff --check`. No se ejecutan tests que entrenen o abran referencias humanas. **79 pruebas pasadas y una omitida corresponden al cierre experimental anterior**, no a una corrida nueva de esta investigación.
- **Siguiente:** decidir si autorizar la comparación de cuatro variantes y fijar el protocolo antes de implementarla; las 86 citas humanas pendientes siguen como asunto documental separado.

## Unidad anterior: influencias y diagnóstico contextual (completada)

- **Alcance:** el candidato (1,4) en cinco folds, no seis longitudes ni examen humano. Se reconstruyeron exactamente las 793 predicciones; no se buscó una nueva configuración.
- **Explicaciones:** top 25 coeficientes contrastivos por etapa/clase/fold; frecuencia documental y reuniones en train. Por intervención, cinco aportes positivos/negativos para A, ganador–segundo de B y H−D, con intercepto y residuo. Las sumas reproducen los márgenes lineales; no son efectos causales ni probabilidades calibradas.
- **Estabilidad:** unión de tops = 261 pares término–contraste / 199 términos únicos. No cambian de signo donde aparecen, pero 12 pares faltan en algún fold. No imputar ausencia como cero ni extrapolar a todo el vocabulario. Los entrenamientos comparten datos.
- **Errores contra IA:** 62 finales = 17 H↔D, 34 N→H/D y 11 H/D→N. A tiene 26 errores de relevancia (17 falsos relevantes, 9 falsos irrelevantes); los 160 forzados neutrales coinciden con postura IA neutral. A no es perfecta aunque no introduzca errores de postura en esas filas.
- **Revisión interpretativa:** 17 confusiones H/D completas, seis aciertos (fragmentos si largos) y cuatro errores con neutral. `revision_17_confusiones_hd.csv` conserva extractos verificados, IDs y razones. Revisor agente IA; no adjudicación humana ni cambio de etiquetas.
- **Hallazgos:** `25 puntos base` favorece H, aunque magnitud no define dirección; `5,25%` se tokeniza como `25`. `mantener` favorece D incluso con sesgo al alza o rechazo de bajas. Importan objeto (reducir estímulo ≠ reducir TPM), recomendación actual frente a pasado/contrafactual/menú y política de otros países. Aparecen también fórmulas y nombres sin dirección propia. No atribuir causalmente cada error a un solo término.
- **Propuesta, no implementación:** TF-IDF completo + representación de fragmentos de decisión contextual + revisión de contradicciones. Normalización numérica y enmascaramiento de nombres en B serían ablaciones separadas, no reglas automáticas de reemplazo. Conservar orientación futura y casos de mantener frente al menú.
- **Controles:** repetición del script 23 en temporal: seis CSV idénticos y resumen coincidente. **79 pruebas superadas; una antigua omitida** para no abrir respuestas humanas. Ocho nuevas pruebas pasaron. 42 fuentes protegidas y cinco CSV del examen previo intactos, comprobados por hash.
- **Archivos:** `scripts/23_diagnosticar_influencias.py`, `tests/test_influencias.py`, `docs/INFLUENCIAS_NGRAMAS.md`, `data/evaluacion/influencias_ngramas_v1/`. Revisión manual del agente e informe ligados a hashes; no modelos persistidos nuevos.
- **Límite/siguiente paso:** estos ejemplos ya sirven al desarrollo del posible híbrido, no a su confirmación independiente. Antes de implementarlo, acordar comparación pequeña y evaluación separada con control de textos repetidos. No abrir de nuevo los 306 humanos, no ampliar la búsqueda de n-gramas ni alterar etiquetas para concordar con el clasificador.

## Unidad anterior: búsqueda del límite 1–6 (completada)

- **Diseño congelado antes de entrenar:** mismos cinco folds que el experimento léxico, 793 intervenciones validadas y 559 siempre adicionales en train. A fija; solo B cambia `(1,n)` para n=1…6; min_df=3, C=2, sin diccionario. Selección por media macro-F1 sin redondear; empate exacto favorece menor longitud. No ampliar la búsqueda tras ver el resultado.
- **Resultados medios:** n=1: 0,7500; n=2: 0,7617; n=3: 0,7673; **n=4: 0,7803**; n=5: 0,7730; n=6: 0,7753.
- **Lectura:** (1,4) es el mejor entre los seis bajo esta configuración. Supera unigramas +0,0303 y mejora en 4/5 folds; supera al segundo (1,6) solo +0,0050. No es demostración de superioridad estadística ni óptimo universal. DE entre folds de (1,4): 0,0640; vocabulario B medio: 36.702, frente a 42.846 con (1,6).
- **Diagnósticos:** F1 H/D conjunto 0,7397/0,6372; recall H/D 0,7826/0,7347, contra IA. Tablas completas incluyen precisión, neutral, soportes, matrices, tamaño de vocabulario y resultados por fold.
- **Límites:** reserva reutilizada y resultados previos conocidos; permanecen 34 textos de validación idénticos a algún texto de su train. No se usa el catálogo completo para construir características. No se abren ni predicen las 306 respuestas humanas; no se reajusta con todas las 1.352 ni se reemplaza TF-IDF v1.
- **Verificación:** límites 1 y 4 reproducen exactamente las predicciones anteriores. Reejecución del script 22 en temporal: cuatro CSV, métricas, selección e informe idénticos. **71 pruebas superadas; una antigua omitida** para no reabrir las respuestas humanas. Las ocho pruebas nuevas pasaron. 42 fuentes protegidas intactas y cinco CSV del examen anterior verificados solo por hash.
- **Archivos:** `scripts/22_seleccionar_longitud_ngramas.py`, `tests/test_longitud_ngramas.py`, `docs/LONGITUD_NGRAMAS.md` y `data/evaluacion/longitud_ngramas_v1/`. No hay nuevas dependencias, modelos persistidos ni temporales dentro del repo.
- **Qué sigue:** cerrar esta búsqueda con (1,4) como candidato y acordar la confirmación antes de adoptarlo/puntuar el corpus. No seguir buscando longitudes para perseguir una mejora; una confirmación independiente debe controlar también los textos repetidos.

## Unidad anterior: n-gramas y diccionario (completada)

1. Se separaron **559 intervenciones / 52 reuniones** para descubrir/revisar expresiones; **793 / 80 reuniones** para validación interna. Semilla 20260935, 40 % de reuniones para descubrimiento.
2. Se extrajeron **9.247 n-gramas** de 1–4 palabras con frecuencia mínima de cinco intervenciones y tres reuniones. Priorización prefijada por frecuencia/asociación H/D y vocabulario monetario.
3. El agente IA revisó **73 candidatos / 219 extractos**: 3 restrictivos, 2 expansivos, 36 contextuales y 32 sin dirección. No es adjudicación humana ni revisión exhaustiva de ocurrencias. Asociación estadística no equivale a significado.
4. Se congeló el diccionario y se compararon cuatro variantes en los mismos cinco folds de la reserva. Descubrimiento entra únicamente en train; A queda fija, B varía representación. C=2 y min_df=3, sin nueva optimización.

| Variante B | Macro-F1 medio de folds |
|---|---:|
| Unigramas | 0,7500 |
| Unigramas + diccionario | 0,7562 |
| N-gramas 1–4 | **0,7803** |
| N-gramas 1–4 + diccionario | 0,7124 |

**Lectura:** ampliar a n-gramas es la opción más prometedora de esta comparación. Añadir el diccionario mejora unigramas solo +0,0061 (3/5 folds) y perjudica n-gramas −0,0679 (4/5 folds). Sus señales cubren 56/793 intervenciones. No se adoptó automáticamente ningún modelo ni se midió una mejora humana.

5. Después de la evaluación se generó el catálogo descriptivo completo: **23.252 n-gramas** de las 1.352 IA. Solo 73 tienen revisión semántica; los demás figuran `no_revisado`. No se usó este catálogo para retocar el diccionario.
6. Se repitieron scripts 20 y 21 en temporales con la revisión v1 intacta: cuatro CSV de extracción y cinco de evaluación idénticos byte a byte, métricas e informe generado coincidentes. **63 pruebas pasaron**; una antigua se omitió expresamente para no reabrir las 306 respuestas guardadas. Las 15 nuevas pruebas sí pasaron.

**Control adicional de cierre:** 42 fuentes protegidas idénticas a HEAD y cinco CSV del examen anterior intactos, comprobados solo por hash. La separación por reunión no elimina textos repetidos: **34/793** filas de validación tienen un texto idéntico a algún texto de su train (5/7/9/5/8 por fold, normalizando espacios). No se eliminan después de ver resultados ni se oculta esta limitación; tampoco es una evaluación estricta de textos inéditos. Detalles en `integridad_cierre.json`.

**Artefactos:** `scripts/lexico_ngramas.py`, `20_extraer_ngramas.py`, `21_evaluar_lexico.py`; `data/lexico/ngramas_v1/`; `data/evaluacion/lexico_ngramas_v1/`; `tests/test_lexico_ngramas.py`. Protocolos/manifiestos y `reproducibilidad.json` conservan hashes y limitaciones. No se guardaron modelos adicionales ni archivos temporales en el repo.

**Límite esencial:** esta reserva protege la construcción del diccionario, pero la selección del baseline anterior ya usó las 1.352 IA. Es comparación interna exploratoria, no test nuevo. El resultado humano agregado anterior ya era conocido. No equiparar 0,7803 con rendimiento humano ni comparar directamente contra el 0,7264 de otra partición. Tras consultar el catálogo completo, cualquier ampliación posterior debe ser una nueva versión con su alcance de validación explícito.


## Resultados y límites

| Clase humana | Casos | Coincidencias | F1 |
|---|---:|---:|---:|
| hawkish | 49 | 27 | 0,6067 |
| dovish | 32 | 17 | 0,4658 |
| neutral | 225 | 216 | 0,9600 |

- Siempre neutral daría accuracy 0,7353 y macro-F1 0,2825. El clasificador supera ese piso en este test, pero distingue peor H/D que neutral: 28 de los 46 errores son intercambios entre hawkish y dovish.
- Sin los 12 textos gold idénticos a training: n=294, accuracy 0,8503, macro-F1 0,6859, κ 0,6512.
- Las 115 reuniones del gold aparecen en training; no es test de reuniones nuevas ni predicción temporal prospectiva. El gold está enriquecido por vocabulario de decisión.
- La media CV de selección es optimista (escoge el mejor de 12); no es una prueba independiente. El macro-F1 OOF agregado del elegido es 0,7271, diferente de la media por fold 0,7264.
- Los desgloses por fase y señal del JSON usan tres clases fijas; algunos subgrupos carecen de ejemplos de alguna clase. Interpretar junto a los soportes, no comparar sus macro-F1 como si tuvieran idéntica composición.
- El κ obtenido es **TF-IDF vs humano**, no IA conversacional vs humano. Esta última comparación es un control opcional, no un requisito para evaluar el clasificador.

## Procedencia y pendiente documental

- Fecha real confirmada por el usuario: **2026-09-16** para las 306 anotaciones.
- Procedimiento declarado: decisiones humanas iniciales, seguidas de consulta a una IA sobre acuerdo/razones; **ninguna etiqueta cambió**, según el anotador. No se auditaron registros previos ni se infiere autoría humana independiente de notas/citas/confianza.
- Se conservan el libro recibido, el canónico, las etiquetas y codebook v2 intactos. La fecha se aplica explícitamente en memoria al validar la referencia; no se generó un canónico llenado ni se usó `--forzar`.
- **Siguen pendientes 85 citas no verbatim y una de 334 caracteres.** No impiden calcular métricas de clases completas, pero sí la importación documental validada. No se cambiaron citas ni etiquetas para concordar con el modelo.
- Registro de procedencia ligado al hash: `data/auditoria/2026-09-16/procedencia_gold.json`. Instrucciones: [INSTRUCCIONES_GOLD.md](INSTRUCCIONES_GOLD.md).

## Trabajo de esta sesión

- Funciones compartidas de entrenamiento/predicción en script 15; ahora aceptan parámetros sin modificar los defaults del baseline. Su OOF de referencia sigue en **0,7173** contra IA.
- `scripts/18_seleccionar_tfidf.py`: protocolo previo, rejilla de 12 candidatos, CV por reunión, selección por media no redondeada, reajuste completo y predicciones sin abrir el Excel humano.
- `scripts/19_evaluar_tfidf_gold.py`: verifica hashes/selección antes de leer respuestas; compara por ID, registra citas pendientes y genera métricas/desgloses/informe. No entrena.
- Resultados congelados en `data/evaluacion/tfidf_gold_v1/`: protocolo, validación, particiones, selección, predicciones, comparación, métricas y manifiestos. Nunca se sobrescriben.
- Modelo local reconstruible: `modelos/tfidf_gold_v1.joblib`, ignorado por Git.
- **49 tests aprobados.** Reejecución completa en temporal: cinco CSV idénticos byte a byte y todas las métricas coincidentes. Evidencia en `reproducibilidad.json`. La repetición no cambió parámetros ni examinó otras alternativas sobre el test.
- Auditoría integral (script 17) reejecutada; documentos de continuidad actualizados.

## Qué sigue

1. Cerrar el pendiente de 86 citas en una nueva versión, sin cambiar las decisiones humanas; conservar esta evaluación y sus hashes.
2. Acordar si probar el híbrido contextual propuesto a partir del diagnóstico, conservando (1,4) como referencia. No está entrenado ni tiene mejora medida. Antes de adopción/scoring, fijar confirmación separada; los errores revisados pertenecen al desarrollo. BETO sigue sin ejecutarse.
3. **El test de 306 ya se examinó.** No ajustar usando sus errores y presentar después el mismo test como intacto; si sus resultados guían cambios de criterios/modelo, reservar una nueva evaluación independiente. Puede mantenerse como benchmark explícitamente ya conocido.
4. Pendientes anteriores: test-retest 30, metadata de actores, manifiesto macro y scoring del resto. No se hicieron en esta sesión.

## Corpus y auditoría conservados

- L0: 9.725 intervenciones, 132 reuniones, 55 actores; 51 textos dañados. 8.373 IDs sin etiqueta IA, 8.016 sanos fuera de training y gold.
- Training: 116 H / 89 D / 1.147 N; 269 irrelevantes. Todos validados y con cobertura exacta de tandas.
- Macro/metadata: 62 reuniones sin desempleo; siete pendientes macro; tres actores con flag histórico de verificación. No se inventaron datos faltantes.
- Serie agregada de etiquetas IA: Spearman 0,6639 vs ΔTPM en 131 reuniones relevantes; solo sanidad descriptiva.
- Limpieza previa: ocho archivos obsoletos retirados, fuentes/muestras protegidas. [Auditoría histórica](REVISION_2026-09-16.md), [convenciones](CONVENCIONES_ETIQUETADO.md), [reglas](REGLAS.md).

## Retoma operativa

```bash
~/venvs/fase2/bin/python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/venvs/fase2/bin/python scripts/17_auditar_estado_gold.py --reproducir-baseline
```

Para repetir 18/19 sin sobrescribir resultados, usar nuevas rutas como se explica en el informe. No volver a ejecutar la búsqueda para escoger por el desempeño humano.

Rama de sesión: `arena/01a0a81b-fase-2`. El registro anterior a la limpieza se recupera con `git show 957200f74b61c0527d57c333dd360b3587d0a7e8:docs/AVANCE.md`; no tomar sus cifras históricas de baseline como actuales.
