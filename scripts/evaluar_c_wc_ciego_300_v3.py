"""Apertura única de C+89 y W+C+600 sobre evaluación ciega agrupada cerrada."""
import hashlib, json, platform, warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import scipy, sklearn
from sklearn.exceptions import ConvergenceWarning

from entrenar_tfidf_supervision_v3 import RAIZ, ajustar_predecir, cargar_datos, clave_texto, metricas_completas, sha256
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import fit_predict
from preparar_evaluacion_ciega_300_v3 import select
from reestimar_c_wc_con_300_v3 import load_300
from reestimar_c_wc_con_600_v3 import load_second

OUT=RAIZ/'data/evaluacion/evaluacion_ciega_300_resultados_v1'
GOLD=RAIZ/'data/evaluacion/evaluacion_ciega_300_v3_cerrada_v1/referencia_ciega_300_v3.csv'
QUAR=RAIZ/'data/muestras/evaluacion_ciega_300_v3_v1/reuniones_cuarentena.csv'
PREREG=RAIZ/'docs/PROTOCOLO_APERTURA_CIEGA_300_V3.md'
WEIGHTS={1:1.0,2:0.5,3:1.0,4:1.0,5:1.0}; ORDER=['hawkish','dovish','neutral']

def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def vote(values):
    counts=Counter(values); return max(ORDER,key=lambda x:(counts[x],-ORDER.index(x)))
def allowed(extra, meetings, keys): return extra[~extra.meeting_id.isin(meetings) & ~extra.texto.map(clave_texto).isin(keys)].copy()

def run(out=OUT):
    out=Path(out)
    if out.exists(): raise FileExistsError('No sobrescribir apertura')
    gold=pd.read_csv(GOLD,dtype=str,keep_default_na=False); blind=gold.copy(); meetings=set(pd.read_csv(QUAR).meeting_id); keys=set(blind.texto.map(clave_texto))
    base,_,base_sources=cargar_datos(); ia89,ia_sources=cargar_nuevos(); first,second=load_300(),load_second()
    ia89=allowed(ia89,meetings,keys); first=allowed(first,meetings,keys); second=allowed(second,meetings,keys)
    members_c=[];members_wc=[]; execution=[]
    with warnings.catch_warnings():
      warnings.simplefilter('error',ConvergenceWarning)
      for fold in range(1,6):
        train=base[~base.fold_validacion.eq(fold) & ~base.meeting_id.isin(meetings) & ~base.texto.map(clave_texto).isin(keys)].copy()
        ctrain=pd.concat([train,ia89.reindex(columns=train.columns)],ignore_index=True)
        wtrain=pd.concat([ctrain,first.reindex(columns=train.columns),second.reindex(columns=train.columns)],ignore_index=True)
        if set(wtrain.meeting_id)&meetings or set(wtrain.texto.map(clave_texto))&keys: raise ValueError('Contaminación')
        _,_,pc,dc=ajustar_predecir(ctrain,blind,'v3'); _,_,pw,dw=fit_predict(wtrain,blind,WEIGHTS[fold])
        members_c.append(pc);members_wc.append(pw);execution.append({'miembro':fold,'peso_char':WEIGHTS[fold],'n_c89':len(ctrain),'n_wc600':len(wtrain),'dim_c':dc,'dim_wc':dw})
    for i in range(5): blind[f'pred_c_m{i+1}']=members_c[i]; blind[f'pred_wc_m{i+1}']=members_wc[i]
    blind['pred_c_89']=[vote(x) for x in zip(*members_c)];blind['pred_wc_600']=[vote(x) for x in zip(*members_wc)]
    blind['fold']=1
    selected=blind[blind.incluir_evaluacion.eq('true')].copy()
    hidden,_,_=select(); strata=hidden.set_index('intervencion_id').estrato.to_dict(); blind['estrato_recuperacion']=blind.intervencion_id.map(strata)
    selected=blind[blind.incluir_evaluacion.eq('true')].copy()
    metrics={name:metricas_completas(selected.rename(columns={col:'pred'}),'pred') for name,col in [('c_89', 'pred_c_89'),('wc_600','pred_wc_600')]}
    metrics['por_estrato']={s:{name:metricas_completas(g.rename(columns={col:'pred'}),'pred') for name,col in [('c_89','pred_c_89'),('wc_600','pred_wc_600')]} for s,g in selected.groupby('estrato_recuperacion')}
    c,w=metrics['c_89'],metrics['wc_600']; controls={'macro_f1':w['macro_f1']>=c['macro_f1'],'f1_hd':w['f1_hd']>=c['f1_hd'],'f1_d':w['por_clase']['dovish']['f1']>=c['por_clase']['dovish']['f1'],'recall_d':w['por_clase']['dovish']['recall']>=c['por_clase']['dovish']['recall'],'f1_n':w['por_clase']['neutral']['f1']>=c['por_clase']['neutral']['f1'],'errores':w['errores']<=c['errores'],'inversiones':w['h_d_cruzados']<=c['h_d_cruzados'],'omisiones':w['direccion_a_neutral']<=c['direccion_a_neutral']}
    result={'version':out.name,'filas_instrumento':300,'filas_evaluadas':len(selected),'modelos':metrics,'controles_wc_vs_c':controls,'decision':'adoptar_wc_600' if all(controls.values()) else 'retener_c_89','evaluacion_agrupada_cuarentena':True,'challenge_enriquecido':True,'prevalencia_natural':False}
    out.mkdir(parents=True);blind.to_csv(out/'predicciones.csv',index=False,lineterminator='\n');save(out/'metricas.json',result);save(out/'ejecucion.json',execution)
    sources={**base_sources,**ia_sources,'gold':GOLD,'cuarentena':QUAR,'prerregistro':PREREG,'script':Path(__file__)}
    save(out/'protocolo.json',{'fuentes_sha256':{k:sha256(v) for k,v in sources.items()},'versiones':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__}})
    c,w=result['modelos']['c_89'],result['modelos']['wc_600']
    summary=f"""# Resultado de evaluación ciega agrupada v3\n\nMétricas sobre {len(selected)} filas decidibles de 300.\n\n| Modelo | Accuracy | Macro-F1 | F1-HD | Errores | H↔D | H/D→N |\n|---|---:|---:|---:|---:|---:|---:|\n| C+89 | {c['accuracy']:.6f} | {c['macro_f1']:.6f} | {c['f1_hd']:.6f} | {c['errores']} | {c['h_d_cruzados']} | {c['direccion_a_neutral']} |\n| W+C+600 | {w['accuracy']:.6f} | {w['macro_f1']:.6f} | {w['f1_hd']:.6f} | {w['errores']} | {w['h_d_cruzados']} | {w['direccion_a_neutral']} |\n\n**Decisión:** `{result['decision']}`. Muestra challenge enriquecida; no estima prevalencia natural.\n"""
    (out/'resumen.md').write_text(summary,encoding='utf-8')
    save(out/'manifest.json',{'sha256_salidas':{n:sha256(out/n) for n in ['predicciones.csv','metricas.json','ejecucion.json','protocolo.json','resumen.md']}});return result
if __name__=='__main__': print(json.dumps(run(),ensure_ascii=False,indent=2))
