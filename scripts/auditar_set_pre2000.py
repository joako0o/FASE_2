"""Audita estructura, citas y duplicados del XLSX pre-2000 sin corregirlo ni entrenar."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
SALIDA = RAIZ / 'data/auditoria/set_pre2000_revision_inicial_v1'


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def columna(referencia):
    numero = 0
    for letra in re.match(r'[A-Z]+', referencia).group():
        numero = numero * 26 + ord(letra) - 64
    return numero - 1


def leer_primera_hoja(ruta):
    with ZipFile(ruta) as libro:
        compartidas = []
        if 'xl/sharedStrings.xml' in libro.namelist():
            raiz = ET.fromstring(libro.read('xl/sharedStrings.xml'))
            compartidas = [''.join(n.text or '' for n in celda.iter(f"{{{NS['m']}}}t"))
                            for celda in raiz.findall('m:si', NS)]
        hoja = ET.fromstring(libro.read('xl/worksheets/sheet1.xml'))
        tabla = []
        for fila in hoja.findall('.//m:sheetData/m:row', NS):
            valores = {}
            for celda in fila.findall('m:c', NS):
                indice = columna(celda.attrib['r'])
                tipo, valor = celda.attrib.get('t'), celda.find('m:v', NS)
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
    return [dict(zip(encabezados, fila + [''] * (len(encabezados) - len(fila)))) for fila in tabla[1:]]


def auditar(origen, salida=SALIDA):
    origen, salida = Path(origen), Path(salida)
    if not origen.is_absolute(): origen = RAIZ / origen
    incidencias_path, resumen_path, protocolo_path, manifest_path = (
        salida / 'incidencias.csv', salida / 'resumen.json', salida / 'protocolo.json', salida / 'manifest.json')
    if any(r.exists() for r in [incidencias_path, resumen_path, protocolo_path, manifest_path]):
        raise FileExistsError('No sobrescribir auditoría pre-2000 existente')
    filas = leer_primera_hoja(origen)
    requeridas = ['frag_id', 'fecha', 'anio', 'etiqueta', 'confianza', 'es_relevante', 'tipo_accion',
                  'instrumento', 'nota', 'frase_justificante', 'texto_original']
    if not filas or not set(requeridas) <= set(filas[0]):
        raise ValueError('Esquema pre-2000 inesperado')
    incidencias = []
    for fila in filas:
        identidad = fila['frag_id']
        faltantes = [campo for campo in requeridas if not fila[campo].strip()]
        if faltantes:
            incidencias.append({'frag_id': identidad, 'tipo': 'campo_vacio', 'detalle': '|'.join(faltantes)})
        if fila['etiqueta'] == 'pendiente':
            incidencias.append({'frag_id': identidad, 'tipo': 'pendiente_en_etiqueta',
                                'detalle': 'Separar estado_revision; etiqueta H/D/N o vacía mientras se resuelve.'})
        cita = ' '.join(fila['frase_justificante'].split())
        texto = ' '.join(fila['texto_original'].split())
        if cita and (cita not in texto or len(cita) > 300):
            incidencias.append({'frag_id': identidad, 'tipo': 'cita_no_literal_o_extensa',
                                'detalle': f'longitud={len(cita)};literal={cita in texto}'})
    por_texto = defaultdict(list)
    for fila in filas:
        por_texto[' '.join(fila['texto_original'].split())].append(fila['frag_id'])
    for ids in por_texto.values():
        if len(ids) > 1:
            for identidad in ids:
                incidencias.append({'frag_id': identidad, 'tipo': 'texto_duplicado_normalizado',
                                    'detalle': '|'.join(ids)})

    salida.mkdir(parents=True, exist_ok=True)
    with incidencias_path.open('x', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=['frag_id', 'tipo', 'detalle'], lineterminator='\n')
        escritor.writeheader(); escritor.writerows(incidencias)
    resumen = {
        'version': salida.name,
        'fecha_auditoria': '2026-09-17',
        'archivo': str(origen.relative_to(RAIZ)),
        'sha256_archivo': sha256(origen),
        'filas': len(filas),
        'ids_unicos': len({f['frag_id'] for f in filas}),
        'textos_normalizados_unicos': len(por_texto),
        'etiquetas': dict(Counter(f['etiqueta'] for f in filas)),
        'confianza': dict(Counter(f['confianza'] for f in filas)),
        'relevancia': dict(Counter(f['es_relevante'] for f in filas)),
        'anios': dict(Counter(f['anio'] for f in filas)),
        'incidencias': dict(Counter(i['tipo'] for i in incidencias)),
        'entrenamiento_ejecutado': False,
        'incorporacion_autorizada': False,
    }
    resumen_path.write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    protocolo_path.write_text(json.dumps({
        'alcance': 'Control estructural; no constituye adjudicación semántica completa.',
        'codebook_objetivo': 'docs/codebook_v3.md',
        'reglas': ['pendiente es estado, no clase', 'cita continua literal <=300',
                   'agrupar duplicados/reuniones antes de particionar', 'no entrenar hasta revisión v3 propia'],
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifest_path.write_text(json.dumps({'sha256_salidas': {
        'incidencias.csv': sha256(incidencias_path), 'resumen.json': sha256(resumen_path),
        'protocolo.json': sha256(protocolo_path)}}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return resumen


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origen', type=Path, default=Path('Set_Entrenamiento_Pre_2000.xlsx'))
    parser.add_argument('--salida', type=Path, default=SALIDA)
    args = parser.parse_args()
    print(json.dumps(auditar(args.origen, args.salida), ensure_ascii=False, indent=2))
