import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/adaptacion_dominio_bcch_v3_v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestAdaptacionDominioBCChV3(unittest.TestCase):
    def test_cobertura_y_anclas(self):
        pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        wc = pd.read_csv(ROOT / "data/evaluacion/palabras_caracteres_tfidf_v3_v1/predicciones.csv",
                         dtype=str, keep_default_na=False).set_index("intervencion_id")
        self.assertEqual(793, len(pred))
        self.assertEqual(793, pred.intervencion_id.nunique())
        self.assertTrue((pred.pred_c == wc.loc[pred.intervencion_id, "pred_c"].to_numpy()).all())
        self.assertTrue((pred.pred_wc == wc.loc[pred.intervencion_id, "pred_word_char"].to_numpy()).all())

    def test_dominio_sin_reuniones_validacion(self):
        pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        corpus = pd.read_csv(ROOT / "data/L0/corpus.csv", dtype=str, keep_default_na=False)
        runs = json.loads((OUT / "ejecucion_folds.json").read_text(encoding="utf-8"))
        self.assertEqual(5, len(runs))
        for run in runs:
            val_meetings = set(pred.loc[pred.fold.astype(int).eq(run["fold"]), "meeting_id"])
            expected = corpus.loc[~corpus.meeting_id.isin(val_meetings), "meeting_id"].nunique()
            self.assertEqual(expected, run["reuniones_dominio"])
            self.assertTrue(val_meetings.isdisjoint(set(corpus.loc[~corpus.meeting_id.isin(val_meetings), "meeting_id"])))

    def test_resultado_multicriterio(self):
        m = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        self.assertEqual("rechazar", m["decision"])
        self.assertEqual(3, m["folds_f1_hd_mejorados"])
        self.assertGreater(m["adaptado_l0"]["f1_hd"], m["candidato_c"]["f1_hd"])
        self.assertFalse(m["controles_multicriterio"]["omisiones_no_aumentan"])
        self.assertFalse(m["controles_multicriterio"]["f1_n_no_baja"])
        self.assertFalse(m["etiquetas_dominio_usadas"])

    def test_manifest(self):
        m = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in m["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))


if __name__ == "__main__":
    unittest.main()
