"""Prepara el inventario inmutable de revisión v3; no adjudica ni entrena."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / 'data/auditoria/migracion_v3'


def leer_csv(ruta):
    with Path(ruta).open(encoding='utf-8', newline='') as archivo:
        return list(csv.DictReader(archivo))


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write('\n')


def preparar(salida=SALIDA):
    salida = Path(salida)
    nombres = ['inventario.csv', 'resumen.json', 'protocolo.json', 'manifest.json']
    if any((salida / nombre).exists() for nombre in nombres):
        raise FileExistsError('No sobrescribir un inventario v3 existente')

    corpus_path = RAIZ / 'data/L0/corpus.csv'
    corpus = {fila['intervencion_id']: fila for fila in leer_csv(corpus_path)}
    registros = []
    fuentes = [corpus_path]

    archivos_base = sorted((RAIZ / 'data/etiquetas').glob('*.csv'))
    for ruta in archivos_base:
        fuentes.append(ruta)
        for fila in leer_csv(ruta):
            registros.append({
                'intervencion_id': fila['intervencion_id'],
                'coleccion': 'ia_base_v2',
                'lote': ruta.name,
                'archivo_origen': str(ruta.relative_to(RAIZ)),
                'etiqueta_origen': fila['etiqueta'],
                'es_relevante_origen': fila['es_relevante'],
            })

    archivos_nuevos = sorted((RAIZ / 'data/auditoria').glob('**/anotacion_ia_v1/tanda_*/anotaciones_ia.csv'))
    for ruta in archivos_nuevos:
        fuentes.append(ruta)
        for fila in leer_csv(ruta):
            registros.append({
                'intervencion_id': fila['intervencion_id'],
                'coleccion': 'ia_nueva_v1',
                'lote': ruta.parent.name,
                'archivo_origen': str(ruta.relative_to(RAIZ)),
                'etiqueta_origen': fila['etiqueta'],
                'es_relevante_origen': fila['es_relevante'],
            })

    humanos_path = RAIZ / 'data/evaluacion/tfidf_gold_v1/comparacion_gold.csv'
    fuentes.append(humanos_path)
    for fila in leer_csv(humanos_path):
        registros.append({
            'intervencion_id': fila['intervencion_id'],
            'coleccion': 'humana_v2',
            'lote': 'gold_humano_306',
            'archivo_origen': str(humanos_path.relative_to(RAIZ)),
            'etiqueta_origen': fila['etiqueta_humana'],
            'es_relevante_origen': fila['es_relevante_humano'],
        })

    referencias_path = RAIZ / 'data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv'
    fuentes.append(referencias_path)
    referencias = {fila['intervencion_id']: fila for fila in leer_csv(referencias_path)}
    for fila in registros:
        if fila['coleccion'] == 'ia_base_v2':
            referencia = referencias[fila['intervencion_id']]
            fila['etiqueta_previa_v3'] = referencia['etiqueta_corregida_v2']
            fila['es_relevante_previa_v3'] = referencia['es_relevante']
        else:
            fila['etiqueta_previa_v3'] = fila['etiqueta_origen']
            fila['es_relevante_previa_v3'] = fila['es_relevante_origen']

    ids = [fila['intervencion_id'] for fila in registros]
    if len(registros) != 1747 or len(set(ids)) != 1747:
        raise ValueError('El universo v3 debe contener 1.747 IDs distintos')
    if not set(ids) <= set(corpus):
        raise ValueError('Hay IDs de revisión que no existen en L0')

    revision_paths = sorted((RAIZ / 'data/auditoria').glob('revision_*_v3/revision*.csv'))
    revisados = {}
    for revision_path in revision_paths:
        fuentes.append(revision_path)
        for revision in leer_csv(revision_path):
            identidad = revision['intervencion_id']
            if identidad in revisados:
                raise ValueError(f'ID revisado en más de un lote v3: {identidad}')
            revisados[identidad] = revision
    if not revisados:
        raise ValueError('No hay lotes v3 revisados')

    for fila in registros:
        identidad = fila['intervencion_id']
        texto = corpus[identidad]['texto']
        previo = revisados.get(identidad)
        fila.update({
            'estado_revision_v3': 'revisado' if previo else 'pendiente',
            'etiqueta_v3': previo['etiqueta_v3'] if previo else '',
            'es_relevante_v3': previo['es_relevante_v3'] if previo else '',
            'confianza_revision_v3': previo['confianza_revision'] if previo else '',
            'sha256_texto': hashlib.sha256(texto.encode()).hexdigest(),
            'n_caracteres_texto': str(len(texto)),
        })

    orden = {'ia_base_v2': 0, 'ia_nueva_v1': 1, 'humana_v2': 2}
    registros.sort(key=lambda fila: (orden[fila['coleccion']], fila['lote'], fila['intervencion_id']))
    salida.mkdir(parents=True, exist_ok=True)
    columnas = list(registros[0])
    with (salida / 'inventario.csv').open('x', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, lineterminator='\n')
        escritor.writeheader()
        escritor.writerows(registros)

    por_coleccion = Counter(fila['coleccion'] for fila in registros)
    por_etiqueta = {coleccion: dict(Counter(fila['etiqueta_origen'] for fila in registros if fila['coleccion'] == coleccion))
                    for coleccion in por_coleccion}
    resumen = {
        'version': 'migracion_v3',
        'fecha_aprobacion_v3': '2026-09-17',
        'ids_totales': len(registros),
        'ids_unicos': len(set(ids)),
        'lotes_totales': len({(fila['coleccion'], fila['lote']) for fila in registros}),
        'por_coleccion': dict(por_coleccion),
        'por_etiqueta_origen': por_etiqueta,
        'revisados_iniciales': sum(fila['estado_revision_v3'] != 'pendiente' for fila in registros),
        'pendientes': sum(fila['estado_revision_v3'] == 'pendiente' for fila in registros),
        'respuestas_humanas_autorizadas_para_revision': True,
        'gold_humano_v3_sigue_siendo_ciego': False,
        'etiquetas_origen_sobrescritas': 0,
        'entrenamiento_ejecutado': False,
    }
    guardar_json(salida / 'resumen.json', resumen)
    protocolo = {
        'codebook': 'docs/codebook_v3.md',
        'unidad': 'ID único; intervención completa de L0',
        'orden_sugerido': ['cerrar 77 prioritarias', '17 rondas IA restantes', '4 tandas IA nuevas', '306 humanas'],
        'regla_correccion': 'Registrar etiqueta v3, relevancia, cita, fundamento, confianza y hash; nunca sobrescribir origen.',
        'control': 'Revisar H, D y N; incluir controles y familias, no solo errores del modelo.',
        'evaluacion': 'Separar cambio de referencia de cambio de supervisión; no reutilizar humana v3 como test ciego.',
        'fuentes_sha256': {str(ruta.relative_to(RAIZ)): sha256(ruta) for ruta in fuentes},
    }
    guardar_json(salida / 'protocolo.json', protocolo)
    guardar_json(salida / 'manifest.json', {
        'sha256_salidas': {nombre: sha256(salida / nombre) for nombre in nombres if nombre != 'manifest.json'}
    })
    return resumen


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, default=SALIDA)
    argumentos = parser.parse_args()
    print(json.dumps(preparar(argumentos.salida), ensure_ascii=False, indent=2))
