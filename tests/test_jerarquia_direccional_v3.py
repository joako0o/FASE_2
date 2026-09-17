import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/jerarquia_direccional_v3_v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestJerarquiaDireccionalV3(unittest.TestCase):
    def test_cobertura_y_anclas(self):
        pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        wc = pd.read_csv(ROOT / "data/evaluacion/palabras_caracteres_tfidf_v3_v1/predicciones.csv",
                         dtype=str, keep_default_na=False).set_index("intervencion_id")
        self.assertEqual(793, len(pred))
        self.assertEqual(793, pred.intervencion_id.nunique())
        self.assertTrue((pred.pred_c == wc.loc[pred.intervencion_id, "pred_c"].to_numpy()).all())
        self.assertTrue((pred.pred_multiclase_wc == wc.loc[pred.intervencion_id, "pred_word_char"].to_numpy()).all())
        self.assertTrue((pred.pred_relevancia == wc.loc[pred.intervencion_id, "pred_a_word_char"].to_numpy()).all())

    def test_tres_etapas_entrenadas(self):
        runs = json.loads((OUT / "ejecucion_folds.json").read_text(encoding="utf-8"))
        self.assertEqual(5, len(runs))
        for run in runs:
            self.assertEqual({"relevancia", "direccion", "signo"},
                             {k for k in run if k in {"relevancia", "direccion", "signo"}})
            self.assertIn(run["char_weight_reutilizado"], {0.5, 1.0})
            self.assertLess(run["signo"]["n_train"], run["direccion"]["n_train"])
            self.assertLess(run["direccion"]["n_train"], run["relevancia"]["n_train"])

    def test_resultado_rechazado(self):
        m = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        self.assertEqual("rechazar", m["decision"])
        self.assertEqual(1, m["folds_f1_hd_mejorados_vs_c"])
        self.assertLess(m["jerarquia"]["f1_hd"], m["candidato_c"]["f1_hd"])
        self.assertGreater(m["jerarquia"]["h_d_cruzados"], m["candidato_c"]["h_d_cruzados"])
        self.assertLess(m["jerarquia"]["direccion_a_neutral"], m["candidato_c"]["direccion_a_neutral"])

    def test_manifest(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))


if __name__ == "__main__":
    unittest.main()
