# Objetivos analíticos después de la clasificación

Este documento recupera y simplifica los entregables definidos en el plan histórico del proyecto. El modelo H/D/N ya fue seleccionado y aplicado; lo siguiente es convertir sus resultados en indicadores económicos y descriptivos.

## 1. Índice por documento o reunión

Unidad: `meeting_id`. Con H, D y N contados por intervención:

- `tono_neto_general = (H-D)/(H+D+N)` — indicador principal;
- `balance_direccional = (H-D)/(H+D)` — orientación condicional; queda vacío si H+D=0;
- `cobertura_direccional = (H+D)/(H+D+N)` — intensidad de contenido direccional;
- conteos y proporciones H, D y N.

No se eliminarán los neutrales sin reportar cobertura. La serie mensual 2005–2015 debe contrastarse descriptivamente con la decisión y variación de TPM cuando esa capa esté disponible.

## 2. Tópicos y keywords

El corpus contiene 13 tópicos humanos originales y una columna histórica de keywords categorizada. Se preservan como `topico_humano` y `keywords_humano`; no son predicciones del modelo de postura.

Entregables:

- frecuencia y participación de tópicos por año y reunión;
- cruce tópico × H/D/N;
- tópicos con mayor balance y cobertura direccional;
- evolución temporal del mix de tópicos;
- comparación futura `topico_humano` frente a `topico_maquina`, si se construye un modelo temático separado;
- comparación equivalente de keywords humanas y extraídas automáticamente.

Los tópicos humanos son: acuerdo/comunicado, debate, escenario internacional, mercados financieros, inflación, actividad interna, mercado laboral, decisión TPM, opciones TPM, riesgos, política fiscal, apertura/cierre y otros.

## 3. Palabras y expresiones

No basta contar palabras funcionales. Se producirán:

- palabras y n-gramas 1–4 más frecuentes, con frecuencia por intervención y por reunión;
- términos distintivos de H, D y N mediante log-odds con prior, no solo frecuencia bruta;
- vocabulario distintivo por actor;
- palabras distintivas por período y cambios semánticos temporales;
- contextos de ejemplo para evitar interpretar asociaciones como reglas causales.

Los términos TF-IDF o log-odds son asociaciones descriptivas. Una palabra aislada no debe convertirse en etiqueta monetaria automática.

## 4. Actores

- número de intervenciones y mezcla de tópicos por actor;
- conteos, cobertura y balance H/D por actor;
- evolución temporal del tono por actor;
- vocabulario distintivo por actor;
- comparación con el tono agregado de su reunión;
- análisis de convergencia entre primeras y últimas intervenciones solo cuando el orden y la decisión final sean identificables.

## 5. Procedencia de etiquetas

Para análisis descriptivo se utilizará la mejor evidencia disponible:

1. etiqueta validada para las 1.596 filas de entrenamiento;
2. gold humano para las 299 filas ciegas decidibles;
3. predicción W+C+600 para las 7.829 restantes;
4. una columna obligatoria de procedencia para no confundir etiqueta observada y predicha.

La fila ciega no decidible permanece separada. Las predicciones in-sample no deben presentarse como validación del modelo.

## 6. Estado de ejecución

Completado en `resultados/analisis_descriptivo/`:

1. tabla maestra con etiqueta y procedencia;
2. agregados por reunión y año, con y sin neutrales;
3. tablas de tópicos y keywords;
4. n-gramas 1–4 frecuentes y distintivos H/D y direccional/neutral;
5. perfiles descriptivos de actores;
6. probabilidades no calibradas y score continuo H−D;
7. cinco modelos ajustados persistidos en `modelos/wc600/`.

Pendiente solo si surge una hipótesis nueva: incorporar TPM para validación económica y generar embeddings para análisis temático. No se generaron embeddings ahora porque no forman parte del modelo final y los 13 tópicos humanos permiten comenzar sin otra representación.
