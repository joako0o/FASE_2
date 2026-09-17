import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.preparar_migracion_v3 import preparar
from scripts.registrar_revision_v3 import registrar


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
            self.assertEqual(1352, resumen['revisados_iniciales'])
            self.assertEqual(395, resumen['pendientes'])

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

    def test_lotes_nuevos_coinciden_con_decisiones_declaradas(self):
        raiz = Path(__file__).resolve().parents[1]
        esperados = {
            'revision_etiquetas_piloto_r4_v3': (17, 0),
            'revision_etiquetas_escalado_r5_v3': (99, 2),
            'revision_etiquetas_escalado_r6_v3': (93, 5),
            'revision_etiquetas_escalado_r7_v3': (103, 5),
            'revision_etiquetas_escalado_r8_v3': (52, 8),
            'revision_etiquetas_escalado_r9_v3': (94, 4),
            'revision_etiquetas_escalado_r10_v3': (120, 7),
            'revision_etiquetas_escalado_r11_v3': (110, 2),
            'revision_etiquetas_escalado_r12_v3': (54, 1),
            'revision_etiquetas_escalado_r13_v3': (58, 1),
            'revision_etiquetas_escalado_r14_v3': (56, 0),
            'revision_etiquetas_escalado_r15_v3': (71, 2),
            'revision_etiquetas_escalado_r16_v3': (58, 2),
            'revision_etiquetas_escalado_r17_v3': (7, 0),
        }
        for nombre, (total, cambios) in esperados.items():
            carpeta = raiz / 'data/auditoria' / nombre
            with (carpeta / 'revision.csv').open(encoding='utf-8', newline='') as archivo:
                filas = list(csv.DictReader(archivo))
            decisiones = json.loads((carpeta / 'decisiones.json').read_text(encoding='utf-8'))
            ids_cambio = {fila['intervencion_id'] for fila in filas
                          if fila['resultado_revision'] != 'compatible'}
            self.assertEqual(total, len(filas))
            self.assertEqual(cambios, len(ids_cambio))
            self.assertEqual({fila['intervencion_id'] for fila in decisiones}, ids_cambio)

    def test_registro_no_sobrescribe_lote_cerrado(self):
        raiz = Path(__file__).resolve().parents[1]
        carpeta = raiz / 'data/auditoria/revision_etiquetas_piloto_r4_v3'
        with self.assertRaises(FileExistsError):
            registrar(raiz / 'data/etiquetas/etiquetas_piloto_r4.csv',
                      carpeta / 'decisiones.json', carpeta)


if __name__ == '__main__':
    unittest.main()
