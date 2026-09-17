"""Identidades y reconstrucción local con fixtures, sin modificar etiquetas."""
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import diagnosticar_ampliacion_tfidf as D


class DiagnosticoAmpliacion(unittest.TestCase):
    def test_identidad_simetrica_y_terminos_nuevos(self):
        rng=np.random.default_rng(13)
        x0,x1,w0,w1=[rng.normal(size=30) for _ in range(4)]
        x0[0]=w0[0]=0
        c0,c1,cw,cx=D.descomponer(x0,x1,w0,w1)
        np.testing.assert_allclose(c1-c0,cw+cx,atol=1e-12)
        self.assertAlmostEqual(cw[0],cx[0])

    def test_solo_coeficiente_o_representacion(self):
        _,_,cw,cx=D.descomponer([1,2],[1,2],[3,4],[5,6])
        np.testing.assert_array_equal(cx,[0,0])
        _,_,cw,cx=D.descomponer([1,2],[3,4],[5,6],[5,6])
        np.testing.assert_array_equal(cw,[0,0])

    def test_rechaza_no_finitos_y_dimensiones(self):
        with self.assertRaises(ValueError):D.descomponer([1],[1,2],[1],[1])
        with self.assertRaises(ValueError):D.descomponer([np.inf],[1],[1],[1])

    def test_aportes_reconstruyen_margen(self):
        textos=['subir tasa','subir ahora','bajar tasa','bajar ahora','analisis financiero','analisis comercial']
        y=['hawkish','hawkish','dovish','dovish','neutral','neutral']
        v=TfidfVectorizer().fit(textos);m=LogisticRegression().fit(v.transform(textos),y)
        x,w,i,score=D.aportes(v,m,'subir tasa desconocida','hawkish','dovish')
        self.assertAlmostEqual(i+sum(value*w[v.vocabulary_[term]] for term,value in x.items()),score)
        self.assertNotIn('desconocida',x)

    def test_no_sobrescribir(self):
        with tempfile.TemporaryDirectory() as t,patch.object(D.E,'cargar_cohorte') as cargar:
            with self.assertRaises(FileExistsError):D.ejecutar(Path(t))
            cargar.assert_not_called()


if __name__=='__main__':unittest.main()
