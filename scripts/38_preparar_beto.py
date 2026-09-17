"""Paquete verificable para BETO; no descarga pesos ni entrena el encoder."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

E = cargar_script('36_evaluar_referencias_corregidas.py')
RAIZ = E.RAIZ
AUDITORIA = RAIZ/'data/auditoria/preparacion_beto_v1'
LOCK = AUDITORIA/'checkpoint.json'
AMBIGUOS = RAIZ/'data/auditoria/inversiones_hd_v1/resultados/ambiguos_excluidos.csv'
PAQUETE = RAIZ/'data/checkpoints/beto_v1/entrada'
CLASES = ['hawkish', 'dovish', 'neutral']
PARAMETROS = {'epocas': 3, 'lr': 2e-5, 'weight_decay': .01, 'warmup': .1,
              'clip': 1., 'acumulacion': 8, 'semilla': 20260915,
              'max_tokens': 512, 'solapamiento': 64, 'dtype': 'float32',
              'agregacion': 'media_logits_por_intervencion', 'gradient_checkpointing': True}


def escribir(ruta, valor):
    with Path(ruta).open('x', encoding='utf-8') as f:
        json.dump(valor, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def digest_json(valor):
    return hashlib.sha256(json.dumps(valor, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def ventanas(ids, contenido=510, solapamiento=64):
    if not ids or not 0 <= solapamiento < contenido:
        raise ValueError('Secuencia vacía o solapamiento inválido')
    tramos = []
    inicio = 0
    while True:
        fin = min(inicio+contenido, len(ids))
        tramos.append((inicio, fin))
        if fin == len(ids): break
        inicio = fin-solapamiento
    reconstruidos = []
    ultimo = 0
    for inicio, fin in tramos:
        if inicio > ultimo: raise ValueError('Hueco de cobertura')
        reconstruidos.extend(ids[max(inicio, ultimo):fin])
        ultimo = fin
    assert reconstruidos == list(ids) and ultimo == len(ids)
    return tramos


def grupos(ids, n=8):
    if n < 1: raise ValueError('Tamaño de grupo inválido')
    return [list(ids[i:i+n]) for i in range(0, len(ids), n)]


def pesos_clase(etiquetas):
    conteos = np.bincount(etiquetas, minlength=3)
    if len(conteos) != 3 or np.any(conteos == 0): raise ValueError('Falta alguna clase de train')
    return len(etiquetas)/(3*conteos.astype(float))


def perdida_referencia(logits_segmentos, etiqueta, peso):
    """Referencia NumPy para probar media de logits + CE ponderada documental."""
    logits = np.asarray(logits_segmentos, dtype=float)
    if logits.ndim != 2 or logits.shape[1] != 3 or not len(logits): raise ValueError('Logits inválidos')
    if not np.isfinite(logits).all() or peso <= 0: raise ValueError('No finitos/peso inválido')
    media = logits.mean(axis=0)
    logsumexp = float(media.max()+np.log(np.exp(media-media.max()).sum()))
    return (logsumexp-float(media[etiqueta]))*peso


def verificar_checkpoint(carpeta, lock):
    carpeta = Path(carpeta)
    for nombre, esperado in lock['archivos'].items():
        p = carpeta/nombre
        if not p.is_file() or p.stat().st_size != esperado['bytes']:
            raise ValueError('Archivo ausente/tamaño distinto: '+nombre)
        if 'sha256' in esperado:
            actual = sha256(p)
            esperado_hash = esperado['sha256']
        else:
            b = p.read_bytes()
            actual = hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
            esperado_hash = esperado['git_blob']
        if actual != esperado_hash: raise ValueError('Hash de checkpoint distinto: '+nombre)
    return True


def validar_datos(documentos, folds, baseline):
    ids = [r['intervencion_id'] for r in documentos]
    assert len(ids) == len(set(ids)) == 1352
    docs = {r['intervencion_id']: r for r in documentos}
    assert [f['fold'] for f in folds] == [1, 2, 3, 4, 5]
    vistos = []
    for r in documentos:
        assert set(r) == {'intervencion_id','meeting_id','texto','sha256_texto','etiqueta','es_relevante'}
        assert r['etiqueta'] in CLASES and r['es_relevante'] in [0, 1]
        assert r['texto'].strip() and hashlib.sha256(r['texto'].encode()).hexdigest() == r['sha256_texto']
    for f in folds:
        tr, va = f['train'], f['validacion']
        assert len(tr) == len(set(tr)) and len(va) == len(set(va))
        assert set(tr+va) <= set(ids) and not set(tr)&set(va)
        assert not {docs[k]['meeting_id'] for k in tr}&{docs[k]['meeting_id'] for k in va}
        assert not {E.H.clave_texto(docs[k]['texto']) for k in tr}&{E.H.clave_texto(docs[k]['texto']) for k in va}
        vistos.extend(va)
    assert len(vistos) == len(set(vistos)) == 793
    assert len(baseline) == len({r['intervencion_id'] for r in baseline}) == 793
    assert set(vistos) == {r['intervencion_id'] for r in baseline}
    for f in folds:
        sub = [r for r in baseline if r['fold'] == f['fold']]
        assert set(f['validacion']) == {r['intervencion_id'] for r in sub}
    for r in baseline:
        assert r['etiqueta_corregida_v2'] == docs[r['intervencion_id']]['etiqueta']
        assert r['pred_a'] in [0, 1] and r['pred'] in CLASES
        assert r['pred'] == ('neutral' if r['pred_a'] == 0 else r['pred_b'])


def preparar(salida=PAQUETE):
    salida = Path(salida); exigir_salidas_nuevas(salida)
    original, _, vista, particiones, _, _ = E.cargar()
    import pandas as pd
    previo = json.loads((E.SALIDA/'protocolo.json').read_text())
    E.PREV.verificar_hashes(previo['sha256_insumos'])
    manifest36 = json.loads((E.SALIDA/'manifest.json').read_text())
    for n, h in manifest36['sha256_salidas'].items(): assert sha256(E.SALIDA/n) == h
    pred = pd.read_csv(E.SALIDA/'predicciones_validacion.csv')
    baseline = pred[pred.supervision.eq('seis_mas_trece')].to_dict('records')
    documentos = [{'intervencion_id':r.intervencion_id,'meeting_id':r.meeting_id,
        'texto':r.texto,'sha256_texto':hashlib.sha256(r.texto.encode()).hexdigest(),
        'etiqueta':r.etiqueta,'es_relevante':int(r.es_relevante)} for r in vista.itertuples()]
    folds = [{'fold':int(f),'train':vista.iloc[tr].intervencion_id.tolist(),
        'validacion':vista.iloc[va].intervencion_id.tolist()} for f, _, tr, va in particiones]
    validar_datos(documentos, folds, baseline)
    fuentes = dict(previo['sha256_insumos'])
    for p in [Path(__file__), RAIZ/'scripts/39_ejecutar_beto.py', LOCK,
              RAIZ/'requirements-beto.txt', RAIZ/'tests/test_preparacion_beto.py', AMBIGUOS,
              RAIZ/'docs/INVESTIGACION_Y_PROTOCOLO_BETO_V1.md', E.SALIDA/'protocolo.json',
              E.SALIDA/'manifest.json', E.SALIDA/'predicciones_validacion.csv']:
        fuentes[str(p.relative_to(RAIZ))] = sha256(p)
    salida.mkdir(parents=True)
    for n, d in [('documentos.json',documentos),('folds.json',folds),('baseline.json',baseline),
                 ('checkpoint.json',json.loads(LOCK.read_text()))]: escribir(salida/n, d)
    ambiguos = sorted(pd.read_csv(AMBIGUOS).intervencion_id.tolist())
    assert len(ambiguos) == len(set(ambiguos)) == 5
    assert set(ambiguos) <= {r['intervencion_id'] for r in baseline}
    m = {'version':'beto_v1','clases':CLASES,'parametros':PARAMETROS,
        'cinco_ambiguos_hd_conocidos':ambiguos,
        'sha256_archivos':{p.name:sha256(p) for p in sorted(salida.iterdir())},
        'sha256_fuentes':fuentes,'codebook_modificado':False,'examen_306_abierto':False}
    m['paquete_id'] = digest_json(m)
    escribir(salida/'manifest.json', m)
    print(json.dumps({'paquete_id':m['paquete_id'],'documentos':1352,'validacion':793,
        'caracteres':sum(len(d['texto']) for d in documentos),'entrenamiento_beto_realizado':False},indent=2))
    return m


def cargar_paquete(carpeta=PAQUETE):
    carpeta = Path(carpeta); m = json.loads((carpeta/'manifest.json').read_text())
    assert m['clases'] == CLASES and m['parametros'] == PARAMETROS
    assert m['paquete_id'] == digest_json({k:v for k,v in m.items() if k!='paquete_id'})
    E.PREV.verificar_hashes(m['sha256_fuentes'])
    for n,h in m['sha256_archivos'].items(): assert sha256(carpeta/n) == h, n
    docs, folds, baseline, lock = [json.loads((carpeta/n).read_text()) for n in
        ['documentos.json','folds.json','baseline.json','checkpoint.json']]
    validar_datos(docs, folds, baseline)
    return m, docs, folds, baseline, lock


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida',type=Path,default=PAQUETE)
    p.add_argument('--verificar',action='store_true')
    a=p.parse_args()
    if a.verificar:
        m,*_ = cargar_paquete(a.salida);print('Paquete verificado:',m['paquete_id'])
    else: preparar(a.salida)
