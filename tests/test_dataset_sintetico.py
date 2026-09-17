import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.auditar_dataset_sintetico import auditar

RAIZ = Path(__file__).resolve().parents[1]


class DatasetSintetico(unittest.TestCase):
    def test_auditoria_reproduce_estructura_y_bloqueos(self):
        origen = RAIZ/'Dataset_Sintetico_Post2020.csv'
        self.assertEqual('f961845e4494b0237f5991fe4a36208213d91513865a9460927ab93382754ff6',
                         hashlib.sha256(origen.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal)/'auditoria'
            r = auditar(origen, salida)
            self.assertEqual(1018, r['filas'])
            self.assertEqual(1018, r['ids_unicos'])
            self.assertEqual(801, r['textos_normalizados_unicos'])
            self.assertEqual({'Hawkish':357, 'Dovish':364, 'Neutral':297}, r['distribucion_clases'])
            self.assertEqual({'Hawkish':274, 'Dovish':285, 'Neutral':242}, r['distribucion_candidatos_unicos'])
            self.assertEqual(217, r['copias_excedentes'])
            self.assertEqual(0, r['duplicados_con_etiquetas_conflictivas'])
            self.assertEqual(542, r['citas_literal_exacta'])
            self.assertEqual(352, r['citas_no_subcadena_continua'])
            self.assertEqual({'textos_normalizados_exactos':0, 'oraciones_largas_exactas':0},
                             r['solapamiento_corpus_real'])
            self.assertFalse(r['incorporacion_autorizada'])
            manifiesto = json.loads((salida/'manifest.json').read_text(encoding='utf-8'))
            for nombre, esperado in manifiesto['sha256_salidas'].items():
                self.assertEqual(esperado, hashlib.sha256((salida/nombre).read_bytes()).hexdigest())

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal:
            with self.assertRaises(FileExistsError):
                auditar(RAIZ/'Dataset_Sintetico_Post2020.csv', Path(temporal))

    def test_gestor_expone_auditoria(self):
        proceso = subprocess.run([sys.executable, 'scripts/40_gestionar_proyecto.py', '--help'],
                                 cwd=RAIZ, text=True, capture_output=True, check=True)
        self.assertIn('auditar-dataset-sintetico', proceso.stdout)


if __name__ == '__main__':
    unittest.main()
