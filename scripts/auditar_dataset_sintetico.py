"""Audita estructura, duplicación, citas y trazabilidad del set sintético sin entrenar."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ/'Dataset_Sintetico_Post2020.csv'
SALIDA = RAIZ/'data/auditoria/dataset_sintetico_post2020_v1'
CLASES = {'Hawkish':'hawkish', 'Dovish':'dovish', 'Neutral':'neutral'}
# Muestra sistemática leída contra v3: diez textos únicos por clase, cubre ambos lotes.
MUESTRA_COMPATIBLE = {
    'SYNTH_00001','SYNTH_00128','SYNTH_00241','SYNTH_00320','SYNTH_00420',
    'SYNTH_00516','SYNTH_00588','SYNTH_00711','SYNTH_00834','SYNTH_01013',
    'SYNTH_00003','SYNTH_00109','SYNTH_00189','SYNTH_00290','SYNTH_00390',
    'SYNTH_00505','SYNTH_00621','SYNTH_00747','SYNTH_00870','SYNTH_01017',
    'SYNTH_00004','SYNTH_00136','SYNTH_00209','SYNTH_00314','SYNTH_00405',
    'SYNTH_00532','SYNTH_00627','SYNTH_00724','SYNTH_00851','SYNTH_01009',
}


def norm(texto):
    return ' '.join(texto.split())


def clave(texto):
    return norm(texto).lower()


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write('\n')


def auditar(origen=ORIGEN, salida=SALIDA):
    origen, salida = Path(origen), Path(salida)
    nombres = ['inventario.csv', 'incidencias.csv', 'candidatos_texto_unico.csv',
               'muestra_semantica_inicial.csv', 'resumen.json', 'protocolo.json', 'manifest.json']
    if salida.exists():
        raise FileExistsError('No sobrescribir auditoría sintética')
    with origen.open(encoding='utf-8-sig', newline='') as archivo:
        filas = list(csv.DictReader(archivo))
    corpus_path = RAIZ/'data/L0/corpus.csv'
    with corpus_path.open(encoding='utf-8', newline='') as archivo:
        corpus_real = list(csv.DictReader(archivo))
    columnas = ['frag_id','fecha_ficticia','clase','tema','texto','cita_textual','justificacion']
    if not filas or list(filas[0]) != columnas:
        raise ValueError('Esquema sintético inesperado')
    textos = defaultdict(list)
    citas = defaultdict(list)
    temas = defaultdict(list)
    fechas = defaultdict(list)
    frecuencia_oraciones = Counter()
    for fila in filas:
        textos[clave(fila['texto'])].append(fila['frag_id'])
        citas[clave(fila['cita_textual'])].append(fila['frag_id'])
        temas[clave(fila['tema'])].append(fila['frag_id'])
        fechas[fila['fecha_ficticia']].append(fila['frag_id'])
        for oracion in re.split(r'(?<=[.!?])\s+', norm(fila['texto'])):
            if len(oracion) >= 80:
                frecuencia_oraciones[clave(oracion)] += 1
    etiqueta_por_id = {f['frag_id']: f['clase'] for f in filas}
    grupo_texto = {identificador: hashlib.sha256(k.encode()).hexdigest()[:16]
                   for k, ids in textos.items() for identificador in ids}
    primera = {ids[0] for ids in textos.values()}
    inventario, incidencias, candidatos = [], [], []
    for i, fila in enumerate(filas, 1):
        cita_exacta = norm(fila['cita_textual']) in norm(fila['texto'])
        cita_sin_caso = clave(fila['cita_textual']) in clave(fila['texto'])
        oraciones = [clave(x) for x in re.split(r'(?<=[.!?])\s+', norm(fila['texto'])) if len(x) >= 80]
        repetidas = [frecuencia_oraciones[x] for x in oraciones if frecuencia_oraciones[x] > 1]
        ids_duplicados = textos[clave(fila['texto'])]
        registro = {
            'frag_id': fila['frag_id'], 'fecha_ficticia': fila['fecha_ficticia'],
            'clase_origen': fila['clase'], 'etiqueta_normalizada': CLASES.get(fila['clase'], ''),
            'tema': fila['tema'], 'lote_inferido': '1_517' if i <= 517 else '518_1018',
            'sha256_texto': hashlib.sha256(fila['texto'].encode()).hexdigest(),
            'grupo_texto_normalizado': grupo_texto[fila['frag_id']],
            'texto_duplicado_exacto_normalizado': str(len(ids_duplicados) > 1).lower(),
            'n_repeticiones_texto': len(ids_duplicados),
            'es_representante_texto_unico': str(fila['frag_id'] in primera).lower(),
            'cita_literal_espacios_normalizados': str(cita_exacta).lower(),
            'cita_coincide_solo_ignorando_mayusculas': str(not cita_exacta and cita_sin_caso).lower(),
            'n_oraciones_largas_repetidas': len(repetidas),
            'max_frecuencia_oracion_larga': max(repetidas, default=1),
            'contiene_caracter_no_ascii': str(any(ord(c)>127 for c in fila['texto'])).lower(),
            'n_caracteres_texto': len(fila['texto']), 'n_caracteres_cita': len(fila['cita_textual']),
        }
        inventario.append(registro)
        if len(ids_duplicados) > 1:
            incidencias.append({'frag_id':fila['frag_id'], 'tipo':'texto_duplicado_normalizado',
                                'detalle':','.join(ids_duplicados)})
        if not cita_exacta:
            incidencias.append({'frag_id':fila['frag_id'], 'tipo':'cita_no_literal_exacta',
                                'detalle':'coincide_sin_caso' if cita_sin_caso else 'no_es_subcadena_continua'})
        if repetidas:
            incidencias.append({'frag_id':fila['frag_id'], 'tipo':'oracion_larga_reutilizada',
                                'detalle':f'max_frecuencia={max(repetidas)}'})
        if fila['frag_id'] in primera:
            candidatos.append({
                'synthetic_id': fila['frag_id'], 'fecha_ficticia': fila['fecha_ficticia'],
                'etiqueta_provisional': CLASES.get(fila['clase'], ''), 'familia_provisional': fila['tema'],
                'texto': fila['texto'], 'cita_textual_origen': fila['cita_textual'],
                'justificacion_origen': fila['justificacion'], 'grupo_texto_normalizado': grupo_texto[fila['frag_id']],
                'estado_revision_v3': 'pendiente', 'autorizado_entrenamiento': 'no',
            })
    muestra = [{
        'frag_id': f['frag_id'], 'clase_origen': f['clase'], 'tema': f['tema'],
        'texto': f['texto'], 'cita_textual': f['cita_textual'],
        'resultado_revision_v3': 'compatible_provisional',
        'nota_revision': 'Dirección respaldada o neutralidad resolutiva coherente con codebook v3.',
    } for f in filas if f['frag_id'] in MUESTRA_COMPATIBLE]
    if len(muestra) != 30 or Counter(f['clase_origen'] for f in muestra) != Counter({'Hawkish':10,'Dovish':10,'Neutral':10}):
        raise ValueError('Muestra semántica inicial incompleta')
    salida.mkdir(parents=True)
    for nombre, datos in [('inventario.csv', inventario), ('incidencias.csv', incidencias),
                          ('candidatos_texto_unico.csv', candidatos),
                          ('muestra_semantica_inicial.csv', muestra)]:
        with (salida/nombre).open('x', encoding='utf-8', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(datos[0]), lineterminator='\n')
            escritor.writeheader(); escritor.writerows(datos)
    grupos_dup = [ids for ids in textos.values() if len(ids)>1]
    textos_reales = {clave(f['texto']) for f in corpus_real}
    oraciones_reales = {
        clave(oracion) for fila in corpus_real
        for oracion in re.split(r'(?<=[.!?])\s+', norm(fila['texto'])) if len(oracion) >= 80
    }
    resumen = {
        'filas': len(filas), 'ids_unicos': len({f['frag_id'] for f in filas}),
        'textos_normalizados_unicos': len(textos),
        'distribucion_clases': dict(Counter(f['clase'] for f in filas)),
        'distribucion_candidatos_unicos': dict(Counter(
            etiqueta_por_id[f['frag_id']] for f in filas if f['frag_id'] in primera)),
        'grupos_texto_duplicado': len(grupos_dup),
        'filas_en_grupos_duplicados': sum(len(x) for x in grupos_dup),
        'copias_excedentes': sum(len(x)-1 for x in grupos_dup),
        'duplicados_con_etiquetas_conflictivas': sum(
            len({etiqueta_por_id[x] for x in ids})>1 for ids in grupos_dup),
        'citas_literal_exacta': sum(x['cita_literal_espacios_normalizados']=='true' for x in inventario),
        'citas_solo_diferencia_mayusculas': sum(x['cita_coincide_solo_ignorando_mayusculas']=='true' for x in inventario),
        'citas_no_subcadena_continua': sum(not (norm(f['cita_textual']) in norm(f['texto']) or
                                                clave(f['cita_textual']) in clave(f['texto'])) for f in filas),
        'filas_con_oracion_larga_reutilizada': sum(x['n_oraciones_largas_repetidas']>0 for x in inventario),
        'oraciones_largas_reutilizadas_unicas': sum(v>1 for v in frecuencia_oraciones.values()),
        'temas_unicos': len(temas), 'temas_con_mas_de_una_clase': sum(
            len({etiqueta_por_id[x] for x in ids})>1 for ids in temas.values()),
        'fechas_ficticias_unicas': len(fechas),
        'solapamiento_corpus_real': {
            'textos_normalizados_exactos': len(set(textos) & textos_reales),
            'oraciones_largas_exactas': sum(oracion in oraciones_reales for oracion in frecuencia_oraciones),
        },
        'lotes_inferidos': {
            '1_517': {'filas':517, 'con_caracter_no_ascii':sum(x['contiene_caracter_no_ascii']=='true' for x in inventario[:517])},
            '518_1018': {'filas':501, 'con_caracter_no_ascii':sum(x['contiene_caracter_no_ascii']=='true' for x in inventario[517:])},
        },
        'muestra_semantica_inicial': {'filas':30, 'por_clase':{'Hawkish':10,'Dovish':10,'Neutral':10},
                                     'compatibles_provisionales':30},
        'metadatos_ausentes': ['generador','version_prompt','semilla','familia_plantilla_explicita'],
        'incorporacion_autorizada': False,
        'motivo': 'Requiere deduplicación, agrupación de familias y revisión semántica v3 antes de cualquier curva de dosis.',
        'entrenamiento_ejecutado': False,
    }
    guardar_json(salida/'resumen.json', resumen)
    guardar_json(salida/'protocolo.json', {
        'origen': str(origen.relative_to(RAIZ)), 'sha256_origen': sha256(origen),
        'corpus_real': str(corpus_path.relative_to(RAIZ)), 'sha256_corpus_real': sha256(corpus_path),
        'operacion': 'Auditoría de solo lectura; no corrige, etiqueta ni entrena.',
        'criterio_cita': 'Subcadena continua tras normalizar solo espacios; conserva mayúsculas y puntuación.',
        'seleccion_candidato': 'Primera fila por texto normalizado; etiqueta aún provisional.',
    })
    guardar_json(salida/'manifest.json', {'sha256_salidas': {
        nombre: sha256(salida/nombre) for nombre in nombres if nombre != 'manifest.json'}})
    return resumen


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origen', type=Path, default=ORIGEN)
    parser.add_argument('--salida', type=Path, default=SALIDA)
    args = parser.parse_args()
    print(json.dumps(auditar(args.origen, args.salida), ensure_ascii=False, indent=2))
