"""Pruebas del piloto WCB; no leen ni predicen referencias humanas."""
# ---- 1. Carga del evaluador versionado y fixtures exclusivamente sintéticos ----
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'scripts'))
from utilidades import cargar_script, sha256
E = cargar_script('25_evaluar_wcb_piloto.py')


def fuente():
    return pd.read_csv(E.RUTA_EXTERNOS / 'muestra.tsv',sep='\t',keep_default_na=False)


def train_sintetico():
    return pd.DataFrame({'texto':['propongo subir tasa','apoyo elevar tasa','propongo bajar tasa',
        'apoyo reducir tasa','mantener tasa actual','mantener tasa neutral','agradezco visita','cierre formal'],
        'es_relevante':[1,1,1,1,1,1,0,0],
        'etiqueta':['hawkish','hawkish','dovish','dovish','neutral','neutral','neutral','neutral']})


# ---- 2. Selección, trazabilidad y separación de idiomas/etiquetas ----
class DatosWCB(unittest.TestCase):
    def test_auditoria_100_filas_y_99_utilizables(self):
        resultado=E.auditar_externos(fuente(),pd.DataFrame({'texto':['texto ajeno']}))
        self.assertEqual(resultado['n_externos'],100)
        self.assertEqual(resultado['n_para_b'],99)
        self.assertEqual(resultado['clases_fuente'],{'neutral':41,'dovish':30,'hawkish':28,'irrelevant':1})
        self.assertFalse(resultado['test_externo_abierto'])

    def test_rechaza_muestra_truncada_ids_y_etiquetas_invalidas(self):
        original=fuente()
        mutantes=[original.iloc[:-1].copy(),original.copy(),original.copy()]
        mutantes[1].loc[1,'source_id']=original.loc[0,'source_id']
        mutantes[2].loc[0,'stance_label']='otra'
        for mutante in mutantes:
            with self.assertRaises(AssertionError):
                E.auditar_externos(mutante,pd.DataFrame({'texto':['texto ajeno']}))

    def test_rechaza_solape_externo_ia_y_duplicados(self):
        original=fuente()
        with self.assertRaises(AssertionError):
            E.auditar_externos(original,pd.DataFrame({'texto':[original.loc[0,'texto_es'].upper()]}))
        mutante=original.copy()
        mutante.loc[1,'texto_en']=mutante.loc[0,'texto_en']
        with self.assertRaises(AssertionError):
            E.auditar_externos(mutante,pd.DataFrame({'texto':['texto ajeno']}))

    def test_rechaza_cambio_numero_signo_y_porcentaje(self):
        for texto in ['La inflación fue 0.1%.','La inflación fue -0.2%.','La inflación fue -0.1.']:
            mutante=fuente()
            mutante.loc[67,'texto_es']=texto
            with self.assertRaises(AssertionError):
                E.auditar_externos(mutante,pd.DataFrame({'texto':['texto ajeno']}))

    def test_originales_incompatibles_no_se_reetiquetan(self):
        externos=fuente().set_index('source_id')
        self.assertEqual(externos.loc[217,'stance_label'],'dovish')
        self.assertEqual(externos.loc[434,'stance_label'],'hawkish')
        self.assertIn('argentina',externos.loc[217,'texto_en'])
        self.assertIn('federal reserve',externos.loc[434,'texto_en'])

    def test_train_b_solo_relevantes_ia_mas_99_mismas_etiquetas(self):
        train,externos=train_sintetico(),fuente()
        copia=externos.copy(deep=True)
        base,y0=E.componer_train_b(train,externos,'B0_base')
        ingles,y1=E.componer_train_b(train,externos,'E1_ingles')
        espanol,y2=E.componer_train_b(train,externos,'E2_espanol')
        self.assertEqual(len(base),6)
        self.assertEqual(len(ingles),105)
        self.assertEqual(len(espanol),105)
        self.assertEqual(y1,y2)
        self.assertEqual(ingles[:6],base)
        self.assertEqual(y1[:6],y0)
        self.assertNotIn('agradezco visita',base)
        self.assertNotIn('irrelevant',y1)
        pd.testing.assert_frame_equal(copia,externos)
        with self.assertRaises(AssertionError):
            E.componer_train_b(train,externos,'otra')


# ---- 3. A compartida, vocabulario train y protección de salidas ----
class EvaluacionWCB(unittest.TestCase):
    def test_vocabulario_no_aprende_validacion(self):
        vector=E.TfidfVectorizer(min_df=1).fit(['subir tasa','bajar tasa'])
        original=dict(vector.vocabulary_)
        self.assertEqual(E.cobertura(vector,['xenotermino']),0)
        self.assertEqual(E.cobertura(vector,['subir']),1)
        self.assertEqual(E.cobertura(vector,[]),0)
        self.assertEqual(vector.vocabulary_,original)

    def test_a_compartida_y_ausencia_de_gold_en_funcion_fold(self):
        externos=pd.DataFrame({'stance_label':['hawkish','dovish','neutral','irrelevant'],
            'texto_en':['raise rate','lower rate','hold rate','unused'],
            'texto_es':['subir tasa','bajar tasa','mantener tasa','sin uso']})
        with patch.dict(E.ANTERIOR.PARAMETROS_TFIDF,{'min_df':1,'max_df':1.0}):
            resultados=E.evaluar_fold(train_sintetico(),pd.DataFrame({'texto':['propongo bajar tasa','xenotermino']}),externos)
        self.assertEqual(list(resultados),list(E.VARIANTES))
        for variante,(pa,pb,pred,dimensiones) in resultados.items():
            np.testing.assert_array_equal(pa,resultados['B0_base'][0])
            np.testing.assert_array_equal(pred,np.where(pa==0,'neutral',pb))
            self.assertEqual(dimensiones['n_externos_b'],0 if variante=='B0_base' else 3)

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as carpeta:
            informe=Path(carpeta)/'informe.md'
            informe.write_text('existente')
            with self.assertRaises(FileExistsError):
                E.preparar(Path(carpeta)/'salida',informe)
            self.assertEqual(informe.read_text(),'existente')

    def test_protocolo_detecta_alteracion(self):
        with tempfile.TemporaryDirectory() as carpeta:
            carpeta=Path(carpeta)
            (carpeta/'asignacion_folds.csv').write_text('asignacion')
            (carpeta/'auditoria_externos.json').write_text('{}')
            protocolo={'variantes':list(E.VARIANTES),'sha256_asignacion':sha256(carpeta/'asignacion_folds.csv'),
                'sha256_auditoria':sha256(carpeta/'auditoria_externos.json'),'sha256_insumos':{}}
            (carpeta/'protocolo.json').write_text(json.dumps(protocolo))
            E.verificar_protocolo(carpeta)
            (carpeta/'asignacion_folds.csv').write_text('cambio')
            with self.assertRaises(AssertionError):
                E.verificar_protocolo(carpeta)

    @unittest.skipUnless((E.RUTA_SALIDA/'manifest.json').exists(),'Todavía no ejecutado')
    def test_artefactos_metrica_independiente_y_ancla(self):
        E.verificar_protocolo(E.RUTA_SALIDA)
        pred=pd.read_csv(E.RUTA_SALIDA/'predicciones_validacion.csv')
        comparacion=pd.read_csv(E.RUTA_SALIDA/'comparacion_variantes.csv').set_index('variante')
        anterior=pd.read_csv(E.LONGITUD.RUTA_SALIDA/'predicciones_validacion.csv')
        base=pred[pred.variante.eq('B0_base')].set_index('intervencion_id').pred
        esperado=anterior[anterior.ngram_max.eq(4)].set_index('intervencion_id').pred
        pd.testing.assert_series_equal(base,esperado)
        self.assertEqual(len(pred),2379)
        self.assertTrue(pred.groupby('intervencion_id').pred_a.nunique().eq(1).all())
        for variante,sub in pred.groupby('variante'):
            media=np.mean([f1_score(s.etiqueta,s.pred,labels=E.ANTERIOR.L.CLASES,average='macro') for _,s in sub.groupby('fold')])
            self.assertAlmostEqual(media,comparacion.loc[variante,'macro_f1_media'],14)
            correcto=sub.pred.eq(sub.etiqueta).sum()
            self.assertEqual(793-correcto,comparacion.loc[variante,'errores'])
            self.assertEqual(62-comparacion.loc[variante,'corregidos']+comparacion.loc[variante,'nuevos'],comparacion.loc[variante,'errores'])
        manifest=json.loads((E.RUTA_SALIDA/'manifest.json').read_text())
        for nombre,huella in manifest['sha256_salidas'].items():
            self.assertEqual(sha256(E.RUTA_SALIDA/nombre),huella)
        self.assertEqual(sha256(E.RUTA_INFORME),manifest['sha256_informe'])


if __name__=='__main__':
    unittest.main()
