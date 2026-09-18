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
├── README.md
├── requirements.txt
├── data/
│   ├── corpus_bcch_2005_2015.csv       Corpus que se quiere clasificar
│   ├── entrenamiento_wc600.csv         Entrenamiento final, ya purgado
│   ├── evaluacion_ciega_gold.csv       Referencia humana final
│   ├── predicciones_evaluacion_ciega.csv
│   ├── resultados_evaluacion_ciega.json
│   ├── analisis_factorial.json
│   └── benchmark_modelos.{csv,json}
├── modelos/wc600/                    Cinco miembros persistidos y manifiesto
├── resultados/
│   ├── clasificacion_wc600_9725.csv
│   └── analisis_descriptivo/         Índices, tópicos, actores y léxico
├── docs/
│   ├── CODEBOOK_ETIQUETADO.md
│   ├── METODOLOGIA_MODELO.md
│   ├── RESULTADOS_Y_ROBUSTEZ.md
│   ├── BENCHMARK_MODELOS.md
│   └── PROTOCOLO_*.md
├── scripts/
│   ├── modelo_final.py
│   └── analisis_resultados.py
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
```

Los modelos ajustados están guardados en `modelos/wc600/`; no es necesario reentrenarlos para una nueva predicción. Los agregados con y sin neutrales, tópicos, actores y léxico están en `resultados/analisis_descriptivo/`.

En Windows, usar `.venv\Scripts\python.exe`. El comando de predicción entrena los cinco miembros con parámetros congelados y crea un CSV nuevo; nunca sobrescribe una salida existente.

## Clasificación completa disponible

El modelo ya fue ejecutado sobre las 9.725 intervenciones. El resultado está en `resultados/clasificacion_wc600_9725.csv`, con las cinco predicciones individuales, el voto final, el rol de cada fila y una señal de acuerdo entre miembros. `resultados/resumen_clasificacion.json` contiene distribuciones y conteos por año.

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

### 10. Tópicos, keywords y embeddings

Los agregados de tópicos y keywords utilizan las 13 categorías humanas preservadas en el corpus. No se generaron embeddings densos porque no forman parte de W+C+600 ni son necesarios para estas tablas. Solo deberían generarse bajo una hipótesis temática separada, indicando encoder, revisión, pooling, dimensión, orden de IDs y hashes.

## Lectura recomendada

1. [`docs/METODOLOGIA_MODELO.md`](docs/METODOLOGIA_MODELO.md)
2. [`docs/RESULTADOS_Y_ROBUSTEZ.md`](docs/RESULTADOS_Y_ROBUSTEZ.md)
3. [`docs/BENCHMARK_MODELOS.md`](docs/BENCHMARK_MODELOS.md)
4. [`docs/CODEBOOK_ETIQUETADO.md`](docs/CODEBOOK_ETIQUETADO.md)
5. [`docs/OBJETIVOS_ANALISIS.md`](docs/OBJETIVOS_ANALISIS.md)

## Límites

La evaluación ciega es una muestra enriquecida como desafío y no estima prevalencia natural. Sus reuniones fueron excluidas del ajuste prospectivo, pero habían aparecido durante el desarrollo histórico. Una anotación no decidible fue excluida, dejando 299 casos evaluables. No se debe reutilizar este conjunto para seleccionar nuevas variantes.

El historial Git conserva todas las auditorías, experimentos y scripts eliminados durante la condensación. El último estado previo a ella es el commit `7aa63cc`.
