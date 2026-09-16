"""Runner GPU de BETO con smoke obligatorio. Implementado; ejecución real pendiente.

No usa citas ni respuestas de 306. Paquete de 38, checkpoint fijo y cinco folds.
Las pruebas locales sin torch no certifican este entrenamiento con pesos reales.
"""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import time

import numpy as np
from utilidades import cargar_script, sha256
P = cargar_script('38_preparar_beto.py')
SALIDA = P.RAIZ/'data/checkpoints/beto_v1/ejecucion'
CACHE = P.RAIZ/'modelos/beto_v1'


def entorno():
    versiones = {}
    for n in ['torch','transformers','tokenizers','huggingface-hub','numpy']:
        try: versiones[n] = importlib.metadata.version(n)
        except importlib.metadata.PackageNotFoundError: versiones[n] = None
    r = {'versiones':versiones,'gpu_disponible':False,'entrenamiento_realizado':False}
    if versiones['torch'] is None:
        r['bloqueo'] = 'PyTorch no instalado; no se puede ejecutar forward/backward.'
        return r
    try:
        import torch
        r['gpu_disponible'] = torch.cuda.is_available()
        if r['gpu_disponible']:
            r['gpu'] = torch.cuda.get_device_name(0)
            r['gpu_memoria_bytes'] = torch.cuda.get_device_properties(0).total_memory
        else: r['bloqueo'] = 'GPU CUDA no disponible; se exige para este ensayo.'
    except Exception as e: r['bloqueo'] = type(e).__name__+': '+str(e)
    return r


def runtime():
    os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
    r = entorno()
    if not r['gpu_disponible']: raise RuntimeError(r.get('bloqueo', 'GPU no disponible'))
    for n, v in [('torch','2.6.0'),('transformers','4.57.6'),('tokenizers','0.22.2'),('huggingface-hub','0.36.2')]:
        if (r['versiones'].get(n) or '').split('+')[0] != v: raise RuntimeError('Versión distinta al protocolo: '+n)
    import torch
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    return torch, r


def semilla(torch):
    seed = P.PARAMETROS['semilla']; random.seed(seed); np.random.seed(seed)
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def descargar(lock, cache=CACHE):
    from huggingface_hub import snapshot_download
    carpeta = snapshot_download(repo_id=lock['model_id'], revision=lock['revision'],
        allow_patterns=list(lock['archivos']), cache_dir=str(cache), token=False)
    P.verificar_checkpoint(carpeta, lock)
    return Path(carpeta)


def cargar_modelo(carpeta, torch):
    from transformers import AutoModelForSequenceClassification
    semilla(torch)
    model, info = AutoModelForSequenceClassification.from_pretrained(str(carpeta),
        num_labels=3, id2label=dict(enumerate(P.CLASES)), label2id={c:i for i,c in enumerate(P.CLASES)},
        local_files_only=True, trust_remote_code=False, weights_only=True,
        attn_implementation='eager', output_loading_info=True)
    faltan = [k for k in info['missing_keys'] if not k.startswith(('classifier.', 'bert.pooler.'))]
    if faltan or info.get('mismatched_keys') or info.get('error_msgs'):
        raise ValueError('Carga incompleta del encoder: '+str(info))
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    model.to(device='cuda', dtype=torch.float32)
    return model, info


def tokenizar(documentos, carpeta):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(str(carpeta), local_files_only=True, trust_remote_code=False)
    if tok.num_special_tokens_to_add(pair=False) != 2: raise ValueError('Especiales incompatibles')
    entradas, cobertura = {}, []
    for doc in documentos:
        ids = tok(doc['texto'], add_special_tokens=False, truncation=False)['input_ids']
        tramos = P.ventanas(ids, P.PARAMETROS['max_tokens']-2, P.PARAMETROS['solapamiento'])
        partes = []
        for inicio, fin in tramos:
            encoded = tok.prepare_for_model(ids[inicio:fin], add_special_tokens=True,
                truncation=False, return_attention_mask=True, return_token_type_ids=True)
            assert len(encoded['input_ids']) == fin-inicio+2 <= 512
            partes.append({k:encoded[k] for k in ['input_ids','attention_mask','token_type_ids']})
        entradas[doc['intervencion_id']] = partes
        cobertura.append({'intervencion_id':doc['intervencion_id'],'sha256_texto':doc['sha256_texto'],
            'n_tokens_contenido':len(ids),'n_segmentos':len(partes),'tramos':tramos,
            'ultimo_token_cubierto':tramos[-1][1],'cobertura_completa':True})
    return entradas, cobertura


def logits_documento(model, segmentos, torch):
    logits = []
    for s in segmentos:
        x = {k:torch.tensor([v],dtype=torch.long,device='cuda') for k,v in s.items()}
        logits.append(model(**x).logits[0])
    return torch.stack(logits).mean(dim=0)


def paso_grupo(model, grupo, docs, entradas, pesos, optimizer, torch):
    """Cada intervención contribuye una vez; último grupo usa su tamaño real."""
    optimizer.zero_grad(set_to_none=True)
    perdidas = []
    for k in grupo:
        y = P.CLASES.index(docs[k]['etiqueta'])
        logits = logits_documento(model, entradas[k], torch)
        ce = torch.nn.functional.cross_entropy(logits[None,:],
            torch.tensor([y],device='cuda'), reduction='none')[0]
        loss = ce*float(pesos[y])/len(grupo)
        if not torch.isfinite(loss): raise FloatingPointError('Pérdida no finita')
        loss.backward(); perdidas.append(float(loss.detach().cpu()))
    grad = torch.nn.utils.clip_grad_norm_(model.parameters(), P.PARAMETROS['clip'], error_if_nonfinite=True)
    if not torch.isfinite(grad): raise FloatingPointError('Gradientes no finitos')
    if not any(p.grad is not None for p in model.bert.parameters()): raise RuntimeError('Encoder sin gradientes')
    optimizer.step()
    return sum(perdidas)


def validar_salida_fold(carpeta, paquete_id, fold):
    m = json.loads((Path(carpeta)/'manifest.json').read_text())
    assert m['paquete_id'] == paquete_id and m['fold'] == fold and m['epocas_completadas'] == 3
    for n,h in m['sha256_archivos'].items(): assert sha256(Path(carpeta)/n) == h, n
    return m


def smoke(paquete, salida=SALIDA, cache=CACHE):
    salida = Path(salida)
    if (salida/'smoke.json').exists(): raise FileExistsError('No sobrescribir smoke existente')
    m, documentos, folds, _, lock = P.cargar_paquete(paquete)
    torch, hardware = runtime(); carpeta = descargar(lock, cache)
    entradas, _ = tokenizar(documentos, carpeta)
    docs = {r['intervencion_id']:r for r in documentos}
    ids = [k for k in folds[0]['train'] if docs[k]['es_relevante'] == 1]
    ids.sort(key=lambda k:(len(entradas[k]),len(docs[k]['texto']),k))
    elegidos = [ids[-1], ids[0]]
    assert len(set(elegidos)) == 2 and not set(elegidos)&set(folds[0]['validacion'])
    pesos = P.pesos_clase([P.CLASES.index(docs[k]['etiqueta']) for k in ids])
    model, info = cargar_modelo(carpeta, torch); model.train()
    optimizer = torch.optim.AdamW(model.parameters(),lr=P.PARAMETROS['lr'],weight_decay=P.PARAMETROS['weight_decay'])
    antes = model.classifier.weight.detach().clone()
    encoder_antes = model.bert.encoder.layer[0].attention.self.query.weight.detach().clone()
    torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); inicio = time.perf_counter()
    loss = paso_grupo(model, elegidos, docs, entradas, pesos, optimizer, torch)
    torch.cuda.synchronize()
    assert not torch.equal(antes, model.classifier.weight.detach())
    assert not torch.equal(encoder_antes, model.bert.encoder.layer[0].attention.self.query.weight.detach())
    registro = {'estado':'aprobado_con_pesos_reales','paquete_id':m['paquete_id'],
        'checkpoint_revision':lock['revision'],'hardware':hardware,'train_ids':elegidos,
        'segmentos':[len(entradas[k]) for k in elegidos],'loss_tecnica':loss,
        'segundos':time.perf_counter()-inicio,'gpu_pico_bytes':torch.cuda.max_memory_allocated(),
        'cabeza_modificada':True,'encoder_modificado':True,'modelo_smoke_descartado':True,'no_es_evaluacion':True,
        'carga':info,'registrado_utc':datetime.now(timezone.utc).isoformat()}
    salida.mkdir(parents=True,exist_ok=True); P.escribir(salida/'smoke.json',registro)
    del model, optimizer; torch.cuda.empty_cache(); print(json.dumps(registro,indent=2))


def entrenar_fold(paquete, fold, salida=SALIDA, cache=CACHE, reanudar=False):
    salida=Path(salida); m, documentos, folds, baseline, lock = P.cargar_paquete(paquete)
    carpeta_fold = salida/f'fold_{fold}'
    if carpeta_fold.exists():
        if reanudar and (carpeta_fold/'manifest.json').exists():
            validar_salida_fold(carpeta_fold,m['paquete_id'],fold); print('Fold completo verificado; no se repite.'); return
        raise FileExistsError('Salida parcial/existente: conservarla y usar otra ruta, sin sobrescribir')
    previo = json.loads((salida/'smoke.json').read_text())
    assert previo['estado']=='aprobado_con_pesos_reales' and previo['paquete_id']==m['paquete_id']
    torch, hardware = runtime(); carpeta = descargar(lock,cache)
    entradas, cobertura = tokenizar(documentos,carpeta)
    docs = {r['intervencion_id']:r for r in documentos}; datos_fold=folds[fold-1]
    ids = [k for k in datos_fold['train'] if docs[k]['es_relevante']==1]
    pesos = P.pesos_clase([P.CLASES.index(docs[k]['etiqueta']) for k in ids])
    model, info = cargar_modelo(carpeta,torch); model.train()
    optimizer = torch.optim.AdamW(model.parameters(),lr=P.PARAMETROS['lr'],weight_decay=P.PARAMETROS['weight_decay'])
    from transformers import get_linear_schedule_with_warmup
    total = math.ceil(len(ids)/8)*3
    scheduler = get_linear_schedule_with_warmup(optimizer,num_warmup_steps=math.ceil(total*.1),num_training_steps=total)
    rng = np.random.default_rng(P.PARAMETROS['semilla']+fold)
    carpeta_fold.mkdir(parents=True); pasos=0; inicio=time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    for epoca in range(3):
        orden = [ids[i] for i in rng.permutation(len(ids))]
        loss_epoca=[]
        for grupo in P.grupos(orden):
            loss_epoca.append(paso_grupo(model,grupo,docs,entradas,pesos,optimizer,torch))
            scheduler.step(); pasos+=1
        with (carpeta_fold/'entrenamiento.jsonl').open('a') as f:
            f.write(json.dumps({'epoca':epoca+1,'pasos':pasos,'media_loss_grupos':float(np.mean(loss_epoca))})+'\n')
        print(f'Fold {fold}, época {epoca+1}/3 terminada; sin seleccionar con validación.',flush=True)
    assert pasos==total
    model.eval(); pred=[]; ancla={r['intervencion_id']:r for r in baseline}
    with torch.no_grad():
        for k in datos_fold['validacion']:
            logits=logits_documento(model,entradas[k],torch)
            if not torch.isfinite(logits).all(): raise FloatingPointError('Logits no finitos')
            probs=torch.softmax(logits,dim=0).cpu().tolist()
            b=P.CLASES[int(np.argmax(probs))]; a=ancla[k]['pred_a']
            pred.append({'intervencion_id':k,'meeting_id':docs[k]['meeting_id'],'fold':fold,
                'etiqueta':docs[k]['etiqueta'],'pred_a':a,'pred_b':b,'pred':'neutral' if a==0 else b,
                **{f'prob_b_{c}':float(v) for c,v in zip(P.CLASES,probs)}})
    import pandas as pd
    pd.DataFrame(pred).to_csv(carpeta_fold/'predicciones.csv',index=False)
    P.escribir(carpeta_fold/'cobertura.json',cobertura)
    P.escribir(carpeta_fold/'ejecucion.json',{'hardware':hardware,'carga':info,'pesos_train':pesos.tolist(),
        'n_train_relevante':len(ids),'pasos':pasos,'segundos':time.perf_counter()-inicio,
        'gpu_pico_bytes':torch.cuda.max_memory_allocated(),'checkpoint_revision':lock['revision']})
    P.escribir(carpeta_fold/'manifest.json',{'paquete_id':m['paquete_id'],'fold':fold,'epocas_completadas':3,
        'sha256_archivos':{p.name:sha256(p) for p in sorted(carpeta_fold.iterdir()) if p.is_file()},
        'finalizado_utc':datetime.now(timezone.utc).isoformat()})
    del model,optimizer; torch.cuda.empty_cache()


def metricas_tabla(tabla):
    from sklearn.metrics import confusion_matrix
    resultado=P.E.H.metricas(tabla.etiqueta,tabla.pred)
    matriz=confusion_matrix(tabla.etiqueta,tabla.pred,labels=P.CLASES)
    resultado.update(matriz=matriz.tolist(),h_a_d=int(matriz[0,1]),d_a_h=int(matriz[1,0]),
        hd_a_n=int(matriz[0,2]+matriz[1,2]),n_a_hd=int(matriz[2,0]+matriz[2,1]))
    return resultado


def consolidar(paquete,salida=SALIDA):
    import pandas as pd
    salida=Path(salida); m, docs, folds, baseline, lock=P.cargar_paquete(paquete)
    if (salida/'comparacion.json').exists(): raise FileExistsError('Comparación existente')
    tablas=[]
    for fold in range(1,6):
        carpeta=salida/f'fold_{fold}'
        if not (carpeta/'manifest.json').exists(): raise RuntimeError('Faltan folds: no emitir evaluación final')
        validar_salida_fold(carpeta,m['paquete_id'],fold)
        t=pd.read_csv(carpeta/'predicciones.csv'); assert t.fold.eq(fold).all()
        assert t.intervencion_id.is_unique and set(t.intervencion_id)==set(folds[fold-1]['validacion'])
        tablas.append(t)
    nuevo=pd.concat(tablas,ignore_index=True).sort_values('intervencion_id').reset_index(drop=True)
    base=pd.DataFrame(baseline).rename(columns={'etiqueta_corregida_v2':'etiqueta'}).sort_values('intervencion_id').reset_index(drop=True)
    assert len(nuevo)==793 and nuevo.intervencion_id.is_unique
    for c in ['intervencion_id','meeting_id','fold','etiqueta','pred_a']:assert nuevo[c].equals(base[c]),c
    assert nuevo.pred_b.isin(P.CLASES).all()
    assert nuevo.pred.equals(nuevo.apply(lambda r:'neutral' if r.pred_a==0 else r.pred_b,axis=1))
    prob=nuevo[[f'prob_b_{c}' for c in P.CLASES]].to_numpy()
    assert np.isfinite(prob).all() and (prob>=0).all() and (prob<=1).all()
    np.testing.assert_allclose(prob.sum(axis=1),1,atol=1e-6)
    assert nuevo.pred_b.tolist()==[P.CLASES[i] for i in prob.argmax(axis=1)]
    puntos=[];resultados={}
    for nombre,tabla in [('tfidf',base),('beto',nuevo)]:
        por_fold=[metricas_tabla(tabla[tabla.fold.eq(f)]) for f in range(1,6)]
        resultados[nombre]={'media_f1_hd':float(np.mean([r['f1_hd'] for r in por_fold])),
            'media_macro_f1':float(np.mean([r['macro_f1'] for r in por_fold])),
            'por_fold':por_fold,'conjunto':metricas_tabla(tabla)}
        puntos.append([r['f1_hd'] for r in por_fold])
    a,b=resultados['tfidf'],resultados['beto'];ac,bc=a['conjunto'],b['conjunto']
    deltas=np.asarray(puntos[1])-puntos[0]
    criterios={'delta_hd':bool(deltas.mean()>=.02),'folds_mejora':bool((deltas>0).sum()>=3),
        'macro':bool(b['media_macro_f1']>=a['media_macro_f1']-.005),
        'recall_h':bool(bc['recall_hawkish']>=ac['recall_hawkish']-.02),
        'recall_d':bool(bc['recall_dovish']>=ac['recall_dovish']-.02),
        'menos_inversiones':bc['h_a_d']+bc['d_a_h']<ac['h_a_d']+ac['d_a_h'],
        'no_ocultar_en_n':bc['hd_a_n']<=ac['hd_a_n']}
    ambiguos = set(m['cinco_ambiguos_hd_conocidos'])
    conocidos = base[base.etiqueta.isin(P.CLASES[:2]) & base.pred.isin(P.CLASES[:2]) & base.etiqueta.ne(base.pred)]
    assert len(conocidos) == 15 and ambiguos <= set(conocidos.intervencion_id)
    diagnostico = conocidos[['intervencion_id','etiqueta','pred']].rename(columns={'pred':'pred_tfidf'}).merge(
        nuevo[['intervencion_id','pred']].rename(columns={'pred':'pred_beto'}),on='intervencion_id',validate='one_to_one')
    diagnostico['ambiguo_hd_conocido'] = diagnostico.intervencion_id.isin(ambiguos)
    sin_cinco = {nombre:metricas_tabla(tabla[~tabla.intervencion_id.isin(ambiguos)])
        for nombre,tabla in [('tfidf',base),('beto',nuevo)]}
    P.escribir(salida/'comparacion.json',{'paquete_id':m['paquete_id'],'condiciones':resultados,
        'diagnostico_15_inversiones_conocidas_no_test':diagnostico.to_dict('records'),
        'suplemento_sin_cinco_ambiguos_hd_conocidos':sin_cinco,
        'criterios_calculados_sobre_todos_los_793':True,
        'deltas_f1_hd':deltas.tolist(),'criterios':criterios,'cumple_criterios_desarrollo':all(criterios.values()),
        'evaluacion_independiente':False,'modelo_adoptado_automaticamente':False})
    print('Cinco folds consolidados. Es desarrollo reutilizado, no confirmación independiente.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    modo=p.add_mutually_exclusive_group(required=True)
    modo.add_argument('--comprobar',action='store_true');modo.add_argument('--smoke',action='store_true')
    modo.add_argument('--fold',type=int,choices=range(1,6));modo.add_argument('--consolidar',action='store_true')
    p.add_argument('--paquete',type=Path,default=P.PAQUETE);p.add_argument('--salida',type=Path,default=SALIDA)
    p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--reanudar',action='store_true')
    a=p.parse_args()
    if a.comprobar:
        m,*_=P.cargar_paquete(a.paquete);r=entorno();r['paquete_id']=m['paquete_id'];print(json.dumps(r,ensure_ascii=False,indent=2))
    elif a.smoke:smoke(a.paquete,a.salida,a.cache)
    elif a.fold:entrenar_fold(a.paquete,a.fold,a.salida,a.cache,a.reanudar)
    else:consolidar(a.paquete,a.salida)


if __name__=='__main__':main()
