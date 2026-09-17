"""Registra un lote manual v3 contra v2 vigente; no decide etiquetas ni entrena."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def leer_csv(ruta):
    with Path(ruta).open(encoding='utf-8', newline='') as archivo:
        return list(csv.DictReader(archivo))


def sha(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write('\n')


def registrar(archivo, decisiones, salida, fuentes_adicionales=()):
    archivo, decisiones, salida = Path(archivo), Path(decisiones), Path(salida)
    if not archivo.is_absolute(): archivo = RAIZ / archivo
    if not decisiones.is_absolute(): decisiones = RAIZ / decisiones
    fuentes_adicionales = [Path(ruta) for ruta in fuentes_adicionales]
    fuentes_adicionales = [ruta if ruta.is_absolute() else RAIZ / ruta for ruta in fuentes_adicionales]
    if not salida.is_absolute(): salida = RAIZ / salida
    nombres = ['revision.csv', 'resumen.json', 'protocolo.json', 'verificacion.json', 'manifest.json']
    if any((salida / nombre).exists() for nombre in nombres):
        raise FileExistsError('No sobrescribir una revisión v3 existente')

    corpus_path = RAIZ / 'data/L0/corpus.csv'
    refs_path = RAIZ / 'data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv'
    codebook_path = RAIZ / 'docs/codebook_v3.md'
    corpus = {fila['intervencion_id']: fila for fila in leer_csv(corpus_path)}
    refs = {fila['intervencion_id']: fila for fila in leer_csv(refs_path)}
    manuales_lista = json.loads(decisiones.read_text(encoding='utf-8'))
    manuales = {fila['intervencion_id']: fila for fila in manuales_lista}
    if len(manuales) != len(manuales_lista):
        raise ValueError('Decisiones manuales con IDs duplicados')

    origen = leer_csv(archivo)
    ids_origen = {fila['intervencion_id'] for fila in origen}
    if not set(manuales) <= ids_origen:
        raise ValueError('Hay decisiones que no pertenecen al lote')
    filas = []
    for fila in origen:
        identidad = fila['intervencion_id']
        texto = corpus[identidad]['texto']
        texto_normalizado = ' '.join(texto.split())
        referencia = refs.get(identidad)
        v2 = referencia['etiqueta_corregida_v2'] if referencia else fila['etiqueta']
        relevancia_v2 = referencia['es_relevante'] if referencia else fila['es_relevante']
        manual = manuales.get(identidad)
        if manual:
            nueva = manual['etiqueta_v3']
            relevancia = str(manual.get('es_relevante_v3', relevancia_v2))
            confianza = manual['confianza_revision']
            cita = ' '.join(manual['cita'].split())
            fundamento = manual['fundamento']
        else:
            nueva, relevancia = v2, relevancia_v2
            confianza = fila['confianza']
            cita = ' '.join(fila['frase_justificante'].split())
            if nueva == 'neutral' and relevancia == '0':
                fundamento = f"Compatible con N/relevancia0: {fila['nota'] or 'formalidad sin contenido evaluable'}."
            elif nueva == 'neutral':
                fundamento = f"Compatible con N: {fila['nota'] or 'sin dirección respaldada'}. La unidad no adopta una dirección monetaria propia."
            else:
                fundamento = f"Compatible con {nueva}: {fila['nota'] or 'dirección respaldada en la unidad'}. No depende solo del menú o fase."
        if nueva not in {'hawkish', 'dovish', 'neutral'} or relevancia not in {'0', '1'}:
            raise ValueError(f'Etiqueta/relevancia inválida: {identidad}')
        if cita and (cita not in texto_normalizado or len(cita) > 300):
            raise ValueError(f'Cita inválida: {identidad}')
        cambio_etiqueta, cambio_relevancia = nueva != v2, relevancia != relevancia_v2
        if cambio_etiqueta and cambio_relevancia: resultado = 'cambio_etiqueta_y_relevancia'
        elif cambio_etiqueta: resultado = 'cambio_etiqueta'
        elif cambio_relevancia: resultado = 'cambio_relevancia'
        else: resultado = 'compatible'
        filas.append({
            'intervencion_id': identidad,
            'archivo_origen': str(archivo.relative_to(RAIZ)),
            'actor': corpus[identidad]['actor'],
            'etiqueta_ia_original': fila['etiqueta'],
            'es_relevante_ia_original': fila['es_relevante'],
            'etiqueta_v2_vigente': v2,
            'es_relevante_v2_vigente': relevancia_v2,
            'etiqueta_v3': nueva,
            'es_relevante_v3': relevancia,
            'resultado_revision': resultado,
            'confianza_revision': confianza,
            'cita_literal_espacios_normalizados': cita,
            'fundamento_revision': fundamento,
            'sha256_texto': hashlib.sha256(texto.encode()).hexdigest(),
            'n_caracteres_texto': len(texto),
        })

    salida.mkdir(parents=True, exist_ok=True)
    with (salida / 'revision.csv').open('x', encoding='utf-8', newline='') as archivo_salida:
        escritor = csv.DictWriter(archivo_salida, fieldnames=list(filas[0]), lineterminator='\n')
        escritor.writeheader(); escritor.writerows(filas)
    resumen = {
        'version': salida.name,
        'fecha': '2026-09-17',
        'archivo': str(archivo.relative_to(RAIZ)),
        'filas_revisadas': len(filas),
        'resultado': dict(Counter(fila['resultado_revision'] for fila in filas)),
        'transiciones_etiqueta': dict(Counter(f"{fila['etiqueta_v2_vigente']}->{fila['etiqueta_v3']}" for fila in filas if fila['etiqueta_v2_vigente'] != fila['etiqueta_v3'])),
        'transiciones_relevancia': dict(Counter(f"{fila['es_relevante_v2_vigente']}->{fila['es_relevante_v3']}" for fila in filas if fila['es_relevante_v2_vigente'] != fila['es_relevante_v3'])),
        'conteo_v2': dict(Counter(fila['etiqueta_v2_vigente'] for fila in filas)),
        'conteo_v3': dict(Counter(fila['etiqueta_v3'] for fila in filas)),
        'pendientes': 0,
        'originales_sobrescritos': 0,
        'entrenamiento': False,
    }
    guardar_json(salida / 'resumen.json', resumen)
    guardar_json(salida / 'protocolo.json', {
        'codebook': 'docs/codebook_v3.md',
        'alcance': f'Todas las filas de {archivo.name}; etiquetas visibles, revisión del agente, no segunda anotación ciega.',
        'decisiones_manuales': str(decisiones.relative_to(RAIZ)),
        'fuentes_sha256': {str(ruta.relative_to(RAIZ)): sha(ruta) for ruta in [corpus_path, archivo, refs_path, codebook_path, decisiones, *fuentes_adicionales]},
        'controles': ['IDs únicos', 'citas exactas tras normalizar espacios y <=300', 'hash por texto', 'sin sobrescribir fuentes'],
    })
    guardar_json(salida / 'verificacion.json', {
        'estado': 'verificado', 'filas': len(filas), 'ids_unicos': len({fila['intervencion_id'] for fila in filas}),
        'citas_validas': sum(not fila['cita_literal_espacios_normalizados'] or fila['cita_literal_espacios_normalizados'] in ' '.join(corpus[fila['intervencion_id']]['texto'].split()) for fila in filas),
        'hashes_validos': sum(fila['sha256_texto'] == hashlib.sha256(corpus[fila['intervencion_id']]['texto'].encode()).hexdigest() for fila in filas),
        'pendientes': 0,
    })
    guardar_json(salida / 'manifest.json', {'sha256_salidas': {nombre: sha(salida / nombre) for nombre in nombres if nombre != 'manifest.json'}})
    return resumen


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archivo', required=True, type=Path)
    parser.add_argument('--decisiones', required=True, type=Path)
    parser.add_argument('--salida', required=True, type=Path)
    parser.add_argument('--fuente-adicional', action='append', type=Path, default=[])
    args = parser.parse_args()
    print(json.dumps(registrar(args.archivo, args.decisiones, args.salida, args.fuente_adicional), ensure_ascii=False, indent=2))
