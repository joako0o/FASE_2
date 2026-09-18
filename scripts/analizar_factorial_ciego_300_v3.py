"""Completa factorial C/W+C × +89/+600 y robustez agrupada del test ya abierto."""
import json, platform, warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import scipy, sklearn
from sklearn.exceptions import ConvergenceWarning

from entrenar_tfidf_supervision_v3 import RAIZ, ajustar_predecir, cargar_datos, clave_texto, metricas_completas, sha256
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import fit_predict
from reestimar_c_wc_con_300_v3 import load_300
from reestimar_c_wc_con_600_v3 import load_second

OUT=RAIZ/'data/evaluacion/analisis_secundario_ciego_300_v3_v1'
PRIMARY=RAIZ/'data/evaluacion/evaluacion_ciega_300_resultados_v1/predicciones.csv'
QUAR=RAIZ/'data/muestras/evaluacion_ciega_300_v3_v1/reuniones_cuarentena.csv'
PREREG=RAIZ/'docs/PROTOCOLO_ANALISIS_SECUNDARIO_CIEGO_300_V3.md'
WEIGHTS={1:1.0,2:0.5,3:1.0,4:1.0,5:1.0}; ORDER=['hawkish','dovish','neutral']; BOOT=10000; SEED=20260917

def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def vote(values):
 c=Counter(values); return max(ORDER,key=lambda x:(c[x],-ORDER.index(x)))
def allowed(x,meetings,keys): return x[~x.meeting_id.isin(meetings)&~x.texto.map(clave_texto).isin(keys)].copy()
def metric(table,col): return metricas_completas(table.rename(columns={col:'pred'}),'pred')
def compact(m): return {k:m[k] for k in ['accuracy','macro_f1','f1_hd','errores','h_d_cruzados','direccion_a_neutral','neutral_a_direccion']}

def run(out=OUT):
 out=Path(out)
 if out.exists(): raise FileExistsError('No sobrescribir análisis secundario')
 data=pd.read_csv(PRIMARY,dtype=str,keep_default_na=False); data['fold']=1
 meetings=set(pd.read_csv(QUAR).meeting_id); keys=set(data.texto.map(clave_texto))
 base,_,base_sources=cargar_datos(); ia89,ia_sources=cargar_nuevos(); first,second=load_300(),load_second()
 ia89=allowed(ia89,meetings,keys);first=allowed(first,meetings,keys);second=allowed(second,meetings,keys)
 c600=[];wc89=[];execution=[]
 with warnings.catch_warnings():
  warnings.simplefilter('error',ConvergenceWarning)
  for fold in range(1,6):
   train=base[~base.fold_validacion.eq(fold)&~base.meeting_id.isin(meetings)&~base.texto.map(clave_texto).isin(keys)].copy()
   low=pd.concat([train,ia89.reindex(columns=train.columns)],ignore_index=True);high=pd.concat([low,first.reindex(columns=train.columns),second.reindex(columns=train.columns)],ignore_index=True)
   if set(high.meeting_id)&meetings or set(high.texto.map(clave_texto))&keys: raise ValueError('Contaminación')
   _,_,pc,dc=ajustar_predecir(high,data,'v3');_,_,pw,dw=fit_predict(low,data,WEIGHTS[fold]);c600.append(pc);wc89.append(pw)
   execution.append({'miembro':fold,'n_mas_89':len(low),'n_mas_600':len(high),'peso_char':WEIGHTS[fold],'dim_c600':dc,'dim_wc89':dw})
 for i in range(5): data[f'pred_c600_m{i+1}']=c600[i];data[f'pred_wc89_m{i+1}']=wc89[i]
 data['pred_c_600']=[vote(x) for x in zip(*c600)];data['pred_wc_89']=[vote(x) for x in zip(*wc89)]
 ev=data[data.incluir_evaluacion.eq('true')].copy(); specs={'c_89':'pred_c_89','wc_89':'pred_wc_89','c_600':'pred_c_600','wc_600':'pred_wc_600'}
 metrics={k:metric(ev,v) for k,v in specs.items()}
 fields=['accuracy','macro_f1','f1_hd']; effects={}
 for f in fields:
  effects[f]={'caracteres_con_89':metrics['wc_89'][f]-metrics['c_89'][f],'caracteres_con_600':metrics['wc_600'][f]-metrics['c_600'][f],'datos_en_c':metrics['c_600'][f]-metrics['c_89'][f],'datos_en_wc':metrics['wc_600'][f]-metrics['wc_89'][f],'interaccion':(metrics['wc_600'][f]-metrics['c_600'][f])-(metrics['wc_89'][f]-metrics['c_89'][f])}
 rng=np.random.default_rng(SEED); groups={m:g for m,g in ev.groupby('meeting_id')}; mids=np.array(sorted(groups)); comparisons={'wc600_vs_c89':('pred_c_89','pred_wc_600'),'wc600_vs_c600':('pred_c_600','pred_wc_600')};draws={name:{f:[] for f in fields} for name in comparisons}
 for _ in range(BOOT):
  sample=pd.concat([groups[m] for m in rng.choice(mids,size=len(mids),replace=True)],ignore_index=True);sample['fold']=1
  for name,(ca,cb) in comparisons.items():
   a,b=metric(sample,ca),metric(sample,cb)
   for f in fields: draws[name][f].append(b[f]-a[f])
 bootstrap={name:{f:{'p2_5':float(np.percentile(v,2.5)),'mediana':float(np.percentile(v,50)),'p97_5':float(np.percentile(v,97.5)),'proporcion_mayor_0':float(np.mean(np.array(v)>0))} for f,v in values.items()} for name,values in draws.items()}
 meeting=[]
 for mid,g in ev.groupby('meeting_id'):
  a,b=metric(g,'pred_c_89'),metric(g,'pred_wc_600');hits89=int((g.etiqueta_v3==g.pred_c_89).sum());hits600=int((g.etiqueta_v3==g.pred_c_600).sum());hitsw=int((g.etiqueta_v3==g.pred_wc_600).sum());meeting.append({'meeting_id':mid,'anio':mid[4:8],'n':len(g),'aciertos_c89':hits89,'aciertos_c600':hits600,'aciertos_wc600':hitsw,'delta_wc600_vs_c89':hitsw-hits89,'delta_wc600_vs_c600':hitsw-hits600,'errores_c89':a['errores'],'errores_wc600':b['errores']})
 by_meeting=pd.DataFrame(meeting); meeting_summary={name:{'gana_wc':int((by_meeting[col]>0).sum()),'empate':int((by_meeting[col]==0).sum()),'gana_c':int((by_meeting[col]<0).sum())} for name,col in [('wc600_vs_c89','delta_wc600_vs_c89'),('wc600_vs_c600','delta_wc600_vs_c600')]}
 robustness={}
 ev['anio']=ev.fecha_reunion.str[:4];ev['longitud']=ev.texto.str.len();ev['banda_longitud']=pd.qcut(ev.longitud,4,labels=['Q1_corto','Q2','Q3','Q4_largo'],duplicates='drop').astype(str)
 ev['desacuerdo_wc600']=np.where(ev[[f'pred_wc_m{i}' for i in range(1,6)]].nunique(axis=1).eq(1),'unánime','con_desacuerdo')
 for dimension in ['anio','estrato_recuperacion','banda_longitud','confianza','desacuerdo_wc600']:
  robustness[dimension]={}
  for value,g in ev.groupby(dimension): robustness[dimension][str(value)]={'n':len(g),'c_89':compact(metric(g,'pred_c_89')),'wc_600':compact(metric(g,'pred_wc_600'))}
 errors=ev[ev.pred_wc_600.ne(ev.etiqueta_v3)].copy();errors['tipo_error']=np.where(errors.etiqueta_v3.eq('neutral'),'N_a_direccion',np.where(errors.pred_wc_600.eq('neutral'),'direccion_a_N','inversion_HD'))
 result={'estatuto':'secundario postapertura; no nueva confirmación independiente','n':len(ev),'metricas_factorial':metrics,'efectos':effects,'bootstrap_reuniones':bootstrap,'reuniones':meeting_summary,'robustez':robustness,'errores_wc600':dict(Counter(errors.tipo_error)),'busqueda_hiperparametros':False,'cambio_decision_primaria':False}
 out.mkdir(parents=True);data.to_csv(out/'predicciones_factorial.csv',index=False,lineterminator='\n');by_meeting.to_csv(out/'resultados_reunion.csv',index=False,lineterminator='\n');errors.to_csv(out/'errores_wc600.csv',index=False,lineterminator='\n');save(out/'resultados.json',result);save(out/'ejecucion.json',execution)
 sources={**base_sources,**ia_sources,'predicciones_primarias':PRIMARY,'cuarentena':QUAR,'prerregistro':PREREG,'script':Path(__file__)};save(out/'protocolo.json',{'bootstrap':BOOT,'seed':SEED,'fuentes_sha256':{k:sha256(v) for k,v in sources.items()},'versiones':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__}})
 outputs=['predicciones_factorial.csv','resultados_reunion.csv','errores_wc600.csv','resultados.json','ejecucion.json','protocolo.json'];save(out/'manifest.json',{'sha256_salidas':{n:sha256(out/n) for n in outputs}});return result
if __name__=='__main__': print(json.dumps(run(),ensure_ascii=False,indent=2))
