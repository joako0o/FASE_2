"""Diagnóstico de los 16 cambios del ensayo +59, sin nuevas variantes ni etiquetas.

Reconstruye los ajustes exactos, verifica sus predicciones y descompone márgenes.
Las contribuciones son asociaciones del modelo, no explicaciones causales.
"""
# ---- 1. Linaje: solo cohortes y parámetros ya evaluados ----
import argparse
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

import evaluar_ampliacion_tfidf as E
from utilidades import exigir_salidas_nuevas, sha256

RAIZ=E.RAIZ
ENSAYO=E.SALIDA
SALIDA=RAIZ/'data/auditoria/diagnostico_ampliacion_tfidf_59_v1'


def descomponer(x0,x1,w0,w1):
    """Identidad simétrica: Δ(xw)=media(x)Δw + media(w)Δx. No intervención causal."""
    x0,x1,w0,w1=map(lambda x:np.asarray(x,dtype=float),(x0,x1,w0,w1))
    if not (x0.shape==x1.shape==w0.shape==w1.shape):raise ValueError('Dimensiones incompatibles')
    if not all(np.isfinite(x).all() for x in [x0,x1,w0,w1]):raise ValueError('Valores no finitos')
    c0=x0*w0;c1=x1*w1
    coef=(x0+x1)/2*(w1-w0)
    repre=(w0+w1)/2*(x1-x0)
    np.testing.assert_allclose(c1-c0,coef+repre,atol=1e-12)
    return c0,c1,coef,repre


def aportes(vector,modelo,texto,clase_nueva,clase_previa):
    clases=list(modelo.classes_);i=clases.index(clase_nueva);j=clases.index(clase_previa)
    x=vector.transform([texto]).tocsr();nombres=vector.get_feature_names_out()
    activos={nombres[k]:float(v) for k,v in zip(x.indices,x.data)}
    pesos=modelo.coef_[i]-modelo.coef_[j]
    intercepto=float(modelo.intercept_[i]-modelo.intercept_[j])
    margen=float((modelo.decision_function(x)[0])[i]-(modelo.decision_function(x)[0])[j])
    return activos,pesos,intercepto,margen


def ejecutar(salida=SALIDA):
    salida=Path(salida);exigir_salidas_nuevas(salida)
    manifest=json.loads((ENSAYO/'manifest.json').read_text())
    for n,h in manifest['sha256_salidas'].items():E.comprobar(sha256(ENSAYO/n)==h,'Ensayo alterado: '+n)
    proto=json.loads((ENSAYO/'protocolo.json').read_text())
    for n,h in proto['sha256_fuentes'].items():E.comprobar(sha256(RAIZ/n)==h,'Fuente del ensayo alterada: '+n)
    m,base,folds,ancla,nuevos,_,fuentes=E.cargar_cohorte()
    pred=pd.read_csv(ENSAYO/'predicciones.csv')
    pares=pd.read_csv(ENSAYO/'comparacion_casos.csv');casos=pares[pares.cambio].copy()
    E.comprobar(len(casos)==16,'Cambiaron los casos a diagnosticar')
    for n in ['scripts/diagnosticar_ampliacion_tfidf.py','tests/test_diagnostico_ampliacion.py',
              'docs/PROTOCOLO_DIAGNOSTICO_AMPLIACION_TFIDF.md']:
        fuentes[n]=sha256(RAIZ/n)
    fuentes.update({str((ENSAYO/n).relative_to(RAIZ)):sha256(ENSAYO/n) for n in ['manifest.json','protocolo.json','predicciones.csv','comparacion_casos.csv','metricas.json']})
    salida.mkdir(parents=True)
    E.escribir(salida/'protocolo.json',{'version':'diagnostico_ampliacion_tfidf_59_v1','paquete_base':m['paquete_id'],
       'sha256_fuentes':fuentes,'casos':casos.intervencion_id.tolist(),
       'metodo':'Margen clase ampliada menos clase control; descomposición simétrica de producto, intercepto separado.',
       'vecinos':'Tres nuevos ejemplos del train permitido más próximos por coseno TF-IDF ampliado; asociación, no influencia causal.',
       'variantes_nuevas':False,'etiquetas_modificadas':False,'reentrenamiento':'Solo reconstrucción exacta de las dos condiciones ya publicadas.'})
    docs=base.set_index('intervencion_id',drop=False);registros=[];terminos=[];vecinos=[];reajustes=[]
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        for f in folds:
            numero=f['fold'];train=docs.loc[f['train']].reset_index(drop=True);val=docs.loc[f['validacion']].reset_index(drop=True)
            extra,_=E.purgar(nuevos,val,numero)
            antiguo=E.H.ajustar_modelos(train,solo_base=True)['H0_historica']
            a,b0,p0=E.H.predecir(antiguo,val.texto.tolist())
            v0=antiguo['vista'].palabras;l0=antiguo['clasificador']
            tr=train[train.es_relevante.eq(1)];amp=pd.concat([tr,extra[tr.columns]],ignore_index=True)
            v1=TfidfVectorizer(**E.H.PARAMETROS_PALABRAS)
            l1=LogisticRegression(**E.H.ANTERIOR.PARAMETROS_LR).fit(v1.fit_transform(amp.texto),amp.etiqueta)
            b1=l1.predict(v1.transform(val.texto));p1=np.where(a==0,'neutral',b1)
            for cond,b,p in [('control',b0,p0),('ampliado_59',b1,p1)]:
                original=pred[pred.condicion.eq(cond)].set_index('intervencion_id').loc[val.intervencion_id]
                for esperado,real in [(original.pred_a.to_numpy(),a),(original.pred_b.to_numpy(),b),(original.pred.to_numpy(),p)]:
                    np.testing.assert_array_equal(esperado,real)
            reajustes.append({'fold':numero,'a_b_final_reproducidos':True,'n_train_b_control':len(tr),'n_train_b_ampliado':len(amp),
                'vocabulario_control':len(v0.vocabulary_),'vocabulario_ampliado':len(v1.vocabulary_),
                'terminos_nuevos':len(set(v1.vocabulary_)-set(v0.vocabulary_)),
                'terminos_retirados':len(set(v0.vocabulary_)-set(v1.vocabulary_)),
                'pesos_balanced_control':{c:len(tr)/(3*int(tr.etiqueta.eq(c).sum())) for c in E.H.CLASES},
                'pesos_balanced_ampliado':{c:len(amp)/(3*int(amp.etiqueta.eq(c).sum())) for c in E.H.CLASES}})
            matriz_nuevos=v1.transform(extra.texto)
            for r in casos[casos.fold.eq(numero)].itertuples():
                texto=docs.loc[r.intervencion_id,'texto'];antes=r.pred_control;despues=r.pred_ampliado
                E.comprobar(r.pred_a==1,'Cambio inesperado con A=0')
                x0,w0,i0,s0=aportes(v0,l0,texto,despues,antes);x1,w1,i1,s1=aportes(v1,l1,texto,despues,antes)
                nombres=sorted(set(x0)|set(x1));xs0=[];xs1=[];ws0=[];ws1=[]
                for n in nombres:
                    xs0.append(x0.get(n,0.));xs1.append(x1.get(n,0.))
                    ws0.append(float(w0[v0.vocabulary_[n]]) if n in v0.vocabulary_ else 0.)
                    ws1.append(float(w1[v1.vocabulary_[n]]) if n in v1.vocabulary_ else 0.)
                c0,c1,dc,dx=descomponer(xs0,xs1,ws0,ws1)
                np.testing.assert_allclose([i0+c0.sum(),i1+c1.sum()],[s0,s1],atol=1e-10)
                np.testing.assert_allclose((i1-i0)+dc.sum()+dx.sum(),s1-s0,atol=1e-10)
                E.comprobar(s0<0 and s1>0,'El par de márgenes no explica el cambio')
                grupo='error_nuevo' if antes==r.etiqueta else 'corregido' if despues==r.etiqueta else 'error_cambia'
                registros.append({'intervencion_id':r.intervencion_id,'fold':numero,'grupo':grupo,'referencia_v2':r.etiqueta,
                    'pred_control':antes,'pred_ampliado':despues,'n_caracteres':len(texto),'sha256_texto':docs.loc[r.intervencion_id,'sha256_texto'],
                    'margen_control':s0,'margen_ampliado':s1,'delta_margen':s1-s0,
                    'intercepto_control':i0,'intercepto_ampliado':i1,'delta_intercepto':i1-i0,
                    'componente_coeficientes':float(dc.sum()),'componente_representacion':float(dx.sum())})
                for j,n in enumerate(nombres):
                    terminos.append({'intervencion_id':r.intervencion_id,'termino':n,'x_control':xs0[j],'x_ampliado':xs1[j],
                       'peso_margen_control':ws0[j],'peso_margen_ampliado':ws1[j],
                       'contrib_control':float(c0[j]),'contrib_ampliado':float(c1[j]),'delta_contrib':float(c1[j]-c0[j]),
                       'componente_coeficientes':float(dc[j]),'componente_representacion':float(dx[j]),
                       'nuevo_en_vocabulario':n not in v0.vocabulary_})
                similitudes=(matriz_nuevos @ v1.transform([texto]).T).toarray().ravel()
                orden=sorted(range(len(extra)),key=lambda j:(-similitudes[j],extra.iloc[j].intervencion_id))[:3]
                for pos,j in enumerate(orden,1):
                    e=extra.iloc[j]
                    vecinos.append({'intervencion_id':r.intervencion_id,'fold':numero,'orden':pos,
                        'nuevo_train_id':e.intervencion_id,'etiqueta_ia_nuevo':e.etiqueta,'coseno':float(similitudes[j]),
                        'meeting_id_nuevo':e.meeting_id,'misma_reunion_validacion':e.meeting_id==docs.loc[r.intervencion_id,'meeting_id']})
            print('Reconstrucción y diagnóstico de fold',numero,'verificados.',flush=True)
    for n,h in fuentes.items():E.comprobar(sha256(RAIZ/n)==h,'Fuente cambió: '+n)
    for n,t in [('margenes',registros),('contribuciones',terminos),('vecinos_nuevos_train',vecinos)]:pd.DataFrame(t).to_csv(salida/(n+'.csv'),index=False)
    E.escribir(salida/'reajustes.json',reajustes)
    E.escribir(salida/'resumen.json',{'casos':len(registros),'por_grupo':pd.Series([r['grupo'] for r in registros]).value_counts().to_dict(),
        'caracteres_textos_completos':sum(r['n_caracteres'] for r in registros),'contribuciones':len(terminos),
        'vecinos':len(vecinos),'predicciones_reproducidas_por_condicion':793,'todas_a_1':True,
        'identidad_algebraica_verificada':True,'causalidad_demostrada':False,'nuevas_variantes':False,
        'nuevas_metricas_de_rendimiento':False,'etiquetas_modificadas':False,'modelos_guardados':False})
    E.escribir(salida/'manifest.json',{'sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir()) if p.is_file()}})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,default=SALIDA)
    ejecutar(p.parse_args().salida)
