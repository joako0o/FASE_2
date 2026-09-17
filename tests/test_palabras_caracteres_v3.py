import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/palabras_caracteres_tfidf_v3_v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestPalabrasCaracteresV3(unittest.TestCase):
    def test_ancla_c_y_cobertura(self):
        pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        anchor = pd.read_csv(ROOT / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv",
                             dtype=str, keep_default_na=False).set_index("intervencion_id")
        self.assertEqual(793, len(pred))
        self.assertEqual(793, pred.intervencion_id.nunique())
        self.assertTrue((pred.pred_c == anchor.loc[pred.intervencion_id, "pred_fase_c"].to_numpy()).all())

    def test_seleccion_interna_prefijada(self):
        selections = json.loads((OUT / "seleccion_interna.json").read_text(encoding="utf-8"))
        self.assertEqual(5, len(selections))
        for outer in selections:
            self.assertIn(outer["peso_seleccionado"], {0.5, 1.0})
            self.assertEqual({"0.5", "1.0"}, set(outer["candidatos"]))
            self.assertEqual(6, len(outer["detalle_folds"]))
            for row in outer["detalle_folds"]:
                self.assertGreater(row["reuniones_train"], 0)
                self.assertGreater(row["reuniones_validacion"], 0)

    def test_metricas_y_regla_multicriterio(self):
        m = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        self.assertEqual("rechazar", m["decision"])
        self.assertEqual(2, m["folds_f1_hd_mejorados"])
        self.assertGreater(m["palabras_caracteres"]["f1_hd"], m["candidato_c"]["f1_hd"])
        self.assertGreater(m["palabras_caracteres"]["por_clase"]["dovish"]["f1"],
                           m["candidato_c"]["por_clase"]["dovish"]["f1"])
        self.assertLess(m["palabras_caracteres"]["h_d_cruzados"], m["candidato_c"]["h_d_cruzados"])
        self.assertFalse(m["controles_multicriterio"]["al_menos_3_folds"])

    def test_manifest(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))


if __name__ == "__main__":
    unittest.main()
