import hashlib
import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/reestimacion_600_c_wc_v3_v1"


class TestReestimacion600CWC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pred = pd.read_csv(OUT / "predicciones.csv", dtype=str, keep_default_na=False)
        cls.audit = pd.read_csv(OUT / "inclusion_por_fold.csv", dtype=str, keep_default_na=False)
        cls.metrics = json.loads((OUT / "metricas.json").read_text(encoding="utf-8")); cls.ver = json.loads((OUT / "verificacion.json").read_text(encoding="utf-8"))

    def test_anclas_y_validacion(self):
        self.assertEqual(len(self.pred), 793); self.assertEqual(self.pred.intervencion_id.nunique(), 793)
        self.assertTrue(self.ver["ancla_c89_reproducida"]); self.assertTrue(self.ver["ancla_c_primera300_reproducida"])
        self.assertFalse(self.metrics["evaluacion_independiente"]); self.assertFalse(self.metrics["busqueda_hiperparametros"])

    def test_purga_segunda_tanda(self):
        included = self.audit.incluido.eq("True")
        self.assertFalse((included & self.audit.excluir_reunion.eq("True")).any()); self.assertFalse((included & self.audit.excluir_texto.eq("True")).any())
        second = self.audit[self.audit.origen.eq("humana300_dirigida")]
        self.assertEqual(len(second), 1500); self.assertEqual(second.groupby("fold").intervencion_id.nunique().tolist(), [300] * 5)
        self.assertEqual(self.ver["inclusion_segunda_por_fold"], [264, 267, 263, 256, 255])

    def test_metricas(self):
        expected = {"c_mas_600": (0.7866939643053897, 0.6975130654171924, 0.6129032258064516, 55, 8, 23), "wc_mas_600": (0.8250031669610834, 0.7527011922503726, 0.7213114754098361, 48, 7, 22)}
        for key, values in expected.items():
            m = self.metrics[key]; self.assertEqual((m["macro_f1"], m["f1_hd"], m["por_clase"]["dovish"]["f1"], m["errores"], m["h_d_cruzados"], m["direccion_a_neutral"]), values)

    def test_decisiones_congeladas(self):
        self.assertEqual(self.metrics["comparacion_wc_vs_c600"]["decision"], "aceptar_wc")
        self.assertTrue(all(self.metrics["comparacion_wc_vs_c600"]["controles"].values()))
        final = self.metrics["comparacion_seleccionada_vs_ancla_c89"]
        self.assertEqual(final["decision"], "retener_ancla_c89"); self.assertFalse(final["controles"]["omisiones_no_aumentan"])
        self.assertEqual(self.metrics["modelo_de_desarrollo_resultante"], "ancla_c_89")

    def test_manifest(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        for name, expected in manifest.items(): self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), expected)


if __name__ == "__main__": unittest.main()
