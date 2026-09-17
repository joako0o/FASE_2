import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.preparar_migracion_v3 import preparar


class MigracionV3(unittest.TestCase):
    def test_inventario_completo_y_disjunto(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'auditoria'
            resumen = preparar(salida)
            with (salida / 'inventario.csv').open(encoding='utf-8', newline='') as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertEqual(1747, len(filas))
            self.assertEqual(1747, len({fila['intervencion_id'] for fila in filas}))
            self.assertEqual({'ia_base_v2': 1352, 'ia_nueva_v1': 89, 'humana_v2': 306},
                             resumen['por_coleccion'])
            self.assertEqual(360, resumen['revisados_iniciales'])
            self.assertEqual(1387, resumen['pendientes'])

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'auditoria'
            preparar(salida)
            with self.assertRaises(FileExistsError):
                preparar(salida)

    def test_cada_texto_tiene_hash(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / 'auditoria'
            preparar(salida)
            with (salida / 'inventario.csv').open(encoding='utf-8', newline='') as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertTrue(all(len(fila['sha256_texto']) == 64 for fila in filas))
            self.assertTrue(all(int(fila['n_caracteres_texto']) > 0 for fila in filas))

    def test_gestor_expone_comando(self):
        raiz = Path(__file__).resolve().parents[1]
        proceso = subprocess.run([sys.executable, 'scripts/40_gestionar_proyecto.py', '--help'],
                                 cwd=raiz, text=True, capture_output=True, check=True)
        self.assertIn('preparar-migracion-v3', proceso.stdout)


if __name__ == '__main__':
    unittest.main()
