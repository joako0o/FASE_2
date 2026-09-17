"""Evalúa dosis sintéticas deduplicadas solo en etapa B; validación siempre real."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from entrenar_tfidf_supervision_v3 import (
    RAIZ, PARAMETROS_B, PARAMETROS_LR, cargar_datos, clave_texto,
    metricas_completas, sha256)
from evaluar_ampliacion_ia89_v3 import cargar_nuevos

POOL = RAIZ/'data/preparacion/dosis_sinteticas_post2020_v1/pool_sintetico_deduplicado.csv'
PREPARACION = RAIZ/'data/preparacion/dosis_sinteticas_post2020_v1'
FASE_B = RAIZ/'data/evaluacion/tfidf_supervision_v3_fase_b/predicciones.csv'
FASE_C = RAIZ/'data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv'
SALIDA = RAIZ/'data/evaluacion/dosis_sinteticas_tfidf_v3_v1'
DOSIS = [250,500,750,801]
BASES = ['B','C']


def guardar_json(ruta, datos):
    with Path(ruta).open('x',encoding='utf-8') as archivo:
        json.dump(datos,archivo,ensure_ascii=False,indent=2,allow_nan=False);archivo.write('\n')


def ajustar_b(train_real, sinteticos, val, pred_a):
    relevantes = train_real.relevancia_v3.eq('1')
    textos = pd.concat([train_real.loc[relevantes,'texto'], sinteticos.texto],ignore_index=True)
    etiquetas = pd.concat([train_real.loc[relevantes,'etiqueta_v3'], sinteticos.etiqueta_provisional],ignore_index=True)
    vector = TfidfVectorizer(**PARAMETROS_B)
    modelo = LogisticRegression(**PARAMETROS_LR).fit(vector.fit_transform(textos),etiquetas)
    pred_b = modelo.predict(vector.transform(val.texto))
    final = np.where(np.asarray(pred_a).astype(str)=='0','neutral',pred_b)
    return pred_b,final,{'n_train_b_real':int(relevantes.sum()),'n_train_b_sintetico':len(sinteticos),
                         'clases_sinteticas':sinteticos.etiqueta_provisional.value_counts().to_dict(),
                         'vocabulario_b':len(vector.vocabulary_),'iteraciones_b':modelo.n_iter_.tolist()}


def criterios(control,tratamiento):
    deltas=[tratamiento['por_fold'][str(f)]['f1_hd']-control['por_fold'][str(f)]['f1_hd'] for f in range(1,6)]
    return {
        'delta_media_folds_f1_hd_ge_002':tratamiento['media_folds_f1_hd']-control['media_folds_f1_hd']>=.02,
        'mejora_al_menos_3_folds':sum(x>0 for x in deltas)>=3,
        'macro_no_baja_mas_005':tratamiento['macro_f1']>=control['macro_f1']-.005,
        'precision_d_no_baja_mas_002':tratamiento['por_clase']['dovish']['precision']>=control['por_clase']['dovish']['precision']-.02,
        'recall_d_no_baja_mas_002':tratamiento['por_clase']['dovish']['recall']>=control['por_clase']['dovish']['recall']-.02,
        'menos_inversiones_h_d':tratamiento['h_d_cruzados']<control['h_d_cruzados'],
        'no_aumenta_neutral_a_direccion':tratamiento['neutral_a_direccion']<=control['neutral_a_direccion'],
    }


def ejecutar(salida=SALIDA):
    salida=Path(salida)
    nombres=['predicciones.csv','comparacion_condiciones.csv','metricas.json','ejecucion_folds.json',
             'protocolo.json','resumen.md','verificacion.json','manifest.json']
    if salida.exists():raise FileExistsError('No sobrescribir ensayo sintético')
    manifest=json.loads((PREPARACION/'manifest.json').read_text(encoding='utf-8'))
    for nombre,esperado in manifest['sha256_salidas'].items():
        if sha256(PREPARACION/nombre)!=esperado:raise ValueError('Preparación alterada: '+nombre)
    pool=pd.read_csv(POOL,dtype={'rango_en_clase':int,'dosis_minima':int},keep_default_na=False)
    if len(pool)!=801 or not pool.synthetic_id.is_unique:raise ValueError('Pool sintético inválido')
    base,_,fuentes_base=cargar_datos();nuevos,_=cargar_nuevos()
    ancla_b=pd.read_csv(FASE_B,dtype=str,keep_default_na=False).set_index('intervencion_id')
    ancla_c=pd.read_csv(FASE_C,dtype=str,keep_default_na=False).set_index('intervencion_id')
    if len(ancla_b)!=793 or len(ancla_c)!=793:raise ValueError('Anclas B/C incompletas')
    predicciones=[];ejecuciones=[]
    # Controles, una fila por ID/condición.
    for nombre,ancla,preda,predb,pred in [
        ('B_0',ancla_b,'pred_a_v3','pred_b_v3','pred_v3'),
        ('C_0',ancla_c,'pred_a_fase_c','pred_b_fase_c','pred_fase_c')]:
        for identificador,fila in ancla.iterrows():
            predicciones.append({'intervencion_id':identificador,'meeting_id':fila.meeting_id,
                'fold':int(fila.fold),'etiqueta_v3':fila.etiqueta_v3,'condicion':nombre,
                'pred_a':fila[preda],'pred_b':fila[predb],'pred':fila[pred]})
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        for fold in range(1,6):
            val=base[base.fold_validacion.eq(fold)].copy()
            previo=base[~base.fold_validacion.eq(fold)].copy();claves_val=set(val.texto.map(clave_texto))
            train_b=previo[~previo.texto.map(clave_texto).isin(claves_val)].copy()
            extra=nuevos[~nuevos.meeting_id.isin(set(val.meeting_id)) &
                         ~nuevos.texto.map(clave_texto).isin(claves_val)].copy()
            train_c=pd.concat([train_b,extra.reindex(columns=train_b.columns)],ignore_index=True)
            for base_nombre,train,ancla,preda in [
                ('B',train_b,ancla_b,'pred_a_v3'),('C',train_c,ancla_c,'pred_a_fase_c')]:
                pred_a=ancla.loc[val.index,preda].to_numpy()
                for dosis in DOSIS:
                    sint=pool[pool.dosis_minima.le(dosis)].copy()
                    if len(sint)!=dosis:raise ValueError('Dosis no anidada/completa')
                    pred_b,pred,dim=ajustar_b(train,sint,val,pred_a)
                    condicion=f'{base_nombre}_{dosis}'
                    for i,(identificador,fila) in enumerate(val.iterrows()):
                        predicciones.append({'intervencion_id':identificador,'meeting_id':fila.meeting_id,
                            'fold':fold,'etiqueta_v3':fila.etiqueta_v3,'condicion':condicion,
                            'pred_a':str(pred_a[i]),'pred_b':pred_b[i],'pred':pred[i]})
                    ejecuciones.append({'fold':fold,'base_real':base_nombre,'dosis':dosis,
                        'n_real_total':len(train),'n_ia89':0 if base_nombre=='B' else len(extra),**dim})
                    print(f'Fold {fold}: {condicion} terminado.',flush=True)
    tabla=pd.DataFrame(predicciones).sort_values(['condicion','fold','intervencion_id']).reset_index(drop=True)
    if len(tabla)!=7930 or not tabla.groupby('condicion').intervencion_id.nunique().eq(793).all():
        raise ValueError('Predicciones incompletas')
    condiciones={nombre:metricas_completas(grupo,'pred') for nombre,grupo in tabla.groupby('condicion')}
    resultados=[];evaluacion_criterios={}
    for base_nombre in BASES:
        control=condiciones[f'{base_nombre}_0']
        for dosis in DOSIS:
            nombre=f'{base_nombre}_{dosis}';m=condiciones[nombre];c=criterios(control,m)
            evaluacion_criterios[nombre]={'criterios':c,'cumple_todos':all(c.values())}
            resultados.append({'base':base_nombre,'dosis':dosis,
                'accuracy':m['accuracy'],'macro_f1':m['macro_f1'],'f1_hd':m['f1_hd'],
                'media_folds_f1_hd':m['media_folds_f1_hd'],'errores':m['errores'],
                'precision_d':m['por_clase']['dovish']['precision'],'recall_d':m['por_clase']['dovish']['recall'],
                'f1_d':m['por_clase']['dovish']['f1'],'inversiones_h_d':m['h_d_cruzados'],
                'neutral_a_direccion':m['neutral_a_direccion'],
                'delta_media_folds_f1_hd':m['media_folds_f1_hd']-control['media_folds_f1_hd']})
    metricas={'condiciones':condiciones,'resultados_dosis':resultados,'evaluacion_criterios':evaluacion_criterios,
              'alguna_dosis_cumple_todos':any(x['cumple_todos'] for x in evaluacion_criterios.values()),
              'validacion_exclusivamente_real':True,'sinteticos_solo_etapa_b':True,
              'motivo_no_entrenar_a':'Los sintéticos son todos relevantes y los 57 errores B previos no provenían de la puerta A.',
              'evaluacion_independiente':False,'modelo_adoptado':False}
    salida.mkdir(parents=True)
    tabla.to_csv(salida/'predicciones.csv',index=False,lineterminator='\n')
    pd.DataFrame(resultados).to_csv(salida/'comparacion_condiciones.csv',index=False,lineterminator='\n')
    guardar_json(salida/'metricas.json',metricas);guardar_json(salida/'ejecucion_folds.json',ejecuciones)
    fuentes={**fuentes_base,'pool':POOL,'preparacion_manifest':PREPARACION/'manifest.json',
             'fase_b':FASE_B,'fase_c':FASE_C,'script':Path(__file__)}
    guardar_json(salida/'protocolo.json',{
        'operacion':'Dosis fijadas 250/500/750/801, B y C por separado, sintéticos solo en clasificador B.',
        'criterios_exito_fijados':list(next(iter(evaluacion_criterios.values()))['criterios']),
        'solo_columna_predictora_sintetica':'texto','busqueda_hiperparametros':False,
        'fuentes_sha256':{k:sha256(v) for k,v in fuentes.items()},
        'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__})
    guardar_json(salida/'verificacion.json',{'controles_b_c_leidos_sin_modificar':True,
        'ids_reales_validacion':tabla.intervencion_id.nunique(),'condiciones':sorted(condiciones),
        'filas_prediccion':len(tabla),'dosis_anidadas':True,'copias_exactas_sintetico_real':0,
        'sinteticos_en_validacion':0})
    lineas=['# Curva de dosis sintética TF-IDF v3','','Validación exclusivamente real (793 IDs). Los sintéticos deduplicados se añadieron solo a la etapa H/D/N; B y C se compararon por separado.','',
        '| Base | Dosis | Accuracy | F1-HD | Media folds F1-HD | Precisión D | Recall D | Errores | H↔D | N→H/D |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for base_nombre in BASES:
        m=condiciones[f'{base_nombre}_0'];lineas.append(f"| {base_nombre} | 0 | {m['accuracy']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {m['por_clase']['dovish']['precision']:.6f} | {m['por_clase']['dovish']['recall']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['neutral_a_direccion']} |")
        for r in [x for x in resultados if x['base']==base_nombre]:
            lineas.append(f"| {base_nombre} | {r['dosis']} | {r['accuracy']:.6f} | {r['f1_hd']:.6f} | {r['media_folds_f1_hd']:.6f} | {r['precision_d']:.6f} | {r['recall_d']:.6f} | {r['errores']} | {r['inversiones_h_d']} | {r['neutral_a_direccion']} |")
    lineas+=['','Las etiquetas sintéticas son provisionales; ningún resultado autoriza adopción automática.']
    (salida/'resumen.md').write_text('\n'.join(lineas)+'\n',encoding='utf-8')
    guardar_json(salida/'manifest.json',{'sha256_salidas':{
        nombre:sha256(salida/nombre) for nombre in nombres if nombre!='manifest.json'}})
    return metricas


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,default=SALIDA)
    r=ejecutar(p.parse_args().salida);print(json.dumps({'resultados':r['resultados_dosis'],'alguna_dosis_cumple':r['alguna_dosis_cumple_todos']},ensure_ascii=False,indent=2))
