import hashlib,json,unittest
from pathlib import Path
import pandas as pd
from scripts.entrenar_tfidf_supervision_v3 import metricas_completas
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/evaluacion/analisis_secundario_ciego_300_v3_v1'
class TestAnalisisSecundarioCiego300V3(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=pd.read_csv(OUT/'predicciones_factorial.csv',dtype=str,keep_default_na=False);cls.r=json.loads((OUT/'resultados.json').read_text())
 def test_factorial_completo(self):
  self.assertEqual(len(self.p),300);self.assertEqual(self.p.intervencion_id.nunique(),300)
  for c in ['pred_c_89','pred_wc_89','pred_c_600','pred_wc_600']:self.assertTrue(c in self.p)
  self.assertFalse(self.r['busqueda_hiperparametros']);self.assertFalse(self.r['cambio_decision_primaria'])
 def test_metricas_recalculadas(self):
  d=self.p[self.p.incluir_evaluacion.eq('true')].copy();d['fold']=1
  for key,col in {'c_89':'pred_c_89','wc_89':'pred_wc_89','c_600':'pred_c_600','wc_600':'pred_wc_600'}.items():
   got=metricas_completas(d.rename(columns={col:'pred'}),'pred');exp=self.r['metricas_factorial'][key]
   self.assertEqual(got['matriz_orden_h_d_n'],exp['matriz_orden_h_d_n']);self.assertEqual(got['errores'],exp['errores'])
 def test_resultado_interpretable(self):
  e=self.r['efectos'];self.assertGreater(e['macro_f1']['datos_en_c'],e['macro_f1']['caracteres_con_600'])
  ci=self.r['bootstrap_reuniones']['wc600_vs_c89']['macro_f1'];self.assertGreater(ci['p2_5'],0)
  ci2=self.r['bootstrap_reuniones']['wc600_vs_c600']['macro_f1'];self.assertLess(ci2['p2_5'],0);self.assertGreater(ci2['p97_5'],0)
  self.assertEqual(self.r['reuniones']['wc600_vs_c89'],{'gana_wc':17,'empate':14,'gana_c':2})
 def test_manifest(self):
  m=json.loads((OUT/'manifest.json').read_text())['sha256_salidas']
  for n,h in m.items():self.assertEqual(hashlib.sha256((OUT/n).read_bytes()).hexdigest(),h)
if __name__=='__main__':unittest.main()
