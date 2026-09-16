# preparar_gold_limpio.py
# =============================================================================
# Copia de trabajo LIMPIA del gold ciego para etiquetar en Excel / LibreOffice.
#
# PROBLEMA QUE RESUELVE
# El archivo canónico data/muestras/gold_ciego_300.csv es UTF-8 válido y está
# bien citado (verificable con el módulo csv de Python), pero en Excel en
# español se ve "sucio" por tres razones:
#   1. No tiene BOM: Excel lo abre como ANSI y las tildes salen mojibake.
#   2. 13 textos conservan saltos de línea internos del acta (uno tiene 72):
#      Excel quiebra la fila en varias líneas y parece que las columnas
#      estuvieran desordenadas.
#   3. El separador es coma y el Excel en español espera punto y coma: todo
#      puede caer en una sola columna.
#
# QUÉ HACE
# Lee el canónico (NO lo modifica) y escribe gold_ciego_300_limpio.csv con:
#   - UTF-8 CON BOM (Excel detecta la codificación automáticamente).
#   - Separador ';' (convención Excel/LibreOffice en español).
#   - Todos los campos citados y filas de una sola línea física: los saltos
#     de línea internos de `texto` se reemplazan por espacio. Esto NO afecta
#     la verificación verbatim de frase_justificante: el validador
#     (05_validar_etiquetas.py) compara con whitespace normalizado.
#   - Mismas 16 columnas, mismo orden, mismas 306 filas.
#
# CUÁNDO CORRERLO: una sola vez, antes de empezar a etiquetar (o si alguien
# borra el archivo limpio). No toca el canónico ni las etiquetas de la IA.
#
# Ejecución:  python scripts/preparar_gold_limpio.py
# =============================================================================

import csv
import sys
from pathlib import Path

RUTA_MUESTRAS = Path(__file__).resolve().parent.parent / "data" / "muestras"
SRC = RUTA_MUESTRAS / "gold_ciego_300.csv"
DST = RUTA_MUESTRAS / "gold_ciego_300_limpio.csv"


def aplanar(s: str) -> str:
    """Saltos de línea internos -> espacio (sin tocar el resto del texto)."""
    return s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ")


def main() -> None:
    with open(SRC, newline="", encoding="utf-8") as f:
        lector = csv.reader(f)
        filas = list(lector)
    cabecera, datos = filas[0], filas[1:]
    ancho = len(cabecera)
    assert all(len(r) == ancho for r in datos), "canónico con filas mal formadas"

    limpias = [[aplanar(campo) for campo in fila] for fila in datos]

    with open(DST, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL,
                              lineterminator="\r\n")
        escritor.writerow(cabecera)
        escritor.writerows(limpias)

    # --- verificación: misma identidad que el canónico ---
    with open(SRC, newline="", encoding="utf-8") as f:
        origen = list(csv.reader(f))[1:]
    with open(DST, newline="", encoding="utf-8-sig") as f:
        copia = list(csv.reader(f, delimiter=";"))[1:]
    assert len(origen) == len(copia), "cambió el número de filas"
    ids_o = [r[1] for r in origen]
    ids_c = [r[1] for r in copia]
    assert ids_o == ids_c, "cambió el orden o los IDs"
    norm = lambda s: " ".join(s.split())
    for o, c in zip(origen, copia):
        for j, (a, b) in enumerate(zip(o, c)):
            assert norm(a) == norm(b), (
                f"contenido alterado fuera de saltos de línea: "
                f"orden {o[0]}, columna {cabecera[j]}")

    con_lf = sum(1 for r in copia for campo in r if "\n" in campo)
    print(f"OK: {DST.name}")
    print(f"  filas: {len(copia)} | columnas: {ancho} | separador: ';' | BOM: sí")
    print(f"  campos con saltos de línea restantes: {con_lf}")
    print("Abre ESTE archivo en Excel/LibreOffice para etiquetar.")


if __name__ == "__main__":
    sys.exit(main())
