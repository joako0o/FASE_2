import hashlib
import json
import unittest
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluar_extension_representaciones_v3 import monetary_tokenizer
OUT = ROOT / "data/evaluacion/extension_representaciones_v3_v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestExtensionRepresentacionesV3(unittest.TestCase):
    def test_tokenizador_monetario(self):
        tokens = monetary_tokenizer("No corresponde subir 25 pb la tasa de política monetaria desde UF+5,0%.")
        self.assertIn("neg_subir", tokens)
        self.assertIn("25", tokens)
        self.assertIn("pb", tokens)
        self.assertIn("tasa_politica", tokens)
        self.assertIn("politica_monetaria", tokens)
        self.assertTrue(any(x.startswith("uf+") for x in tokens))

    def test_seleccion_solo_core(self):
        metrics = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        protocol = json.loads((OUT / "protocolo.json").read_text(encoding="utf-8"))
        self.assertEqual("nbsvm", metrics["ganador_interno"])
        self.assertEqual("nbsvm", protocol["ganador_fijado_antes_evaluacion_externa"])
        self.assertEqual(559, protocol["n_core_seleccion"])
        self.assertTrue(protocol["outer_no_usado_para_seleccion"])
        self.assertEqual({"token_monetario", "nbsvm", "lsa128", "suavizado_oraciones"},
                         set(metrics["seleccion_interna"]))
        for result in metrics["seleccion_interna"].values():
            self.assertEqual(559, result["agregadas"]["filas"])
            self.assertEqual(3, len(result["por_fold"]))

    def test_evaluacion_externa_unico_ganador_y_ancla(self):
        pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        anchor = pd.read_csv(ROOT / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv",
                             dtype=str, keep_default_na=False).set_index("intervencion_id")
        self.assertEqual(793, len(pred))
        self.assertEqual(793, pred.intervencion_id.nunique())
        self.assertEqual({"nbsvm"}, set(pred.metodo_ganador_interno))
        self.assertTrue((pred.pred_c == anchor.loc[pred.intervencion_id, "pred_fase_c"].to_numpy()).all())
        self.assertNotIn("pred_token_monetario", pred.columns)
        self.assertNotIn("pred_lsa128", pred.columns)
        self.assertNotIn("pred_suavizado_oraciones", pred.columns)

    def test_resultado_y_regla(self):
        m = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        self.assertEqual("rechazar", m["decision"])
        self.assertFalse(m["metodos_no_ganadores_evaluados_externamente"])
        self.assertGreater(m["extension"]["f1_hd"], m["candidato_c"]["f1_hd"])
        self.assertLess(m["extension"]["por_clase"]["dovish"]["recall"],
                        m["candidato_c"]["por_clase"]["dovish"]["recall"])
        self.assertLess(m["extension"]["errores"], m["candidato_c"]["errores"])

    def test_manifest(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))


if __name__ == "__main__":
    unittest.main()
