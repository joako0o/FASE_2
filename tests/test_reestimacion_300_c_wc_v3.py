import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/reestimacion_300_c_wc_v3_v1"
WEIGHTS = {1: 1.0, 2: 0.5, 3: 1.0, 4: 1.0, 5: 1.0}


class TestReestimacion300CWC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        cls.audit = pd.read_csv(OUT / "inclusion_por_fold.csv", dtype=str, keep_default_na=False)
        cls.metrics = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))
        cls.verification = json.loads((OUT / "verificacion.json").read_text(encoding="utf-8"))

    def test_validacion_historica_completa_y_ancla(self):
        self.assertEqual(len(self.pred), 793)
        self.assertEqual(self.pred.intervencion_id.nunique(), 793)
        self.assertEqual(set(self.pred.fold), {"1", "2", "3", "4", "5"})
        self.assertTrue(self.verification["ancla_c89_reproducida_exactamente"])
        self.assertFalse(self.metrics["evaluacion_independiente"])

    def test_exclusiones_de_reunion_y_texto(self):
        included = self.audit.incluido.eq("True")
        self.assertFalse((included & self.audit.excluir_reunion.eq("True")).any())
        self.assertFalse((included & self.audit.excluir_texto.eq("True")).any())
        human = self.audit[self.audit.origen.eq("humana300")]
        self.assertEqual(len(human), 1500)
        self.assertEqual(human.groupby("fold").intervencion_id.nunique().tolist(), [300] * 5)
        self.assertEqual(self.verification["inclusion_humana_por_fold"], [270, 268, 266, 260, 257])

    def test_pesos_y_sin_busqueda(self):
        execution = json.loads((OUT / "ejecucion_folds.json").read_text(encoding="utf-8"))
        self.assertEqual({int(r["fold"]): r["peso_char"] for r in execution}, WEIGHTS)
        self.assertFalse(self.metrics["busqueda_hiperparametros"])

    def test_metricas_principales(self):
        expected = {
            "ancla_c_89": (0.772956468462667, 0.6763392857142858, 57, 12, 15),
            "c_mas_300": (0.7803404500271257, 0.6865434863755133, 54, 11, 19),
            "wc_mas_300": (0.8116728880265337, 0.732728337236534, 49, 8, 21),
        }
        for key, values in expected.items():
            m = self.metrics[key]
            self.assertEqual((m["macro_f1"], m["f1_hd"], m["errores"], m["h_d_cruzados"],
                              m["direccion_a_neutral"]), values)

    def test_decisiones_preregistradas(self):
        wc = self.metrics["comparacion_wc_vs_c300"]
        self.assertEqual(wc["decision"], "retener_c")
        self.assertFalse(wc["controles"]["omisiones_no_aumentan"])
        final = self.metrics["comparacion_seleccionada_vs_ancla_c89"]
        self.assertEqual(final["decision"], "retener_ancla_c89")
        self.assertFalse(final["controles"]["recall_d_no_baja"])
        self.assertFalse(final["controles"]["omisiones_no_aumentan"])
        self.assertEqual(self.metrics["modelo_de_desarrollo_resultante"], "ancla_c_89")

    def test_manifest(self):
        hashes = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        for name, expected in hashes.items():
            self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
