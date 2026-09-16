"""Ronda cerrada de clasificadores H/D: purga textual, cinco candidatos y ancla.

No es BETO: no se pudieron adquirir sus pesos. Sin gold humano, fuentes externas,
refit final ni modelos persistidos. Primero --preparar; después --ejecutar.
"""
# ---- 1. Parámetros prefijados y dependencias históricas inmutables ----
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time
import warnings

import numpy as np
import pandas as pd
import scipy
from scipy.sparse import hstack
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer, strip_accents_unicode
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize
from sklearn.svm import LinearSVC

import config
import representaciones_contextuales as R
from utilidades import cargar_script, exigir_salidas_nuevas, norm, sha256

L = cargar_script('22_seleccionar_longitud_ngramas.py')
ANTERIOR = L.ANTERIOR
ESCRIBIR = ANTERIOR.ESCRITURA.escribir_json
CANDIDATAS = ('B0_limpia','B1_svm','B2_lr_mixta','B3_svm_mixta','B4_jerarquica')
VARIANTES = ('H0_historica',) + CANDIDATAS
CLASES = ANTERIOR.L.CLASES
PARAMETROS_PALABRAS = {**ANTERIOR.PARAMETROS_TFIDF,'ngram_range':(1,4)}
PARAMETROS_CARACTERES = {**ANTERIOR.PARAMETROS_TFIDF,'analyzer':'char_wb',
                       'ngram_range':(3,5),'max_features':50000}
PARAMETROS_SVM = {'C':1.0,'class_weight':'balanced','loss':'squared_hinge',
                 'penalty':'l2','dual':'auto','max_iter':10000,'tol':.0001,'random_state':20260915}
TOLERANCIAS = {'delta_hd':.02,'folds_mejora':3,'perdida_macro':.005,
              'perdida_recall':.02,'perdida_conductual':.05}
RUTA_SALIDA = config.RUTA_DATOS / 'evaluacion/clasificadores_hd_v1'
RUTA_PROTOCOLO = config.RUTA_REPO / 'docs/PROTOCOLO_CLASIFICADORES_HD_V1.md'
RUTA_INFORME = config.RUTA_REPO / 'docs/EVALUACION_CLASIFICADORES_HD_V1.md'


# ---- 2. Misma validación, exclusión explícita de copias de cada train ----
def clave_texto(texto):
    return strip_accents_unicode(norm(texto).lower())


def particionar(datos, mascara):
    originales, asignacion = L.asignar_folds(datos, mascara)
    claves = datos.texto.map(clave_texto)
    particiones, exclusiones, auditoria = [], [], []
    for numero, train, val in originales:
        coinciden = claves.iloc[train].isin(set(claves.iloc[val])).to_numpy()
        limpio = np.asarray(train)[~coinciden]
        retirados = np.asarray(train)[coinciden]
        assert not set(claves.iloc[limpio]) & set(claves.iloc[val])
        assert not set(datos.iloc[limpio].meeting_id) & set(datos.iloc[val].meeting_id)
        assert set(datos.iloc[limpio].etiqueta) == set(CLASES)
        for posicion in retirados:
            fila = datos.iloc[posicion]
            exclusiones.append({'fold':numero,'intervencion_id':fila.intervencion_id,
                'meeting_id':fila.meeting_id,'era_descubrimiento':bool(mascara[posicion]),
                'sha256_texto_normalizado':hashlib.sha256(claves.iloc[posicion].encode()).hexdigest()})
        auditoria.append({'fold':numero,'n_train_original':len(train),'n_train_limpio':len(limpio),
            'n_retirados':len(retirados),'n_descubrimiento_retirados':int(mascara[retirados].sum()),
            'n_val':len(val),'n_val_con_copia_previa':int(claves.iloc[val].isin(set(claves.iloc[train])).sum()),
            'n_val_con_copia_despues':0,'n_textos_unicos_val':claves.iloc[val].nunique()})
        particiones.append((numero,np.asarray(train),limpio,np.asarray(val)))
    columnas = ['fold','intervencion_id','meeting_id','era_descubrimiento','sha256_texto_normalizado']
    return particiones,asignacion,pd.DataFrame(exclusiones,columns=columnas),pd.DataFrame(auditoria)


def preparar(salida=RUTA_SALIDA,informe=RUTA_INFORME):
    salida,informe = Path(salida),Path(informe)
    exigir_salidas_nuevas(salida,informe)
    datos,mascara,_,fuentes = L.cargar_insumos()
    _,asignacion,exclusiones,auditoria = particionar(datos,mascara)
    archivos = list((config.RUTA_REPO/'scripts').glob('*.py')) + [RUTA_PROTOCOLO,
        config.RUTA_REPO/'tests/test_clasificadores_hd.py',
        L.RUTA_SALIDA/'predicciones_validacion.csv',config.RUTA_REPO/'modelos/tfidf_gold_v1.joblib']
    fuentes.update({str(p.relative_to(config.RUTA_REPO)):sha256(p) for p in archivos})
    protegidos = json.loads((ANTERIOR.L.RUTA_VALIDACION/'integridad_cierre.json').read_text())['sha256_fuentes']
    fuentes.update(protegidos)
    for nombre,huella in fuentes.items():
        assert sha256(config.RUTA_REPO/nombre)==huella,nombre
    salida.mkdir(parents=True)
    tablas = {'asignacion_folds':asignacion,'exclusiones_train':exclusiones,'auditoria_folds':auditoria}
    for nombre,tabla in tablas.items():
        tabla.to_csv(salida/(nombre+'.csv'),index=False)
    ESCRIBIR(salida/'protocolo.json',{
        'version':'clasificadores_hd_v1','fecha_preparacion_utc':datetime.now(timezone.utc).isoformat(),
        'sha256_insumos':fuentes,'sha256_particiones':{n+'.csv':sha256(salida/(n+'.csv')) for n in tablas},
        'variantes':VARIANTES,'candidatas':CANDIDATAS,'tolerancias':TOLERANCIAS,
        'metrica_principal':'Media por fold de (F1_H + F1_D)/2, sobre todas las filas.',
        'parametros_palabras':PARAMETROS_PALABRAS,'parametros_caracteres':PARAMETROS_CARACTERES,
        'parametros_lr':ANTERIOR.PARAMETROS_LR,'parametros_svm':PARAMETROS_SVM,
        'bateria_conocida':R.CASOS_CONDUCTUALES,'pares_invariantes':R.PARES_INVARIANTES,
        'versiones':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
                    'scipy':scipy.__version__,'scikit_learn':sklearn.__version__},
        'beto_ejecutado':False,'motivo_beto':'Sin pesos locales; petición HF config.json falló TLS EOF; sin GPU.',
        'gold_abierto_o_predicho':False,'datos_externos_usados':False,'refit_final_o_reemplazo':False})
    print('Protocolo preparado antes del fit.',flush=True)
    print(auditoria.to_string(index=False),flush=True)


def verificar(salida):
    protocolo = json.loads((salida/'protocolo.json').read_text())
    assert protocolo['variantes']==list(VARIANTES)
    assert protocolo['tolerancias']==TOLERANCIAS
    for nombre,huella in protocolo['sha256_insumos'].items():
        assert sha256(config.RUTA_REPO/nombre)==huella,nombre
    for nombre,huella in protocolo['sha256_particiones'].items():
        assert sha256(salida/nombre)==huella,nombre
    return protocolo


# ---- 3. Representaciones y modelos: todo aprendizaje restringido a train ----
class VistaTfidf:
    """Palabras o palabras+caracteres; mezcla L2 global, sin aprender de transform."""
    def __init__(self,mixta=False):
        self.palabras = TfidfVectorizer(**PARAMETROS_PALABRAS)
        self.caracteres = TfidfVectorizer(**PARAMETROS_CARACTERES) if mixta else None

    def fit_transform(self,textos):
        palabras = self.palabras.fit_transform(textos)
        if self.caracteres is None:
            return palabras
        return normalize(hstack([palabras,self.caracteres.fit_transform(textos)],format='csr'),norm='l2')

    def transform(self,textos):
        palabras = self.palabras.transform(textos)
        if self.caracteres is None:
            return palabras
        return normalize(hstack([palabras,self.caracteres.transform(textos)],format='csr'),norm='l2')

    def dimensiones(self):
        return {'vocabulario_palabras':len(self.palabras.vocabulary_),
                'vocabulario_caracteres':len(self.caracteres.vocabulary_) if self.caracteres else 0}


def ajustar_modelos(train,solo_base=False):
    vector_a = TfidfVectorizer(**ANTERIOR.PARAMETROS_TFIDF)
    relevantes = train.es_relevante.astype(str).eq('1').to_numpy()
    modelo_a = LogisticRegression(**ANTERIOR.PARAMETROS_LR).fit(vector_a.fit_transform(train.texto),relevantes.astype(int))
    textos = train.loc[relevantes,'texto'].tolist()
    etiquetas = train.loc[relevantes,'etiqueta'].to_numpy()
    direccionales = etiquetas!='neutral'
    assert set(etiquetas)==set(CLASES)
    vistas,matrices = {},{}
    for mixta in ([False] if solo_base else [False,True]):
        vista = VistaTfidf(mixta)
        matrices[mixta] = vista.fit_transform(textos)
        vistas[mixta] = vista
    modelos = {}
    for variante in (['H0_historica'] if solo_base else CANDIDATAS):
        mixta = variante in ('B2_lr_mixta','B3_svm_mixta')
        matriz = matrices[mixta]
        clasificador = LinearSVC(**PARAMETROS_SVM) if variante in ('B1_svm','B3_svm_mixta') else LogisticRegression(**ANTERIOR.PARAMETROS_LR)
        puerta = None
        if variante=='B4_jerarquica':
            puerta = LogisticRegression(**ANTERIOR.PARAMETROS_LR).fit(matriz,direccionales.astype(int))
            clasificador.fit(matriz[direccionales],etiquetas[direccionales])
        else:
            clasificador.fit(matriz,etiquetas)
        modelos[variante] = {'vector_a':vector_a,'modelo_a':modelo_a,'vista':vistas[mixta],
            'clasificador':clasificador,'puerta':puerta,'dimensiones':{
                'n_train_a':len(train),'n_train_b':len(textos),'n_train_hd':int(direccionales.sum()),
                'vocabulario_a':len(vector_a.vocabulary_),**vistas[mixta].dimensiones()}}
    return modelos


def predecir(modelo,textos):
    pred_a = modelo['modelo_a'].predict(modelo['vector_a'].transform(textos))
    matriz = modelo['vista'].transform(textos)
    pred_b = modelo['clasificador'].predict(matriz)
    if modelo['puerta'] is not None:
        pred_b = np.where(modelo['puerta'].predict(matriz)==1,pred_b,'neutral')
    return pred_a,pred_b,np.where(pred_a==0,'neutral',pred_b)


# ---- 4. Métricas H/D sin omitir falsas alarmas sobre neutrales ----
def metricas(reales,pred):
    resultado = ANTERIOR.metricas(reales,pred)
    reales,pred = np.asarray(reales),np.asarray(pred)
    direccionales = np.isin(reales,['hawkish','dovish'])
    bien = reales==pred
    resultado.update(f1_hd=(resultado['f1_hawkish']+resultado['f1_dovish'])/2,
        recall_hd_balanceado=(resultado['recall_hawkish']+resultado['recall_dovish'])/2,
        acierto_sobre_hd=float(bien[direccionales].mean()) if direccionales.any() else 0.,
        n_hd=int(direccionales.sum()),errores=int((~bien).sum()),
        errores_hd=int((~bien & direccionales & np.isin(pred,['hawkish','dovish'])).sum()),
        neutral_a_direccion=int((~bien & ~direccionales).sum()),
        direccion_a_neutral=int((~bien & direccionales & (pred=='neutral')).sum()))
    return resultado


def referencias(train,n):
    """Constantes elegidas con train; nunca se consulta la clase real de cada fila."""
    mayoritaria = train.etiqueta.value_counts().idxmax()
    hd = train[train.etiqueta.isin(['hawkish','dovish'])].etiqueta.value_counts().idxmax()
    return {'mayoritaria':np.repeat(mayoritaria,n),'mayoritaria_hd':np.repeat(hd,n)}


def resumir(predicciones,folds,conducta):
    base = predicciones[predicciones.variante.eq('B0_limpia')].set_index('intervencion_id')
    puntos_base = folds[folds.variante.eq('B0_limpia')].set_index('fold')
    filas = []
    for variante in VARIANTES:
        sub = predicciones[predicciones.variante.eq(variante)].set_index('intervencion_id').loc[base.index]
        puntos = folds[folds.variante.eq(variante)].set_index('fold')
        pruebas = conducta[conducta.variante.eq(variante)]
        invariantes = []
        for _,prueba in pruebas.groupby('fold'):
            por_id = prueba.set_index('caso_id').pred
            invariantes += [por_id[a]==por_id[b] for a,b in R.PARES_INVARIANTES]
        bien,bien_base = sub.pred.eq(sub.etiqueta),base.pred.eq(base.etiqueta)
        filas.append({'variante':variante,**metricas(sub.etiqueta,sub.pred),
            'f1_hd_media':float(puntos.f1_hd.mean()),'f1_hd_sd':float(puntos.f1_hd.std(ddof=1)),
            'macro_f1_media':float(puntos.macro_f1.mean()),'macro_f1_sd':float(puntos.macro_f1.std(ddof=1)),
            'delta_hd':float((puntos.f1_hd-puntos_base.f1_hd).mean()),
            'delta_macro':float((puntos.macro_f1-puntos_base.macro_f1).mean()),
            'folds_mejora':int((puntos.f1_hd>puntos_base.f1_hd).sum()),
            'corregidos':int((~bien_base & bien).sum()),'nuevos':int((bien_base & ~bien).sum()),
            'exactitud_conductual':float(pruebas.pred.eq(pruebas.etiqueta).mean()),
            'invariancia':float(np.mean(invariantes))})
    tabla = pd.DataFrame(filas)
    tabla['cumple_para_confirmar'] = criterios(tabla)
    return tabla


def criterios(tabla):
    base = tabla[tabla.variante.eq('B0_limpia')].iloc[0]
    return (tabla.variante.isin(CANDIDATAS[1:]) &
        tabla.delta_hd.ge(TOLERANCIAS['delta_hd']) & tabla.folds_mejora.ge(TOLERANCIAS['folds_mejora']) &
        tabla.delta_macro.ge(-TOLERANCIAS['perdida_macro']) &
        tabla.recall_hawkish.ge(base.recall_hawkish-TOLERANCIAS['perdida_recall']) &
        tabla.recall_dovish.ge(base.recall_dovish-TOLERANCIAS['perdida_recall']) &
        tabla.exactitud_conductual.ge(base.exactitud_conductual-TOLERANCIAS['perdida_conductual']))


# ---- 5. Informe reproducible: distinguir desarrollo, test humano y bloqueo BETO ----
def construir_informe(tabla,resumen,ingenuas,auditoria):
    lineas = ['# Comparación de clasificadores con foco en H/D', '',
        f'**Mejor candidato observado: {resumen["mejor_observado"]}.** Variantes que cumplen el criterio previo: **{", ".join(resumen["elegibles"]) or "ninguna"}**.', '',
        '**Estos resultados son contra etiquetas IA, no un nuevo examen humano. BETO no fue ejecutado.** No se reemplazó el modelo guardado.', '',
        '## Qué se hizo', '',
        '- [Protocolo congelado antes del ajuste](PROTOCOLO_CLASIFICADORES_HD_V1.md). Se comparan cinco alternativas con la misma validación y una ancla histórica aparte.',
        '- No se pudieron adquirir pesos de BETO: la petición a Hugging Face falló con TLS EOF. Tampoco había checkpoint local o GPU; dos CPU y ~3,8 GiB de RAM. No se instalaron dependencias grandes ni se creó un script ficticio de BETO. Esto no mide su calidad.',
        '- A (relevancia) unigramas compartida entre los cinco modelos limpios. B solo se ajusta con IA relevante. A=0 produce neutral. Palabras 1–4, LR C=2 o SVM C=1, balanced, sin búsqueda posterior.',
        '- Las variantes mixtas agregan caracteres 3–5 (char_wb, máximo 50.000) con igual peso por bloque y L2 global. La jerárquica aprende una puerta neutral/direccional y después H/D, sin conocer la verdad de validación al predecir.',
        '- No se añadieron WCB, FinancES, traducciones ni etiquetas externas. No se reajustó sobre todo el corpus ni se guardaron clasificadores.', '',
        '## Control de copias textuales', '',
        'Se mantuvieron las mismas 793 intervenciones de validación. De cada train se retiraron las copias de validación normalizando espacios, minúsculas y acentos. No se tocaron L0 ni las etiquetas; algunos de los 559 ejemplos inicialmente fijos en train pueden salir por esta regla.', '',
        '| Fold | Train original | Train purgado | Retirados | Validación con copia antes | Con copia después |',
        '|---|---:|---:|---:|---:|---:|']
    for r in auditoria.itertuples():
        lineas.append(f'| {r.fold} | {r.n_train_original} | {r.n_train_limpio} | {r.n_retirados} | {r.n_val_con_copia_previa} | {r.n_val_con_copia_despues} |')
    lineas += ['', 'La ancla H0 reproduce exactamente las 793 predicciones históricas; **la comparación de candidatos se hace contra B0 limpia**, no contra H0. Quitar copias no elimina equivalencias semánticas, repeticiones dentro de cada conjunto ni el uso previo de esta validación para seleccionar métodos.', '',
        '## Resultado principal', '',
        '**F1 H/D = (F1 hawkish + F1 dovish)/2**, calculado sobre todas las filas: las falsas alarmas sobre neutrales también penalizan. La columna principal es su media entre folds. No es una probabilidad por predicción ni el porcentaje de aciertos de una moneda.', '',
        '| Modelo | F1 H/D medio | DE | Delta vs B0 | Folds mejores | Macro-F1 H/D/N medio |',
        '|---|---:|---:|---:|---:|---:|']
    for r in tabla.itertuples():
        lineas.append(f'| {r.variante} | {r.f1_hd_media:.4f} | {r.f1_hd_sd:.4f} | {r.delta_hd:+.4f} | {r.folds_mejora}/5 | {r.macro_f1_media:.4f} |')
    lineas += ['', 'H0 es referencia histórica sin purga, no candidata. B0=LR palabras; B1=SVM palabras; B2=LR mixta; B3=SVM mixta; B4=jerárquica palabras.', '',
        '## ¿Reconoce H/D o predice la clase más frecuente?', '',
        'La siguiente tabla usa las predicciones conjuntas de las 793 filas. Acierto H/D restringe **solo la evaluación** a H/D verdaderos; una salida neutral cuenta como error. Los modelos no reciben esa selección al predecir. Recall H y D muestran por separado lo que se recupera de cada clase.', '',
        '| Modelo | Recall H | Recall D | Acierto sobre H/D | Accuracy global | Errores | H↔D | N→dirección | Dirección→N |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in tabla.itertuples():
        lineas.append(f'| {r.variante} | {r.recall_hawkish:.4f} | {r.recall_dovish:.4f} | {r.acierto_sobre_hd:.4f} | {r.accuracy:.4f} | {r.errores} | {r.errores_hd} | {r.neutral_a_direccion} | {r.direccion_a_neutral} |')
    lineas += ['', '**Referencias ingenuas:** clase más frecuente elegida en cada train purgado, aplicada a todas las filas sin puerta A. No son candidatas.', '',
        '| Regla constante | F1 H/D conjunto | Accuracy global | Acierto sobre H/D |',
        '|---|---:|---:|---:|']
    for r in ingenuas[ingenuas.fold.eq(0)].itertuples():
        lineas.append(f'| {r.referencia} | {r.f1_hd:.4f} | {r.accuracy:.4f} | {r.acierto_sobre_hd:.4f} |')
    lineas += ['', 'Una moneda entre H/D tiene 50% de acierto esperado sobre H/D verdaderos; el desbalance permite superar ese número con una regla constante. Superar 50% no demuestra significación ni confiabilidad humana. La tabla no debe compararse directamente con el examen humano anterior: son otras referencias y otro conjunto.', '',
        '## Errores cambiados y batería conocida', '',
        '| Modelo | Corregidos vs B0 | Nuevos vs B0 | Aciertos sintéticos / 70 | Invariancia / 20 |',
        '|---|---:|---:|---:|---:|']
    for r in tabla.itertuples():
        lineas.append(f'| {r.variante} | {r.corregidos} | {r.nuevos} | {round(r.exactitud_conductual*70)} | {round(r.invariancia*20)} |')
    lineas += ['', 'Son 14 textos inventados conocidos × 5 modelos por variante, no 70 observaciones independientes. Los cuatro pares por fold también son conocidos; invariancia no equivale a corrección. No se ajustó el clasificador para aprobarlos.', '',
        '## Decisión y límites', '',
        ('Hay candidatas que cumplen el umbral práctico para proponer confirmación separada; todavía no se adoptan.' if resumen['elegibles'] else '**Ninguna alternativa cumple todos los criterios prefijados. Cerrar esta ronda sin adopción ni ampliar la rejilla.**'),
        'Requisitos: +0,02 de F1 H/D medio; ≥3/5 folds mejores; pérdida de macro-F1 ≤0,005; pérdidas de recall H y D ≤0,02; pérdida de exactitud sintética ≤0,05. No son pruebas de significación. La mayor media observada por sí sola no basta.',
        '**No se ha demostrado mejora contra personas.** Las 793 IA son desarrollo reutilizado, los folds comparten train y los métodos fueron propuestos con conocimiento de diagnósticos previos. Una confirmación futura necesita una referencia humana nueva y reservada, no reutilizar los 306 conocidos para ajustar.',
        'SVM, caracteres y jerarquía siguen siendo métodos léxicos. Un resultado aquí no descarta un transformer ni demuestra comprensión de emisor, objeto, negación o preferencia. BETO y entrenamiento auxiliar financiero quedan sin ejecutar, no como métodos fallidos.', '',
        '## Archivos y repetición', '',
        '`data/evaluacion/clasificadores_hd_v1/`: protocolo, asignaciones, exclusiones de train por ID/hash, auditoría, predicciones, métricas por fold, referencias ingenuas, pruebas sintéticas, comparación, tiempos y manifiesto. `reproducibilidad.json` registra la repetición y tests posteriores cuando estén terminados.', '',
        '```bash', 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/26_comparar_clasificadores_hd.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/26_comparar_clasificadores_hd.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md',
        'python -m unittest discover -s tests -p test_clasificadores_hd.py -v', '```', '']
    return '\n'.join(lineas)


# ---- 6. Ejecución exclusiva: verificar ancla, guardar resultados, nunca modelos ----
def ejecutar(salida=RUTA_SALIDA,informe=RUTA_INFORME):
    salida,informe = Path(salida),Path(informe)
    protocolo = verificar(salida)
    assert {p.name for p in salida.iterdir()}=={'protocolo.json',*protocolo['sha256_particiones']}, 'Carpeta ejecutada o parcial'
    exigir_salidas_nuevas(informe)
    datos,mascara,anteriores,_ = L.cargar_insumos()
    particiones,asignacion,exclusiones,auditoria = particionar(datos,mascara)
    for nombre,tabla in [('asignacion_folds',asignacion),('exclusiones_train',exclusiones),('auditoria_folds',auditoria)]:
        pd.testing.assert_frame_equal(tabla,pd.read_csv(salida/(nombre+'.csv')))
    predicciones,folds,conducta,ingenuas,tiempos = [],[],[],[],[]
    textos_conductuales = [c[2] for c in R.CASOS_CONDUCTUALES]
    with warnings.catch_warnings():
        warnings.simplefilter('error',ConvergenceWarning)
        for numero,original,limpio,val in particiones:
            inicio = time.perf_counter()
            modelos = {**ajustar_modelos(datos.iloc[original],solo_base=True),**ajustar_modelos(datos.iloc[limpio])}
            validacion = datos.iloc[val]
            referencias_fold = referencias(datos.iloc[limpio],len(val))
            for nombre,pred in referencias_fold.items():
                ingenuas.append(pd.DataFrame({'fold':numero,'intervencion_id':validacion.intervencion_id.to_numpy(),
                    'etiqueta':validacion.etiqueta.to_numpy(),'referencia':nombre,'pred':pred}))
            for variante,modelo in modelos.items():
                pa,pb,pred = predecir(modelo,validacion.texto.tolist())
                sub = validacion[['intervencion_id','meeting_id','etiqueta','es_relevante']].copy()
                sub['fold'],sub['variante'],sub['pred_a'],sub['pred_b'],sub['pred'] = numero,variante,pa,pb,pred
                predicciones.append(sub)
                fila = {'fold':numero,'variante':variante,**modelo['dimensiones'],**metricas(sub.etiqueta,sub.pred)}
                folds.append(fila)
                pa,pb,pred = predecir(modelo,textos_conductuales)
                for caso,a,b,p in zip(R.CASOS_CONDUCTUALES,pa,pb,pred):
                    conducta.append({'fold':numero,'variante':variante,'caso_id':caso[0],'fenomeno':caso[1],
                        'texto':caso[2],'etiqueta':caso[3],'pred_a':int(a),'pred_b':b,'pred':p})
                print(f'Fold {numero} {variante}: F1 H/D={fila["f1_hd"]:.6f}; macro-F1={fila["macro_f1"]:.6f}',flush=True)
            tiempos.append({'fold':numero,'segundos_ajuste_y_evaluacion':time.perf_counter()-inicio})
    predicciones,folds,conducta,ingenuas = pd.concat(predicciones,ignore_index=True),pd.DataFrame(folds),pd.DataFrame(conducta),pd.concat(ingenuas,ignore_index=True)
    assert len(predicciones)==6*793 and len(conducta)==6*5*14
    assert not predicciones.duplicated(['variante','intervencion_id']).any()
    assert predicciones[predicciones.variante.isin(CANDIDATAS)].groupby('intervencion_id').pred_a.nunique().eq(1).all()
    columnas = ['intervencion_id','meeting_id','etiqueta','fold','pred']
    pd.testing.assert_frame_equal(predicciones[predicciones.variante.eq('H0_historica')][columnas].reset_index(drop=True),
        anteriores[anteriores.variante.eq('ngramas_1_4')][columnas].reset_index(drop=True))
    tabla = resumir(predicciones,folds,conducta)
    metricas_ingenuas = []
    for nombre,sub in ingenuas.groupby('referencia'):
        metricas_ingenuas.append({'referencia':nombre,'fold':0,**metricas(sub.etiqueta,sub.pred)})
        for numero,parte in sub.groupby('fold'):
            metricas_ingenuas.append({'referencia':nombre,'fold':numero,**metricas(parte.etiqueta,parte.pred)})
    metricas_ingenuas = pd.DataFrame(metricas_ingenuas)
    resumen = {'mejor_observado':tabla[tabla.variante.isin(CANDIDATAS)].sort_values('f1_hd_media',ascending=False,kind='stable').iloc[0].variante,
        'elegibles':tabla[tabla.cumple_para_confirmar].variante.tolist(),'ancla_identica':True,
        'clases':CLASES,'n_validacion':793,'n_exclusiones_por_fold':auditoria.n_retirados.tolist(),
        'n_validacion_con_copias_antes':int(auditoria.n_val_con_copia_previa.sum()),'n_copias_despues':0,
        'matrices':{v:confusion_matrix(s.etiqueta,s.pred,labels=CLASES).tolist() for v,s in predicciones.groupby('variante')},
        'beto_ejecutado':False,'gold_abierto_o_predicho':False,'datos_externos_usados':False,'refit_final_o_reemplazo':False}
    tablas = {'predicciones_validacion':predicciones,'resultados_folds':folds,'comparacion_variantes':tabla,
              'conducta':conducta,'predicciones_ingenuas':ingenuas,'metricas_ingenuas':metricas_ingenuas}
    for nombre,contenido in tablas.items():
        contenido.to_csv(salida/(nombre+'.csv'),index=False)
    ESCRIBIR(salida/'metricas.json',resumen)
    ESCRIBIR(salida/'tiempos.json',tiempos)
    verificar(salida)
    informe.parent.mkdir(parents=True,exist_ok=True)
    with informe.open('x',encoding='utf-8') as archivo:
        archivo.write(construir_informe(tabla,resumen,metricas_ingenuas,auditoria))
    ESCRIBIR(salida/'manifest.json',{'fecha_fin_utc':datetime.now(timezone.utc).isoformat(),
        'sha256_salidas':{p.name:sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},'sha256_informe':sha256(informe)})
    print(tabla[['variante','f1_hd_media','macro_f1_media','cumple_para_confirmar']].to_string(index=False))
    return resumen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    accion = parser.add_mutually_exclusive_group(required=True)
    accion.add_argument('--preparar',action='store_true')
    accion.add_argument('--ejecutar',action='store_true')
    parser.add_argument('--salida',type=Path,default=RUTA_SALIDA)
    parser.add_argument('--informe',type=Path,default=RUTA_INFORME)
    args = parser.parse_args()
    (preparar if args.preparar else ejecutar)(args.salida,args.informe)


if __name__=='__main__':
    main()
