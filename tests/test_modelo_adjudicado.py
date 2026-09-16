"""Controles de la vista aprobada y referencia IA; no abre respuestas de 306."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script,sha256
E=cargar_script('31_evaluar_adjudicacion.py')


def inventados():
    datos=pd.DataFrame({'intervencion_id':['a','b','c'],'meeting_id':['m1','m2','m3'],
        'texto':['Subir más adelante.','Sin dirección.','Bajar pronto.'],
        'etiqueta':['neutral','neutral','dovish'],'es_relevante':['1','1','1']})
    asignacion=pd.DataFrame({'intervencion_id':['a','b','c'],'fold_validacion':[0,1,2]})
    adjudicacion=pd.DataFrame([{'caso_id':'R01','intervencion_id':'a','etiqueta_ia_original':'neutral',
        'etiqueta_adjudicada':'hawkish','sha256_texto_original':hashlib.sha256(datos.texto.iloc[0].encode()).hexdigest(),
        'estado':'aprobada_por_investigador','procedencia':'propuesta_agente_aceptada_tras_comparacion'}])
    return datos,asignacion,adjudicacion


class Vista(unittest.TestCase):
    def test_aplica_por_id_sin_mutar_ni_cambiar_relevancia(self):
        datos,folds,aceptadas=inventados();original=datos.copy(deep=True)
        nueva,cambios=E.aplicar_adjudicaciones(datos,folds.iloc[::-1],aceptadas)
        pd.testing.assert_frame_equal(datos,original)
        self.assertEqual(nueva.etiqueta.tolist(),['hawkish','neutral','dovish'])
        pd.testing.assert_series_equal(datos.es_relevante,nueva.es_relevante)
        self.assertEqual(int(cambios.cambia_ia.sum()),1)

    def test_rechaza_una_propuesta_no_aprobada(self):
        datos,folds,aceptadas=inventados();aceptadas.loc[0,'estado']='pendiente_confirmacion_usuario'
        with self.assertRaises(AssertionError):E.aplicar_adjudicaciones(datos,folds,aceptadas)

    def test_rechaza_cualquier_adjudicacion_en_validacion(self):
        datos,folds,aceptadas=inventados();folds.loc[0,'fold_validacion']=1
        with self.assertRaises(AssertionError):E.aplicar_adjudicaciones(datos,folds,aceptadas)

    def test_rechaza_hash_etiqueta_id_clase_o_procedencia_discordantes(self):
        for columna,valor in [('sha256_texto_original','otro'),('etiqueta_ia_original','dovish'),
                              ('intervencion_id','ajeno'),('etiqueta_adjudicada','no_puedo_decidir'),
                              ('procedencia','anotador_independiente')]:
            with self.subTest(columna=columna):
                datos,folds,aceptadas=inventados();aceptadas.loc[0,columna]=valor
                with self.assertRaises(AssertionError):E.aplicar_adjudicaciones(datos,folds,aceptadas)

    def test_no_imputa_relevancia_ni_admite_duplicados(self):
        datos,folds,aceptadas=inventados();datos.loc[0,'es_relevante']='0'
        with self.assertRaises(AssertionError):E.aplicar_adjudicaciones(datos,folds,aceptadas)
        datos,folds,aceptadas=inventados()
        with self.assertRaises(AssertionError):E.aplicar_adjudicaciones(datos,folds,pd.concat([aceptadas,aceptadas]))

    def test_aprobada_que_ya_coincidia_no_es_cambio_ia(self):
        datos,folds,aceptadas=inventados();aceptadas.loc[0,'etiqueta_adjudicada']='neutral'
        nueva,cambios=E.aplicar_adjudicaciones(datos,folds,aceptadas)
        pd.testing.assert_frame_equal(datos,nueva)
        self.assertEqual(int(cambios.cambia_ia.sum()),0)


class Evaluacion(unittest.TestCase):
    def test_falsos_positivos_sobre_neutral_penalizan_hd(self):
        perfecto=E.H.metricas(['hawkish','dovish','neutral'],['hawkish','dovish','neutral'])
        falso=E.H.metricas(['hawkish','dovish','neutral'],['hawkish','dovish','hawkish'])
        self.assertEqual(perfecto['f1_hd'],1)
        self.assertLess(falso['f1_hd'],1)
        self.assertAlmostEqual(falso['f1_hd'],5/6)

    def test_fuentes_reales_solo_tres_cambios_train_y_validacion_intacta(self):
        datos,nueva,particiones,cambios,control,ancla=E.cargar()
        self.assertEqual(len(datos),1352)
        self.assertEqual(set(cambios[cambios.cambia_ia].caso_id),{'R01','R03','R12'})
        self.assertEqual(int(datos.etiqueta.ne(nueva.etiqueta).sum()),3)
        self.assertEqual(len(ancla),793)
        self.assertTrue(control.cambios_en_validacion.eq(0).all())
        for _,_,train,val in particiones:
            pd.testing.assert_frame_equal(datos.iloc[val],nueva.iloc[val])
            self.assertFalse(set(datos.iloc[train].meeting_id)&set(datos.iloc[val].meeting_id))
            self.assertFalse(set(datos.iloc[train].texto.map(E.H.clave_texto))&set(datos.iloc[val].texto.map(E.H.clave_texto)))

    def test_rechaza_preparar_sobre_salida_existente(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileExistsError):E.preparar(Path(t),Path(t)/'informe.md')

    @unittest.skipUnless((E.SALIDA/'manifest.json').exists(),'Aún sin entrenamiento de esta unidad')
    def test_resultados_ancla_y_metricas_independientes(self):
        m=json.loads((E.SALIDA/'manifest.json').read_text())
        for nombre,digest in m['sha256_salidas'].items():self.assertEqual(sha256(E.SALIDA/nombre),digest)
        self.assertEqual(sha256(E.INFORME),m['sha256_informe'])
        p=pd.read_csv(E.SALIDA/'predicciones_validacion.csv')
        f=pd.read_csv(E.SALIDA/'resultados_folds.csv')
        esperado=json.loads((E.SALIDA/'metricas.json').read_text())
        from sklearn.metrics import f1_score
        for variante in E.VARIANTES:
            valores=[]
            for _,sub in p[p.variante.eq(variante)].groupby('fold'):
                valores.append(float(f1_score(sub.etiqueta,sub.pred,labels=['hawkish','dovish'],average='macro',zero_division=0)))
            self.assertAlmostEqual(sum(valores)/len(valores),esperado['condiciones'][variante]['media_fold_f1_hd'])
        calculado=E.resumir(p,f)
        self.assertEqual(calculado['errores_corregidos'],esperado['errores_corregidos'])
        self.assertEqual(calculado['errores_nuevos'],esperado['errores_nuevos'])
        ancla=pd.read_csv(E.H.RUTA_SALIDA/'predicciones_validacion.csv')
        columnas=['intervencion_id','fold','etiqueta','pred_a','pred_b','pred']
        a=p[p.variante.eq('original')][columnas].sort_values('intervencion_id').reset_index(drop=True)
        b=ancla[ancla.variante.eq('B0_limpia')][columnas].sort_values('intervencion_id').reset_index(drop=True)
        pd.testing.assert_frame_equal(a,b)


if __name__=='__main__':unittest.main()
