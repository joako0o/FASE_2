# Clasificación de postura monetaria del Banco Central de Chile

Proyecto final y condensado para clasificar intervenciones de actas BCCh de **2005–2015** como `hawkish`, `dovish` o `neutral`.

## Resultado final

El modelo formal es **W+C+600**: TF-IDF de palabras y caracteres, regresión logística en dos etapas y voto de cinco miembros agrupados. En la evaluación ciega agrupada obtuvo:

| Accuracy | Macro-F1 | F1-HD | F1 H | F1 D | Recall D | Errores |
|---:|---:|---:|---:|---:|---:|---:|
| 0,8562 | 0,7463 | 0,6632 | 0,7111 | 0,6154 | 0,7619 | 43/299 |

Superó de forma robusta al modelo anterior C+89. El análisis factorial mostró que la mayor parte de la mejora proviene de las 600 anotaciones adicionales; el aporte incremental de caracteres frente a C+600 es pequeño e incierto. Esta distinción está preservada en la documentación.

## Estructura

```text
├── README.md                          Guía principal, arquitectura y fórmulas
├── requirements.txt                   Dependencias mínimas reproducibles
├── data/
│   ├── corpus_bcch_2005_2015.csv       Fuente canónica única del texto del corpus
│   ├── entrenamiento_wc600.csv         Entrenamiento final (1.596 filas)
│   ├── evaluacion_ciega_gold.csv       Gold estándar ciego (300 filas)
│   ├── predicciones_evaluacion_ciega.csv
│   ├── resultados_evaluacion_ciega.json
│   ├── analisis_factorial.json
│   └── benchmark_modelos.{csv,json}
├── modelos/wc600/                    Cinco miembros persistidos y manifiesto
├── resultados/
│   ├── clasificacion_wc600_9725.csv  Predicciones y probabilidades sin texto duplicado
│   └── analisis_descriptivo/         Índices, acuerdos, votos, tópicos K=14 y radar
├── datos_web/                         Paquete generado bajo demanda para scrollytelling
├── docs/
│   ├── CODEBOOK.md                   Criterios formales de postura H/D/N
│   ├── METODOLOGIA_Y_BENCHMARK.md    Pipeline W+C+600, análisis factorial y benchmark
│   └── RESULTADOS_LIMITACIONES.md    Tópicos NMF K=14, dinámica y límites inferenciales
├── scripts/
│   ├── modelo_final.py
│   ├── analisis_resultados.py
│   └── preparar_datos_web.py
└── tests/test_proyecto_esencial.py
```

## Uso

Python 3.11 recomendado:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/modelo_final.py verificar
.venv/bin/python scripts/modelo_final.py predecir data/corpus_bcch_2005_2015.csv predicciones_corpus.csv --cargar-modelos modelos/wc600
.venv/bin/python scripts/analisis_resultados.py
.venv/bin/python scripts/preparar_datos_web.py --sobrescribir
```

Los modelos ajustados están guardados en `modelos/wc600/`; no es necesario reentrenarlos para una nueva predicción. Los agregados con y sin neutrales, tópicos, actores y léxico están en `resultados/analisis_descriptivo/`.

En Windows, usar `.venv\Scripts\python.exe`. El comando de predicción entrena los cinco miembros con parámetros congelados y crea un CSV nuevo; nunca sobrescribe una salida existente.

## Clasificación completa disponible

El modelo ya fue ejecutado sobre las 9.725 intervenciones. El resultado está en `resultados/clasificacion_wc600_9725.csv`, con las cinco predicciones individuales, el voto final, el rol de cada fila y señales de acuerdo entre miembros. También conserva `pred_relevancia_v3`, `prob_relevancia_no_calibrada` y `acuerdo_relevancia_miembros`, lo que permite filtrar relevancia sin inferirla desde H/D/N. `resultados/resumen_clasificacion.json` contiene distribuciones y conteos por año.

## Objetivo sustantivo y por qué se solicitaron datos de actores

La clasificación H/D/N no era el producto final por sí sola. El plan histórico definió dos resultados principales:

1. construir una serie 2005–2015 de postura agregada del Consejo y contrastarla con la TPM;
2. estudiar cómo se forma esa postura a través de los participantes: especialización temática, posiciones persistentes o coyunturales, convergencia, disenso y afinidad.

Por eso se solicitaron nombres, cargos y metadatos de actores. El propósito era distinguir quién habla, en qué calidad y durante qué mandato, en vez de tratar todas las intervenciones como si provinieran de un único actor. Los productos previstos son:

- **perfil temático:** distribución de las intervenciones en seis ejes auditados —actividad/demanda/ciclo, mercado laboral/empleo, inflación/expectativas/meta, entorno externo/commodities/economías, tipo de cambio real/nominal y tasas de interés/plazos— para un radar comparativo;
- **vocabulario distintivo:** palabras y expresiones sobrerrepresentadas por actor mediante log-odds con prior informativo;
- **serie individual:** evolución del puntaje $s_{it}=P(H)-P(D)$ de cada actor y media móvil de 12 meses;
- **postura estructural y coyuntural:** descomposición

$$
s_{it}=\alpha_i+\beta_i\,ciclo_t+\varepsilon_{it},
$$

  donde $\alpha_i$ representa la inclinación media persistente del actor y $\beta_i$ su sensibilidad al ciclo común. Esta interpretación solo es válida con cobertura temporal suficiente y controles adecuados;
- **matriz de votos:** voto explícito por reunión y actor, con dirección, magnitud, fuente y confianza. Los votos deben extraerse del texto; una predicción de tono no equivale automáticamente a un voto;
- **convergencia dentro de la reunión:** si $s_{i,t}^{primera}$ y $s_{i,t}^{ultima}$ son los puntajes de la primera y última intervención pertinente y $d_t$ representa la decisión final:

$$
Convergencia_{it}=|s_{i,t}^{primera}-d_t|-|s_{i,t}^{ultima}-d_t|.
$$

  Un valor positivo indica acercamiento al resultado final durante la reunión;
- **disenso:** distancia entre el puntaje del actor y el consenso de su reunión:

$$
Disenso_{it}=|s_{it}-\bar{s}_t|;
$$

- **red de afinidad:** para cada par de actores, proporción de votos coincidentes o correlación de sus puntajes en reuniones compartidas. Esto permite explorar coaliciones y la posición del Presidente;
- **controles biográficos e institucionales:** mandato, presidencia o vicepresidencia, autoridad nominadora, formación y trayectoria profesional, siempre que existan fuentes verificables.

Convergencia, disenso y afinidad deben restringirse a miembros comparables del Consejo y reuniones con solapamiento suficiente. Staff, ministros y la fila institucional “Consejo del Banco Central de Chile” no deben mezclarse automáticamente con consejeros individuales.

Actualmente `resultados/analisis_descriptivo/indices_por_actor.csv` contiene el primer perfil cuantitativo: intervenciones, H/D/N, tono general, balance, cobertura y score continuo medio para 55 actores. `data/actores_metadata.csv` recupera la tabla histórica de nombres, cargos y fechas observadas, pero debe tratarse como **incompleta**: solo tres filas tenían verificación externa y los campos de nominación, formación y trayectoria permanecían vacíos. No se deben completar automáticamente ni usar como controles hasta documentarlos con fuentes confiables.

Estos resultados estaban destinados a tablas para investigación, visualizaciones tipo radar/red y eventualmente un *scrollytelling* y un paper. El detalle se encontraba en el antiguo `PLAN.md`, no en el README histórico de manera suficiente; se incorpora aquí para que no vuelva a perderse durante la condensación.

## Análisis rápido de actores

Se recuperaron `orden_habla` y `subindice` para las 9.725 filas, verificando correspondencia exacta de ID y texto con la fuente histórica. El análisis reproducible de `scripts/analisis_resultados.py` ahora entrega:

- `indices_por_tipo_y_actor.csv` e `indices_actor_por_anio.csv`: H/D/N, tono general, balance, cobertura y score medio, separando `miembro_consejo`, `staff_tecnico`, `hacienda_gobierno` y `consejo_institucional`;
- `variacion_anual_por_actor.csv`: primer y último score anual, cambio, mínimo, máximo, rango y pendiente descriptiva para actores con al menos 20 intervenciones y dos años;
- `topicos_por_actor.csv`: frecuencia, proporción y ranking de los 13 tópicos **anotados históricamente por la persona investigadora**; no es una detección del modelo;
- `topicos_modelo_nmf.csv`, `asignacion_topicos_modelo_nmf.csv` y `topicos_modelo_por_{reunion,anio,actor}.csv`: patrones temáticos descubiertos de forma no supervisada exclusivamente desde el texto, sin entregar `topico_humano` ni `keywords_humano` al modelo;
- `vocabulario_{frecuente,distintivo}_por_actor.csv`: 20 n-gramas sustantivos por actor con al menos 20 intervenciones sustantivas; el segundo usa log-odds contra el resto;
- `candidatos_votos_explicitos.csv` y `matriz_votos_candidatos.csv`: detección por expresiones como “vota” o “voto”, extracción de acción, magnitud, TPM objetivo y sesgo, siempre con estado de validación;
- `acuerdo_consejo_por_reunion.csv`: acción, magnitud, TPM objetivo, unanimidad/mayoría y texto fuente del acuerdo institucional para las 132 reuniones;
- `base_votos_acta_actor.csv`: base larga reunión–consejero que une cada voto individual con el acuerdo del Consejo y conserva texto, procedencia e inferencias separadas;
- `decision_institucional_proxy.csv`, `convergencia_actor_reunion_proxy.csv` y `convergencia_resumen_actor_proxy.csv`: proxy exploratorio de acercamiento dentro de cada reunión.

### Lectura rápida de resultados

Entre los miembros del Consejo con al menos 100 intervenciones, los scores medios continuos más positivos son Jorge Desormeaux (0,116; $n=221$), Vittorio Corbo (0,052; $n=455$), José De Gregorio (0,037; $n=1.047$) y Manuel Marfán (0,036; $n=855$). Los más negativos son Pablo García (-0,064; $n=100$), Enrique Marshall (-0,036; $n=483$), Rodrigo Vergara (-0,030; $n=1.026$), Joaquín Vial (-0,028; $n=231$) y Sebastián Claro (-0,022; $n=592$). Estas cifras describen tono clasificado, **no votos ni preferencias estructurales**. Siempre deben leerse junto con cobertura direccional: por ejemplo, va de 5,2% para Vial a 23,1% para Desormeaux en este conjunto.

Según las **anotaciones humanas históricas**, los tres tópicos principales varían: De Gregorio y Vergara concentran primero `debate`; Desormeaux y Vial, `escenario_internacional`; Marshall, `debate`; Marfán, `debate` y `mercados_financieros`; Claro, `debate`, `escenario_internacional` y `mercados_financieros`. Estas afirmaciones no deben atribuirse a W+C+600 ni al modelo temático. Las tablas conservan conteos y proporciones para no confundir volumen de habla con especialización. El vocabulario frecuente muestra uso; el distintivo, sobrerrepresentación. Ambos excluyen apertura/cierre, comunicado y decisión final, pero todavía pueden reflejar estilo y función institucional además de contenido económico.

### Tópicos descubiertos por un modelo, sin anotaciones humanas

Para responder una pregunta distinta se ajustó un modelo **NMF no supervisado** sobre TF-IDF de 57.452 oraciones de al menos 80 caracteres. Recibe solo texto: la lista de columnas humanas utilizadas está vacía y se registra así en `topicos_modelo_metodo.json`. Los IDs no llevan nombres sustantivos impuestos; `etiqueta_automatica_top5` concatena literalmente los cinco términos de mayor peso.

#### Selección de la segmentación y prueba K=6

Ya no se supone que 14 sea correcto por definición. `segmentacion_nmf_benchmark.csv` compara $K=6,8,10,12,14,16,18,20,22,24$ mediante error de reconstrucción, coherencia NPMI, diversidad de términos, redundancia coseno, estabilidad entre inicializaciones y concentración de prevalencia. También se contrastan oración, intervención y actor–reunión en `segmentacion_nmf_unidades.csv`.

K=6 obtiene la mayor coherencia NPMI (0,350) y estabilidad prácticamente perfecta, pero un solo componente concentra 46,1% de la masa temática. Sus seis componentes son: actividad/crecimiento; División Estudios/estructura; inflación mezclada con tipo de cambio; política monetaria genérica; Estados Unidos/internacional; y puntos base. Por tanto, solo unos tres son dominios económicos sustantivos comparables y los seis no funcionan como seis atributos FIFA. La prueba completa y el radar directo K=6 se preservan en `segmentacion_nmf_k6_topicos.csv` y `radar_nmf_k6_prueba*.csv`; no se oculta el resultado negativo.

K=14 mantiene estabilidad de 0,99999, diversidad top-10 de 0,979 y reduce la prevalencia máxima a 14,8%; además es el primer candidato que separa de manera simultánea actividad, trabajo, inflación, commodities, tipo de cambio y tasas. K=16 pierde estabilidad relativa (0,961) y K=18 reduce diversidad (0,956). La extensión confirma la fragmentación: K=20 baja a 0,930 de diversidad y 0,946 de estabilidad; K=22 a 0,918 y 0,926; K=24 recupera estabilidad, pero la diversidad cae a 0,913 y divide actividad/crecimiento, inflación/expectativas, horizontes de tasas y escenario externo en pares parcialmente solapados. El error de reconstrucción mejora mecánicamente —solo 1,1% de K=6 a K=14 y 2,0% hasta K=24—, por lo que no se utilizó solo.

La oración se conserva como unidad de ajuste. La intervención completa tiene menor diversidad (0,836) y produce más componentes de apertura, votación y cierre; actor–reunión eleva la redundancia temática a 0,234. La selección formal queda entonces en **K=14 sobre oraciones**, mediante criterio multicriterio y no porque coincida con el número deseado de ejes gráficos.

La auditoría de `auditoria_nombres_topicos_nmf.csv` contrasta los 20 términos principales con cinco intervenciones representativas por componente y registra nombre alternativo, tipo, confianza y límite. El resultado obliga a matizar la lectura inicial: hay ocho componentes económicos sustantivos, dos de decisión o medición mixta y cuatro institucionales, temporales o documentales. En particular, el tema 05 se renombra **“Decisión, mantención y acuerdo de TPM”**, no política monetaria general; el 07, **“Coyuntura reciente y comparación con el último IPoM”**; el 11 es una transición de presentaciones; y el 14 se corrige a **“Magnitudes en puntos base: TPM y diferenciales”**, porque sus ejemplos incluyen CDS y spreads además de cambios de tasa. Los nombres son glosas auditadas posteriores al modelo, no etiquetas aprendidas ni verdades ontológicas.

NMF permite mezclas: cada intervención conserva pesos para los 14 componentes, además del primero y segundo más fuertes y una medida de entropía. Por eso estos resultados deben describirse como **tópicos del modelo NMF**, no como tópicos de W+C+600: W+C+600 clasifica postura H/D/N y nunca fue entrenado para detectar temas.

### Diseño preservado para tarjetas tipo FIFA

`radar_tematico_actores.csv`, su versión ancha y `radar_tematico_metodo.json` dejan calculado y documentado un radar de seis ejes con nombres auditados: actividad/demanda/ciclo; mercado laboral/empleo; inflación/expectativas/meta; entorno externo/commodities/economías; tipo de cambio real/nominal; y tasas de interés/plazos. Se excluyen los componentes técnicos, institucionales, temporales y de presentación; también decisión/acuerdo de TPM por circularidad y magnitudes en puntos base porque mezcla cambios de TPM con spreads y CDS.

Para cada eje se suman sus pesos NMF, se promedian por actor, se renormalizan entre los seis ejes, se comparan con la proporción del corpus (índice base 100) y se convierten a percentil 0–100 entre miembros del Consejo con al menos 100 intervenciones. El archivo conserva el peso bruto, proporción, índice y percentil; este último sirve para dibujar la tarjeta, pero es grueso porque solo nueve actores cumplen el umbral. Un valor alto significa **mayor énfasis relativo**, nunca habilidad, calidad o influencia. Las palabras distintivas deben mostrarse como etiquetas complementarias, no como ejes variables del radar.

### Evolución temporal de los tópicos del modelo

Los mismos seis ejes se agregan en `evolucion_topicos_modelo_por_reunion.csv` y `evolucion_topicos_modelo_anual.csv`, de modo que las tarjetas y la serie temporal usen exactamente la misma definición. La tabla por reunión contiene las 132 actas × 6 ejes, proporción condicionada a esos ejes, índice contra el corpus, ranking, media móvil retrospectiva de 12 reuniones y cambio contra doce reuniones antes. `evolucion_topicos_modelo_resumen.csv` registra extremos y pendiente descriptiva; el método queda congelado en JSON.

La evolución anual muestra patrones plausibles, no monotónicos: actividad/demanda/ciclo alcanza su máximo en 2009 (24,7% de los seis ejes) después de su mínimo de 2008 (16,4%); entorno externo/commodities/economías culmina en 2011 (38,0%); inflación/expectativas/meta cae a un mínimo en 2013 (8,6%) y llega a su máximo en 2015 (13,9%); tipo de cambio real/nominal alcanza su máximo en 2010 (12,6%); y tasas de interés/plazos pierde participación desde 12,2% en 2005 a 7,8% en 2015. Mercado laboral/empleo resulta comparativamente estable. Son cambios en atención textual relativa, no medidas directas de importancia económica ni efectos causales.

La comparación de primera versus última intervención direccional pertinente produjo solo **39 pares actor-reunión** con al menos dos intervenciones antes de la decisión institucional. En conjunto, la distancia media al proxy final bajó de 0,564 a 0,541: convergencia media 0,0227, mediana 0,0513 y acercamiento en 61,5% de los pares. Solo José De Gregorio y Rodrigo Vergara alcanzaron 11 reuniones cada uno: De Gregorio tuvo convergencia media 0,100 y acercamiento en 9/11; Vergara, 0,0246 y 7/11. Los demás actores tienen cuatro reuniones o menos y **no deben rankearse**. La evidencia sugiere un acercamiento débil en esta muestra seleccionada, pero no permite concluir un patrón general.

La restricción es sustantiva: la decisión proxy es la última fila institucional `Consejo del Banco Central de Chile` clasificada en cada reunión (132/132; 107 N, 18 H y 7 D), no un voto observado. Para reemplazarla progresivamente se construyó `base_votos_acta_actor.csv`, con **649 pares reunión–consejero**: 516 acciones se extrajeron de formulaciones explícitas de voto, 87 se infirieron separadamente porque el acta declara unanimidad y 45 se resolvieron mediante revisión textual asistida documentada en `data/revision_votos_actores.csv`. Solo quedó un caso como `no_extraido`: Sebastián Claro en noviembre de 2009, porque su intervención discute la salida de la FLAP pero no formula inequívocamente su acción sobre la TPM. Los 132 acuerdos institucionales tienen acción y TPM objetivo: 80 mantenciones, 35 alzas y 17 bajas. Hay nueve votos cuya acción final difiere del acuerdo, candidatos naturales a disenso. Toda extracción conserva fragmento, texto, criterio y procedencia; `voto_accion` nunca mezcla inferencias, `voto_accion_con_inferencia` añade solo unanimidad y `voto_accion_final` incorpora además la revisión asistida. Ninguna revisión asistida debe presentarse como validación humana. Las tendencias anuales tampoco separan inclinación personal del ciclo macroeconómico o del cambio en composición temática; `variacion_anual_por_actor.csv` es descriptivo, no la estimación de $\alpha_i$ y $\beta_i$.

## Fórmulas y procedimiento de cálculo

### 1. Representación TF-IDF

Para un término o n-grama $t$ en una intervención $d$, el modelo usa frecuencia sublineal:

$$
\operatorname{tf}(t,d)=
\begin{cases}
1+\log(c_{t,d}), & c_{t,d}>0,\\
0, & c_{t,d}=0,
\end{cases}
$$

donde $c_{t,d}$ es el número de apariciones. El IDF suavizado de `scikit-learn` es:

$$
\operatorname{idf}(t)=\log\left(\frac{1+N}{1+\operatorname{df}(t)}\right)+1,
$$

con $N$ intervenciones de entrenamiento y $\operatorname{df}(t)$ intervenciones que contienen $t$. La característica previa a normalización es:

$$
\operatorname{tfidf}(t,d)=\operatorname{tf}(t,d)\operatorname{idf}(t).
$$

Cada vector se normaliza con norma L2, que es el valor predeterminado de `TfidfVectorizer`:

$$
\widehat{x}_d=\frac{x_d}{\lVert x_d\rVert_2}.
$$

El sistema combina dos bloques mediante `FeatureUnion`:

$$
x_d=[x_d^{\text{palabras}},\;w_c x_d^{\text{caracteres}}],
$$

con peso de palabras igual a 1 y pesos de caracteres $w_c=(1,0;\;0,5;\;1,0;\;1,0;\;1,0)$ para los cinco miembros.

Parámetros de los n-gramas:

| Etapa | Palabras | Caracteres | Filtros |
|---|---|---|---|
| A: relevancia | 1-gramas | `char_wb` 3–5 | palabras `min_df=3`, `max_df=0,9`; caracteres `min_df=3`, `max_df=0,98` |
| B: H/D/N | 1–4 gramas | `char_wb` 3–5 | mismos filtros; máximo 120.000 características de caracteres |

En ambas etapas se convierten los textos a minúsculas, se normalizan acentos Unicode y se utiliza frecuencia sublineal.

### 2. Regresión logística

Cada etapa emplea regresión logística con regularización L2, `C=2,0`, máximo 2.000 iteraciones y semilla 20260915. En términos generales se minimiza:

$$
\mathcal{L}(\beta)=-\sum_i w_{y_i}\log P(y_i\mid x_i)+\lambda\lVert\beta\rVert_2^2,
$$

con fuerza de regularización inversamente relacionada con $C$. `class_weight="balanced"` asigna a la clase $k$:

$$
w_k=\frac{n}{K n_k},
$$

con $n$ casos de entrenamiento, $K$ clases y $n_k$ casos de la clase $k$.

### 3. Arquitectura de dos etapas

- La etapa A predice relevancia monetaria $R\in\{0,1\}$.
- La etapa B predice H, D o N entre los casos relevantes del entrenamiento.
- En la clasificación dura, si A predice $R=0$, el resultado es N; si predice $R=1$, se utiliza la clase de B.

Para los puntajes continuos se combinan las probabilidades de cada miembro:

$$
P(H)=P(R=1)P_B(H),
$$

$$
P(D)=P(R=1)P_B(D),
$$

$$
P(N)=P(R=0)+P(R=1)P_B(N).
$$

Luego se promedian las probabilidades de los cinco miembros. El puntaje continuo es:

$$
s_i=\overline{P_i(H)}-\overline{P_i(D)}\in[-1,1].
$$

Estos valores se guardan como **no calibrados**. La etiqueta final dura es el voto mayoritario de los cinco miembros, con desempate fijo H, D, N. No se obtiene tomando necesariamente el máximo de las probabilidades promedio.

### 4. Entrenamiento, agrupación y purga

El entrenamiento final contiene 1.596 intervenciones únicas. Cada uno de los cinco miembros recibe las filas indicadas en la columna `miembros`, con tamaños 1.494, 1.450, 1.453, 1.473 y 1.466. La evaluación se agrupó por `meeting_id` para impedir que una reunión apareciera a ambos lados del ajuste. También se eliminaron coincidencias de texto normalizado.

Las 33 reuniones de la evaluación ciega fueron excluidas completamente del ajuste prospectivo. De 300 decisiones humanas cerradas, una quedó como `no_puedo_decidir`; las métricas se calcularon sobre 299.

### 5. Métricas de clasificación

Para cada clase $k$:

$$
\operatorname{Precision}_k=\frac{VP_k}{VP_k+FP_k},\qquad
\operatorname{Recall}_k=\frac{VP_k}{VP_k+FN_k},
$$

$$
F1_k=\frac{2\,\operatorname{Precision}_k\operatorname{Recall}_k}{\operatorname{Precision}_k+\operatorname{Recall}_k}.
$$

Las métricas agregadas son:

$$
\operatorname{Accuracy}=\frac{\text{aciertos}}{n},
$$

$$
\operatorname{MacroF1}=\frac{F1_H+F1_D+F1_N}{3},
$$

$$
F1_{HD}=\frac{F1_H+F1_D}{2}.
$$

También se cuentan directamente desde la matriz de confusión ordenada H, D, N:

- inversiones: $H\rightarrow D+D\rightarrow H$;
- omisiones: $H\rightarrow N+D\rightarrow N$;
- falsas direcciones: $N\rightarrow H+N\rightarrow D$;
- errores: todos los casos fuera de la diagonal.

### 6. Incertidumbre agrupada

Las diferencias entre modelos se evaluaron mediante 10.000 remuestras bootstrap con semilla 20260917. En cada remuestra se seleccionaron con reemplazo las 33 reuniones completas, no filas individuales. Para cada métrica se calcularon percentiles 2,5, 50 y 97,5, además de la proporción de remuestras donde la diferencia fue positiva.

### 7. Etiqueta utilizada para el análisis del corpus

La tabla maestra utiliza la mejor evidencia disponible, en este orden:

1. etiqueta validada de las 1.596 filas de entrenamiento;
2. gold de las 299 filas ciegas decidibles;
3. predicción W+C+600 para 7.829 filas restantes;
4. separación explícita del único caso no decidible.

La columna `procedencia_etiqueta` permite distinguir observaciones etiquetadas y predichas.

### 8. Agregación por documento, año, tópico y actor

Sea un grupo con conteos H, D y N y total $T=H+D+N$. Se calculan:

$$
\text{tono neto general}=\frac{H-D}{T},
$$

$$
\text{balance direccional}=\frac{H-D}{H+D},
$$

$$
\text{cobertura direccional}=\frac{H+D}{T}.
$$

Además se reportan $H/T$, $D/T$, $N/T$ y la media del puntaje continuo $s_i$. Si $H+D=0$, el balance direccional queda vacío. Así se conservan dos vistas: la composición completa H/D/N y la orientación condicionada a los casos H/D.

### 9. Palabras y n-gramas descriptivos

El análisis léxico usa `CountVectorizer`, minúsculas, normalización de acentos, n-gramas de una a cuatro palabras y `min_df=5`. Para la tabla global se exige además presencia en al menos tres reuniones. Se registran:

- ocurrencias totales;
- número de intervenciones que contienen la expresión;
- número de reuniones que la contienen;
- una tabla cruda y otra de contenido que filtra palabras funcionales y fórmulas institucionales.

Los términos distintivos se estiman mediante log-odds con prior informativo. Para término $j$, grupos A y B y conteos $c_{Aj},c_{Bj}$:

$$
\alpha_j=1000\frac{c_{Aj}+c_{Bj}+1}{\sum_l(c_{Al}+c_{Bl})+V},
$$

$$
\delta_j=\log\frac{c_{Aj}+\alpha_j}{n_A+\alpha_0-c_{Aj}-\alpha_j}
-\log\frac{c_{Bj}+\alpha_j}{n_B+\alpha_0-c_{Bj}-\alpha_j},
$$

$$
z_j=\frac{\delta_j}{\sqrt{1/(c_{Aj}+\alpha_j)+1/(c_{Bj}+\alpha_j)}}.
$$

Se producen dos contrastes: H frente a D y direccional H/D frente a N. Los resultados son asociaciones descriptivas, no reglas causales de etiquetado.

### 10. Tópicos humanos, tópicos del modelo y embeddings

`topico_humano` y `keywords_humano` son anotaciones históricas preservadas en el corpus. Los archivos `indices_por_topico.csv`, `indices_por_keywords.csv`, `mix_topicos_por_anio.csv` y `topicos_por_actor.csv` se calculan directamente desde esas columnas y, por tanto, **no son temas descubiertos por W+C+600**.

El análisis independiente NMF forma una matriz TF-IDF de oraciones con n-gramas de una y dos palabras, `min_df=12`, `max_df=0,5` y máximo 20.000 características. Tras el benchmark de diez valores de $K$ y tres unidades textuales, se seleccionan 14 componentes sobre oraciones. Con inicialización `nndsvda` y semilla 20260918, factoriza aproximadamente:

$$
X\approx WH,\qquad W\ge 0,\quad H\ge 0,
$$

donde cada fila de $W$ contiene los pesos temáticos y cada fila de $H$ los pesos de términos de un componente. Los pesos por intervención se normalizan para sumar uno; el tópico dominante es el de mayor peso. Este ajuste usa texto, no las columnas humanas, y es exploratorio: el número de componentes y el preprocesamiento siguen siendo decisiones metodológicas, y los términos requieren interpretación posterior.

No se generaron embeddings densos. NMF usa la matriz TF-IDF dispersa y no forma parte del clasificador formal W+C+600.

## Datos preparados para el scrollytelling

`datos_web/` es la interfaz estable entre este repositorio analítico y la página. Se genera exclusivamente con `scripts/preparar_datos_web.py`: no se deben copiar resultados a mano ni editar sus JSON. Contiene resumen, metodología y advertencias, series generales, tópicos auditados, cruce tópico–H/D/N, estructura por quintil documental, perfiles de actores, 132 fichas de reuniones y las 9.725 intervenciones divididas en once archivos anuales para carga diferida.

El explorador puede filtrar por reunión, actor, tipo de actor, relevancia, orientación, procedencia humana/modelo y tópico. Cada intervención mantiene probabilidades no calibradas, acuerdo del ensamble, tópico principal/secundario y los 14 pesos NMF. Las etiquetas humanas históricas viven en un objeto separado y explícito. `datos_web/README.md` documenta qué debe cargar primero el frontend; `datos_web/manifest.json` registra tamaño y SHA-256 de cada archivo.

La estructura por quintiles describe la posición dentro del acta publicada, no duración ni tiempo de palabra. Las actas deben presentarse como **secuencias de intervenciones reconstruidas desde el registro institucional**, nunca como transcripciones estenográficas. El paquete tampoco autoriza inferencias de habilidad, personalidad permanente, persuasión, influencia o causalidad.

## Robustez supervisada y comparación de arquitecturas (2026-09)

Análisis agregados tras la condensación, en `resultados/robustez_supervisada/`, sin tocar la selección de modelos ni reabrir la ciega.

**Δ pareado en la ciega** (`scripts/bootstrap_ciega_pareado.py`; Δ = W+C+600 − C+89, bootstrap de reuniones completas, 10.000 remuestras, semilla 20260917). Gold: 234 N / 44 H / 21 D; solo 12/33 reuniones contienen dovish, lo que limita toda métrica por clase de D:

| Δ | punto | IC95 % | P(Δ>0) |
|---|---:|---|---:|
| macro-F1 | +0,116 | [0,054; 0,195] | 1,000 |
| F1-HD | +0,149 | [0,062; 0,262] | 1,000 |
| F1-D | +0,234 | [0,084; 0,437] | 0,998 |
| recall-D | +0,190 | [0,000; 0,471] | 0,939 |

La mejora interna es significativa en conjunto; **no** en recall-D. Una diferencia de ~5 puntos de F1 entre dos modelos cabe entera dentro del ruido de este diseño: todo claim futuro se escribe contra estos intervalos, no contra medias sueltas.

**Estabilidad del lineal** (`scripts/estabilidad_lineal.py`): la arquitectura W+C de un miembro bajo GroupKFold(5) da macro-F1 0,761±0,053 y bajo GroupShuffleSplit×10 0,744±0,054; el F1-D oscila entre 0,31 y 0,87 siguiendo el soporte de D del test (6–35 filas). `lbfgs` es determinista: esta es la varianza por muestreo que un encoder debe superar antes de comparar medias.

**Curvas de aprendizaje** (`scripts/curvas_aprendizaje.py`; evaluación fija de 24 reuniones/330 filas/23 D, muestreo de reuniones completas estratificado por presencia de D, 15 repeticiones):

| N entrenamiento | macro-F1 | F1-D | recall-D |
|---:|---|---|---|
| ≈233 | 0,576±0,045 | 0,212 | 0,255 |
| ≈433 | 0,642±0,044 | 0,351 | 0,490 |
| ≈815 | 0,670±0,020 | 0,395 | 0,565 |
| ≈1222 | 0,690±0,009 | 0,426 | 0,586 |

Retornos marginales decrecientes tras ~400–800 etiquetas: con ≈433 el macro-F1 ya alcanza ~93 % del valor de ≈1222. Este es el insumo del argumento de costo de anotación.

**Piloto encoder:** `scripts/piloto_encoder_dev.py` ejecuta en GPU la comparación pareada BETO vs. lineal en el mismo split agrupado, 5 semillas, tuning simétrico opcional (`--grid`) y bootstrap pareado por semilla. La evaluación ciega permanece cerrada: extenderla requiere decisión documentada. Requiere `torch` y `transformers` (no incluidos en `requirements.txt`); este entorno no tiene acceso a HuggingFace.

## Lectura recomendada

1. [`docs/METODOLOGIA_MODELO.md`](docs/METODOLOGIA_MODELO.md)
2. [`docs/RESULTADOS_Y_ROBUSTEZ.md`](docs/RESULTADOS_Y_ROBUSTEZ.md)
3. [`docs/BENCHMARK_MODELOS.md`](docs/BENCHMARK_MODELOS.md)
4. [`docs/CODEBOOK_ETIQUETADO.md`](docs/CODEBOOK_ETIQUETADO.md)
5. [`docs/OBJETIVOS_ANALISIS.md`](docs/OBJETIVOS_ANALISIS.md)

## Límites

La evaluación ciega es una muestra enriquecida como desafío y no estima prevalencia natural. Sus reuniones fueron excluidas del ajuste prospectivo, pero habían aparecido durante el desarrollo histórico. Una anotación no decidible fue excluida, dejando 299 casos evaluables. No se debe reutilizar este conjunto para seleccionar nuevas variantes.

El historial Git conserva todas las auditorías, experimentos y scripts eliminados durante la condensación. El último estado previo a ella es el commit `7aa63cc`.
