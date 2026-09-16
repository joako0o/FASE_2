# Siguiente paso: ejecutar BETO en una GPU

## Qué está listo y qué no

**Listo:** entrada verificada con 1.352 intervenciones completas (1.997.823 caracteres), las mismas cinco particiones y las 793 predicciones TF-IDF de control; referencias v2 y filtro de relevancia A sin cambios. Código de entrenamiento, comparación y notebook preparados.

**Pendiente:** descargar los pesos oficiales, superar la prueba técnica con el encoder real y entrenar/evaluar los cinco grupos. Aquí no hay GPU y los servidores de pesos fallan con TLS. **No hay resultados BETO ni una mejora demostrada todavía.** La ejecución completa en Colab tampoco ha sido validada desde este entorno.

## Qué tienes que hacer

1. **[Abrir el notebook en Google Colab](https://colab.research.google.com/github/joako0o/FASE_2/blob/arena/01a0a81b-fase-2/notebooks/BETO_comparacion_v1.ipynb).** Puedes guardar una copia en tu cuenta. El código del experimento que descarga está fijado a un commit, no al último estado de una rama.
2. En **Entorno de ejecución → Cambiar tipo de entorno de ejecución**, elegir **GPU**; T4 si está disponible. No contratar un plan ni pagar: si no te ofrecen GPU gratuita, detenerse y avisarme. La disponibilidad y duración de la sesión no están garantizadas.
3. Ejecutar las celdas **en orden**. Dejar `RESTAURAR_ZIP = False` la primera vez. Primero instala un entorno aislado y verifica los datos; después prueba dos textos completos de entrenamiento con BETO. Si aparece un error, no saltarlo ni cambiar las etiquetas/longitud: enviarme el mensaje, sin contraseñas ni tokens.
4. Si esa prueba pasa, ejecutará los **cinco grupos** y luego la comparación. No hay una estimación fiable de duración antes de medir la GPU real. La instalación también descarga dependencias grandes.
5. Conservar los archivos **`beto_resultados.zip`** que descarga al completar cada grupo; el último es el más completo. Si el navegador bloquea descargas múltiples, permitirlas o usar la carpeta de archivos de Colab. **Devolver aquí el ZIP final** para revisar los resultados. No necesitas hacer nuevas anotaciones.

La GPU la asigna Colab en tu sesión; este agente no puede iniciarla ni mantenerla abierta por ti. El notebook no monta Drive, no solicita claves HF/GitHub y no configura servicios de pago. Las fuentes y el modelo seleccionado son de acceso público.

## Qué comprobaré al recibir el resultado

- Que los cinco grupos corresponden al paquete fijo y no se mezclaron corridas.
- Que todos los tokens de cada texto fueron cubiertos, no solo el principio o citas elegidas manualmente.
- **H→D y D→H**, sin esconderlos mediante más **H/D→N**; también N→H/D, F1 H/D, recalls y matriz completa.
- Las cinco inversiones conocidas con referencia ambigua se muestran aparte, pero no desaparecen del resultado principal de 793 casos.
- Criterios previamente fijados: mejora media F1 H/D de al menos 0,02 y en al menos 3/5 grupos, sin deterioro excesivo de macro-F1/recalls, menos inversiones y sin más H/D→N. No significa adopción automática ni prueba independiente.

El control actual tiene **15 inversiones H↔D, 12 H/D→N y 24 N→H/D**. No hay cifras equivalentes para BETO todavía. Acertar los diez ejemplos ya examinados, por sí solo, no demostraría que el modelo generaliza mejor.

## Si se interrumpe Colab

- La sesión puede perder archivos al desconectarse. Los ZIP descargados son el respaldo; no se guardan pesos entrenados ni el estado del optimizador.
- En una sesión nueva: ejecutar instalación y preparación; activar `RESTAURAR_ZIP = True` en la celda opcional y subir **un solo ZIP**, el más reciente. El notebook verifica el paquete y los manifiestos. Los grupos completos se reconocen y no se entrenan otra vez.
- **No se reanuda a mitad de un grupo.** Si queda `fold_N/` sin su `manifest.json`, el runner se detiene para no sobrescribir. Enviarme el mensaje y el respaldo; conservaremos ese intento aparte antes de repetir únicamente ese grupo. No borrar ni mezclar resultados por cuenta propia.
- Si hay falta de memoria, checkpoint distinto, error de dependencias o GPU incompatible, detenerse. No reducir a la primera ventana ni cambiar silenciosamente el método.

## Reproducción local y límites de las pruebas

Con el entorno indicado en `requirements-beto.txt`, desde la raíz del repositorio:

```bash
python scripts/38_preparar_beto.py                    # una sola vez en ruta nueva
python scripts/38_preparar_beto.py --verificar
python -m unittest discover -s tests -p test_preparacion_beto.py -v
python scripts/39_ejecutar_beto.py --comprobar
python scripts/39_ejecutar_beto.py --smoke             # requiere GPU y pesos
python scripts/39_ejecutar_beto.py --fold 1 --reanudar  # repetir para 2, 3, 4, 5
python scripts/39_ejecutar_beto.py --consolidar
```

No ejecutar la suite histórica completa: algunos módulos abren las respuestas antiguas de 306. Los 14 tests nuevos verifican datos, segmentación, una pérdida NumPy de referencia, tokenización de juguete y el comparador mediante copias **sintéticas y temporales** del control. No prueban que BETO se haya entrenado ni sustituyen la prueba técnica GPU.

[Investigación y protocolo](INVESTIGACION_Y_PROTOCOLO_BETO_V1.md) · [Evidencia de preparación](../data/auditoria/preparacion_beto_v1/preparacion.json) · [Verificación local](../data/auditoria/preparacion_beto_v1/verificacion.json) · [Notebook](../notebooks/BETO_comparacion_v1.ipynb).
