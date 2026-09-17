# FASE_2 — postura monetaria H/D/N

Clasificación **hawkish / dovish / neutral por intervención** en actas del Banco Central de Chile (2005–2015).

## Empezar por aquí

**Trabajo actual del agente:** migración auditada al [codebook v3](docs/codebook_v3.md), aprobado el 17-09-2026. Universo: 19 rondas IA/1.352 IDs, 89 IA nuevas y 306 humanas; 1.747 IDs distintos. Las [dos rondas prioritarias](docs/REVISION_RONDAS_PRIORITARIAS_V3.md) están cerradas: 77/77 revisadas, 11 cambios de etiqueta y uno de relevancia frente a v2 vigente. Quedan 1.670 IDs. V2 y sus métricas se preservan; no se reentrena hasta consolidar v3.

- **[Llevar a otro PC y ejecutar](EMPEZAR_AQUI.md)**: descarga, instalación, datos y comandos, sin tener que leer todo el historial.
- **[Continuidad para otra sesión](docs/CONTINUIDAD.md)**: estado exacto, decisiones ya tomadas y siguiente tarea.
- **[Carpeta de código](scripts/README.md)** · **[Mapa de datos](data/README.md)** · **[Índice de documentación](docs/README.md)**.

## Criterios importantes para clasificar: postura y relevancia

**Aprobados por el investigador el 17-09-2026 como [`codebook v3`](docs/codebook_v3.md).** Rigen nuevas anotaciones y la revisión de consistencia. El codebook v2 queda congelado como referencia histórica para reproducir datos y métricas anteriores.

- **Qué medimos:** orientación monetaria para Chile respaldada por el actor o el Consejo en la unidad completa. No mero sentimiento económico, presencia de “TPM”, nivel de una tasa ni ranking entre consejeros. En el plan B se incluyen los nombres históricos del instrumento cuando su función monetaria esté identificada.
- **H:** respalda endurecer, subir la tasa, retirar estímulo o un sesgo al alza. **D:** respalda relajar, bajar la tasa, ampliar estímulo o un sesgo a la baja. Una oposición a más relajamiento/retirada de estímulo exige justificación sustantiva; no se invierte el signo mecánicamente por discrepar.
- **N relevante existe:** análisis monetario, opciones sin preferencia, preguntas sin respuesta, relato sin nueva adhesión y mantención sin orientación identificable pueden ser `neutral` y **`es_relevante=1`**. La ausencia de voto no los hace irrelevantes.
- **Irrelevante no equivale a neutral:** `es_relevante=0` se reserva para unidades realmente ajenas al objetivo o puramente administrativas, no para todo texto sin dirección. Un N relevante debe seguir disponible para que B aprenda esa distinción.
- **La dirección actual explícita prima:** bajar 50 frente a 70 pb sigue siendo D; subir 25 frente a 50 sigue siendo H. Mantener se interpreta con su contexto/sesgo; no es automáticamente N ni una postura relativa frente a otra propuesta.
- **Historia, expectativas ajenas y mención no equivalen a adhesión.** Identificar quién respalda qué y cuándo. Si falta información esencial o se mezclan asuntos, registrar la limitación y apartar el caso del entrenamiento hasta resolverla; no asignar N de alta confianza para llenar el campo.
- **Texto y evidencia:** conservar el original, leer la unidad completa y usar cita literal de hasta 300 caracteres. No sustituirlo por correcciones de IA sin cotejo ni completar dirección con otras intervenciones. Agrupar por acta/reunión para evitar contaminación entre train y validación.

Detalle vigente: [codebook v3](docs/codebook_v3.md). Sus antecedentes son el [criterio acotado para el plan B](docs/CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md) y la [propuesta conceptual general](docs/DEFINICION_POSTURA_MONETARIA_PROPUESTA_V1.md).

**Migración en curso.** La [auditoría inicial](docs/AUDITORIA_COMPATIBILIDAD_CRITERIOS_V1.md) confirmó convenciones relativas al menú/fase. El [cierre completo de las 77 filas prioritarias](docs/REVISION_RONDAS_PRIORITARIAS_V3.md) registra 65 compatibles, 11 cambios de etiqueta y uno de relevancia frente a v2 vigente, incluidos los falsos N. El investigador autorizó revisar también las 306 respuestas humanas; desde esa decisión dejan de ser un test ciego para v3, aunque su versión v2 se conserva intacta. Toda corrección se registra por ID en una capa nueva. El efecto de recodificar referencias se separará del efecto de reentrenar.

## Estado real

| Componente | Estado |
|---|---|
| Corpus y datos de trabajo | Incluidos: 9.725 intervenciones; desarrollo de 1.352 textos. |
| Referencias | V2 histórica fijada y preservada. V3 aprobada; revisión de 1.747 IDs en curso, todavía sin referencia consolidada ni reentrenamiento. |
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

Revisión y migración v3 en curso en el [PR #5](https://github.com/joako0o/FASE_2/pull/5).
