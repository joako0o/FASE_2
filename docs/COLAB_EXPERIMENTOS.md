# Ejecución de experimentos FASE 2 en Google Colab

Notebook: [`colab/FASE_2_experimentos.ipynb`](../colab/FASE_2_experimentos.ipynb)

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/joako0o/FASE_2/blob/arena%2F01a0b014-fase-2/colab/FASE_2_experimentos.ipynb)

## Uso

1. Abrir el enlace.
2. Opcionalmente cambiar `EXPERIMENTO` en la primera celda.
3. Para un futuro encoder contextual, seleccionar primero **Entorno de ejecución → Cambiar tipo de entorno de ejecución → GPU**.
4. Pulsar **Entorno de ejecución → Ejecutar todo**.
5. Esperar la descarga automática de `resultados_fase2_<experimento>.zip`.
6. Adjuntar ese ZIP a la conversación para revisar logs, manifiestos y hashes.

La opción predeterminada es `suite_pruebas`. Las opciones disponibles son:

- `suite_pruebas`: valida la cadena de resultados recientes;
- `diagnostico_gpu`: registra CPU, PyTorch, CUDA y `nvidia-smi`;
- `palabras_caracteres`: reproduce la ronda W+C en una salida nueva;
- `extension_representaciones`: reproduce tokenización monetaria, NB-SVM, LSA y suavizado;
- `ensamble_calibrado`: reproduce el ensamble preregistrado.

## Seguridad y reproducibilidad

- El notebook clona únicamente la rama `arena/01a0b014-fase-2`.
- No solicita tokens, contraseñas ni acceso de escritura a GitHub.
- Instala el entorno mediante `scripts/40_gestionar_proyecto.py instalar`.
- Limita los hilos numéricos para reducir variación y consumo.
- Cada ZIP incluye `checksums_colab.json`.
- Los experimentos nuevos deben agregarse al repositorio y preregistrarse antes de incorporarlos al menú.

El enlace por rama apunta a la versión vigente. Para ejecuciones que deban quedar congeladas se debe usar un enlace de Colab basado en el hash exacto del commit.

## Reejecución en la misma sesión

El notebook cambia explícitamente el directorio activo a `/content` antes de eliminar una copia anterior de `/content/FASE_2`. Esto permite pulsar **Ejecutar todo** varias veces en la misma sesión sin dejar a Git dentro de un directorio borrado. El mensaje `fatal: Unable to read current working directory` corresponde a una versión anterior del notebook y no a un problema de permisos o visibilidad del repositorio.
