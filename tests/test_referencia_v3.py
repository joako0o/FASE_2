import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.auditar_set_pre2000 import auditar
from scripts.consolidar_referencia_v3 import consolidar


RAIZ = Path(__file__).resolve().parents[1]


class ReferenciaV3(unittest.TestCase):
    def test_consolidacion_completa_y_roles_separados(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'referencia'
            resumen = consolidar(salida)
            with (salida / 'referencia_v3.csv').open(encoding='utf-8', newline='') as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertEqual(1747, len(filas))
            self.assertEqual(1747, len({fila['intervencion_id'] for fila in filas}))
            self.assertTrue(all(fila['estado_revision_v3'] == 'revisado' for fila in filas))
            self.assertEqual({'si': 1352, 'no': 395},
                             dict(__import__('collections').Counter(f['incluir_control_primario'] for f in filas)))
            self.assertEqual({'neutral': 1414, 'hawkish': 218, 'dovish': 115}, resumen['etiquetas_v3'])
            self.assertEqual(0, resumen['pendientes'])
            self.assertFalse(resumen['referencia_humana_v3_es_test_ciego'])

    def test_consolidacion_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'referencia'
            consolidar(salida)
            with self.assertRaises(FileExistsError):
                consolidar(salida)

    def test_gestor_expone_comandos_sin_ejecutarlos(self):
        proceso = subprocess.run([sys.executable, 'scripts/40_gestionar_proyecto.py', '--help'],
                                 cwd=RAIZ, text=True, capture_output=True, check=True)
        self.assertIn('consolidar-referencia-v3', proceso.stdout)
        self.assertIn('auditar-set-pre2000', proceso.stdout)

    def test_auditoria_pre2000_reproduce_incidencias(self):
        origen = RAIZ / 'Set_Entrenamiento_Pre_2000.xlsx'
        self.assertEqual('662ec786e234a8bd8824214c81cf8139ad0955a8f139a596ba9bbf18859ad3fb',
                         hashlib.sha256(origen.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'auditoria'
            resumen = auditar(origen, salida)
            self.assertEqual(257, resumen['filas'])
            self.assertEqual(257, resumen['ids_unicos'])
            self.assertEqual(253, resumen['textos_normalizados_unicos'])
            self.assertEqual({'pendiente_en_etiqueta': 6, 'cita_no_literal_o_extensa': 8,
                              'texto_duplicado_normalizado': 8}, resumen['incidencias'])
            self.assertFalse(resumen['incorporacion_autorizada'])
            manifiesto = json.loads((salida / 'manifest.json').read_text(encoding='utf-8'))
            for nombre, esperado in manifiesto['sha256_salidas'].items():
                obtenido = hashlib.sha256((salida / nombre).read_bytes()).hexdigest()
                self.assertEqual(esperado, obtenido)


if __name__ == '__main__':
    unittest.main()
