"""Fixtures de auditoría de compatibilidad; no abre respuestas humanas."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import auditar_compatibilidad_criterios as A


class Compatibilidad(unittest.TestCase):
    def datos(self):
        rows=[];corpus={};refs={}
        for e,r in [('hawkish','1'),('dovish','1'),('neutral','1'),('neutral','0')]:
            for i in range(4):
                k=f'{e}-{r}-{i}'
                rows.append({'intervencion_id':k,'etiqueta':e,'es_relevante':r})
                corpus[k]={'texto':'Texto distinto '+k}
                refs[k]={'etiqueta_corregida_v2':e}
        return rows,corpus,refs

    def test_normalizacion(self):
        self.assertEqual(A.clave('  POLÍTICA\nmonetaria '),A.clave('politica monetaria'))

    def test_neutral_no_es_igual_a_irrelevante(self):
        r=A.conteos([{'etiqueta':'neutral','es_relevante':'1'},{'etiqueta':'neutral','es_relevante':'0'}])
        self.assertEqual(len(r),2);self.assertEqual(sum(x['n'] for x in r),2)

    def test_controles_reproducibles(self):
        r,c,f=self.datos();x=A.seleccionar_controles(r,c,f,set(),set())
        y=A.seleccionar_controles(list(reversed(r)),c,f,set(),set())
        self.assertEqual(x,y);self.assertEqual(len(x),8)

    def test_excluye_focos_y_textos_del_marco(self):
        r,c,f=self.datos();c['humano']={'texto':c['hawkish-1-1']['texto'].upper()}
        x=A.seleccionar_controles(r,c,f,{'humano'},{'hawkish-1-0'})
        self.assertFalse({p['intervencion_id'] for p in x}&{'hawkish-1-0','hawkish-1-1','humano'})

    def test_excluye_adjudicaciones_y_falla_si_no_alcanza(self):
        r,c,f=self.datos();f['dovish-1-0']['etiqueta_corregida_v2']='neutral'
        x=A.seleccionar_controles(r,c,f,set(),set())
        self.assertNotIn('dovish-1-0',{p['intervencion_id'] for p in x})
        with self.assertRaises(ValueError):A.seleccionar_controles([],{}, {},set(),set())

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'conteos.json').write_text('conservar')
            with self.assertRaises(FileExistsError):A.ejecutar(p)
            self.assertEqual((p/'conteos.json').read_text(),'conservar')


if __name__=='__main__':unittest.main()
