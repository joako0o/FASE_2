"""Controles del ensayo de ampliación con fixtures; no abre respuestas humanas."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import evaluar_ampliacion_tfidf as E


class AmpliacionTfidf(unittest.TestCase):
    def test_01_purga_reunion_y_texto_sin_modificar_fuentes(self):
        val=pd.DataFrame([{'meeting_id':'m1','texto':'ÁLZA  de tasa'}])
        nuevos=pd.DataFrame([
            {'intervencion_id':'a','meeting_id':'m1','texto':'diferente','etiqueta':'hawkish'},
            {'intervencion_id':'b','meeting_id':'m2','texto':'alza de tasa','etiqueta':'hawkish'},
            {'intervencion_id':'c','meeting_id':'m3','texto':'recortar ahora','etiqueta':'dovish'}])
        antes=nuevos.copy(deep=True);incluidos,aud=E.purgar(nuevos,val,1)
        self.assertEqual(incluidos.intervencion_id.tolist(),['c'])
        self.assertEqual(aud.incluido.tolist(),[False,False,True])
        pd.testing.assert_frame_equal(antes,nuevos)

    def test_02_control_debe_reproducir_a_b_y_final(self):
        t=pd.DataFrame([dict(intervencion_id='a',meeting_id='m1',fold=1,pred_a=1,pred_b='hawkish',pred='hawkish')])
        E.verificar_ancla(t,t.copy())
        mod=t.copy();mod.loc[0,'pred_b']='dovish'
        with self.assertRaises(AssertionError):E.verificar_ancla(mod,t)

    def test_03_b_solo_ajusta_train_y_respeta_a(self):
        filas=[]
        for etiqueta,texto in [('hawkish','elevar subir endurecer'),('dovish','bajar recortar relajar'),('neutral','describir mercado actividad')]:
            filas.extend(dict(etiqueta=etiqueta,texto=texto,es_relevante=1) for _ in range(6))
        train=pd.DataFrame(filas);val=pd.DataFrame({'texto':['elevar subir termino_solo_validacion','bajar recortar termino_solo_validacion']})
        vector=E.TfidfVectorizer(**E.H.PARAMETROS_PALABRAS)
        with patch.object(E,'TfidfVectorizer',return_value=vector):
            b,final,p,clases,dim=E.ajustar_b(train,val,np.array([0,1]))
        self.assertNotIn('termino_solo_validacion',vector.vocabulary_)
        self.assertEqual(final[0],'neutral');self.assertEqual(final[1],b[1])
        self.assertEqual(dim['n_train_b'],18)
        np.testing.assert_allclose(p.sum(axis=1),1)

    def test_04_sin_mejora_no_se_aprueba(self):
        filas=[]
        for cond in ['control','ampliado_59']:
            for f in range(1,6):
                filas.extend(dict(condicion=cond,fold=f,etiqueta=y,pred=y) for y in ['hawkish','dovish','neutral'])
        r=E.resumir(pd.DataFrame(filas))
        self.assertFalse(r['cumple_criterios_desarrollo']);self.assertFalse(r['criterios']['menos_inversiones'])
        self.assertFalse(r['modelo_adoptado']);self.assertFalse(r['evaluacion_independiente'])

    def test_05_no_sobrescribe_resultados(self):
        with tempfile.TemporaryDirectory() as t,patch.object(E,'cargar_cohorte') as cargar:
            with self.assertRaises(FileExistsError):E.ejecutar(Path(t))
            cargar.assert_not_called()


if __name__=='__main__':unittest.main()
