import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from preparar_dosis_sinteticas_v3 import preparar
from evaluar_dosis_sinteticas_tfidf_v3 import ejecutar

RAIZ=Path(__file__).resolve().parents[1]


class DosisSinteticasV3(unittest.TestCase):
    def test_preparacion_deduplica_y_fija_dosis(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida=Path(temporal)/'dosis';r=preparar(salida)
            self.assertEqual(801,r['textos_unicos'])
            self.assertEqual([250,500,750,801],[x['n'] for x in r['dosis']])
            self.assertEqual([211,336,465,501],[x['familias_lote_tema'] for x in r['dosis']])
            with (salida/'pool_sintetico_deduplicado.csv').open(encoding='utf-8',newline='') as f:
                pool=list(csv.DictReader(f))
            self.assertEqual(801,len(pool));self.assertEqual(801,len({x['synthetic_id'] for x in pool}))
            self.assertTrue(r['anidadas']);self.assertTrue(r['etiquetas_sinteticas_son_provisionales'])

    def test_resultado_canonico_no_aprueba_dosis(self):
        salida=RAIZ/'data/evaluacion/dosis_sinteticas_tfidf_v3_v1'
        m=json.loads((salida/'metricas.json').read_text(encoding='utf-8'))
        self.assertFalse(m['alguna_dosis_cumple_todos']);self.assertFalse(m['modelo_adoptado'])
        resultados={(x['base'],x['dosis']):x for x in m['resultados_dosis']}
        self.assertEqual(55,resultados[('B',250)]['errores'])
        self.assertEqual(52,resultados[('C',750)]['errores'])
        self.assertEqual(0.40625,resultados[('C',750)]['recall_d'])
        self.assertEqual(0.660241593718051,resultados[('C',750)]['media_folds_f1_hd'])
        manifiesto=json.loads((salida/'manifest.json').read_text(encoding='utf-8'))
        for nombre,esperado in manifiesto['sha256_salidas'].items():
            self.assertEqual(esperado,hashlib.sha256((salida/nombre).read_bytes()).hexdigest())

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal:
            with self.assertRaises(FileExistsError):preparar(Path(temporal))
            with self.assertRaises(FileExistsError):ejecutar(Path(temporal))

    def test_gestor_expone_comandos(self):
        p=subprocess.run([sys.executable,'scripts/40_gestionar_proyecto.py','--help'],cwd=RAIZ,
                         text=True,capture_output=True,check=True)
        self.assertIn('preparar-dosis-sinteticas',p.stdout)
        self.assertIn('evaluar-dosis-sinteticas-v3',p.stdout)


if __name__=='__main__':unittest.main()
