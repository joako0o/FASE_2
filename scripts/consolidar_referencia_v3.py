"""Consolida la capa auditada v3 sin entrenar ni modificar fuentes históricas."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / 'data/evaluacion/referencia_v3'


def leer_csv(ruta):
    with Path(ruta).open(encoding='utf-8', newline='') as archivo:
        return list(csv.DictReader(archivo))


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write('\n')


def consolidar(salida=SALIDA):
    salida = Path(salida)
    nombres = ['referencia_v3.csv', 'resumen.json', 'protocolo.json', 'manifest.json']
    if any((salida / nombre).exists() for nombre in nombres):
        raise FileExistsError('No sobrescribir una referencia v3 consolidada')

    inventario_path = RAIZ / 'data/auditoria/migracion_v3/inventario.csv'
    codebook_path = RAIZ / 'docs/codebook_v3.md'
    inventario = leer_csv(inventario_path)
    revisiones = {}
    rutas_revision = sorted((RAIZ / 'data/auditoria').glob('revision_*_v3/revision*.csv'))
    for ruta in rutas_revision:
        for fila in leer_csv(ruta):
            identidad = fila['intervencion_id']
            if identidad in revisiones:
                raise ValueError(f'ID repetido entre revisiones v3: {identidad}')
            revisiones[identidad] = (ruta, fila)

    ids_inventario = {fila['intervencion_id'] for fila in inventario}
    if len(inventario) != 1747 or len(ids_inventario) != 1747:
        raise ValueError('El inventario debe contener 1.747 IDs únicos')
    if set(revisiones) != ids_inventario:
        raise ValueError('La consolidación exige cobertura exacta de las 1.747 revisiones')

    roles = {
        'ia_base_v2': ('desarrollo_base_v3', 'si', 'supervision_oof_control_primario'),
        'ia_nueva_v1': ('ampliacion_ia_v3', 'no', 'evaluar_adicion_por_separado'),
        'humana_v2': ('referencia_humana_v3_no_ciega', 'no', 'evaluacion_descriptiva_no_independiente'),
    }
    consolidadas = []
    for base in inventario:
        identidad = base['intervencion_id']
        ruta_revision, revision = revisiones[identidad]
        rol, control, uso = roles[base['coleccion']]
        if revision['etiqueta_v3'] != base['etiqueta_v3'] or revision['es_relevante_v3'] != base['es_relevante_v3']:
            raise ValueError(f'Inventario y revisión discrepan: {identidad}')
        consolidadas.append({
            'intervencion_id': identidad,
            'coleccion': base['coleccion'],
            'lote': base['lote'],
            'archivo_origen': base['archivo_origen'],
            'archivo_revision_v3': str(ruta_revision.relative_to(RAIZ)),
            'etiqueta_origen': base['etiqueta_origen'],
            'es_relevante_origen': base['es_relevante_origen'],
            'etiqueta_previa_v3': base['etiqueta_previa_v3'],
            'es_relevante_previa_v3': base['es_relevante_previa_v3'],
            'etiqueta_v3': revision['etiqueta_v3'],
            'es_relevante_v3': revision['es_relevante_v3'],
            'resultado_revision': revision['resultado_revision'],
            'confianza_revision_v3': revision['confianza_revision'],
            'cita_literal_espacios_normalizados': revision['cita_literal_espacios_normalizados'],
            'fundamento_revision_v3': revision['fundamento_revision'],
            'estado_revision_v3': 'revisado',
            'sha256_texto': revision['sha256_texto'],
            'n_caracteres_texto': revision['n_caracteres_texto'],
            'rol_recomendado': rol,
            'incluir_control_primario': control,
            'uso_recomendado': uso,
        })

    orden = {'ia_base_v2': 0, 'ia_nueva_v1': 1, 'humana_v2': 2}
    consolidadas.sort(key=lambda f: (orden[f['coleccion']], f['lote'], f['intervencion_id']))
    salida.mkdir(parents=True, exist_ok=True)
    with (salida / 'referencia_v3.csv').open('x', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(consolidadas[0]), lineterminator='\n')
        escritor.writeheader()
        escritor.writerows(consolidadas)

    por_coleccion = defaultdict(list)
    for fila in consolidadas:
        por_coleccion[fila['coleccion']].append(fila)
    resumen_colecciones = {}
    for coleccion, filas in por_coleccion.items():
        resumen_colecciones[coleccion] = {
            'filas': len(filas),
            'etiquetas_v3': dict(Counter(f['etiqueta_v3'] for f in filas)),
            'relevancia_v3': dict(Counter(f['es_relevante_v3'] for f in filas)),
            'resultados_revision': dict(Counter(f['resultado_revision'] for f in filas)),
        }
    resumen = {
        'version': 'referencia_v3',
        'fecha': '2026-09-17',
        'filas': len(consolidadas),
        'ids_unicos': len({f['intervencion_id'] for f in consolidadas}),
        'pendientes': 0,
        'etiquetas_v3': dict(Counter(f['etiqueta_v3'] for f in consolidadas)),
        'relevancia_v3': dict(Counter(f['es_relevante_v3'] for f in consolidadas)),
        'por_coleccion': resumen_colecciones,
        'control_primario_ids': sum(f['incluir_control_primario'] == 'si' for f in consolidadas),
        'entrenamiento_ejecutado': False,
        'referencia_humana_v3_es_test_ciego': False,
    }
    guardar_json(salida / 'resumen.json', resumen)
    fuentes = [inventario_path, codebook_path, *rutas_revision]
    guardar_json(salida / 'protocolo.json', {
        'codebook': 'docs/codebook_v3.md',
        'objetivo': 'Vista única trazable de las 1.747 decisiones v3; no entrena ni puntúa modelos.',
        'control_primario': 'Reproducir primero los mismos 1.352 IDs IA base, folds y parámetros; no añadir las 89 IA nuevas en esa comparación.',
        'recodificacion': 'Puntuar predicciones históricas congeladas contra v2 y v3 antes de reentrenar.',
        'supervision': 'Después reentrenar el mismo TF-IDF con v3, manteniendo folds, A y parámetros, para separar el efecto de supervisión.',
        'ia_nueva': 'Evaluar las 89 IA nuevas como adición separada posterior al control primario.',
        'humana': 'Las 306 humanas v3 solo permiten evaluación descriptiva no independiente; fueron abiertas y revisadas.',
        'plan_b_pre_2000': 'Excluir del control hasta terminar auditoría v3 propia, reparar citas, separar estado pendiente y fijar agrupación/procedencia.',
        'fuentes_sha256': {str(ruta.relative_to(RAIZ)): sha256(ruta) for ruta in fuentes},
    })
    guardar_json(salida / 'manifest.json', {
        'sha256_salidas': {nombre: sha256(salida / nombre) for nombre in nombres if nombre != 'manifest.json'}
    })
    return resumen


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, default=SALIDA)
    args = parser.parse_args()
    print(json.dumps(consolidar(args.salida), ensure_ascii=False, indent=2))
