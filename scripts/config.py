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
RUTA_EXCEL_MACRO = RUTA_REPO / "consolidado_macro.xlsx"  # descarga local del usuario (mindicador/BCCh)

RUTA_DATOS = RUTA_REPO / "data"
RUTA_L0 = RUTA_DATOS / "L0"                 # corpus inmutable derivado del Excel
RUTA_L2 = RUTA_DATOS / "L2"                 # macro, votos, metadata de actores
RUTA_MUESTRAS = RUTA_DATOS / "muestras"     # muestras piloto y test-retest
RUTA_ETIQUETAS = RUTA_DATOS / "etiquetas"   # corridas de etiquetado (append-only)

# -----------------------------------------------------------------------------
# Parametros del corpus
# -----------------------------------------------------------------------------
HOJA_TRANSCRIPCION = "Transcripción"  # hoja de datos del Excel consolidado (con tilde)
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

# Regla de tandas: cada ronda de etiquetado en chat se rige por presupuesto de
# palabras (carga real de lectura), no por numero fijo de intervenciones.
PRESUPUESTO_PALABRAS_TANDA = 20000

# Fases del ciclo de politica monetaria 2005-2015, derivadas de las
# transiciones reales de policy_decision en data/L2/macro_por_reunion.csv
# (limite = fecha de la reunion RPM). Fuente unica para los scripts de
# muestreo 08/09/10 (en 08 figura tambien la descripcion narrativa de cada
# fase; los intervalos son identicos).
FASES_TPM = [
    ("2005_alzas",           "2005-01-01", "2005-07-12"),
    ("2006_alza_fin",        "2005-07-13", "2006-12-31"),
    ("2007_mixto",           "2007-01-01", "2007-12-31"),
    ("2008_crisis_alza",     "2008-01-01", "2008-12-31"),
    ("2009_bajas",           "2009-01-01", "2009-12-31"),
    ("2010_alza_emergencia", "2010-01-01", "2010-12-31"),
    ("2011_alza",            "2011-01-01", "2011-12-31"),
    ("2012_13_mantiene",     "2012-01-01", "2013-09-30"),
    ("2013_14_bajas",        "2013-10-01", "2014-12-31"),
    ("2015_quiebre",         "2015-01-01", "2015-12-31"),
]

# Vocabulario de decision de politica monetaria: heuristica de pre-muestreo
# (scripts 09 y 10) para enriquecer muestras con intervenciones "con stance".
# No es un clasificador: solo ordena el muestreo y queda registrada aqui.
PATRON_DECISION = (
    r"\b(?:vota[rc]?|votó|votar|acuerda|acordó|acuerdo|subir|bajar|rebajar|recortar|"
    r"mantener|alza|baja|recorte|opción|opciones|comunicado|sesgo)\b"
)

# Cargos con capacidad de voto en el Consejo (mas el Consejo como entidad y el
# Ministro de Hacienda, cuyas intervenciones suelen tener postura): pool
# prioritario para el enriquecimiento de clases minoritarias (decision 10).
CARGOS_CONSEJO = (
    "Presidente del Banco Central", "Vicepresidente del Banco Central",
    "Consejero", "Consejo", "Ministro de Hacienda",
)

# Cargo del staff que presenta la minuta de opciones de politica monetaria
# (recomendacion del equipo tecnico): pool secundario de enriquecimiento.
CARGOS_OPCIONES = ("Gerente de División Estudios", "Gerente de División Estudios (S)")
