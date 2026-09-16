# fusionar_gold_llenado.py
# =============================================================================
# Reintegra el etiquetado humano del gold ciego al formato canónico.
#
# CONTEXTO
# El etiquetador trabaja sobre gold_ciego_300.xlsx (libro Excel con
# desplegables; ver preparar_gold_xlsx.py) o, alternativamente, sobre
# gold_ciego_300_limpio.csv (copia Excel-amable: UTF-8 con BOM, separador
# ';', filas de una línea; ver preparar_gold_limpio.py). Al terminar — o
# para revisar avances por lote —
# este script toma ese archivo YA LLENADO y vuelve a dejar las 5 columnas de
# etiquetado dentro de una copia del canónico (coma, sin BOM, texto original
# con sus saltos de línea), lista para concatenar a capa L1 y correr el kappa.
#
# QUÉ VALIDA (criterio de docs/INSTRUCCIONES_GOLD.md y codebook v2)
#   - Mismas 306 intervenciones, mismo orden que el canónico.
#   - `texto` sin editar (comparado con whitespace normalizado).
#   - etiqueta ∈ {hawkish, dovish, neutral}; confianza ∈ {alta, media};
#     es_relevante ∈ {0, 1}. Filas sin llenar se cuentan como pendientes.
#   - nota obligatoria si es_relevante=0.
#   - frase_justificante obligatoria si etiqueta ∈ {hawkish, dovish};
#     máx. 300 caracteres y contenida VERBATIM en el texto (whitespace
#     normalizado, igual que 05_validar_etiquetas.py).
#
# SALIDA
#   data/muestras/gold_ciego_300_llenado.csv (por defecto): el canónico más
#   las 5 columnas llenas. Si hay ERRORES duros no escribe nada salvo que se
#   pase --forzar; las filas pendientes no bloquean (permite guardar a medias).
#
# Ejecución:
#   python scripts/fusionar_gold_llenado.py <archivo_llenado.csv> [--salida X]
# =============================================================================

import csv
import sys
from pathlib import Path

RUTA_MUESTRAS = Path(__file__).resolve().parent.parent / "data" / "muestras"
CANONICO = RUTA_MUESTRAS / "gold_ciego_300.csv"
SALIDA_DEFECTO = RUTA_MUESTRAS / "gold_ciego_300_llenado.csv"

COLS_LLENAR = ["etiqueta", "confianza", "es_relevante", "nota",
               "frase_justificante"]
ETIQUETAS = {"hawkish", "dovish", "neutral"}
CONFIANZAS = {"alta", "media"}


def norm(s: str) -> str:
    """Whitespace normalizado (misma regla que 05_validar_etiquetas.py)."""
    return " ".join(s.split())


def leer_xlsx(ruta: Path):
    """Lee el .xlsx llenado (hoja 'etiquetar') devolviendo cabecera + filas
    de strings, igual que leer_tabla. Normaliza números de Excel (orden,
    es_relevante) a su forma canónica en texto."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise AssertionError(
            "para leer .xlsx instala openpyxl (pip install -r requirements.txt)")
    wb = load_workbook(ruta, read_only=True, data_only=True)
    if "etiquetar" not in wb.sheetnames:
        raise AssertionError("el .xlsx no trae la hoja 'etiquetar'")
    filas = list(wb["etiquetar"].iter_rows(values_only=True))

    def txt(v):
        if v is None:
            return ""
        if isinstance(v, bool):
            return "1" if v else "0"
        if isinstance(v, (int, float)) and float(v).is_integer():
            return str(int(v))
        return str(v)

    cab = [txt(c).strip() for c in filas[0]]
    datos = [[txt(c) for c in fila] for fila in filas[1:]]
    datos = [f for f in datos if any(c.strip() for c in f)]
    ancho = len(cab)
    assert all(len(f) == ancho for f in datos), \
        "el .xlsx trae filas con distinto número de columnas"
    return cab, datos, "xlsx"


def leer_tabla(ruta: Path):
    """Lee el archivo llenado (.xlsx o .csv) tolerando BOM, ';' o ',', y
    cp1252 como último recurso (Excel antiguo guarda ANSI si no se elige
    'CSV UTF-8'). Devuelve (cabecera, filas, etiqueta_formato)."""
    if ruta.suffix.lower() in (".xlsx", ".xlsm"):
        return leer_xlsx(ruta)
    crudo = ruta.read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            texto = crudo.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise AssertionError("no se pudo decodificar el archivo")
    if enc == "cp1252":
        print("AVISO: el archivo no era UTF-8; se leyó como cp1252. Revisa las "
              "tildes de tus notas.")
    for delimitador in (";", ",", "\t"):
        cab = next(csv.reader(texto.splitlines(), delimiter=delimitador))
        if "intervencion_id" in cab and len(cab) >= 11:
            filas = list(csv.reader(texto.splitlines(), delimiter=delimitador))
            return filas[0], filas[1:], delimitador
    raise AssertionError("no reconocí el separador (';' o ',') ni la cabecera")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    assert args, "uso: python scripts/fusionar_gold_llenado.py <archivo_llenado.csv> [--salida X] [--forzar]"
    ruta_lleno = Path(args[0])
    salida = SALIDA_DEFECTO
    if "--salida" in sys.argv:
        salida = Path(sys.argv[sys.argv.index("--salida") + 1])
    forzar = "--forzar" in sys.argv

    # --- canónico ---
    with open(CANONICO, newline="", encoding="utf-8") as f:
        filas_c = list(csv.reader(f))
    cab_c, datos_c = filas_c[0], filas_c[1:]
    idx = {nombre: i for i, nombre in enumerate(cab_c)}
    texto_canon = {fila[idx["intervencion_id"]]: fila[idx["texto"]]
                   for fila in datos_c}

    # --- archivo llenado ---
    cab_l, datos_l, sep = leer_tabla(ruta_lleno)
    idx_l = {nombre: i for i, nombre in enumerate(cab_l)}
    falta = [c for c in idx if c not in idx_l]
    assert not falta, f"al archivo llenado le faltan columnas: {falta}"
    ids_l = [fila[idx_l["intervencion_id"]] for fila in datos_l]
    ids_c = [fila[idx["intervencion_id"]] for fila in datos_c]
    assert sorted(ids_l) == sorted(ids_c), (
        "los IDs del archivo llenado no coinciden con los 306 del canónico")
    llenado = {fila[idx_l["intervencion_id"]]: fila for fila in datos_l}

    errores, pendientes = [], []
    cuenta = {"hawkish": 0, "dovish": 0, "neutral": 0}
    irrelevantes = 0

    for fila_c in datos_c:
        iid = fila_c[idx["intervencion_id"]]
        fila_l = llenado[iid]
        orden = fila_c[idx["orden"]]
        donde = f"orden {orden} ({iid})"

        if norm(fila_l[idx_l["texto"]]) != norm(fila_c[idx["texto"]]):
            errores.append(f"{donde}: la columna texto fue editada "
                           "(debe quedar igual al original)")
            continue

        valores = {}
        for col in COLS_LLENAR:
            v = fila_l[idx_l[col]]
            valores[col] = "" if v is None else v.strip()

        if not (valores["etiqueta"] or valores["confianza"]
                or valores["es_relevante"]):
            pendientes.append(donde)
            continue

        etiqueta = valores["etiqueta"].lower()
        confianza = valores["confianza"].lower()
        relevante = valores["es_relevante"]

        if etiqueta not in ETIQUETAS:
            errores.append(f"{donde}: etiqueta vacía o inválida: "
                           f"{valores['etiqueta']!r} (hawkish/dovish/neutral)")
        else:
            cuenta[etiqueta] += 1
        if confianza not in CONFIANZAS:
            errores.append(f"{donde}: confianza vacía o inválida: "
                           f"{valores['confianza']!r} (alta/media)")
        if relevante not in {"0", "1"}:
            errores.append(f"{donde}: es_relevante inválido: {relevante!r} (0/1)")
        else:
            if relevante == "0":
                irrelevantes += 1
                if not valores["nota"]:
                    errores.append(f"{donde}: falta la nota (obligatoria con "
                                   "es_relevante=0)")
            frase = valores["frase_justificante"]
            if etiqueta in {"hawkish", "dovish"} and not frase:
                errores.append(f"{donde}: falta frase_justificante (obligatoria "
                               f"en {etiqueta})")
            if frase:
                if len(frase) > 300:
                    errores.append(f"{donde}: frase_justificante de {len(frase)} "
                                   "caracteres (máx. 300)")
                elif norm(frase) not in norm(texto_canon[iid]):
                    errores.append(f"{donde}: frase_justificante no está "
                                   "verbatim en el texto")

    # --- reporte ---
    print(f"leído: {ruta_lleno} (separador {sep!r}, {len(datos_l)} filas)")
    print(f"etiquetas: {cuenta} | es_relevante=0: {irrelevantes} | "
          f"pendientes de llenar: {len(pendientes)}")
    if pendientes and len(pendientes) <= 12:
        print("  pendientes:", "; ".join(pendientes))

    if errores:
        print(f"\nERRORES ({len(errores)}) — corrígelos en el archivo llenado:")
        for e in errores[:20]:
            print("  -", e)
        if len(errores) > 20:
            print(f"  ... y {len(errores) - 20} más")
        if not forzar:
            print("No se escribió la salida (usa --forzar para escribir igual).")
            sys.exit(1)

    # --- escritura: canónico + columnas llenas, formato canónico ---
    with open(salida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL,
                              lineterminator="\n")
        escritor.writerow(cab_c)
        for fila_c in datos_c:
            iid = fila_c[idx["intervencion_id"]]
            fila_l = llenado[iid]
            nueva = list(fila_c)
            for col in COLS_LLENAR:
                nueva[idx[col]] = fila_l[idx_l[col]].strip()
            escritor.writerow(nueva)
    print(f"\nOK: {salida}")
    print("Este archivo mantiene el formato canónico y puede concatenarse a "
          "capa L1 / usarse para el kappa.")


if __name__ == "__main__":
    sys.exit(main())
