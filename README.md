# FASE_2

Proyecto D&H: score **hawkish/dovish por intervención** en las Actas de las Reuniones de Política Monetaria del Banco Central de Chile (2005–2015).

- Datos: `consolidado_D&H.xlsx` — 9.725 intervenciones, 132 reuniones, 55 actores
- Plan metodológico + roadmap + cómo retomar: [`PLAN.md`](PLAN.md) (sección 9.1 handoff)
- Reglas de trabajo: [`docs/REGLAS.md`](docs/REGLAS.md)
- Estado y continuidad entre sesiones: [`docs/AVANCE.md`](docs/AVANCE.md)
- Codebook de etiquetado vigente (v2, congelado): [`docs/codebook_v2.md`](docs/codebook_v2.md)

## Estado (2026-09-16)

**Siguiente paso preparado: BETO en GPU.** [Abrir en Colab](https://colab.research.google.com/github/joako0o/FASE_2/blob/c93eef3f1fdd9ea3e43b52a7dcff9d46b1035259/notebooks/BETO_comparacion_v1.ipynb) · [guía paso a paso](docs/GUIA_EJECUTAR_BETO_COLAB_V1.md) · [investigación y protocolo](docs/INVESTIGACION_Y_PROTOCOLO_BETO_V1.md). Entrada fija: 1.352 textos íntegros (1.997.823 caracteres), cinco particiones originales, 793 predicciones TF-IDF, referencias v2 y filtro A sin cambios. **78 pruebas aprobadas** (14 nuevas sin encoder + 64 anteriores), paquete reproducido byte a byte y **313 archivos anteriores intactos**. El notebook descarga una revisión fija del código y exige prueba técnica GPU antes del experimento. **Pesos, prueba real y entrenamiento BETO aún pendientes**: aquí no hay GPU y persiste el bloqueo TLS. No hay métricas BETO ni mejora demostrada; no hacen falta nuevas anotaciones.

**Diagnóstico H/D completado:** [lectura y recomendación](docs/LECTURA_DIAGNOSTICO_INVERSIONES_HD_V1.md) · [aportes exactos por caso](docs/DIAGNOSTICO_INVERSIONES_HD_V1.md). Relectura íntegra de diez inversiones (40.937 caracteres), cinco ambiguas aparte y 793 predicciones reproducidas. La evidencia direccional puede perder frente al resto del texto; también aparecen problemas de objeto/condición/nivel y contribución del intercepto. La sonda de primera cita da 4 coincidencias, 4 N y 2 inversiones: no es un extractor ni una métrica de mejora, y algunas citas aisladas pierden contexto necesario. **64 pruebas aprobadas**, seis salidas e informe técnico reproducidos exactamente y 298 archivos anteriores intactos. Etiquetas/métricas sin cambios; comparación contextual diseñada, BETO no ejecutado.

**Entrenamiento más reciente:** las 13 propuestas fueron aceptadas mediante «corrige las referencias» y se aplicaron en una [referencia versionada de desarrollo](data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv), sin borrar originales ni cambiar los 12 ambiguos. **TF-IDF ejecutado localmente:** contra la misma referencia corregida, F1 H/D **0,711084 → 0,747060**, errores **55 → 51**, mejora en 4/5 folds. El efecto de cambiar referencias se muestra aparte; no es test independiente. [Informe](docs/EVALUACION_REFERENCIAS_CORREGIDAS_V2.md) · [Protocolo](docs/PROTOCOLO_REFERENCIAS_CORREGIDAS_V2.md). **56 pruebas aprobadas**, replay exacto y 284 archivos previos intactos. BETO sigue sin pesos: nuevo intento urllib/curl bloqueado por TLS.

Los puntos siguientes documentan la secuencia histórica; la aceptación de las 13 propuestas sustituye su estado anterior de pendientes.

- **Entrenamiento:** 1.352 etiquetas IA en 19 CSV, validadas y sin duplicados.
- **Validación para elegir hiperparámetros:** 12 configuraciones × cinco particiones por reunión, solo con IA. Ganador: unigramas, min_df=3, C=2; macro-F1 promedio **0,7264**.
- **Examen contra tus 306 etiquetas:** **260 coincidencias (84,97 %)**, 46 errores; **macro-F1 0,6775**, **κ 0,6458**. El modelo se reajustó con las 1.352 y sus predicciones se guardaron antes de abrir las respuestas humanas.
- **Pendiente documental:** 86 citas por corregir; fecha confirmada 2026-09-16. Decisiones humanas con revisión posterior de IA y sin cambios declarados. No se forzó la importación ni se alteraron etiquetas.
- **Nuevo experimento léxico:** 73 expresiones revisadas por IA sobre 559 intervenciones de descubrimiento; comparación en otras 793, separadas por reunión. Mejor media interna: **0,7803 con n-gramas 1–4 sin diccionario**, frente a 0,7500 con unigramas. El diccionario no mejoró consistentemente. No se reemplazó el modelo ni se repitió el test humano.
- **Búsqueda de longitud completada:** seis límites (1–6), mismos folds y parámetros, sin diccionario. Ganó **(1,4): 0,7803**, frente a 0,7753 con (1,6). Es selección interna, no óptimo universal ni confirmación humana.
- **Diagnóstico de influencias:** se explicaron las 793 predicciones del candidato (1,4) en cinco folds. Se revisaron las 17 confusiones H/D y una muestra de otros 10 casos. Hallazgos: magnitud/decimales sin dirección, mantener frente a sesgo o rechazo, objeto de reducir, pasado/menús y fórmulas. Se propuso un híbrido contextual; su primera versión mínima ya se comparó (ver abajo).
- **Investigación externa completada:** revisión dirigida de trabajos monetarios, extracción estructurada, números, evaluación y foros; 20 fuentes registradas. Recomienda comparar representación numérica y contexto por separado, sin reglas que inviertan automáticamente H/D. La guía chilena de WCB presenta inconsistencias en el HTML consultado; no se importaron datos en esa unidad; el piloto posterior se describe abajo. [Informe y fuentes](docs/INVESTIGACION_HIBRIDO.md).
- **Híbrido v1 comparado:** base **0,7803**, números **0,7793**, contexto **0,7764**, ambos **0,7764** de macro-F1 medio. Ninguna modificación supera la referencia ni cumple el criterio previo. Se cierra esta ronda **sin adoptar el híbrido**. Es una vista de fragmentos, no un extractor semántico completo. [Resultados](docs/EVALUACION_HIBRIDO_V1.md).
- **Piloto WCB completado:** 100 frases del train público, 99 incorporadas a B; traducción del agente, no oficial. Macro-F1 medio: base **0,7803**, +inglés **0,7285**, +español **0,7259**; errores con español **62 → 74**. No adoptar esta importación. Muestra acotada, criterios distintos sin armonizar y traducción no independiente: no es prueba de las 700/1.000 frases completas. [Informe](docs/EVALUACION_WCB_PILOTO_V1.md).
- **Comparación H/D con control de copias:** cinco candidatos sobre train purgado y las mismas 793 IA. F1 H/D medio: **LR palabras 0,6915**, SVM 0,6285, LR mixta 0,6496, SVM mixta 0,6412, jerárquica 0,6470. Ninguna alternativa gana. La SVM mixta tiene mayor accuracy global, pero recupera solo 44,9 % de D: no se adopta. [Informe](docs/EVALUACION_CLASIFICADORES_HD_V1.md).
- **BETO no ejecutado:** sin pesos locales; descarga HF falla con TLS EOF, sin GPU. No se instalaron dependencias grandes ni se simuló entrenamiento. No hay resultados de BETO o de entrenamiento auxiliar con FinancES.
- **Revisión de entrenamiento recibida y comparada:** los 30 casos corresponden íntegramente a la muestra congelada. **24 acuerdos / 6 diferencias** con las etiquetas IA: H 10/10, D 5/10 y N 9/10. Los cinco D restantes fueron N humanos; el otro desacuerdo fue N IA → H humano. No es accuracy de un clasificador ni estimación poblacional. [Resultado reproducible](docs/REVISION_HUMANA_ENTRENAMIENTO_30_V1.md).
- **Seis adjudicaciones aprobadas:** el investigador respondió «acepto todas»: R01 H / R03 N / R08 D / R12 H / R17 D / R21 D. [Registro de aceptación](docs/ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md), separado de originales y propuestas históricas. Es adjudicación asistida por IA posterior al feedback, no nuevo test independiente. No repetir anotaciones. **Etapa posterior:** referencia TF-IDF ya comparada en una vista experimental (ver abajo); las corridas canónicas siguen intactas.
- **Referencia tras adjudicación ejecutada:** mismos cinco folds purgados, 793 etiquetas IA de validación y parámetros fijos. Tres cambios efectivos de train (R01/R03/R12): F1 H/D medio **0,691477 → 0,648822**; macro-F1 **0,783501 → 0,754311**; errores **60 → 66**. Un error corregido y siete nuevos. No es mejora humana ni prueba de que la adjudicación sea incorrecta; no revertir decisiones para subir acuerdo IA. [Informe](docs/EVALUACION_MODELO_ADJUDICADO_V1.md).
- **Revisión de etiquetas cerrada: 66/66 casos leídos completos.** [Informe consolidado y última tanda](docs/REVISION_ERRORES_CIERRE_66_V1.md): **41 referencias respaldadas, 13 cuestionables y 12 ambiguas**, según el agente en ese cierre, antes de la aceptación posterior. Últimos 13 textos: 105.621 caracteres íntegros, 8 N respaldadas y 5 propuestas nuevas. El informe histórico reúne las 13 propuestas, ahora aceptadas y aplicadas por el experimento 36; CSV consolidado con las 66 opiniones y evidencia. A=1 y final=B en los 13 nuevos. 34 pruebas específicas aprobadas, cinco salidas e informe reproducidos exactamente y 273 archivos previos intactos. Cobertura completa de los desacuerdos, no estimación representativa del corpus ni nuevo test independiente.
- **Próximo bloqueo técnico:** BETO sigue sin pesos; nuevo chequeo config/API falla TLS EOF, dos CPU y sin GPU detectada. [Protocolo previo y diseño para textos completos](docs/PROTOCOLO_MODELO_ADJUDICADO_V1.md). Su runner aún no está implementado/validado con pesos reales. Se necesita acceso a Hugging Face y preferiblemente un entorno GPU, no más anotaciones ni otra búsqueda léxica.
- **Controles del entrenamiento adjudicado:** 10 pruebas nuevas + 9 de recepción aprobadas; cuatro CSV, métricas e informe reproducidos exactamente; 233 archivos previos intactos. La referencia original reproduce B0 limpia. Sin respuestas de 306, refit final, modelo persistido o modificación de corridas canónicas.
- **Custodia y límites:** XLSX original archivado con commit/hash de recepción; ninguna decisión sobrescrita. 18 citas literales y 12 marcadores de ausencia; relevancia, fecha y ayuda/acceso a IA no declarados. No se imputan. No se afirma revisión ciega independiente ni importación canónica completa.
- **Controles de esta devolución:** nueve pruebas aprobadas; tres CSV, resumen e informe reproducidos exactamente; 216 archivos previos intactos. Se verificaron también las siete citas adicionales del análisis del agente. Sin reabrir los 306 humanos ni ejecutar la suite ML histórica.
- **Entrega anterior conservada:** [XLSX de los 30 casos](data/auditoria/revision_entrenamiento_30_v1/revision_entrenamiento_30.xlsx) y [formulario](data/auditoria/revision_entrenamiento_30_v1/formulario/index.html). Son plantillas vacías, no el archivo rellenado ni recuperación del avance perdido. **No es necesario volver a completarlas.** Los controles anteriores (127 de preparación y 18 de Excel/interfaz) corresponden a esas etapas, no a la comparación nueva.

[Comparación de clasificadores H/D](docs/EVALUACION_CLASIFICADORES_HD_V1.md) · [Piloto WCB Chile](docs/EVALUACION_WCB_PILOTO_V1.md) · [Comparación del híbrido v1](docs/EVALUACION_HIBRIDO_V1.md) · [Investigación de trabajos y foros](docs/INVESTIGACION_HIBRIDO.md) · [Influencia de palabras y propuesta de híbrido](docs/INFLUENCIAS_NGRAMAS.md) · [Búsqueda del límite 1–6](docs/LONGITUD_NGRAMAS.md) · [N-gramas: revisión y comparación IA](docs/LEXICO_NGRAMAS.md) · [Resultado del examen y matriz de confusión](docs/EVALUACION_TFIDF_GOLD.md) · [Auditoría y limpieza](docs/REVISION_2026-09-16.md) · [Correcciones gold](docs/INSTRUCCIONES_GOLD.md)

El baseline de configuración fija sigue disponible: macro-F1 OOF **0,7173 contra IA**. Es distinto del 0,7264 de selección y del 0,6775 del test humano; no intercambiar estas cifras.

## Setup y comprobaciones

Python **3.11**; dependencias fijadas a las versiones auditadas.

```bash
python3 -m venv ~/venvs/fase2
~/venvs/fase2/bin/pip install -r requirements.txt
~/venvs/fase2/bin/pip check
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  ~/venvs/fase2/bin/python -m unittest discover -s tests -p test_referencias_corregidas.py -v
```

**Precaución:** la suite general y el auditor 17 pertenecen a la auditoría integral y pueden abrir referencias humanas; no usarlos para verificar esta etapa. El bloque anterior ejecuta solo las pruebas de la referencia corregida. Para verificar además el entrenamiento anterior sin abrir las respuestas del examen: `python -m unittest discover -s tests -p test_modelo_adjudicado.py -v`. La devolución tiene su propia unidad: `python -m unittest discover -s tests -p test_revision_humana_30.py -v`. Las pruebas del formulario original son otra unidad y algunas requieren el checkpoint histórico. El test DOM opcional requiere jsdom y su variable de entorno, como explica el [protocolo](docs/PROTOCOLO_REVISION_ENTRENAMIENTO_30_V1.md). El cierre global registrado omitió explícitamente `test_seleccion_y_test.ExamenCongelado.test_recalculo_independiente_metricas_guardadas`.

La auditoría escribe sus informes en `data/auditoria/2026-09-16/`; todas las reconstrucciones de insumos se hacen en temporales. **No ejecutar scripts 01–10 sobre las selecciones existentes para “actualizarlas”**: están congeladas y sus generadores rechazan sobrescrituras.

## Organización

- Excel originales en raíz: fuentes corpus/macro y devolución gold del usuario.
- `data/L0/`: corpus inmutable y EDA.
- `data/L2/`: macro, metadata y resultados derivados.
- `data/etiquetas/`: training IA append-only.
- `data/muestras/`: marcos de selección, tandas, resúmenes y test-retest.
- `data/auditoria/`: evidencias y controles reproducibles; revisión activa en `revision_entrenamiento_30_v1/formulario/`, con clave fuera de esa carpeta pública.
- `data/evaluacion/tfidf_gold_v1/`: protocolo, búsqueda, predicciones y examen humano congelados.
- `data/lexico/ngramas_v1/`: catálogo de descubrimiento, 73 decisiones, 219 contextos y revisión congelada.
- `data/evaluacion/lexico_ngramas_v1/`: comparación de cuatro variantes y catálogo completo descriptivo (23.252 n-gramas de las 1.352 IA).
- `data/evaluacion/longitud_ngramas_v1/`: búsqueda de seis longitudes, vocabularios por fold, selección y reproducibilidad.
- `data/evaluacion/influencias_ngramas_v1/`: top de coeficientes por fold, estabilidad, aportes locales y revisión de errores IA.
- `data/externos/wcb_chile_piloto_v1/`: muestra inglesa y traducción IA, separadas de las etiquetas; licencia CC BY-NC-SA 4.0 y atribución.
- `data/evaluacion/wcb_chile_piloto_v1/`: protocolo, auditoría y comparación de la ampliación con 99 frases.
- `data/evaluacion/clasificadores_hd_v1/`: purga textual de train, comparación de cinco candidatos H/D y ancla histórica, reproducción.
- `modelos/`: modelo local reconstruible, ignorado por Git.
- `scripts/`: transformaciones, validadores, modelos y auditoría; utilidades compartidas.
- `tests/`: regresiones automatizadas sin escrituras en datos originales.

## Consultar la interfaz de los 30 casos (entrega ya devuelta)

La vista previa permite únicamente el formulario y la descarga XLSX, nunca la raíz del repositorio ni la clave IA:

```bash
python scripts/29_preparar_excel_revision.py --servir --puerto 8080
```

**Ya recibimos las 30 decisiones en un XLSX separado; no repetir el trabajo.** Las instrucciones siguientes describen la entrega original y no importan la devolución al navegador.

Para completar en Excel basta descargar el XLSX enlazado arriba y devolverlo por el chat. El botón XLSX de la web usa el servidor del script 29; no un Blob. También se puede abrir su `index.html` autónomo para el modo anterior, pero la descarga web del libro requiere el servidor. La interfaz v1.1 permite copiar el JSON manualmente si el visor bloquea las descargas; conserva la misma muestra y clave de autoguardado. Al reabrir, comprobar el aviso de avance recuperado. Si no aparece, no rellenar nuevamente todavía y avisar por chat. Las respuestas no llegan al servidor: descargar JSON o usar «Mostrar / copiar JSON» y pegarlo en el chat. El autoguardado depende del navegador/origen; el JSON permite respaldar y recuperar avances. No abrir `NO_ABRIR_hasta_finalizar_clave.csv` antes de decidir.

Rama de sesión: `arena/01a0a81b-fase-2`.
