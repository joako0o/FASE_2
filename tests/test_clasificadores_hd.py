"""Pruebas sintéticas y auditoría IA de la ronda H/D; nunca abren gold humano."""
# ---- 1. Evaluador versionado y ejemplos pequeños, no datos de test humano ----
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score,recall_score

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script,sha256
E = cargar_script('26_comparar_clasificadores_hd.py')


def muestra_sintetica():
    return pd.DataFrame({'texto':['prefiero subir tasa','propongo elevar tasa','apoyo aumentar tasa',
        'prefiero bajar tasa','propongo recortar tasa','apoyo reducir tasa',
        'mantener tasa constante','exposicion de cifras','resumen del informe','gracias por venir'],
        'etiqueta':['hawkish']*3+['dovish']*3+['neutral']*4,'es_relevante':[1]*9+[0]})


# ---- 2. Higiene: nunca borrar validación ni aprender de sus etiquetas ----
class Purga(unittest.TestCase):
    def test_normaliza_solo_espacios_mayusculas_acentos(self):
        self.assertEqual(E.clave_texto('  Inflación\n  ALTA  '),E.clave_texto('inflacion alta'))
        self.assertNotEqual(E.clave_texto('subir tasa'),E.clave_texto('bajar tasa'))

    def test_retira_copia_train_y_preserva_validacion(self):
        datos=pd.DataFrame({'intervencion_id':['a','b','c','d','e'],
            'meeting_id':['train']*4+['val'],'texto':['subir tasa','bajar tasa','resumen',' INFLACIÓN ALTA ','inflacion alta'],
            'etiqueta':['hawkish','dovish','neutral','neutral','neutral']})
        mascara=np.array([1,1,1,1,0],dtype=bool)
        original=datos.copy(deep=True)
        with patch.object(E.L,'asignar_folds',return_value=([(1,np.array([0,1,2,3]),np.array([4]))],pd.DataFrame())):
            particiones,_,exclusiones,auditoria=E.particionar(datos,mascara)
        np.testing.assert_array_equal(particiones[0][2],[0,1,2])
        np.testing.assert_array_equal(particiones[0][3],[4])
        self.assertEqual(exclusiones.intervencion_id.tolist(),['d'])
        self.assertTrue(exclusiones.era_descubrimiento.all())
        self.assertEqual(auditoria.n_val_con_copia_despues.tolist(),[0])
        pd.testing.assert_frame_equal(datos,original)

    def test_purga_no_depende_de_etiqueta_val(self):
        datos=muestra_sintetica()
        datos['intervencion_id']=[str(i) for i in range(len(datos))]
        datos['meeting_id']=['train']*9+['val']
        datos.loc[9,'texto']=datos.loc[0,'texto']
        mascara=np.array([True]*9+[False])
        with patch.object(E.L,'asignar_folds',return_value=([(1,np.arange(9),np.array([9]))],pd.DataFrame())):
            antes=E.particionar(datos,mascara)[0][0][2]
            datos.loc[9,'etiqueta']='dovish'
            despues=E.particionar(datos,mascara)[0][0][2]
        np.testing.assert_array_equal(antes,despues)
        self.assertNotIn(0,antes)


# ---- 3. Representaciones y jerarquía entrenadas únicamente con train ----
class Modelos(unittest.TestCase):
    def test_vistas_no_aprenden_validacion_y_norma_mixta(self):
        with patch.dict(E.PARAMETROS_PALABRAS,{'min_df':1,'max_df':1.0}),patch.dict(E.PARAMETROS_CARACTERES,{'min_df':1,'max_df':1.0}):
            vista=E.VistaTfidf(mixta=True)
            matriz=vista.fit_transform(['subir la tasa','bajar la tasa'])
            palabras=dict(vista.palabras.vocabulary_)
            caracteres=dict(vista.caracteres.vocabulary_)
            vista.transform(['xenoterminoquimerico'])
        self.assertNotIn('xenoterminoquimerico',palabras)
        self.assertEqual(vista.palabras.vocabulary_,palabras)
        self.assertEqual(vista.caracteres.vocabulary_,caracteres)
        np.testing.assert_allclose(np.asarray(matriz.multiply(matriz).sum(axis=1)).ravel(),1.)
        separador=len(palabras)
        np.testing.assert_allclose(np.asarray(matriz[:,:separador].multiply(matriz[:,:separador]).sum(axis=1)).ravel(),.5)
        self.assertLessEqual(len(caracteres),50000)

    def test_todas_las_variantes_a_compartida_y_cabeza_hd_sin_n(self):
        with patch.dict(E.ANTERIOR.PARAMETROS_TFIDF,{'min_df':1,'max_df':1.0}),patch.dict(E.PARAMETROS_PALABRAS,{'min_df':1,'max_df':1.0}),patch.dict(E.PARAMETROS_CARACTERES,{'min_df':1,'max_df':1.0}):
            modelos=E.ajustar_modelos(muestra_sintetica())
        self.assertEqual(tuple(modelos),E.CANDIDATAS)
        base=modelos['B0_limpia']
        for nombre,modelo in modelos.items():
            self.assertIs(modelo['modelo_a'],base['modelo_a'])
            self.assertEqual(modelo['dimensiones']['n_train_b'],9)
            self.assertEqual(modelo['dimensiones']['n_train_hd'],6)
            pa,pb,pred=E.predecir(modelo,['prefiero bajar tasa','texto desconocido'])
            np.testing.assert_array_equal(pred,np.where(pa==0,'neutral',pb))
        jerarquica=modelos['B4_jerarquica']
        self.assertEqual(set(jerarquica['clasificador'].classes_),{'hawkish','dovish'})
        self.assertEqual(set(jerarquica['puerta'].classes_),{0,1})
        self.assertIs(jerarquica['vista'],base['vista'])
        self.assertIs(modelos['B2_lr_mixta']['vista'],modelos['B3_svm_mixta']['vista'])

    def test_puerta_jerarquica_se_aplica_sin_oraculo(self):
        with patch.dict(E.ANTERIOR.PARAMETROS_TFIDF,{'min_df':1,'max_df':1.0}),patch.dict(E.PARAMETROS_PALABRAS,{'min_df':1,'max_df':1.0}),patch.dict(E.PARAMETROS_CARACTERES,{'min_df':1,'max_df':1.0}):
            modelo=E.ajustar_modelos(muestra_sintetica())['B4_jerarquica']
        with patch.object(modelo['puerta'],'predict',return_value=np.array([0,1])),patch.object(modelo['clasificador'],'predict',return_value=np.array(['hawkish','dovish'])),patch.object(modelo['modelo_a'],'predict',return_value=np.ones(2,dtype=int)):
            _,pb,pred=E.predecir(modelo,['uno','dos'])
        np.testing.assert_array_equal(pb,['neutral','dovish'])
        np.testing.assert_array_equal(pred,pb)


# ---- 4. Métricas direccionales con falsas alarmas y criterios previos ----
class Metricas(unittest.TestCase):
    def test_f1_hd_penaliza_neutral_mal_etiquetado(self):
        r=E.metricas(['hawkish','dovish','neutral'],['hawkish','dovish','hawkish'])
        self.assertAlmostEqual(r['f1_hd'],(2/3+1)/2)
        self.assertEqual(r['acierto_sobre_hd'],1.)
        self.assertEqual(r['neutral_a_direccion'],1)
        self.assertEqual(r['errores'],1)

    def test_neutral_en_hd_no_se_excluye_del_denominador(self):
        r=E.metricas(['hawkish','dovish','neutral'],['hawkish','neutral','neutral'])
        self.assertEqual(r['acierto_sobre_hd'],.5)
        self.assertEqual(r['direccion_a_neutral'],1)
        self.assertEqual(r['recall_hd_balanceado'],.5)

    def test_ingenuas_son_constantes_no_oraculos(self):
        pred=E.referencias(muestra_sintetica(),7)
        self.assertEqual(set(pred['mayoritaria']),{'neutral'})
        self.assertEqual(len(pred['mayoritaria_hd']),7)
        self.assertEqual(len(set(pred['mayoritaria_hd'])),1)
        self.assertIn(pred['mayoritaria_hd'][0],['hawkish','dovish'])

    def test_no_basta_ganar_una_metrica(self):
        base={'variante':'B0_limpia','delta_hd':0.,'folds_mejora':0,'delta_macro':0.,
              'recall_hawkish':.8,'recall_dovish':.7,'exactitud_conductual':.5}
        buena={**base,'variante':'B1_svm','delta_hd':.03,'folds_mejora':3}
        self.assertTrue(E.criterios(pd.DataFrame([base,buena])).iloc[1])
        cambios=[{'delta_hd':.019},{'folds_mejora':2},{'delta_macro':-.006},
                 {'recall_hawkish':.77},{'recall_dovish':.67},{'exactitud_conductual':.44},{'variante':'H0_historica'}]
        for cambio in cambios:
            self.assertFalse(E.criterios(pd.DataFrame([base,{**buena,**cambio}])).iloc[1])


# ---- 5. Archivos: no sobrescribir y auditoría independiente de resultados IA ----
class Artefactos(unittest.TestCase):
    def test_preparacion_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as carpeta:
            informe=Path(carpeta)/'informe.md'
            informe.write_text('previo')
            with self.assertRaises(FileExistsError):
                E.preparar(Path(carpeta)/'salida',informe)
            self.assertEqual(informe.read_text(),'previo')

    def test_verificacion_detecta_cambio_particiones(self):
        with tempfile.TemporaryDirectory() as carpeta:
            carpeta=Path(carpeta)
            (carpeta/'particiones.csv').write_text('original')
            protocolo={'variantes':list(E.VARIANTES),'tolerancias':E.TOLERANCIAS,'sha256_insumos':{},
                       'sha256_particiones':{'particiones.csv':sha256(carpeta/'particiones.csv')}}
            (carpeta/'protocolo.json').write_text(json.dumps(protocolo))
            E.verificar(carpeta)
            (carpeta/'particiones.csv').write_text('cambio')
            with self.assertRaises(AssertionError):
                E.verificar(carpeta)

    @unittest.skipUnless((E.RUTA_SALIDA/'manifest.json').exists(),'Aún no ejecutado')
    def test_recalculo_independiente_y_ancla(self):
        E.verificar(E.RUTA_SALIDA)
        pred=pd.read_csv(E.RUTA_SALIDA/'predicciones_validacion.csv')
        tabla=pd.read_csv(E.RUTA_SALIDA/'comparacion_variantes.csv').set_index('variante')
        self.assertEqual(len(pred),4758)
        self.assertTrue(pred[pred.variante.isin(E.CANDIDATAS)].groupby('intervencion_id').pred_a.nunique().eq(1).all())
        for variante,sub in pred.groupby('variante'):
            media=np.mean([f1_score(p.etiqueta,p.pred,labels=['hawkish','dovish'],average='macro',zero_division=0) for _,p in sub.groupby('fold')])
            self.assertAlmostEqual(media,tabla.loc[variante,'f1_hd_media'],14)
            self.assertAlmostEqual(recall_score(sub.etiqueta,sub.pred,labels=['hawkish','dovish'],average='macro'),tabla.loc[variante,'recall_hd_balanceado'],14)
            self.assertEqual(tabla.loc['B0_limpia','errores']-tabla.loc[variante,'corregidos']+tabla.loc[variante,'nuevos'],tabla.loc[variante,'errores'])
        anterior=pd.read_csv(E.L.RUTA_SALIDA/'predicciones_validacion.csv')
        pd.testing.assert_series_equal(pred[pred.variante.eq('H0_historica')].set_index('intervencion_id').pred,
            anterior[anterior.ngram_max.eq(4)].set_index('intervencion_id').pred)
        manifest=json.loads((E.RUTA_SALIDA/'manifest.json').read_text())
        for nombre,huella in manifest['sha256_salidas'].items():
            self.assertEqual(sha256(E.RUTA_SALIDA/nombre),huella)
        self.assertEqual(sha256(E.RUTA_INFORME),manifest['sha256_informe'])

    @unittest.skipUnless((E.RUTA_SALIDA/'manifest.json').exists(),'Aún no ejecutado')
    def test_particiones_reconstruidas_sin_copias_ni_reuniones_comunes(self):
        datos,mascara,_,_=E.L.cargar_insumos()
        partes,_,exclusiones,auditoria=E.particionar(datos,mascara)
        for _,original,train,val in partes:
            self.assertTrue(set(train)<=set(original))
            self.assertFalse(set(datos.iloc[train].texto.map(E.clave_texto)) & set(datos.iloc[val].texto.map(E.clave_texto)))
            self.assertFalse(set(datos.iloc[train].meeting_id) & set(datos.iloc[val].meeting_id))
        pd.testing.assert_frame_equal(exclusiones,pd.read_csv(E.RUTA_SALIDA/'exclusiones_train.csv'))
        pd.testing.assert_frame_equal(auditoria,pd.read_csv(E.RUTA_SALIDA/'auditoria_folds.csv'))


if __name__=='__main__':
    unittest.main()
