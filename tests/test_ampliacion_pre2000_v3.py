import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/ampliacion_pre2000_tfidf_v3_v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestAmpliacionPre2000V3(unittest.TestCase):
    def test_ancla_y_cobertura(self):
        pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        self.assertEqual(793, len(pred))
        self.assertEqual(793, pred.intervencion_id.nunique())
        self.assertTrue((pred.pred_c == pd.read_csv(
            ROOT / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv",
            dtype=str, keep_default_na=False).set_index("intervencion_id").loc[
                pred.intervencion_id, "pred_fase_c"].to_numpy()).all())
        runs = json.loads((OUT / "ejecucion_folds.json").read_text(encoding="utf-8"))
        augmented = [x for x in runs if x["condicion"] == "c_mas_pre2000"]
        self.assertEqual(5, len(augmented))
        self.assertEqual({250}, {x["n_pre2000"] for x in augmented})

    def test_decision_predefinida(self):
        metrics = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        self.assertEqual("rechazar_dosis_pre2000", metrics["decision"])
        self.assertEqual(2, metrics["folds_f1_hd_mejorados"])
        self.assertGreater(metrics["c_mas_pre2000"]["por_clase"]["dovish"]["f1"],
                           metrics["candidato_c"]["por_clase"]["dovish"]["f1"])
        self.assertGreater(metrics["c_mas_pre2000"]["errores"], metrics["candidato_c"]["errores"])

    def test_manifest(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))


if __name__ == "__main__":
    unittest.main()
