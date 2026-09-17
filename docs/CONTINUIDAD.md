# Continuidad: tomar el trabajo desde otra sesión

## 1. Estado que debes asumir — y comprobar

**Actualización más reciente:** el investigador subió seis respaldos BETO a GitHub. El último contiene cinco folds y comparación; se verificó la cadena acumulativa, los hashes y la evaluación de 793 IDs contra v2/folds/A. **BETO no mejora y no se adopta:** F1 H/D medio 0,625043 frente a 0,747060; errores 66 frente a 51; H↔D 25 frente a 15; H/D→N 14 frente a 12. Solo mejora 1/5 folds. Leer [RESULTADOS_BETO_V1.md](RESULTADOS_BETO_V1.md).

Fuente inmutable: `af99d510da75b5a54f63fe46b56af3bcbb55217b` de `main`, ZIP `resultados_beto_20260917T012512_748901Z.zip`; origen/hashes en `data/auditoria/recepcion_beto_v1/origen.json`. No son seis corridas: los otros cinco respaldos son acumulativos. La auditoría se reproduce con `40_gestionar_proyecto.py auditar-resultados ZIP --salida RUTA_NUEVA.json`, sin GPU ni sobrescribir resultados. El resultado no se instaló en la carpeta activa de entrenamiento; las copias locales descargadas están ignoradas, y GitHub conserva los originales.

Se recibió un smoke que declara éxito y hardware RTX 5060; no se repitió aquí ni se recibieron pesos/código remoto. **Pendiente cerrar procedencia con el agente externo**, especialmente cambios de código, entorno completo/CUDA y manifiesto de entrada. `hardware.entrenamiento_realizado=false` es un campo estático del runner, no un veredicto de no ejecución. No solicitar ni publicar credenciales, venv ni pesos.

La [investigación web](INVESTIGACION_SOTA_POSTURA_MONETARIA.md) es anterior a esta recepción y propone candidatos, no una adopción. No lanzar MrBERT ni otra variante automáticamente: primero cerrar procedencia y diagnosticar las nuevas inversiones sin cambiar etiquetas.
Antes se ordenó el proyecto y se preparó una entrega con código/datos para otro PC; la limpieza extrema final sigue pendiente. No se autorizó cerrar/fusionar el PR ni nuevas anotaciones.

- Entrega de origen: rama `arena/01a0a81b-fase-2`, **PR #4**: https://github.com/joako0o/FASE_2/pull/4.
- Comprobar si el PR está abierto, integrado o cerrado sin integrar. Una nueva sesión desde `main` no recibe cambios de un PR simplemente cerrado.
- Trabajar en la rama que el nuevo entorno asigne. No recrear ni cambiar automáticamente a la rama anterior.
- Entrada operativa: `scripts/40_gestionar_proyecto.py`. Orientación para el usuario: `EMPEZAR_AQUI.md`.
- El ZIP portable contiene código, datos, historia necesaria y paquete BETO; no `.git`, entornos, pesos ni credenciales. El inventario está en `entrega/archivos_proyecto.txt`; el ZIP añade `MANIFIESTO_ENTREGA.json` para verificarlo sin dependencias.
- Se simplificaron README/AVANCE y se añadieron índices. No se movieron rutas congeladas ni se eliminaron fuentes/resultados necesarios por parecer antiguos. No repetir limpieza destruyendo manifiestos.

**Verificación del traslado:** 90 pruebas aprobadas, 0 omitidas; instalación limpia desde ZIP sin Git, ruta con espacios, preparación idéntica y reexportación comprobadas en Linux/Python 3.11. En aquella auditoría se verificaron 330 archivos previos intactos; los cambios posteriores están versionados. Evidencia en `data/auditoria/entrega_portable_v1/verificacion.json`. No es validación GPU ni ejecución Windows/macOS.

## 2. Lo pendiente de verdad

**Falta cerrar la procedencia remota y explicar el deterioro, no calcular por primera vez las métricas.** Ya se reprodujo exactamente la comparación recibida, se verificaron probabilidades/IDs/cobertura declarada y se hizo una segunda cuenta aritmética. 98 pruebas de software aprobadas, 0 omitidas. No se repitieron entrenamiento ni tokenización oficiales localmente.

Entorno anterior: Linux, Python 3.11, 2 CPU, ~4 GB RAM, sin NVIDIA. GitHub API y PyPI funcionaban; Hugging Face, descarga histórica DCC y ruedas CPU PyTorch fallaban con TLS EOF. No es un problema de contraseña. El navegador de investigación leyó metadatos, pero no transfirió pesos al cómputo.

Se rechazó y retiró un vocabulario histórico distinto al checkpoint elegido; hashes y motivo en `data/auditoria/preparacion_beto_v1/acceso.json`. No volver a usarlo como sustituto aproximado. No desactivar TLS, inventar una prueba exitosa ni contratar recursos sin autorización.

## 3. Primeros pasos en la nueva sesión

1. Leer `AGENTS.md`, este documento y `docs/AVANCE.md`. Revisar `git status`/rama y estado real del PR si hay Git.
2. Si es el ZIP portable, ejecutar `python scripts/40_gestionar_proyecto.py verificar-entrega` **antes de editar**. En ZIP GitHub normal no existe ese manifiesto; usar los controles de preparación.
3. Instalar Python 3.11 recomendado y ejecutar `instalar`, `preparar`, `probar --regresion`. El gestor crea `.venv`; no depende de `/home/user/venvs/fase2` del entorno anterior.
4. Confirmar paquete **`f7aa15894b1c0a4cdcf64a2a5c26e9b5029393e960a44c57f474a90fcc2b681a`**, 1.352 textos íntegros / 1.997.823 caracteres, 793 validaciones y cinco grupos. Tamaños de train antes del filtro de relevancia: 1178, 1178, 1178, 1183, 1183.
5. No iniciar otra corrida por defecto. Recuperar el ZIP final desde el origen fijado, ejecutar `auditar-resultados` si se necesita verificar la recepción y leer las métricas/limitaciones. Conservar TF-IDF; revisar procedencia y nuevas inversiones antes de proponer otro experimento.
6. Si el investigador trae resultados GPU, **primero verificar procedencia/manifiestos/paquete, cobertura y los cinco grupos**. Un ZIP de resultados no es un proyecto completo. Colab usa la carpeta `ejecucion/`; el gestor local usa `data/checkpoints/beto_v1/ejecucion/`: trasladar solo esos resultados a una ruta nueva, sin sobrescribir intentos previos.

El notebook fijó código al commit **`8a088fc3fc283c9e2cccaf179ea3261f61bccd1d`**; la versión del notebook enlazada en la guía está publicada en **`c93eef3f1fdd9ea3e43b52a7dcff9d46b1035259`**. Aunque descargue esa revisión anterior a la organización, produce el mismo paquete. No mezclar resultados si una corrección futura del runner cambia esa identidad.

## 4. Fuentes de verdad y decisiones cerradas

- `data/L0/corpus.csv`: 9.725 intervenciones, 132 reuniones. Texto/OCR original inmutable.
- `data/etiquetas/`: 1.352 anotaciones IA originales. No cambiarlas ni incorporar nuevas bases externas a este experimento.
- `data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv`: referencia activa, columna **`etiqueta_corregida_v2`**.
- Seis decisiones humanas aprobadas: **R01 H, R03 N, R08 D, R12 H, R17 D, R21 D**. Después se aceptaron las **13 propuestas concretas** de la revisión de 66 mediante «corrige las referencias…» y «sigue».
- Son **19 decisiones aceptadas / 16 cambios efectivos** frente a IA. Los **12 ambiguos permanecen sin modificar**. Aceptaciones en `data/auditoria/revision_entrenamiento_30_v1/devolucion_humana_v1/adjudicacion_aprobada_v1/` y `data/auditoria/revision_errores_adjudicada_v1/adjudicacion_cierre_66_v1/aceptacion.json`.
- Control actual: `data/evaluacion/referencias_corregidas_v2/predicciones_validacion.csv`, **supervision=`seis_mas_trece`**, 793 filas. Filtro A congelado; no reentrenarlo ni cambiar folds.
- Las antiguas 306 anotaciones no son un test independiente intacto. **No abrir sus respuestas ni ejecutar pruebas integrales que las relean.** Fecha humana confirmada: 2026-09-16. Las 30 anotaciones posteriores ya fueron devueltas en XLSX; no pedirlas otra vez.

Criterio semántico: dirección futura respaldada en la intervención completa sí cuenta. Mención, historia o riesgo condicional no equivalen a adhesión. Mantener no implica N automáticamente; subir más lento no es D; reducir estímulo no es reducir TPM. No inferir tasas/direcciones desde otras intervenciones ni reparar OCR.

## 5. Resultados ya obtenidos — no repetir la búsqueda

Contra la misma referencia v2:

| Supervisión TF-IDF | F1 H/D medio | Errores / 793 |
|---|---:|---:|
| Seis adjudicaciones anteriores | 0,711084 | 55 |
| Seis más trece correcciones | **0,747060** | **51** |

Cambio atribuible al reentrenamiento contra referencia fija: **+0,035976**, mejora en 4/5 folds. Cambiar la referencia del control daba un efecto distinto, +0,062262; no mezclarlo con mejora del modelo. Evaluación asistida posterior a ver desacuerdos, no evidencia independiente.

Matriz actual: filas referencia H/D/N, columnas predicción H/D/N:

```text
62   6   8
 9  38   4
10  14 642
```

Son **15 H↔D**, **12 H/D→N** y **24 N→H/D**, con soportes H=76/D=51/N=666. Diez inversiones más claras fueron examinadas; cinco ambiguas aparte: IDs terminados en 671, 215, 867, 1019 y 621 (lista completa en el paquete/diagnóstico).

El diagnóstico 37 reconstruyó exactamente 793 predicciones y 8.558 contribuciones activas. Sonda de primera cita: 4 coincidencias, 4 N, 2 inversiones; **no es un extractor ni una métrica de mejora**. Algunas primeras citas pierden contexto necesario. Coeficientes no prueban causalidad lingüística. Informes en `docs/LECTURA_DIAGNOSTICO_INVERSIONES_HD_V1.md` y `docs/DIAGNOSTICO_INVERSIONES_HD_V1.md`.

Ya se probaron n-gramas hasta 6, híbridos, alternativas H/D y un piloto WCB limitado. No repetir esas búsquedas ni añadir neutrales como respuesta automática a las inversiones. La siguiente comparación autorizada es BETO propio.

## 6. Protocolo BETO que no se debe cambiar silenciosamente

- Cased: `dccuchile/bert-base-spanish-wwm-cased`, revisión **`c4d86612f51b4f46759c8390d1798c2febe71b93`**. Hashes de archivos en `checkpoint.json`; pesa 439.621.341 bytes y el seleccionado es `.bin`, no safetensors.
- Mismos datos v2, folds y A. Todo el texto, sin citas manuales: 510 tokens de contenido + 2 especiales, solapamiento 64, cobertura completa.
- Media de logits por intervención; una CE documental ponderada por clase calculada solo en train relevante. Acumulación de 8, tamaño real en el último grupo.
- Tres épocas, AdamW 2e-5, weight_decay 0,01, warmup 10%, clipping 1, FP32, gradient checkpointing, semilla 20260915. Sin elegir época con validación.
- Prueba real en dos documentos train, uno largo, verificando forward/backward y cambios de encoder/cabeza. Descartar instancia; checkpoint inicial nuevo por fold.
- Criterios: F1 H/D medio +0,02, mejora en ≥3/5 folds, pérdida macro ≤0,005 y recall H/D ≤0,02; **menos inversiones sin aumentar H/D→N**. Cinco ambiguos desglosados, sin quitarlos del criterio principal de 793.
- No adopción automática, refit final, scoring masivo ni declaración de generalización. Confirmación realmente nueva solo después de evidencia de desarrollo.

## 7. Si la primera prueba GPU falla

Conservar el error completo y la versión del entorno, sin secretos. La implementación no fue validada extremo a extremo con GPU; puede requerir correcciones. No reducir a la primera ventana ni cambiar etiquetas para que termine.

Si hay que modificar 38/39 o el protocolo, hacerlo explícitamente en una etapa nueva, con tests y nueva preparación. El manifiesto captura sus bytes: **no editarlo para saltarse una incompatibilidad**. No mezclar folds completados de paquetes distintos. Un grupo parcial no tiene reanudación de optimizador; conservarlo aparte antes de repetirlo.

## 8. Limpieza final extrema: requisito pendiente del investigador

**No dar por terminada la limpieza con el gestor 40.** El investigador considera incorrecto entregar aproximadamente 40 scripts y exige que, al final, quede solo lo necesario y esencial. La organización para traslado fue provisional. Ver la regla obligatoria [REGLAS §12](REGLAS.md#12-limpieza-extrema-obligatoria-antes-de-la-entrega-final).

Antes de la entrega definitiva: sustituir dependencias de etapas antiguas por una entrada y pocos módulos claros; eliminar duplicación/material muerto; separar del paquete operativo el histórico necesario, dejándolo recuperable. No basta con esconder los 40 scripts detrás de un lanzador ni moverlos sin eliminar la dependencia. Preservar datos/adjudicaciones esenciales y demostrar equivalencia en instalación limpia, con inventario reducido y nuevos manifiestos, sin alterar los históricos. No se ejecuta esa refactorización en esta nota: queda como condición de cierre explícita.

## 9. Cierre de la próxima sesión

Actualizar AVANCE/CONTINUIDAD y el inventario al añadir archivos. Ejecutar controles seleccionados, exportar, extraer y verificar el ZIP. Mantener pesos/venv/caches/ZIP fuera de Git. Informar resultados reales y límites. No borrar referencias/artefactos verificables ni cerrar/fusionar el PR sin autorización.
