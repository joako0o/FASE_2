import hashlib, json, unittest
from pathlib import Path
import pandas as pd
from scripts.entrenar_tfidf_supervision_v3 import metricas_completas

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data/evaluacion/evaluacion_ciega_300_resultados_v1'
class TestResultadoCiego300V3(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=pd.read_csv(OUT/'predicciones.csv',dtype=str,keep_default_na=False); cls.m=json.loads((OUT/'metricas.json').read_text())
 def test_cobertura(self):
  self.assertEqual(len(self.p),300); self.assertEqual(self.p.intervencion_id.nunique(),300); self.assertEqual((self.p.incluir_evaluacion=='true').sum(),299)
  self.assertEqual(self.p.estrato_recuperacion.value_counts().to_dict(),{'aleatorio_contextual':109,'neutral_dificil':79,'candidato_hawkish':71,'candidato_dovish':41})
 def test_metricas_recalculadas(self):
  d=self.p[self.p.incluir_evaluacion=='true'].copy()
  for key,col in [('c_89','pred_c_89'),('wc_600','pred_wc_600')]:
   got=metricas_completas(d.rename(columns={col:'pred'}),'pred'); exp=self.m['modelos'][key]
   for field in ['accuracy','macro_f1','f1_hd','errores','h_d_cruzados','direccion_a_neutral','neutral_a_direccion']: self.assertEqual(got[field],exp[field])
 def test_decision_congelada(self):
  self.assertEqual(self.m['decision'],'adoptar_wc_600'); self.assertTrue(all(self.m['controles_wc_vs_c'].values())); self.assertTrue(self.m['evaluacion_agrupada_cuarentena']); self.assertFalse(self.m['prevalencia_natural'])
 def test_manifest(self):
  man=json.loads((OUT/'manifest.json').read_text())['sha256_salidas']
  for name,h in man.items(): self.assertEqual(hashlib.sha256((OUT/name).read_bytes()).hexdigest(),h)
if __name__=='__main__': unittest.main()
