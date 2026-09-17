"""Controles compartidos de datos, anotaciones y trazabilidad del proyecto."""

# ---- 1. Dominios y utilidades de solo lectura ----
import hashlib
import importlib.util
from pathlib import Path

ETIQUETAS = {"hawkish", "dovish", "neutral"}
CONFIANZAS = {"alta", "media", "baja"}
MAX_CARACTERES_FRASE = 300


def norm(texto):
    """Normaliza solo whitespace: no cambia puntuación, OCR ni mayúsculas."""
    return " ".join(texto.split())


def sha256(ruta):
    """Huella de un insumo o artefacto sin modificarlo."""
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def cargar_script(nombre):
    """Carga scripts numerados para reutilizar sus funciones en tests/auditorías."""
    ruta = Path(__file__).resolve().parent / nombre
    spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# ---- 2. Protección de fuentes y selecciones congeladas ----
# No se permite regenerar inadvertidamente L0, muestras o anotaciones pasadas.
def exigir_salidas_nuevas(*rutas):
    existentes = [str(ruta) for ruta in rutas if Path(ruta).exists()]
    if existentes:
        raise FileExistsError("No se sobrescriben archivos existentes: " + ", ".join(existentes))


# ---- 3. Reglas comunes a IA y gold humano ----
# La misma regla R10 aplica a todos los relevantes; toda cita aportada se valida.
def errores_anotacion(etiqueta, confianza, es_relevante, nota, frase, texto,
                       confianzas=CONFIANZAS):
    errores = []
    if etiqueta not in ETIQUETAS:
        errores.append("etiqueta inválida")
    if confianza not in confianzas:
        errores.append("confianza inválida")
    if str(es_relevante) not in {"0", "1"}:
        errores.append("relevancia inválida")
    if str(es_relevante) == "0":
        if etiqueta != "neutral":
            errores.append("irrelevante no neutral")
        if not nota.strip():
            errores.append("falta nota")
    if str(es_relevante) == "1" and not frase.strip():
        errores.append("falta frase")
    if len(frase) > MAX_CARACTERES_FRASE:
        errores.append("frase excede 300 caracteres")
    if frase.strip() and norm(frase) not in norm(texto):
        errores.append("frase no verbatim")
    return errores


# ---- 4. Tandas por presupuesto (una única implementación) ----
def asignar_tandas(palabras, presupuesto, tanda_inicial=1):
    """Greedy estable; un texto mayor al presupuesto queda en una tanda propia."""
    assert presupuesto > 0 and tanda_inicial > 0
    tandas, tanda, acumulado = [], tanda_inicial, 0
    for cantidad in palabras:
        assert cantidad >= 0
        if acumulado > 0 and acumulado + cantidad > presupuesto:
            tanda, acumulado = tanda + 1, 0
        tandas.append(tanda)
        acumulado += cantidad
    return tandas


# ---- 5. Training IA: carga validada y sin duplicados entre corridas ----
def cargar_entrenamiento():
    import pandas as pd
    import config

    archivos = sorted(config.RUTA_ETIQUETAS.glob("etiquetas_*.csv"))
    assert archivos, "no hay corridas de entrenamiento"
    validador = cargar_script("05_validar_etiquetas.py")
    tablas = []
    for archivo in archivos:
        datos = pd.read_csv(archivo)
        validador.validar(datos)
        assert datos.metodo.eq("ia_ronda").all(), f"método no IA en training: {archivo}"
        tablas.append(datos)
    conjunto = pd.concat(tablas, ignore_index=True)
    assert conjunto.intervencion_id.is_unique, "IDs duplicados entre corridas IA"
    return conjunto
