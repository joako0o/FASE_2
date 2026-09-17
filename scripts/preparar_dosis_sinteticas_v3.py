"""Deduplica y fija dosis sintéticas anidadas/diversas; no entrena modelos."""
import argparse
from collections import Counter, defaultdict, deque
import csv
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ/'Dataset_Sintetico_Post2020.csv'
AUDITORIA = RAIZ/'data/auditoria/dataset_sintetico_post2020_v1'
SALIDA = RAIZ/'data/preparacion/dosis_sinteticas_post2020_v1'
DOSIS = {
    250: {'hawkish':83, 'dovish':84, 'neutral':83},
    500: {'hawkish':167, 'dovish':167, 'neutral':166},
    750: {'hawkish':254, 'dovish':254, 'neutral':242},
    801: {'hawkish':274, 'dovish':285, 'neutral':242},
}
CLASES = {'Hawkish':'hawkish', 'Dovish':'dovish', 'Neutral':'neutral'}
SEMILLA = 'sinteticos-v3-20260917'


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def hash_orden(valor):
    return hashlib.sha256((SEMILLA+'|'+valor).encode()).hexdigest()


def guardar_json(ruta, datos):
    with Path(ruta).open('x', encoding='utf-8') as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
        archivo.write('\n')


def ordenar_diverso(filas):
    """Alterna lotes y recorre familias antes de repetir una familia."""
    por_lote = defaultdict(lambda: defaultdict(list))
    for fila in filas:
        por_lote[fila['lote_inferido']][fila['familia_provisional']].append(fila)
    secuencias = {}
    for lote, familias in por_lote.items():
        orden_familias = sorted(familias, key=hash_orden)
        for familia in familias:
            familias[familia].sort(key=lambda x: hash_orden(x['synthetic_id']))
        secuencia = []
        profundidad = 0
        while True:
            nuevos = [familias[f][profundidad] for f in orden_familias if profundidad < len(familias[f])]
            if not nuevos:
                break
            secuencia.extend(nuevos)
            profundidad += 1
        secuencias[lote] = deque(secuencia)
    lotes = sorted(secuencias, key=hash_orden)
    salida = []
    while any(secuencias[l] for l in lotes):
        for lote in lotes:
            if secuencias[lote]:
                salida.append(secuencias[lote].popleft())
    return salida


def preparar(salida=SALIDA):
    salida = Path(salida)
    nombres = ['pool_sintetico_deduplicado.csv','plan_dosis.csv','resumen.json','protocolo.json','manifest.json']
    if salida.exists():
        raise FileExistsError('No sobrescribir preparación sintética')
    resumen_auditoria = json.loads((AUDITORIA/'resumen.json').read_text(encoding='utf-8'))
    manifiesto = json.loads((AUDITORIA/'manifest.json').read_text(encoding='utf-8'))
    for nombre, esperado in manifiesto['sha256_salidas'].items():
        if sha256(AUDITORIA/nombre) != esperado:
            raise ValueError('Auditoría alterada: '+nombre)
    with (AUDITORIA/'candidatos_texto_unico.csv').open(encoding='utf-8', newline='') as archivo:
        candidatos = list(csv.DictReader(archivo))
    with (AUDITORIA/'inventario.csv').open(encoding='utf-8', newline='') as archivo:
        inventario = {f['frag_id']: f for f in csv.DictReader(archivo)}
    if len(candidatos) != 801 or resumen_auditoria['incorporacion_autorizada']:
        raise ValueError('Se esperaba pool provisional de 801, aún no autorizado como referencia')
    por_clase = defaultdict(list)
    for fila in candidatos:
        fila = dict(fila)
        fila['lote_inferido'] = inventario[fila['synthetic_id']]['lote_inferido']
        fila['cita_literal'] = inventario[fila['synthetic_id']]['cita_literal_espacios_normalizados']
        por_clase[fila['etiqueta_provisional']].append(fila)
    ordenados = {clase: ordenar_diverso(filas) for clase, filas in por_clase.items()}
    if {k:len(v) for k,v in ordenados.items()} != {'hawkish':274,'dovish':285,'neutral':242}:
        raise ValueError('Distribución deduplicada distinta')
    pool = []
    for clase in ['hawkish','dovish','neutral']:
        for rango, fila in enumerate(ordenados[clase], 1):
            dosis_minima = next(d for d in DOSIS if rango <= DOSIS[d][clase])
            pool.append({**fila, 'rango_en_clase':rango, 'dosis_minima':dosis_minima})
    pool.sort(key=lambda x: x['synthetic_id'])
    planes = []
    for dosis, cuotas in DOSIS.items():
        seleccion = [f for f in pool if int(f['rango_en_clase']) <= cuotas[f['etiqueta_provisional']]]
        conteos = Counter(f['etiqueta_provisional'] for f in seleccion)
        lotes = Counter(f['lote_inferido'] for f in seleccion)
        familias = len({(f['lote_inferido'],f['familia_provisional']) for f in seleccion})
        planes.append({'dosis':dosis, 'n':len(seleccion),
                       'hawkish':conteos['hawkish'],'dovish':conteos['dovish'],'neutral':conteos['neutral'],
                       'lote_1_517':lotes['1_517'],'lote_518_1018':lotes['518_1018'],
                       'familias_lote_tema':familias})
        if len(seleccion) != dosis:
            raise ValueError(f'Dosis incompleta: {dosis}')
    salida.mkdir(parents=True)
    for nombre, datos in [('pool_sintetico_deduplicado.csv',pool),('plan_dosis.csv',planes)]:
        with (salida/nombre).open('x', encoding='utf-8', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=list(datos[0]), lineterminator='\n')
            escritor.writeheader(); escritor.writerows(datos)
    resumen = {'textos_unicos':801,'dosis':planes,'anidadas':True,'seleccion_balanceada_aproximada':True,
               'familia_provisional':'lote_inferido + tema','solo_texto_como_predictor':True,
               'etiquetas_sinteticas_son_provisionales':True,'entrenamiento_ejecutado':False}
    guardar_json(salida/'resumen.json',resumen)
    guardar_json(salida/'protocolo.json',{
        'operacion':'Deduplicar texto normalizado y fijar dosis anidadas antes de observar resultados.',
        'semilla_orden':SEMILLA,'cuotas':DOSIS,
        'fuentes_sha256':{str(p.relative_to(RAIZ)):sha256(p) for p in
            [ORIGEN,AUDITORIA/'manifest.json',AUDITORIA/'candidatos_texto_unico.csv',AUDITORIA/'inventario.csv',Path(__file__)]},
        'limitacion':'Tema es familia provisional; etiquetas no equivalen a referencia humana.'})
    guardar_json(salida/'manifest.json',{'sha256_salidas':{
        nombre:sha256(salida/nombre) for nombre in nombres if nombre!='manifest.json'}})
    return resumen


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,default=SALIDA)
    print(json.dumps(preparar(p.parse_args().salida),ensure_ascii=False,indent=2))
