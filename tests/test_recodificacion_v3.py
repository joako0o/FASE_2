import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.evaluar_recodificacion_v3 import evaluar

RAIZ = Path(__file__).resolve().parents[1]


class RecodificacionV3FaseA(unittest.TestCase):
    def test_reproduce_ancla_y_recodifica_sin_entrenar(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'fase_a'
            metricas = evaluar(salida)
            v2, v3 = metricas['referencia_v2'], metricas['referencia_v3']
            self.assertEqual(793, metricas['predicciones_congeladas'])
            self.assertEqual(0.935687263556116, v2['accuracy'])
            self.assertEqual(0.8199279654489144, v2['macro_f1'])
            self.assertEqual(0.7435283118097353, v2['f1_hd'])
            self.assertEqual(0.7470596639017691, v2['media_folds_f1_hd'])
            self.assertEqual(0.9192938209331651, v3['accuracy'])
            self.assertEqual(0.6623931623931624, v3['f1_hd'])
            self.assertEqual(51, v2['errores'])
            self.assertEqual(64, v3['errores'])
            self.assertEqual(28, metricas['cambios_etiqueta_en_validacion'])
            self.assertEqual(1, metricas['cambios_relevancia_en_validacion'])
            self.assertEqual(767, metricas['clasificador_relevancia_congelado']['v2']['aciertos'])
            self.assertEqual(768, metricas['clasificador_relevancia_congelado']['v3']['aciertos'])
            self.assertEqual({'sin_cambio': 768, 'acierto_a_error': 19, 'error_a_acierto': 6},
                             metricas['efecto_en_aciertos'])
            desglose = json.loads((salida / 'desagregacion_errores.json').read_text(encoding='utf-8'))
            self.assertEqual({'inversion_h_d': 15, 'direccion_a_neutral': 15,
                              'neutral_a_direccion': 34}, desglose['tipos_operativos'])
            self.assertEqual(23, desglose['por_clase_real']['hawkish']['errores'])
            self.assertEqual(7, desglose['por_clase_real']['dovish']['errores'])
            self.assertEqual(34, desglose['por_clase_real']['neutral']['errores'])
            self.assertEqual(37, desglose['concentracion_reuniones']['reuniones_con_error'])
            self.assertFalse(metricas['entrenamiento_ejecutado'])
            with (salida / 'predicciones_referencias_v2_v3.csv').open(encoding='utf-8', newline='') as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertEqual(793, len(filas))
            self.assertEqual(793, len({fila['intervencion_id'] for fila in filas}))
            self.assertEqual({'seis_mas_trece'}, {fila['supervision_prediccion_congelada'] for fila in filas})
            manifiesto = json.loads((salida / 'manifest.json').read_text(encoding='utf-8'))
            for nombre, esperado in manifiesto['sha256_salidas'].items():
                self.assertEqual(esperado, hashlib.sha256((salida / nombre).read_bytes()).hexdigest())

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'fase_a'
            evaluar(salida)
            with self.assertRaises(FileExistsError):
                evaluar(salida)

    def test_gestor_expone_fase_a_sin_ejecutarla(self):
        proceso = subprocess.run([sys.executable, 'scripts/40_gestionar_proyecto.py', '--help'],
                                 cwd=RAIZ, text=True, capture_output=True, check=True)
        self.assertIn('evaluar-recodificacion-v3', proceso.stdout)


if __name__ == '__main__':
    unittest.main()
