import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import evaluar_ampliacion_ia89_v3 as E

RAIZ = Path(__file__).resolve().parents[1]


class AmpliacionIA89V3(unittest.TestCase):
    def test_fase_c_reproduce_b_y_agrega_solo_train(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal)/'fase_c'
            m = E.ejecutar(salida)
            b, c = m['fase_b_base'], m['fase_c_mas_89']
            self.assertEqual(57, b['errores'])
            self.assertEqual(57, c['errores'])
            self.assertEqual(0.6763392857142858, c['f1_hd'])
            self.assertEqual(0.661681600053693, c['media_folds_f1_hd'])
            self.assertEqual(12, c['h_d_cruzados'])
            self.assertEqual([79, 79, 79, 72, 76], m['n_ia_nueva_por_fold'])
            self.assertEqual(11, m['predicciones_finales_cambiadas'])
            self.assertEqual({'sin_cambio': 785, 'acierto_a_error': 4, 'error_a_acierto': 4},
                             m['efecto_en_aciertos'])
            self.assertFalse(m['sinteticos_incluidos'])
            v = json.loads((salida/'verificacion.json').read_text(encoding='utf-8'))
            self.assertTrue(v['fase_b_reproducida_exactamente_793'])
            self.assertTrue(v['ia_nueva_no_usada_en_validacion'])
            manifiesto = json.loads((salida/'manifest.json').read_text(encoding='utf-8'))
            for nombre, esperado in manifiesto['sha256_salidas'].items():
                self.assertEqual(esperado, hashlib.sha256((salida/nombre).read_bytes()).hexdigest())

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal:
            with self.assertRaises(FileExistsError):
                E.ejecutar(Path(temporal))

    def test_gestor_expone_fase_c(self):
        proceso = subprocess.run([sys.executable, 'scripts/40_gestionar_proyecto.py', '--help'],
                                 cwd=RAIZ, text=True, capture_output=True, check=True)
        self.assertIn('evaluar-ampliacion-ia89-v3', proceso.stdout)


if __name__ == '__main__':
    unittest.main()
