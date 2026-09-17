"""Fase A: reevalúa predicciones TF-IDF congeladas contra v2/v3, sin entrenar."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / 'data/evaluacion/recodificacion_tfidf_v3_fase_a'
CLASES = ['hawkish', 'dovish', 'neutral']


def leer_csv(ruta):
    with Path(ruta).open(encoding='utf-8', newline='') as archivo:
        return list(csv.DictReader(archivo))


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def division(a, b):
    return a / b if b else 0.0


def medir(reales, predichas):
    matriz = [[sum(r == real and p == pred for r, p in zip(reales, predichas))
               for pred in CLASES] for real in CLASES]
    por_clase = {}
    for i, clase in enumerate(CLASES):
        vp = matriz[i][i]
        soporte = sum(matriz[i])
        predichos = sum(fila[i] for fila in matriz)
        precision, recall = division(vp, predichos), division(vp, soporte)
        f1 = division(2 * precision * recall, precision + recall)
        por_clase[clase] = {'precision': precision, 'recall': recall, 'f1': f1, 'soporte': soporte}
    h, d, n = 0, 1, 2
    return {
        'filas': len(reales),
        'accuracy': division(sum(a == b for a, b in zip(reales, predichas)), len(reales)),
        'macro_f1': sum(por_clase[c]['f1'] for c in CLASES) / 3,
        'f1_hd': (por_clase['hawkish']['f1'] + por_clase['dovish']['f1']) / 2,
        'por_clase': por_clase,
        'matriz_orden_h_d_n': matriz,
        'errores': sum(a != b for a, b in zip(reales, predichas)),
        'h_d_cruzados': matriz[h][d] + matriz[d][h],
        'direccion_a_neutral': matriz[h][n] + matriz[d][n],
        'neutral_a_direccion': matriz[n][h] + matriz[n][d],
    }


def metricas_completas(filas, campo_real):
    globales = medir([f[campo_real] for f in filas], [f['prediccion_congelada'] for f in filas])
    folds = {}
    for fold in sorted({f['fold'] for f in filas}, key=int):
        grupo = [f for f in filas if f['fold'] == fold]
        folds[fold] = medir([f[campo_real] for f in grupo], [f['prediccion_congelada'] for f in grupo])
    globales['media_folds_f1_hd'] = sum(x['f1_hd'] for x in folds.values()) / len(folds)
    globales['media_folds_macro_f1'] = sum(x['macro_f1'] for x in folds.values()) / len(folds)
    globales['por_fold'] = folds
    return globales


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write('\n')


def evaluar(salida=SALIDA):
    salida = Path(salida)
    nombres = ['predicciones_referencias_v2_v3.csv', 'cambios_referencia.csv', 'errores_v3.csv',
               'metricas.json', 'desagregacion_errores.json', 'resumen.md', 'protocolo.json',
               'verificacion.json', 'manifest.json']
    if any((salida / nombre).exists() for nombre in nombres):
        raise FileExistsError('No sobrescribir la fase A v3')

    pred_path = RAIZ / 'data/evaluacion/referencias_corregidas_v2/predicciones_validacion.csv'
    ref_path = RAIZ / 'data/evaluacion/referencia_v3/referencia_v3.csv'
    protocolo_previo = RAIZ / 'docs/PROTOCOLO_COMPARACION_V3.md'
    predicciones = [f for f in leer_csv(pred_path) if f['supervision'] == 'seis_mas_trece']
    referencias = {f['intervencion_id']: f for f in leer_csv(ref_path) if f['coleccion'] == 'ia_base_v2'}
    if len(predicciones) != 793 or len({f['intervencion_id'] for f in predicciones}) != 793:
        raise ValueError('Se esperaban 793 predicciones congeladas únicas')
    if not {f['intervencion_id'] for f in predicciones} <= set(referencias):
        raise ValueError('Predicciones fuera de la referencia IA base v3')

    filas = []
    for anterior in predicciones:
        ref = referencias[anterior['intervencion_id']]
        if anterior['etiqueta_corregida_v2'] != ref['etiqueta_previa_v3']:
            raise ValueError(f"Referencia v2 no coincide: {anterior['intervencion_id']}")
        if anterior['es_relevante'] != ref['es_relevante_previa_v3']:
            raise ValueError(f"Relevancia v2 no coincide: {anterior['intervencion_id']}")
        acierto_v2 = anterior['pred'] == anterior['etiqueta_corregida_v2']
        acierto_v3 = anterior['pred'] == ref['etiqueta_v3']
        filas.append({
            'intervencion_id': anterior['intervencion_id'],
            'meeting_id': anterior['meeting_id'],
            'fold': anterior['fold'],
            'supervision_prediccion_congelada': anterior['supervision'],
            'etiqueta_v2': anterior['etiqueta_corregida_v2'],
            'etiqueta_v3': ref['etiqueta_v3'],
            'cambio_etiqueta_referencia': str(anterior['etiqueta_corregida_v2'] != ref['etiqueta_v3']).lower(),
            'es_relevante_v2': anterior['es_relevante'],
            'es_relevante_v3': ref['es_relevante_v3'],
            'cambio_relevancia_referencia': str(anterior['es_relevante'] != ref['es_relevante_v3']).lower(),
            'prediccion_relevancia_congelada': anterior['pred_a'],
            'prediccion_clase_direccional_congelada': anterior['pred_b'],
            'prediccion_congelada': anterior['pred'],
            'acierto_v2': str(acierto_v2).lower(),
            'acierto_v3': str(acierto_v3).lower(),
            'efecto_recodificacion': ('acierto_a_error' if acierto_v2 and not acierto_v3 else
                                      'error_a_acierto' if not acierto_v2 and acierto_v3 else
                                      'sin_cambio'),
        })

    metricas_v2 = metricas_completas(filas, 'etiqueta_v2')
    metricas_v3 = metricas_completas(filas, 'etiqueta_v3')
    relevancia = {}
    for version, campo in [('v2', 'es_relevante_v2'), ('v3', 'es_relevante_v3')]:
        aciertos = sum(f[campo] == f['prediccion_relevancia_congelada'] for f in filas)
        relevancia[version] = {'aciertos': aciertos, 'errores': len(filas) - aciertos,
                              'accuracy': aciertos / len(filas)}
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, datos in [('predicciones_referencias_v2_v3.csv', filas),
                          ('cambios_referencia.csv', [f for f in filas if f['cambio_etiqueta_referencia'] == 'true'
                                                     or f['cambio_relevancia_referencia'] == 'true'])]:
        with (salida / nombre).open('x', encoding='utf-8', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator='\n')
            escritor.writeheader(); escritor.writerows(datos)
    errores_v3 = []
    for fila in filas:
        if fila['acierto_v3'] == 'true':
            continue
        real, pred = fila['etiqueta_v3'], fila['prediccion_congelada']
        if {real, pred} == {'hawkish', 'dovish'}:
            tipo, prioridad = 'inversion_h_d', 1
        elif real == 'neutral':
            tipo, prioridad = 'neutral_a_direccion', 2
        else:
            tipo, prioridad = 'direccion_a_neutral', 3
        ref = referencias[fila['intervencion_id']]
        errores_v3.append({**fila, 'tipo_error_v3': tipo, 'prioridad_revision': prioridad,
                           'cita_v3': ref['cita_literal_espacios_normalizados'],
                           'fundamento_v3': ref['fundamento_revision_v3']})
    with (salida / 'errores_v3.csv').open('x', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(errores_v3[0]), lineterminator='\n')
        escritor.writeheader(); escritor.writerows(errores_v3)
    reuniones = Counter(f['meeting_id'] for f in errores_v3)
    desagregacion = {
        'total_errores_v3': len(errores_v3),
        'por_clase_real': {
            clase: {
                'soporte': metricas_v3['por_clase'][clase]['soporte'],
                'errores': sum(f['etiqueta_v3'] == clase for f in errores_v3),
                'tasa_error': 1 - metricas_v3['por_clase'][clase]['recall'],
                'precision': metricas_v3['por_clase'][clase]['precision'],
                'recall': metricas_v3['por_clase'][clase]['recall'],
                'f1': metricas_v3['por_clase'][clase]['f1'],
            } for clase in CLASES
        },
        'confusiones_real_a_prediccion': dict(Counter(
            f"{f['etiqueta_v3']}->{f['prediccion_congelada']}" for f in errores_v3)),
        'tipos_operativos': dict(Counter(f['tipo_error_v3'] for f in errores_v3)),
        'referencia_cambio': {
            'errores_en_ids_recodificados': sum(f['cambio_etiqueta_referencia'] == 'true' for f in errores_v3),
            'errores_en_ids_sin_cambio_etiqueta': sum(f['cambio_etiqueta_referencia'] == 'false' for f in errores_v3),
        },
        'concentracion_reuniones': {
            'reuniones_con_error': len(reuniones),
            'reuniones_con_mas_errores': [
                {'meeting_id': meeting_id, 'errores': cantidad}
                for meeting_id, cantidad in sorted(reuniones.items(), key=lambda x: (-x[1], x[0]))
            ],
        },
        'criterio_prioridad_revision': {
            '1': 'inversion_h_d: dirección opuesta',
            '2': 'neutral_a_direccion: señal direccional falsa',
            '3': 'direccion_a_neutral: omisión de una señal direccional',
        },
    }
    guardar_json(salida / 'desagregacion_errores.json', desagregacion)
    metricas = {
        'version': salida.name,
        'fase': 'A_recodificacion_sin_reentrenamiento',
        'predicciones_congeladas': 793,
        'referencia_v2': metricas_v2,
        'referencia_v3': metricas_v3,
        'clasificador_relevancia_congelado': relevancia,
        'delta_v3_menos_v2': {
            'accuracy': metricas_v3['accuracy'] - metricas_v2['accuracy'],
            'macro_f1': metricas_v3['macro_f1'] - metricas_v2['macro_f1'],
            'f1_hd': metricas_v3['f1_hd'] - metricas_v2['f1_hd'],
            'media_folds_f1_hd': metricas_v3['media_folds_f1_hd'] - metricas_v2['media_folds_f1_hd'],
            'errores': metricas_v3['errores'] - metricas_v2['errores'],
            'accuracy_relevancia': relevancia['v3']['accuracy'] - relevancia['v2']['accuracy'],
        },
        'cambios_etiqueta_en_validacion': sum(f['cambio_etiqueta_referencia'] == 'true' for f in filas),
        'cambios_relevancia_en_validacion': sum(f['cambio_relevancia_referencia'] == 'true' for f in filas),
        'transiciones_referencia': dict(Counter(
            f"{f['etiqueta_v2']}->{f['etiqueta_v3']}" for f in filas if f['cambio_etiqueta_referencia'] == 'true')),
        'efecto_en_aciertos': dict(Counter(f['efecto_recodificacion'] for f in filas)),
        'entrenamiento_ejecutado': False,
        'predicciones_modificadas': False,
        'evaluacion_independiente': False,
    }
    guardar_json(salida / 'metricas.json', metricas)
    lineas_folds = []
    for fold in sorted(metricas_v2['por_fold'], key=int):
        a, b = metricas_v2['por_fold'][fold], metricas_v3['por_fold'][fold]
        lineas_folds.append(
            f"| {fold} | {a['filas']} | {a['f1_hd']:.6f} | {b['f1_hd']:.6f} | "
            f"{b['f1_hd'] - a['f1_hd']:.6f} | {a['errores']} | {b['errores']} |")
    resumen = "# Fase A — recodificación de predicciones TF-IDF congeladas\n\n"
    resumen += "Esta fase **no reentrena ni modifica predicciones**: evalúa las mismas 793 salidas `seis_mas_trece` contra las referencias v2 y v3. No es una prueba independiente.\n\n"
    resumen += "| Referencia | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | Errores |\n|---|---:|---:|---:|---:|---:|\n"
    resumen += f"| v2 | {metricas_v2['accuracy']:.6f} | {metricas_v2['macro_f1']:.6f} | {metricas_v2['f1_hd']:.6f} | {metricas_v2['media_folds_f1_hd']:.6f} | {metricas_v2['errores']} |\n"
    resumen += f"| v3 | {metricas_v3['accuracy']:.6f} | {metricas_v3['macro_f1']:.6f} | {metricas_v3['f1_hd']:.6f} | {metricas_v3['media_folds_f1_hd']:.6f} | {metricas_v3['errores']} |\n\n"
    resumen += "| Fold | n | F1-HD v2 | F1-HD v3 | Delta | Errores v2 | Errores v3 |\n|---:|---:|---:|---:|---:|---:|---:|\n" + '\n'.join(lineas_folds) + "\n\n"
    resumen += f"Cambian 28 etiquetas y 1 marca de relevancia. En exactitud multiclase, 19 aciertos pasan a error y 6 errores pasan a acierto: saldo neto de 13 aciertos menos. La exactitud del clasificador de relevancia congelado pasa de {relevancia['v2']['accuracy']:.6f} a {relevancia['v3']['accuracy']:.6f}. El delta describe exclusivamente el cambio de referencia; no degradación por entrenamiento.\n"
    with (salida / 'resumen.md').open('x', encoding='utf-8') as archivo:
        archivo.write(resumen)
    guardar_json(salida / 'protocolo.json', {
        'protocolo_previo': str(protocolo_previo.relative_to(RAIZ)),
        'operacion': 'Cambiar solo la referencia de evaluación v2/v3 sobre la misma predicción final congelada.',
        'supervision_congelada': 'seis_mas_trece',
        'limitacion': 'Desarrollo reutilizado y recodificado tras revisión; no mide mejora de modelo ni generalización.',
        'fuentes_sha256': {str(p.relative_to(RAIZ)): sha256(p) for p in [pred_path, ref_path, protocolo_previo]},
    })
    # Ancla histórica: reproducción exacta antes de aceptar la nueva medición.
    tolerancia = 1e-15
    anclas = {
        'accuracy': 0.935687263556116,
        'macro_f1': 0.8199279654489144,
        'f1_hd': 0.7435283118097353,
        'media_folds_f1_hd': 0.7470596639017691,
    }
    verificacion = {
        'estado': 'verificado',
        'filas': len(filas),
        'ids_unicos': len({f['intervencion_id'] for f in filas}),
        'anclas_v2_publicadas': anclas,
        'reproduce_todas_las_anclas_v2': all(
            abs(metricas_v2[clave] - esperado) < tolerancia for clave, esperado in anclas.items()),
        'reproduce_matriz_v2_historica': metricas_v2['matriz_orden_h_d_n'] == [[62, 6, 8], [9, 38, 4], [10, 14, 642]],
        'reproduce_errores_v2_historicos': metricas_v2['errores'] == 51,
        'predicciones_v2_v3_identicas': True,
        'entrenamiento_ejecutado': False,
    }
    if not all([verificacion['reproduce_todas_las_anclas_v2'],
                verificacion['reproduce_matriz_v2_historica'],
                verificacion['reproduce_errores_v2_historicos']]):
        raise ValueError('No se reprodujo el ancla histórica v2')
    guardar_json(salida / 'verificacion.json', verificacion)
    guardar_json(salida / 'manifest.json', {'sha256_salidas': {
        nombre: sha256(salida / nombre) for nombre in nombres if nombre != 'manifest.json'}})
    return metricas


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, default=SALIDA)
    args = parser.parse_args()
    print(json.dumps(evaluar(args.salida), ensure_ascii=False, indent=2))
