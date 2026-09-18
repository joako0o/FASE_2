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
- comparación futura entre tópicos humanos y componentes NMF solo como validación externa, sin usar las columnas humanas para ajustar NMF;
- comparación equivalente de keywords humanas y extraídas automáticamente.

Los tópicos humanos son: acuerdo/comunicado, debate, escenario internacional, mercados financieros, inflación, actividad interna, mercado laboral, decisión TPM, opciones TPM, riesgos, política fiscal, apertura/cierre y otros. Separadamente, ya existe un modelo no supervisado NMF de 14 componentes ajustado solo con texto. Sus archivos usan el prefijo `topicos_modelo_`; nunca deben atribuirse a W+C+600.

Para visualización tipo FIFA se definieron seis ejes económicos comunes a todos los actores: actividad/demanda, mercado laboral, inflación/expectativas, entorno externo/commodities, tipo de cambio y mercados/estructura de tasas. Se excluyeron política monetaria genérica y puntos base porque todos participan en una RPM y esos ejes serían circulares; también se excluyó estructura documental. El percentil 0–100 se calcula únicamente entre miembros del Consejo con al menos 100 intervenciones y representa énfasis relativo, no habilidad.

La evolución temporal reutiliza exactamente esos seis ejes. Se entrega por las 132 reuniones, por año y como resumen de extremos/tendencia. La serie principal es la proporción de atención condicionada a los seis ejes; la vista suavizada es una media móvil retrospectiva de 12 reuniones. Esto evita cambiar la definición entre la tarjeta de actor y el gráfico temporal.

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
7. cinco modelos ajustados persistidos en `modelos/wc600/`;
8. modelo temático NMF de 14 componentes, asignaciones por intervención y agregados por reunión, año y actor;
9. insumos largo y ancho para radar temático tipo FIFA, con especificación reproducible;
10. evolución de los seis ejes temáticos por reunión y año, media móvil y resumen de extremos.

Pendiente solo si surge una hipótesis nueva: validación económica adicional o embeddings densos. NMF ya cubre el análisis temático automático mediante una matriz TF-IDF dispersa y no altera el modelo formal W+C+600.
