import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import entrenar_tfidf_supervision_v3 as E

RAIZ = Path(__file__).resolve().parents[1]


class TfidfSupervisionV3(unittest.TestCase):
    def test_fase_b_reproduce_ancla_y_entrena_v3(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'fase_b'
            metricas = E.ejecutar(salida)
            a = metricas['fase_a_congelada_contra_v3']
            b = metricas['fase_b_reentrenada_contra_v3']
            self.assertEqual(64, a['errores'])
            self.assertEqual(57, b['errores'])
            self.assertEqual(0.6683673469387755, b['f1_hd'])
            self.assertEqual(0.6615741079040312, b['media_folds_f1_hd'])
            self.assertEqual(13, b['h_d_cruzados'])
            self.assertEqual(28, b['neutral_a_direccion'])
            self.assertEqual(40, metricas['predicciones_finales_cambiadas'])
            self.assertEqual({'sin_cambio': 762, 'error_a_acierto': 19, 'acierto_a_error': 12},
                             metricas['efecto_en_aciertos'])
            self.assertFalse(metricas['ia_nueva_89_incluida'])
            verificacion = json.loads((salida/'verificacion.json').read_text(encoding='utf-8'))
            self.assertTrue(verificacion['ancla_v2_reproducida_exactamente_793'])
            self.assertEqual([1178, 1178, 1178, 1183, 1183], verificacion['conteos_train_por_fold'])
            manifiesto = json.loads((salida/'manifest.json').read_text(encoding='utf-8'))
            for nombre, esperado in manifiesto['sha256_salidas'].items():
                self.assertEqual(esperado, hashlib.sha256((salida/nombre).read_bytes()).hexdigest())

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal:
            with self.assertRaises(FileExistsError):
                E.ejecutar(Path(temporal))

    def test_gestor_expone_fase_b(self):
        proceso = subprocess.run([sys.executable, 'scripts/40_gestionar_proyecto.py', '--help'],
                                 cwd=RAIZ, text=True, capture_output=True, check=True)
        self.assertIn('entrenar-tfidf-v3', proceso.stdout)


if __name__ == '__main__':
    unittest.main()
