import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/encoder_contextual_factibilidad_v3_v1"


class TestEncoderFactibilidadV3(unittest.TestCase):
    def test_bloqueo_documentado(self):
        r = json.loads((OUT / "resumen.json").read_text(encoding="utf-8"))
        self.assertEqual("no_ejecutar_finetuning_contextual_en_este_entorno", r["decision"])
        self.assertFalse(r["backend_torch"] or r["backend_tensorflow"] or r["backend_flax"])
        self.assertEqual(0, r["pesos_encoder_locales"])
        self.assertFalse(r["modelo_descargado"])
        self.assertFalse(r["etiquetas_validacion_consultadas"])

    def test_manifest(self):
        m = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in m["sha256_salidas"].items():
            actual = hashlib.sha256((OUT / name).read_bytes()).hexdigest()
            self.assertEqual(digest, actual)


if __name__ == "__main__":
    unittest.main()
