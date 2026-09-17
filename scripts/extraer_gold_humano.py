"""Extrae de forma reproducible el gold humano OOXML sin depender de openpyxl."""
import argparse
import csv
import re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def indice_columna(referencia):
    letras = re.match(r'[A-Z]+', referencia).group()
    numero = 0
    for letra in letras:
        numero = numero * 26 + ord(letra) - 64
    return numero - 1


def extraer(origen, salida):
    origen, salida = Path(origen), Path(salida)
    if not origen.is_absolute():
        origen = RAIZ / origen
    if not salida.is_absolute():
        salida = RAIZ / salida
    with ZipFile(origen) as libro:
        compartidas = []
        if 'xl/sharedStrings.xml' in libro.namelist():
            raiz = ET.fromstring(libro.read('xl/sharedStrings.xml'))
            compartidas = [
                ''.join(nodo.text or '' for nodo in celda.iter(f"{{{NS['m']}}}t"))
                for celda in raiz.findall('m:si', NS)
            ]
        hoja = ET.fromstring(libro.read('xl/worksheets/sheet1.xml'))
        tabla = []
        for fila in hoja.findall('.//m:sheetData/m:row', NS):
            valores = {}
            for celda in fila.findall('m:c', NS):
                indice = indice_columna(celda.attrib['r'])
                tipo = celda.attrib.get('t')
                valor = celda.find('m:v', NS)
                if tipo == 'inlineStr':
                    contenido = ''.join(n.text or '' for n in celda.iter(f"{{{NS['m']}}}t"))
                elif valor is None:
                    contenido = ''
                elif tipo == 's':
                    contenido = compartidas[int(valor.text)]
                else:
                    contenido = valor.text or ''
                valores[indice] = contenido
            tabla.append([valores.get(i, '') for i in range(max(valores) + 1 if valores else 0)])
    encabezados = tabla[0]
    if len(tabla) != 307 or 'intervencion_id' not in encabezados:
        raise ValueError('El libro humano esperado debe contener 306 datos y encabezados conocidos')
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open('x', encoding='utf-8', newline='') as archivo:
        escritor = csv.writer(archivo, lineterminator='\n')
        escritor.writerow(encabezados)
        for fila in tabla[1:]:
            escritor.writerow(fila + [''] * (len(encabezados) - len(fila)))
    return salida


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origen', type=Path, default=Path('gold_ciego_300_listo.xlsx'))
    parser.add_argument('--salida', type=Path, default=Path('data/auditoria/revision_humana_v3/fuente_humana_v2_extraida.csv'))
    args = parser.parse_args()
    print(extraer(args.origen, args.salida))
