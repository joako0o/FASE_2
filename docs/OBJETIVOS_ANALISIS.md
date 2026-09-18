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

La segmentación fue revisada con $K=6,8,10,12,14,16,18,20,22,24$, dos reinicializaciones adicionales y tres unidades —oración, intervención y actor–reunión—. K=6 se conserva como prueba y como radar alternativo, pero mezcla dominios económicos con estructura institucional y concentra 46,1% en un solo componente. K=20–24 fragmenta dominios ya interpretables y reduce la diversidad de términos. Se retiene K=14 sobre oraciones por estabilidad, diversidad, menor concentración y capacidad de separar los seis dominios económicos. El radar principal agrupa seis ejes desde K=14; no equivale a afirmar que NMF descubrió exactamente seis habilidades.

Los nombres de los 14 componentes se auditan con 20 términos y cinco intervenciones representativas. La auditoría debe conservar nombre alternativo, tipo, confianza y límite. Corrige especialmente los componentes de decisión/acuerdo de TPM, actualización temporal, transición de presentaciones y magnitudes en puntos base, evitando convertirlos en dominios económicos puros.

Para visualización tipo FIFA se definieron seis ejes auditados comunes a todos los actores: actividad/demanda/ciclo, mercado laboral/empleo, inflación/expectativas/meta, entorno externo/commodities/economías, tipo de cambio real/nominal y tasas de interés/plazos. Se excluyeron decisión/acuerdo de TPM por circularidad; magnitudes en puntos base porque mezcla TPM, spreads y CDS; y los componentes de estructura documental. El percentil 0–100 se calcula únicamente entre miembros del Consejo con al menos 100 intervenciones y representa énfasis relativo, no habilidad.

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
10. evolución de los seis ejes temáticos por reunión y año, media móvil y resumen de extremos;
11. benchmark de segmentación K=6–24, sensibilidad a unidad textual y radar alternativo K=6;
12. auditoría de nombres con términos, textos representativos, confianza, alternativa y límite;
13. predicción explícita de relevancia con probabilidad y acuerdo del ensamble, separada de H/D/N;
14. paquete `datos_web/` con tópicos × postura, quintiles documentales, actores, reuniones y 9.725 intervenciones divididas por año para el scrollytelling.

El paquete web es una capa de publicación derivada: se regenera con `scripts/preparar_datos_web.py --sobrescribir` y no se edita manualmente. Sus secuencias describen el acta institucional, no una transcripción literal; la dispersión y las transiciones son textuales, no pruebas de persuasión o causalidad.

Pendiente solo si surge una hipótesis nueva: validación económica adicional o embeddings densos. NMF ya cubre el análisis temático automático mediante una matriz TF-IDF dispersa y no altera el modelo formal W+C+600.
