"""Ensayo controlado: TF-IDF B original frente a B con 59 ejemplos IA nuevos.

No cambia referencias/folds/A, no busca hiperparámetros ni reemplaza modelos.
Se ejecuta desde el gestor 40; cada salida debe ser nueva.
"""
# ---- 1. Fuentes congeladas y preparación anterior al ajuste ----
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

from utilidades import cargar_script, exigir_salidas_nuevas, sha256, errores_anotacion
P = cargar_script('38_preparar_beto.py')
H = P.E.H
RAIZ = P.RAIZ
SALIDA = RAIZ/'data/evaluacion/ampliacion_tfidf_59_v1'
TANDAS = [
    'data/auditoria/ampliacion_hd_60_v1/anotacion_ia_v1/tanda_01',
    'data/auditoria/ampliacion_hd_60_v1/anotacion_ia_v1/tanda_02',
    'data/auditoria/meta_hd_300_v1/anotacion_ia_v1/tanda_03',
    'data/auditoria/meta_hd_300_v1/anotacion_ia_v1/tanda_04',
]


def comprobar(condicion, mensaje):
    if not condicion: raise ValueError(mensaje)


def escribir(ruta, obj):
    with Path(ruta).open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')


def cargar_cohorte():
    m, documentos, folds, ancla, _ = P.cargar_paquete()
    fuentes = dict(m['sha256_fuentes'])
    for n in P.PAQUETE.iterdir():
        if n.is_file(): fuentes[str(n.relative_to(RAIZ))] = sha256(n)
    base = pd.DataFrame(documentos)
    ids_base = set(base.intervencion_id)
    corpus = pd.read_csv(RAIZ/'data/L0/corpus.csv', dtype=str, keep_default_na=False).set_index('intervencion_id')
    marco = RAIZ/'data/muestras/gold_ciego_300.csv'
    humanos = set(pd.read_csv(marco, usecols=['intervencion_id'], dtype=str).intervencion_id)
    fuentes[str(marco.relative_to(RAIZ))] = sha256(marco)
    nuevos = []; planes = []
    for ruta in TANDAS:
        d = RAIZ/ruta; manifest = json.loads((d/'manifest.json').read_text(encoding='utf-8'))
        for nombre, huella in manifest['sha256_fuentes'].items():
            comprobar(sha256(RAIZ/nombre) == huella, 'Fuente alterada: '+nombre)
        for nombre, huella in manifest['sha256_salidas'].items():
            comprobar(sha256(d/nombre) == huella, 'Tanda alterada: '+nombre)
        tabla = pd.read_csv(d/'anotaciones_ia.csv', keep_default_na=False)
        altos = tabla[tabla.uso_propuesto.eq('hd_alta_confianza')]
        datos = json.loads((d/'documentos_hd_alta.json').read_text(encoding='utf-8'))
        comprobar(set(altos.intervencion_id) == {r['intervencion_id'] for r in datos}, 'Payload no coincide con altas')
        anotaciones = altos.set_index('intervencion_id')
        for r in datos:
            k = r['intervencion_id']; a = anotaciones.loc[k]
            comprobar(k not in ids_base|humanos and r['texto'] == corpus.loc[k,'texto'], 'ID/texto inválido')
            comprobar(r['meeting_id'] == corpus.loc[k,'meeting_id'], 'Reunión distinta')
            comprobar(hashlib.sha256(r['texto'].encode()).hexdigest() == r['sha256_texto'], 'Hash de texto distinto')
            comprobar(r['etiqueta'] in ['hawkish','dovish'] and r['etiqueta'] == a.etiqueta and
                      r['confianza'] == a.confianza == 'alta' and a.estado_revision == 'anotada', 'Etiqueta/confianza/estado inválidos')
            comprobar(not errores_anotacion(a.etiqueta,a.confianza,a.es_relevante,a.nota,a.frase_justificante,r['texto']) and
                      a.frase_justificante in r['texto'], 'Cita inválida')
        nuevos.extend(datos)
        planes.append(pd.read_csv(d/'plan_por_fold.csv'))
        for n in ['manifest.json','anotaciones_ia.csv','documentos_hd_alta.json','plan_por_fold.csv']:
            fuentes[ruta+'/'+n] = sha256(d/n)
    nuevos = pd.DataFrame(nuevos).sort_values('intervencion_id').reset_index(drop=True)
    comprobar(len(nuevos) == 59 and nuevos.intervencion_id.is_unique, 'La cohorte v1 debe tener 59 IDs únicos')
    comprobar(nuevos.etiqueta.value_counts().to_dict() == {'dovish':30,'hawkish':29}, 'Cohorte distinta')
    comprobar(not set(nuevos.texto.map(H.clave_texto)) & set(base.texto.map(H.clave_texto)), 'Copia normalizada de base')
    return m, base, folds, pd.DataFrame(ancla), nuevos, pd.concat(planes,ignore_index=True), fuentes


def purgar(nuevos, validacion, fold):
    reuniones = set(validacion.meeting_id); textos = set(validacion.texto.map(H.clave_texto))
    copia = nuevos.copy()
    copia['excluir_reunion'] = copia.meeting_id.isin(reuniones)
    copia['excluir_texto'] = copia.texto.map(H.clave_texto).isin(textos)
    copia['incluido'] = ~(copia.excluir_reunion | copia.excluir_texto)
    copia['fold'] = fold
    return copia[copia.incluido].copy(), copia[['fold','intervencion_id','meeting_id','etiqueta','excluir_reunion','excluir_texto','incluido']]


def verificar_ancla(actual, ancla):
    columnas = ['intervencion_id','meeting_id','fold','pred_a','pred_b','pred']
    a = actual[columnas].sort_values('intervencion_id').reset_index(drop=True)
    b = ancla[columnas].sort_values('intervencion_id').reset_index(drop=True)
    pd.testing.assert_frame_equal(a,b)


# ---- 2. B se ajusta exclusivamente con su train; A nunca ve ejemplos nuevos ----
def ajustar_b(train, val, pred_a):
    relevante = train.es_relevante.astype(str).eq('1')
    train = train[relevante]
    vector = TfidfVectorizer(**H.PARAMETROS_PALABRAS)
    matriz = vector.fit_transform(train.texto.tolist())
    modelo = LogisticRegression(**H.ANTERIOR.PARAMETROS_LR).fit(matriz,train.etiqueta)
    x = vector.transform(val.texto.tolist())
    b = modelo.predict(x)
    prob = modelo.predict_proba(x)
    final = np.where(np.asarray(pred_a) == 0,'neutral',b)
    dimensiones = {'n_train_b':len(train),'clases_train':train.etiqueta.value_counts().to_dict(),
                   'vocabulario_b':len(vector.vocabulary_),'iteraciones_b':modelo.n_iter_.tolist()}
    return b, final, prob, modelo.classes_.tolist(), dimensiones


def metricas(tabla):
    r = H.metricas(tabla.etiqueta,tabla.pred)
    matriz = confusion_matrix(tabla.etiqueta,tabla.pred,labels=H.CLASES)
    r.update(matriz=matriz.tolist(),h_a_d=int(matriz[0,1]),d_a_h=int(matriz[1,0]),
             hd_a_n=int(matriz[0,2]+matriz[1,2]),n_a_hd=int(matriz[2,0]+matriz[2,1]))
    return r


def resumir(predicciones):
    condiciones = {}
    for nombre in ['control','ampliado_59']:
        t = predicciones[predicciones.condicion.eq(nombre)]
        fs = [metricas(t[t.fold.eq(f)]) for f in range(1,6)]
        condiciones[nombre] = {'media_f1_hd':float(np.mean([r['f1_hd'] for r in fs])),
            'media_macro_f1':float(np.mean([r['macro_f1'] for r in fs])), 'por_fold':fs,'conjunto':metricas(t)}
    a,b = condiciones['control'],condiciones['ampliado_59'];ac,bc=a['conjunto'],b['conjunto']
    deltas = [y['f1_hd']-x['f1_hd'] for x,y in zip(a['por_fold'],b['por_fold'])]
    criterios = {'delta_hd':b['media_f1_hd']-a['media_f1_hd']>=.02,'folds_mejora':sum(d>0 for d in deltas)>=3,
        'macro':b['media_macro_f1']>=a['media_macro_f1']-.005,'recall_h':bc['recall_hawkish']>=ac['recall_hawkish']-.02,
        'recall_d':bc['recall_dovish']>=ac['recall_dovish']-.02,
        'menos_inversiones':bc['h_a_d']+bc['d_a_h']<ac['h_a_d']+ac['d_a_h'],'no_ocultar_en_n':bc['hd_a_n']<=ac['hd_a_n']}
    return {'condiciones':condiciones,'deltas_f1_hd':deltas,'criterios':criterios,
        'cumple_criterios_desarrollo':all(criterios.values()),'evaluacion_independiente':False,
        'modelo_adoptado':False,'nuevos_ejemplos':59,'referencias_modificadas':False,'filtro_a_modificado':False}


# ---- 3. Ensayo exclusivo y resultados auditables; no se guardan modelos ----
def ejecutar(salida=SALIDA):
    salida=Path(salida);exigir_salidas_nuevas(salida)
    m, base, folds, ancla, nuevos, planes, fuentes=cargar_cohorte()
    por_id=base.set_index('intervencion_id',drop=False)
    preparadas={};auditorias=[]
    for f in folds:
        val=por_id.loc[f['validacion']].reset_index(drop=True)
        extra,aud=purgar(nuevos,val,f['fold'])
        previo=planes[planes.fold.eq(f['fold']) & planes.intervencion_id.isin(nuevos.intervencion_id)]
        comprobar(set(extra.intervencion_id)==set(previo.loc[previo.potencialmente_incorporable.eq(1),'intervencion_id']), 'Purga difiere del plan registrado')
        preparadas[f['fold']]=extra;auditorias.append(aud)
    comprobar([len(preparadas[i]) for i in range(1,6)]==[53,51,52,50,53], 'Conteos de la cohorte distintos')
    for n in ['scripts/evaluar_ampliacion_tfidf.py','tests/test_ampliacion_tfidf.py','docs/PROTOCOLO_AMPLIACION_TFIDF_59_V1.md','requirements.txt']:
        fuentes[n]=sha256(RAIZ/n)
    salida.mkdir(parents=True)
    escribir(salida/'protocolo.json',{'version':'ampliacion_tfidf_59_v1','preparado_utc':datetime.now(timezone.utc).isoformat(),
        'paquete_base':m['paquete_id'],'tandas':TANDAS,'sha256_fuentes':fuentes,
        'parametros_a':H.ANTERIOR.PARAMETROS_TFIDF,'parametros_b':H.PARAMETROS_PALABRAS,'parametros_lr':H.ANTERIOR.PARAMETROS_LR,
        'condiciones':['control','ampliado_59'],'n_validacion':793,'nuevos_por_fold':[53,51,52,50,53],
        'fit_a':'solo train original; compartido entre condiciones',
        'fit_b':'relevantes del train respectivo; vocabulario/IDF y pesos balanced se recalculan dentro de train',
        'busqueda_hiperparametros':False,'python':platform.python_version(),'numpy':np.__version__,
        'pandas':pd.__version__,'sklearn':sklearn.__version__})
    pd.concat(auditorias,ignore_index=True).to_csv(salida/'inclusion_nuevos_por_fold.csv',index=False)
    predicciones=[];ejecuciones=[]
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        for f in folds:
            inicio=time.perf_counter();numero=f['fold']
            train=por_id.loc[f['train']].reset_index(drop=True);val=por_id.loc[f['validacion']].reset_index(drop=True)
            modelo=H.ajustar_modelos(train,solo_base=True)['H0_historica']
            a,b,pred=H.predecir(modelo,val.texto.tolist())
            control=val[['intervencion_id','meeting_id','etiqueta']].copy()
            control['fold']=numero;control['pred_a']=a;control['pred_b']=b;control['pred']=pred
            verificar_ancla(control,ancla[ancla.fold.eq(numero)])
            comprobar(control.etiqueta.tolist()==ancla.set_index('intervencion_id').loc[val.intervencion_id,'etiqueta_corregida_v2'].tolist(),'Referencias distintas')
            control['condicion']='control';predicciones.append(control)
            extra=preparadas[numero];ampliado=pd.concat([train,extra[train.columns]],ignore_index=True)
            b,pred,prob,clases,dim=ajustar_b(ampliado,val,a)
            t=control.copy();t['condicion']='ampliado_59';t['pred_b']=b;t['pred']=pred
            for j,c in enumerate(clases):t['prob_b_'+c]=prob[:,j]
            comprobar(np.isfinite(prob).all() and np.allclose(prob.sum(axis=1),1), 'Probabilidades inválidas')
            predicciones.append(t)
            ejecuciones.append({'fold':numero,'n_train_original':len(train),'n_train_b_original':int(train.es_relevante.eq(1).sum()),
                'n_nuevos':len(extra),'nuevos_por_clase':extra.etiqueta.value_counts().to_dict(),
                'n_validacion':len(val),'vocabulario_b_original':modelo['dimensiones']['vocabulario_palabras'],
                **dim,'control_reproduce_a_b_final':True,'a_identica':True,'segundos':time.perf_counter()-inicio})
            print(f'Fold {numero}: control exacto; +{len(extra)} ejemplos, terminado.',flush=True)
            del modelo
    tabla=pd.concat(predicciones,ignore_index=True)
    comprobar(len(tabla)==1586 and tabla.groupby('condicion').intervencion_id.nunique().eq(793).all(),'Predicciones incompletas')
    r=resumir(tabla)
    control=tabla[tabla.condicion.eq('control')].set_index('intervencion_id')
    amp=tabla[tabla.condicion.eq('ampliado_59')].set_index('intervencion_id').loc[control.index]
    cambios=control[['meeting_id','fold','etiqueta','pred_a','pred']].rename(columns={'pred':'pred_control'}).copy()
    cambios['pred_ampliado']=amp.pred
    cambios['cambio']=cambios.pred_control.ne(cambios.pred_ampliado)
    antes=cambios.pred_control.eq(cambios.etiqueta);ahora=cambios.pred_ampliado.eq(cambios.etiqueta)
    r.update(predicciones_cambiadas=int(cambios.cambio.sum()),errores_corregidos=int((~antes&ahora).sum()),errores_nuevos=int((antes&~ahora).sum()))
    ambiguos=set(m['cinco_ambiguos_hd_conocidos'])
    r['suplemento_sin_cinco_ambiguos']={nombre:metricas(tabla[tabla.condicion.eq(nombre)&~tabla.intervencion_id.isin(ambiguos)]) for nombre in ['control','ampliado_59']}
    r['criterios_sobre_todos_los_793']=True
    for n,h in fuentes.items():comprobar(sha256(RAIZ/n)==h,'Fuente modificada durante ensayo: '+n)
    tabla.to_csv(salida/'predicciones.csv',index=False);cambios.reset_index().to_csv(salida/'comparacion_casos.csv',index=False)
    escribir(salida/'metricas.json',r);escribir(salida/'ejecucion.json',ejecuciones)
    escribir(salida/'manifest.json',{'version':'ampliacion_tfidf_59_v1','sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},
        'modelo_guardado':False,'refit_global':False,'gold_306_abierto':False})
    print(json.dumps({n:r[n] for n in ['criterios','predicciones_cambiadas','errores_corregidos','errores_nuevos']},indent=2))
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,default=SALIDA)
    ejecutar(p.parse_args().salida)
