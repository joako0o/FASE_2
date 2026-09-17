# FASE_2 — postura monetaria H/D/N

Clasificación **hawkish / dovish / neutral por intervención** en actas del Banco Central de Chile (2005–2015).

## Empezar por aquí

**Trabajo actual del agente:** [anotar ejemplos nuevos para entrenamiento](docs/ANOTACION_IA_AMPLIACION_HD_V1.md). Meta 300 H/300 D: 89 candidatos revisados por IA; base más nuevos altos utilizables H154/D119. El ensayo TF-IDF con 59 aumentos ya se ejecutó y **no mejoró**: [resultados](docs/RESULTADOS_AMPLIACION_TFIDF_59_V1.md). No se reemplazó el control. El investigador **no necesita completar el Excel** para que continúe este trabajo.

- **[Llevar a otro PC y ejecutar](EMPEZAR_AQUI.md)**: descarga, instalación, datos y comandos, sin tener que leer todo el historial.
- **[Continuidad para otra sesión](docs/CONTINUIDAD.md)**: estado exacto, decisiones ya tomadas y siguiente tarea.
- **[Carpeta de código](scripts/README.md)** · **[Mapa de datos](data/README.md)** · **[Índice de documentación](docs/README.md)**.

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
