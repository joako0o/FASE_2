import hashlib
import json
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluar_ensamble_calibrado_v3 import POLICIES, split_sentences

OUT = ROOT / "data/evaluacion/ensamble_calibrado_v3_v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestEnsambleCalibradoV3(unittest.TestCase):
    def test_preregistro_y_seleccion_interna(self):
        metrics = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        protocol = json.loads((OUT / "protocolo.json").read_text(encoding="utf-8"))
        self.assertEqual(1.0, metrics["peso_char_interno"])
        self.assertEqual("blend_50", metrics["politica_ganadora_interna"])
        self.assertEqual(set(POLICIES), set(metrics["seleccion_politicas"]))
        self.assertTrue(protocol["seleccion_solo_fold0"])
        self.assertEqual(559, protocol["n_seleccion"])
        self.assertEqual("blend_50", protocol["politica_fijada_antes_outer"])
        for result in metrics["seleccion_politicas"].values():
            self.assertEqual(559, result["metricas"]["filas"])
            self.assertEqual(3, len(result["metricas"]["por_fold"]))

    def test_apertura_externa_unica_y_ancla(self):
        pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        anchor = pd.read_csv(ROOT / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv",
                             dtype=str, keep_default_na=False).set_index("intervencion_id")
        self.assertEqual(793, len(pred))
        self.assertEqual(793, pred.intervencion_id.nunique())
        self.assertEqual({"blend_50"}, set(pred.politica_ganadora))
        self.assertTrue((pred.pred_c == anchor.loc[pred.intervencion_id, "pred_fase_c"].to_numpy()).all())
        self.assertEqual({"pred_c", "pred_ensamble"}, {c for c in pred.columns if c.startswith("pred_")})

    def test_resultado_rechazado(self):
        m = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        self.assertEqual("rechazar", m["decision"])
        self.assertFalse(m["politicas_perdedoras_abiertas_externamente"])
        self.assertGreater(m["ensamble"]["por_clase"]["dovish"]["f1"],
                           m["candidato_c"]["por_clase"]["dovish"]["f1"])
        self.assertLess(m["ensamble"]["h_d_cruzados"], m["candidato_c"]["h_d_cruzados"])
        self.assertGreater(m["ensamble"]["direccion_a_neutral"], m["candidato_c"]["direccion_a_neutral"])
        self.assertEqual(1, m["folds_f1_hd_mejorados"])

    def test_segmentacion_oraciones(self):
        self.assertEqual(["Primera.", "Segunda;", "Tercera?"], split_sentences("Primera. Segunda; Tercera?"))

    def test_manifest(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))


if __name__ == "__main__":
    unittest.main()
