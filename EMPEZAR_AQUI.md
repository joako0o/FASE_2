# Llevar el proyecto a otro PC y continuar

## 1. Qué debes llevar

**Descarga `FASE_2_portable.zip` y descomprímelo completo.** Dentro está la carpeta `FASE_2/`, con código, datos, referencias, resultados históricos y entrada BETO preparada. No copies solo el notebook o solo los scripts. Puedes guardar el ZIP en un pendrive.

No incluye Python, dependencias instaladas, Git interno ni pesos BETO. Esas dependencias se instalan en el nuevo PC. **No es una entrega de un modelo BETO entrenado.**

Si descargas un ZIP normal desde GitHub también tendrás las fuentes y datos, pero no el paquete regenerable ni `MANIFIESTO_ENTREGA.json`: omite únicamente `verificar-entrega`; `preparar` lo reconstruirá.

**No hace falta cerrar el PR para descargar.** En GitHub puedes descargar desde la rama del PR mediante **Code → Download ZIP**. Para que una próxima sesión creada desde `main` reciba estos cambios, usa **Merge pull request** cuando decidas integrarlos, no solo **Close pull request**. No se ha cerrado ni fusionado el PR por ti.

## 2. Dónde está cada cosa

| Carpeta/archivo | Para qué sirve |
|---|---|
| **`scripts/`** | Todo el código Python. Punto de entrada: **`40_gestionar_proyecto.py`**. |
| **`data/`** | Corpus, anotaciones, referencias corregidas, particiones, resultados y auditoría. Incluidos en el ZIP. |
| `data/checkpoints/beto_v1/entrada/` | Paquete BETO preparado: textos, folds, control TF-IDF, checkpoint y manifiesto. Incluido en el ZIP portable; regenerable. |
| `data/checkpoints/beto_v1/ejecucion/` | Se crea cuando se ejecuta BETO; ahí van resultados por grupo, no pesos. |
| `notebooks/` | Alternativa Google Colab si el PC no tiene GPU compatible. |
| **`docs/CONTINUIDAD.md`** | Instrucciones para que otra sesión siga sin reconstruir toda la conversación. |
| `docs/`, `PLAN.md` | Metodología, evidencia y explicación histórica; no hay que ejecutarlos. |
| `entrega/archivos_proyecto.txt` | Lista explícita de archivos fuente que el exportador debe llevar. |
| `entregas/` | ZIP que produzcas localmente; fuera de Git. Copiarlos fuera del PC/entorno. |

Los Excel originales y devueltos se conservan como fuentes/evidencia. **No tienes que rellenarlos de nuevo**. El histórico no se mueve de carpeta porque sus rutas y hashes se usan en las verificaciones.

## 3. Preparar el nuevo PC (sin GPU)

Instala **Python 3.11 de 64 bits**, recomendado. El gestor admite también 3.12, pero la reproducción realizada aquí fue con 3.11/Linux. Windows/macOS no se han ejecutado aquí. En Windows activa la opción de añadir Python al PATH; puedes sustituir `python` por `py -3.11`. En Linux/macOS, por `python3.11`.

Abre una terminal **dentro de `FASE_2/`**, la carpeta que contiene este archivo. Ejecuta una línea a la vez:

```bash
python scripts/40_gestionar_proyecto.py verificar-entrega
python scripts/40_gestionar_proyecto.py instalar
python scripts/40_gestionar_proyecto.py preparar
python scripts/40_gestionar_proyecto.py probar --regresion
python scripts/40_gestionar_proyecto.py comprobar
```

- `verificar-entrega` solo necesita Python: comprueba los bytes después del traslado. Si falla, vuelve a extraer el ZIP; no alteres el manifiesto para hacerlo pasar.
- `instalar` crea **`.venv/`** con dependencias fijadas y requiere internet/PyPI. No copia el entorno de este equipo ni descarga los pesos. El gestor fuerza lectura UTF-8 en los procesos Python del proyecto para conservar tildes entre equipos.
- `preparar` verifica el paquete existente; si no existe, lo reconstruye desde los datos incluidos. Esperado: **1.352 documentos, 793 validaciones, cinco grupos**.
- `probar --regresion` ejecuta únicamente controles permitidos. **No ejecutar `unittest discover` sin filtro ni los scripts 01–39 en bloque.**
- `comprobar` puede informar «PyTorch no instalado» o «GPU no disponible»: eso impide el entrenamiento, no significa que hayas perdido los datos.

Si Python/venv/pip falla, conserva el error y compártelo en la siguiente sesión. No cambies versiones al azar ni regeneres etiquetas para resolver una instalación.

## 4. Entrenar BETO: solo con GPU NVIDIA/CUDA y acceso a los pesos

**La ejecución real sigue pendiente.** En un PC con GPU compatible y conexión a Hugging Face:

```bash
python scripts/40_gestionar_proyecto.py instalar --beto
python scripts/40_gestionar_proyecto.py comprobar
python scripts/40_gestionar_proyecto.py smoke
python scripts/40_gestionar_proyecto.py entrenar
python scripts/40_gestionar_proyecto.py comparar
```

`smoke` debe terminar correctamente antes del entrenamiento. `entrenar` ejecuta los cinco grupos y guarda un respaldo ZIP al completar cada uno. `comparar` exige los cinco completos. Si falla memoria, descarga o dependencias, detenerse y llevar el error a la próxima sesión. No existe una estimación fiable de duración ni una ejecución GPU certificada todavía.

El runner reconoce grupos completos al repetir `entrenar`, pero **no recupera un grupo a mitad de entrenamiento**. No sobrescribe un `smoke` o una comparación ya existentes. Conservar resultados y consultar antes de retirar un intento parcial. No se guardan pesos entrenados ni estado del optimizador.

Si el PC no tiene GPU, usar la [guía Colab](docs/GUIA_EJECUTAR_BETO_COLAB_V1.md). No pagar ni compartir contraseñas. Basta con devolver el ZIP de resultados; no hacen falta más anotaciones.

## 5. Volver a exportar y respaldar

Tras trabajar en el nuevo PC:

```bash
python scripts/40_gestionar_proyecto.py exportar
```

Creará una entrega nueva en `entregas/`, sin sobrescribir otra. Incluye los archivos declarados, el paquete y los resultados de las rutas previstas que existan. **No incluye archivos personales ni nuevos códigos fuera del inventario**: si la próxima sesión añade archivos fuente, debe actualizar `entrega/archivos_proyecto.txt` antes de exportar.

Para respaldar solo resultados GPU:

```bash
python scripts/40_gestionar_proyecto.py respaldar
```

Ese ZIP pequeño **no sustituye** al ZIP completo del proyecto. Guarda los respaldos fuera de la sesión/PC. Si ya utilizas Git y PR, también conserva los resultados locales: `data/checkpoints/` se ignora deliberadamente y no viaja al hacer push.

## 6. Mensaje para la siguiente sesión

Copia y pega:

> Continúa FASE_2. Lee primero AGENTS.md y docs/CONTINUIDAD.md. Tengo el proyecto con datos y la entrada BETO. No cambies referencias v2/folds/A ni repitas anotaciones. Verifica la entrega y las pruebas seguras. BETO todavía necesita pesos y una prueba real GPU; no confundas preparación con entrenamiento. Revisa el estado del PR #4 y trabaja en la rama asignada a esta nueva sesión. Si entrego resultados de GPU, verifica su procedencia antes de comparar.
