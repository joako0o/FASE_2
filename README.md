# FASE_2 — postura monetaria H/D/N

Clasificación **hawkish / dovish / neutral por intervención** en actas del Banco Central de Chile (2005–2015).

## Empezar por aquí

**Trabajo actual del agente:** [revisar compatibilidad entre criterios y etiquetas](docs/AUDITORIA_COMPATIBILIDAD_CRITERIOS_V1.md), sin reclasificar automáticamente. La meta300H/300D y las89anotaciones IA nuevas permanecen registradas (base+altos H154/D119). El ensayo TF-IDF con59aumentos no mejoró y el control no se reemplazó. El investigador no necesita volver a completar un Excel para esta auditoría.

- **[Llevar a otro PC y ejecutar](EMPEZAR_AQUI.md)**: descarga, instalación, datos y comandos, sin tener que leer todo el historial.
- **[Continuidad para otra sesión](docs/CONTINUIDAD.md)**: estado exacto, decisiones ya tomadas y siguiente tarea.
- **[Carpeta de código](scripts/README.md)** · **[Mapa de datos](data/README.md)** · **[Índice de documentación](docs/README.md)**.

## Criterios importantes para clasificar: postura y relevancia

**Registrados por indicación del investigador el 17-09-2026.** Son la referencia documental para calibrar y auditar consistencia; **no implican reclasificar automáticamente los datos ni sustituir el codebook v2 congelado**.

- **Qué medimos:** orientación monetaria para Chile respaldada por el actor o el Consejo en la unidad completa. No mero sentimiento económico, presencia de “TPM”, nivel de una tasa ni ranking entre consejeros. En el plan B se incluyen los nombres históricos del instrumento cuando su función monetaria esté identificada.
- **H:** respalda endurecer, subir la tasa, retirar estímulo o un sesgo al alza. **D:** respalda relajar, bajar la tasa, ampliar estímulo o un sesgo a la baja. Una oposición a más relajamiento/retirada de estímulo exige justificación sustantiva; no se invierte el signo mecánicamente por discrepar.
- **N relevante existe:** análisis monetario, opciones sin preferencia, preguntas sin respuesta, relato sin nueva adhesión y mantención sin orientación identificable pueden ser `neutral` y **`es_relevante=1`**. La ausencia de voto no los hace irrelevantes.
- **Irrelevante no equivale a neutral:** `es_relevante=0` se reserva para unidades realmente ajenas al objetivo o puramente administrativas, no para todo texto sin dirección. Un N relevante debe seguir disponible para que B aprenda esa distinción.
- **La dirección actual explícita prima:** bajar 50 frente a 70 pb sigue siendo D; subir 25 frente a 50 sigue siendo H. Mantener se interpreta con su contexto/sesgo; no es automáticamente N ni una postura relativa frente a otra propuesta.
- **Historia, expectativas ajenas y mención no equivalen a adhesión.** Identificar quién respalda qué y cuándo. Si falta información esencial o se mezclan asuntos, registrar la limitación y apartar el caso del entrenamiento hasta resolverla; no asignar N de alta confianza para llenar el campo.
- **Texto y evidencia:** conservar el original, leer la unidad completa y usar cita literal de hasta 300 caracteres. No sustituirlo por correcciones de IA sin cotejo ni completar dirección con otras intervenciones. Agrupar por acta/reunión para evitar contaminación entre train y validación.

Detalle: [criterio acotado para el plan B](docs/CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md) y [fundamentos y decisiones aún por acordar](docs/DEFINICION_POSTURA_MONETARIA_PROPUESTA_V1.md).

**¿Reclasificar lo anterior?** La [auditoría inicial de compatibilidad](docs/AUDITORIA_COMPATIBILIDAD_CRITERIOS_V1.md) confirmó convenciones relativas al menú/fase en parte del entrenamiento IA, no invalidez de toda la colección. La separación N/relevancia ya existía: 878 N relevantes y 269 irrelevantes en los originales. Priorizar las 77 filas de las dos rondas con convenciones documentadas, extender a familias similares en otras rondas y revisar también la ampliación de 89 con el criterio que se acuerde; incluir controles, no solo errores del modelo. No se conoce aún el total de cambios y las 306 respuestas humanas no se reevaluaron. Las reglas nuevas de alcance/pendientes que difieran de v2 requieren una versión explícita. Conservar originales, decisiones humanas aceptadas y resultados; registrar por ID cualquier cambio propuesto. No abrir las antiguas 306 respuestas. Si se aprueba otra referencia, separar el efecto de cambiar etiquetas de evaluación del efecto de volver a entrenar. **Se hizo una auditoría inicial estructural y de 12 textos; no una reclasificación o migración.**

## Estado real

| Componente | Estado |
|---|---|
| Corpus y datos de trabajo | Incluidos: 9.725 intervenciones; desarrollo de 1.352 textos. |
| Referencias | V2 fijada: seis adjudicaciones anteriores + trece correcciones aceptadas. Originales preservados. |
| Control TF-IDF | Ejecutado: F1 H/D medio **0,747060**, 51 errores en 793 validaciones corregidas. |
| Diagnóstico H/D | Diez inversiones examinadas y cinco ambiguas tratadas aparte. |
| BETO v1 recibido | Cinco folds externos: F1 H/D medio **0,625043**, 66 errores, 25 inversiones. **No mejora; no adoptado.** [Auditoría y resultados](docs/RESULTADOS_BETO_V1.md). |
| Tipo de evaluación | Desarrollo reutilizado y asistido; no test independiente ni evidencia de generalización. |

No se reemplazó el modelo histórico ni se puntuó todo el corpus. No hacen falta nuevas anotaciones para el siguiente paso.

## Un punto de entrada

Desde la raíz, con Python 3.11 recomendado:

```bash
python scripts/40_gestionar_proyecto.py instalar
python scripts/40_gestionar_proyecto.py preparar
python scripts/40_gestionar_proyecto.py probar --regresion
python scripts/40_gestionar_proyecto.py comprobar
```

Estos comandos preparan/verifican: **no entrenan BETO**. Para GPU, exportación y recuperación, seguir [EMPEZAR_AQUI.md](EMPEZAR_AQUI.md). No ejecutar todos los scripts numerados ni la suite histórica completa: algunas etapas abren referencias humanas o intentan generar salidas ya congeladas.

## Organización

```text
FASE_2/
├── EMPEZAR_AQUI.md             Instrucciones para el investigador
├── AGENTS.md                  Reglas de continuidad para agentes
├── scripts/                   Código; entrada 40_gestionar_proyecto.py
├── data/                      Fuentes procesadas, referencias y evidencia
├── notebooks/                 Alternativa Colab GPU
├── docs/                      Continuidad, metodología e informes
├── tests/                     Pruebas; ejecutar mediante el gestor
├── entrega/                   Inventario explícito del ZIP
├── requirements*.txt          Dependencias fijadas
├── PLAN.md                    Plan y decisiones históricas detalladas
└── *.xlsx                     Fuentes/devoluciones originales conservadas
```

Se mantienen rutas históricas para no romper los manifiestos. `.venv/`, `modelos/`, `data/checkpoints/` y `entregas/` son locales/ignorados. El ZIP portable incluye explícitamente la entrada y los resultados previstos, **no pesos ni dependencias instaladas**.

PR de esta entrega: [#4](https://github.com/joako0o/FASE_2/pull/4). No es necesario cerrarlo para descargar. Para integrar a `main`, distinguir **Merge** de simplemente **Close**.
