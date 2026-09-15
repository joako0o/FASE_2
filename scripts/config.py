"""
config.py — Parametros centrales del proyecto D&H.

Regla de uso: todo parametro reutilizable (semillas, rutas, tamanos de muestra,
URLs) vive aqui y solo aqui. Los scripts importan desde este modulo y nunca
definen valores magicos propios (REGLAS.md, seccion 4).
"""

from pathlib import Path

# -----------------------------------------------------------------------------
# Rutas del repositorio
# -----------------------------------------------------------------------------
# RUTA_REPO se deriva de la ubicacion de este archivo (scripts/config.py),
# por lo que el proyecto funciona igual en cualquier maquina sin editar rutas.
RUTA_REPO = Path(__file__).resolve().parent.parent

RUTA_EXCEL = RUTA_REPO / "consolidado_D&H.xlsx"

RUTA_DATOS = RUTA_REPO / "data"
RUTA_L0 = RUTA_DATOS / "L0"                 # corpus inmutable derivado del Excel
RUTA_L2 = RUTA_DATOS / "L2"                 # macro, votos, metadata de actores
RUTA_L2_RAW = RUTA_L2 / "raw"               # JSON crudos descargados de las APIs
RUTA_MUESTRAS = RUTA_DATOS / "muestras"     # muestras piloto y test-retest
RUTA_ETIQUETAS = RUTA_DATOS / "etiquetas"   # corridas de etiquetado (append-only)

# -----------------------------------------------------------------------------
# Parametros del corpus
# -----------------------------------------------------------------------------
HOJA_TRANSCRIPCION = "Transcripción"  # hoja de datos del Excel consolidado (con tilde)
ANIO_MIN = 2005
ANIO_MAX = 2015
N_REUNIONES_ESPERADAS = 132           # 12 reuniones al año x 11 años
N_INTERVENCIONES_ESPERADAS = 9725

# -----------------------------------------------------------------------------
# Parametros de muestreo (Fase 3) y de etiquetado (Fase 4+)
# -----------------------------------------------------------------------------
# Semilla maestra unica del proyecto: toda aleatoriedad se deriva de ella,
# lo que garantiza reproducibilidad total (REGLAS.md, seccion 4).
SEED_MAESTRA = 20260915

N_PILOTO = 300          # tamano de la muestra piloto de etiquetado
N_TEST_RETEST = 30      # submuestra fija re-etiquetada en cada ronda (estabilidad)
MIN_POR_ESTRATO = 2     # minimo de intervenciones por estrato en la muestra piloto

# -----------------------------------------------------------------------------
# Fuente de datos macroeconomicos
# -----------------------------------------------------------------------------
# mindicador.cl: API REST gratuita, sin clave, con series diarias/mensuales
# desde 2001 a la fecha (TPM, IPC, IMACEC, tasa de desempleo, entre otras).
URL_MINDICADOR = "https://mindicador.cl/api"
INDICADORES_DESCARGA = ["tpm", "ipc", "imacec", "tasa_desempleo"]

USER_AGENT_HTTP = "Mozilla/5.0 (proyecto-DyH; uso academico)"
TIMEOUT_HTTP_SEG = 20
