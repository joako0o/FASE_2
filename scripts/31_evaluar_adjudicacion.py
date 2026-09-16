"""Efecto de adjudicaciones aprobadas en la referencia TF-IDF; no ejecuta BETO.

--preparar congela fuentes/controles; --ejecutar ajusta solo dos condiciones
con los parámetros y folds históricos, sin abrir respuestas del examen de 306.
"""
# ---- 1. Parámetros y funciones históricas: sin modificar experimentos cerrados ----
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import confusion_matrix

from utilidades import cargar_script, exigir_salidas_nuevas, sha256

H = cargar_script('26_comparar_clasificadores_hd.py')
RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ/'data/evaluacion/adjudicacion_modelo_v1'
PROTOCOLO = RAIZ/'docs/PROTOCOLO_MODELO_ADJUDICADO_V1.md'
INFORME = RAIZ/'docs/EVALUACION_MODELO_ADJUDICADO_V1.md'
ACEPTACION = RAIZ/'data/auditoria/revision_entrenamiento_30_v1/devolucion_humana_v1/adjudicacion_aprobada_v1'
VARIANTES = ('original','adjudicada')
ESPERADAS = {'R01':'hawkish','R03':'neutral','R08':'dovish','R12':'hawkish','R17':'dovish','R21':'dovish'}


def escribir_json(ruta,valor):
    with Path(ruta).open('x',encoding='utf-8') as archivo:
        json.dump(valor,archivo,ensure_ascii=False,indent=2,allow_nan=False)
        archivo.write('\n')


def verificar_hashes(hashes):
    for nombre,huella in hashes.items():
        assert sha256(RAIZ/nombre)==huella,f'Archivo alterado: {nombre}'


# ---- 2. Capa en memoria: solo postura, IDs aprobados y fuera de validación ----
def aplicar_adjudicaciones(datos,asignacion,adjudicaciones):
    assert datos.intervencion_id.is_unique and asignacion.intervencion_id.is_unique
    assert adjudicaciones.intervencion_id.is_unique and adjudicaciones.caso_id.is_unique
    assert set(datos.intervencion_id)==set(asignacion.intervencion_id)
    assert adjudicaciones.estado.eq('aprobada_por_investigador').all()
    assert adjudicaciones.procedencia.eq('propuesta_agente_aceptada_tras_comparacion').all()
    assert adjudicaciones.etiqueta_adjudicada.isin(H.CLASES).all()
    resultado=datos.copy(deep=True)
    filas=resultado.set_index('intervencion_id')
    folds=asignacion.set_index('intervencion_id').fold_validacion
    cambios=[]
    for registro in adjudicaciones.itertuples():
        identificador=registro.intervencion_id
        assert identificador in filas.index,'Adjudicación ajena al entrenamiento'
        fila=filas.loc[identificador]
        assert folds.loc[identificador]==0,'No adjudicar etiquetas de validación'
        assert str(fila.es_relevante)=='1','No imputar relevancia humana ni cambiar la puerta A'
        assert fila.etiqueta==registro.etiqueta_ia_original,'Etiqueta IA de origen discordante'
        assert hashlib.sha256(fila.texto.encode()).hexdigest()==registro.sha256_texto_original,'Texto discordante'
        mascara=resultado.intervencion_id.eq(identificador)
        resultado.loc[mascara,'etiqueta']=registro.etiqueta_adjudicada
        cambios.append({'caso_id':registro.caso_id,'intervencion_id':identificador,
            'etiqueta_ia_original':fila.etiqueta,'etiqueta_experimental':registro.etiqueta_adjudicada,
            'cambia_ia':fila.etiqueta!=registro.etiqueta_adjudicada,
            'relevancia_conservada_de_ia':str(fila.es_relevante),
            'procedencia':'adjudicacion_asistida_aprobada','fold_validacion':0})
    pd.testing.assert_frame_equal(datos.drop(columns='etiqueta'),resultado.drop(columns='etiqueta'))
    assert not (datos.etiqueta.ne(resultado.etiqueta) & ~datos.intervencion_id.isin(adjudicaciones.intervencion_id)).any()
    return resultado,pd.DataFrame(cambios)


def cargar():
    manifiesto=json.loads((ACEPTACION/'manifest.json').read_text())
    verificar_hashes(manifiesto['sha256_insumos'])
    verificar_hashes(manifiesto['sha256_salidas'])
    aprobacion=json.loads((ACEPTACION/'aceptacion.json').read_text())
    assert aprobacion['estado']=='aprobada_por_investigador'
    assert aprobacion['mensaje_confirmacion_usuario']=='acepto todas'
    adjudicaciones=pd.read_csv(ACEPTACION/'adjudicaciones.csv',dtype=str,keep_default_na=False)
    pd.testing.assert_frame_equal(adjudicaciones,pd.DataFrame(aprobacion['adjudicaciones']))
    assert dict(zip(adjudicaciones.caso_id,adjudicaciones.etiqueta_adjudicada))==ESPERADAS
    datos=H.ANTERIOR.BASELINE.cargar_muestra()  # IA + L0; del examen solo IDs de exclusión.
    assert len(datos)==1352
    anterior=json.loads((H.RUTA_SALIDA/'protocolo.json').read_text())
    for nombre,huella in anterior['sha256_particiones'].items():
        assert sha256(H.RUTA_SALIDA/nombre)==huella,nombre
    asignacion=pd.read_csv(H.RUTA_SALIDA/'asignacion_folds.csv')
    assert datos.intervencion_id.tolist()==asignacion.intervencion_id.tolist()
    assert datos.meeting_id.tolist()==asignacion.meeting_id.tolist()
    particiones,recalculada,exclusiones,auditoria=H.particionar(datos,asignacion.fold_validacion.eq(0).to_numpy())
    pd.testing.assert_frame_equal(recalculada,asignacion)
    pd.testing.assert_frame_equal(exclusiones,pd.read_csv(H.RUTA_SALIDA/'exclusiones_train.csv'))
    pd.testing.assert_frame_equal(auditoria,pd.read_csv(H.RUTA_SALIDA/'auditoria_folds.csv'))
    adjudicada,cambios=aplicar_adjudicaciones(datos,asignacion,adjudicaciones)
    assert len(cambios)==6 and int(cambios.cambia_ia.sum())==3
    control=[]
    for fold,_,train,val in particiones:
        assert set(adjudicaciones.intervencion_id)<=set(datos.iloc[train].intervencion_id)
        assert not set(adjudicaciones.intervencion_id)&set(datos.iloc[val].intervencion_id)
        pd.testing.assert_frame_equal(datos.iloc[val],adjudicada.iloc[val])
        control.append({'fold':fold,'n_train':len(train),'n_val':len(val),
            'adjudicaciones_en_train':6,'cambios_ia_en_train':3,'cambios_en_validacion':0})
    manifiesto_ancla=json.loads((H.RUTA_SALIDA/'manifest.json').read_text())
    assert sha256(H.RUTA_SALIDA/'predicciones_validacion.csv')==manifiesto_ancla['sha256_salidas']['predicciones_validacion.csv']
    ancla=pd.read_csv(H.RUTA_SALIDA/'predicciones_validacion.csv')
    ancla=ancla[ancla.variante.eq('B0_limpia')].copy()
    assert len(ancla)==793 and ancla.intervencion_id.is_unique
    return datos,adjudicada,particiones,cambios,pd.DataFrame(control),ancla


# ---- 3. Preparación exclusiva y huellas antes de cualquier fit ----
def preparar(salida=SALIDA,informe=INFORME):
    salida,informe=Path(salida),Path(informe)
    exigir_salidas_nuevas(salida,informe)
    _,_,_,cambios,control,_=cargar()
    archivos=list((RAIZ/'scripts').glob('*.py'))+list((RAIZ/'data/etiquetas').glob('etiquetas_*.csv'))
    archivos += [RAIZ/'data/L0/corpus.csv',RAIZ/'requirements.txt',PROTOCOLO,
        RAIZ/'tests/test_modelo_adjudicado.py',RAIZ/'docs/codebook_v2.md']
    archivos += [RAIZ/'data/muestras'/n for n in ['piloto_300_tandas.csv','escalado_tandas.csv','gold_ciego_300.csv']]
    archivos += list(ACEPTACION.glob('*.json'))+list(ACEPTACION.glob('*.csv'))
    aprobacion=json.loads((ACEPTACION/'manifest.json').read_text())
    archivos += [RAIZ/n for n in aprobacion['sha256_insumos']]
    archivos += [H.RUTA_SALIDA/n for n in ['protocolo.json','manifest.json','asignacion_folds.csv','exclusiones_train.csv','auditoria_folds.csv','predicciones_validacion.csv']]
    fuentes={str(p.relative_to(RAIZ)):sha256(p) for p in sorted(set(archivos))}
    historico=json.loads((H.RUTA_SALIDA/'protocolo.json').read_text())
    for nombre,huella in fuentes.items():
        if nombre in historico['sha256_insumos']:
            assert huella==historico['sha256_insumos'][nombre],nombre
    # El checkpoint ignorado y ausente no es insumo: ajustamos modelos efímeros nuevos.
    salida.mkdir(parents=True)
    cambios.to_csv(salida/'cambios_entrenamiento.csv',index=False)
    control.to_csv(salida/'control_folds.csv',index=False)
    escribir_json(salida/'protocolo.json',{'version':'adjudicacion_modelo_v1',
        'preparado_utc':datetime.now(timezone.utc).isoformat(),'sha256_insumos':fuentes,
        'sha256_preparacion':{p.name:sha256(p) for p in sorted(salida.glob('*.csv'))},
        'variantes':VARIANTES,'parametros_a':H.ANTERIOR.PARAMETROS_TFIDF,
        'parametros_b':H.PARAMETROS_PALABRAS,'parametros_lr':H.ANTERIOR.PARAMETROS_LR,
        'metrica_principal':'media_fold_f1_hd','beto_ejecutado':False,
        'python':platform.python_version(),'sklearn':sklearn.__version__,'numpy':np.__version__,'pandas':pd.__version__})
    print('Preparado antes del fit: seis adjudicaciones, tres cambios IA; validación intacta.')


def verificar_preparacion(salida):
    protocolo=json.loads((salida/'protocolo.json').read_text())
    assert protocolo['variantes']==list(VARIANTES)
    verificar_hashes(protocolo['sha256_insumos'])
    for nombre,huella in protocolo['sha256_preparacion'].items():assert sha256(salida/nombre)==huella,nombre
    return protocolo


# ---- 4. Métricas descriptivas; no elegir la verdad por su score contra IA ----
def resumir(predicciones,folds):
    resumen={}
    for variante in VARIANTES:
        sub=predicciones[predicciones.variante.eq(variante)]
        puntos=folds[folds.variante.eq(variante)]
        resumen[variante]={'media_fold_f1_hd':float(puntos.f1_hd.mean()),
            'sd_fold_f1_hd':float(puntos.f1_hd.std(ddof=1)),
            'media_fold_macro_f1':float(puntos.macro_f1.mean()),
            'conjunto':H.metricas(sub.etiqueta,sub.pred),
            'matriz_filas_reales_columnas_pred':confusion_matrix(sub.etiqueta,sub.pred,labels=H.CLASES).tolist()}
    base=predicciones[predicciones.variante.eq('original')].set_index('intervencion_id')
    nueva=predicciones[predicciones.variante.eq('adjudicada')].set_index('intervencion_id').loc[base.index]
    assert base.etiqueta.equals(nueva.etiqueta)
    bien=base.pred.eq(base.etiqueta);ahora=nueva.pred.eq(nueva.etiqueta)
    puntos=folds.pivot(index='fold',columns='variante',values='f1_hd')
    deltas=puntos.adjudicada-puntos.original
    return {'condiciones':resumen,'orden_clases':list(H.CLASES),'delta_f1_hd_medio':float(deltas.mean()),
        'deltas_f1_hd_por_fold':{str(k):float(v) for k,v in deltas.items()},
        'folds_mejora':int(deltas.gt(0).sum()),'predicciones_finales_distintas':int(base.pred.ne(nueva.pred).sum()),
        'errores_corregidos':int((~bien&ahora).sum()),'errores_nuevos':int((bien&~ahora).sum()),
        'interpretacion':'Desarrollo IA reutilizado; no evidencia de mejora humana ni evaluación BETO.',
        'entrenamiento_canonico_modificado':False,'modelo_persistido':False,'beto_ejecutado':False,'examen_306_abierto':False}


def redactar(resumen):
    lineas=['# Referencia TF-IDF tras adjudicación: resultado', '',
        '**Se entrenaron las dos condiciones TF-IDF. BETO no se ejecutó.**', '',
        'Mismos parámetros, textos, cinco folds purgados y 793 etiquetas IA de validación. Solo tres etiquetas de train cambian: R01 N→H, R03 D→N y R12 D→H. Seis adjudicaciones se aplican en una vista experimental; tres ya coincidían con IA. Originales y relevancia IA intactos.', '',
        '| Condición | F1 H/D medio | Macro-F1 medio | Errores | Recall H | Recall D |', '|---|---:|---:|---:|---:|---:|']
    for v in VARIANTES:
        r=resumen['condiciones'][v];m=r['conjunto']
        lineas.append(f'| {v} | {r["media_fold_f1_hd"]:.6f} | {r["media_fold_macro_f1"]:.6f} | {m["errores"]} | {m["recall_hawkish"]:.6f} | {m["recall_dovish"]:.6f} |')
    lineas+=['',f'- Delta F1 H/D medio: **{resumen["delta_f1_hd_medio"]:+.6f}**; mejora en {resumen["folds_mejora"]}/5 folds.',
        f'- {resumen["predicciones_finales_distintas"]} predicciones finales distintas; {resumen["errores_corregidos"]} errores corregidos y {resumen["errores_nuevos"]} nuevos, respecto de la misma referencia IA.',
        '- La condición original reproduce exactamente A, B y salida final de B0 limpia del experimento 26. La puerta A y vocabularios no cambian entre condiciones.', '',
        '## Interpretación y cierre', '',
        'Esto aísla el efecto de tres etiquetas, no una mejora de comprensión del lenguaje. Las adjudicaciones no se revierten por bajar un score contra IA; tampoco se extrapolan al corpus. La validación ya se utilizó en desarrollo y puede contener etiquetas discutibles. No es test nuevo ni confirmación humana.', '',
        'No se ajustaron n-gramas/C/umbrales ni se seleccionó otra variante tras medir. Se conserva la referencia adjudicada para comparar BETO con exactamente la misma supervisión cuando sus pesos sean accesibles. El modelo histórico no se reemplazó; estos ajustes por fold son efímeros, sin refit final o scoring general.', '',
        '## BETO y textos largos', '',
        'El acceso a config/API de Hugging Face volvió a fallar con TLS EOF y no hay GPU detectada. No hay resultados de BETO ni bibliotecas/pesos grandes descargados. El protocolo fija cobertura completa por segmentos, agregación por intervención y un ensayo sin búsqueda de hiperparámetros; ese runner todavía no está implementado ni validado con pesos reales. No confundir el diseño con una ejecución.', '',
        '## Reproducir', '',
        '```bash', 'python scripts/31_evaluar_adjudicacion.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/31_evaluar_adjudicacion.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        '```', '',
        '[Protocolo previo](PROTOCOLO_MODELO_ADJUDICADO_V1.md) · [Aceptación humana asistida](ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md).', '',
        'Las nueve pruebas de recepción anteriores no son las pruebas de este entrenamiento. La verificación/reproducción de esta unidad se registra en su propio `reproducibilidad.json`. No se abre el libro de 306 respuestas.','']
    return '\n'.join(lineas)


# ---- 5. Ejecución exclusiva: entrenamiento, ancla exacta e integridad final ----
def ejecutar(salida=SALIDA,informe=INFORME):
    salida,informe=Path(salida),Path(informe)
    exigir_salidas_nuevas(informe,*[salida/n for n in ['predicciones_validacion.csv','resultados_folds.csv','metricas.json','manifest.json']])
    protocolo=verificar_preparacion(salida)
    datos,adjudicada,particiones,cambios,control,ancla=cargar()
    pd.testing.assert_frame_equal(cambios,pd.read_csv(salida/'cambios_entrenamiento.csv',dtype={'relevancia_conservada_de_ia':str}))
    pd.testing.assert_frame_equal(control,pd.read_csv(salida/'control_folds.csv'))
    predicciones=[];resultados=[]
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        for fold,_,train,val in particiones:
            puerta=None;dimensiones=None
            for variante,vista in [('original',datos),('adjudicada',adjudicada)]:
                modelo=H.ajustar_modelos(vista.iloc[train],solo_base=True)['H0_historica']
                pred_a,pred_b,pred=H.predecir(modelo,datos.iloc[val].texto.tolist())
                if variante=='original':
                    puerta=pred_a;dimensiones=modelo['dimensiones']
                    vocabularios=(modelo['vector_a'].vocabulary_,modelo['vista'].palabras.vocabulary_)
                    idf=(modelo['vector_a'].idf_,modelo['vista'].palabras.idf_)
                else:
                    np.testing.assert_array_equal(pred_a,puerta)
                    assert vocabularios==(modelo['vector_a'].vocabulary_,modelo['vista'].palabras.vocabulary_)
                    np.testing.assert_array_equal(idf[0],modelo['vector_a'].idf_)
                    np.testing.assert_array_equal(idf[1],modelo['vista'].palabras.idf_)
                    for k in ['vocabulario_a','vocabulario_palabras','vocabulario_caracteres','n_train_a','n_train_b']:
                        assert dimensiones[k]==modelo['dimensiones'][k],k
                tabla=datos.iloc[val][['intervencion_id','meeting_id','etiqueta','es_relevante']].copy()
                tabla['fold']=fold;tabla['variante']=variante
                tabla['pred_a']=pred_a;tabla['pred_b']=pred_b;tabla['pred']=pred
                predicciones.append(tabla)
                resultados.append({'fold':fold,'variante':variante,**modelo['dimensiones'],**H.metricas(tabla.etiqueta,pred)})
                print(f'Fold {fold}: {variante} terminado.',flush=True)
                del modelo
    predicciones=pd.concat(predicciones,ignore_index=True);folds=pd.DataFrame(resultados)
    columnas=['intervencion_id','meeting_id','etiqueta','fold','pred_a','pred_b','pred']
    actual=predicciones[predicciones.variante.eq('original')][columnas].sort_values('intervencion_id').reset_index(drop=True)
    previo=ancla[columnas].sort_values('intervencion_id').reset_index(drop=True)
    pd.testing.assert_frame_equal(actual,previo)
    for variante in VARIANTES:
        sub=predicciones[predicciones.variante.eq(variante)]
        assert len(sub)==793 and sub.intervencion_id.is_unique
    resumen=resumir(predicciones,folds)
    verificar_hashes(protocolo['sha256_insumos'])
    predicciones.to_csv(salida/'predicciones_validacion.csv',index=False)
    folds.to_csv(salida/'resultados_folds.csv',index=False)
    escribir_json(salida/'metricas.json',resumen)
    informe.parent.mkdir(parents=True,exist_ok=True)
    with informe.open('x',encoding='utf-8') as archivo:archivo.write(redactar(resumen))
    escribir_json(salida/'manifest.json',{'finalizado_utc':datetime.now(timezone.utc).isoformat(),
        'sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},
        'sha256_informe':sha256(informe),'ancla_b0_reproducida':True,'beto_ejecutado':False})
    print(json.dumps(resumen,ensure_ascii=False,indent=2))
    return resumen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modos=parser.add_mutually_exclusive_group(required=True)
    modos.add_argument('--preparar',action='store_true');modos.add_argument('--ejecutar',action='store_true')
    parser.add_argument('--salida',type=Path,default=SALIDA)
    parser.add_argument('--informe',type=Path,default=INFORME)
    args=parser.parse_args()
    (preparar if args.preparar else ejecutar)(args.salida,args.informe)


if __name__=='__main__':main()
