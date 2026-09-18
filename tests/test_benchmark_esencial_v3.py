import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.consolidar_benchmark_esencial_v3 import OUT, run

ROOT = Path(__file__).resolve().parents[1]


class TestBenchmarkEsencialV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((OUT / "registro.json").read_text(encoding="utf-8"))
        with (OUT / "tabla_modelos.csv").open(encoding="utf-8", newline="") as f: cls.rows = list(csv.DictReader(f))

    def test_modelos_y_estados_clave(self):
        self.assertEqual(len(self.rows), 14)
        self.assertEqual(self.registry["mejor_numerico_v3"], "W+C+600")
        self.assertEqual(self.registry["modelo_formal_vigente"], "W+C+600")
        self.assertIn("W+C+600 adoptado", self.registry["ciega_300_estado"])
        self.assertEqual(self.registry["mrbert_estado"], "ejecutado; no adoptado")
        self.assertEqual({r["modelo"] for r in self.rows} & {"MrBERT-es+600"}, {"MrBERT-es+600"})

    def test_metricas_copiadas_de_fuentes(self):
        by = {r["modelo"]: r for r in self.rows}
        source = json.loads((ROOT / "data/evaluacion/reestimacion_600_c_wc_v3_v1/metricas.json").read_text(encoding="utf-8"))["wc_mas_600"]
        self.assertEqual(float(by["W+C+600"]["macro_f1"]), source["macro_f1"])
        self.assertEqual(float(by["W+C+600"]["f1_hd"]), source["f1_hd"])
        self.assertEqual(int(by["W+C+600"]["errores"]), source["errores"])
        legacy = json.loads((ROOT / "data/auditoria/recepcion_beto_v1/auditoria.json").read_text(encoding="utf-8"))["comparacion"]["condiciones"]
        self.assertEqual(float(by["BETO"]["macro_f1"]), legacy["beto"]["conjunto"]["macro_f1"])
        mrbert = json.loads((ROOT / "data/evaluacion/mrbert_600_v3_v1/metricas.json").read_text(encoding="utf-8"))["mrbert_600"]
        self.assertEqual(float(by["MrBERT-es+600"]["macro_f1"]), mrbert["macro_f1"])
        self.assertEqual(int(by["MrBERT-es+600"]["omisiones_direccion"]), 27)

    def test_parametros_congelados(self):
        params = self.registry["parametros_tfidf"]
        self.assertEqual(params["logistic_regression"], {"class_weight": "balanced", "max_iter": 2000, "random_state": 20260915, "C": 2.0})
        self.assertEqual(params["tfidf_palabras_B"]["ngram_range"], [1, 4])
        self.assertEqual(params["tfidf_caracteres"]["ngram_range"], [3, 5])
        self.assertEqual(params["pesos_char_congelados_por_outer_fold"], {"1": 1.0, "2": 0.5, "3": 1.0, "4": 1.0, "5": 1.0})

    def test_documento_preserva_defensa_y_limites(self):
        text = (ROOT / "docs/BENCHMARK_ESENCIAL_MODELOS_V3.md").read_text(encoding="utf-8")
        for phrase in ("Por qué se sostiene TF-IDF/W+C", "Comparación controlada histórica con BETO", "Elementos que no deben eliminarse", "no evaluación final independiente"):
            self.assertIn(phrase, text)

    def test_manifest_y_reproducibilidad(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        for name, expected in manifest.items(): self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), expected)
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "benchmark"; run(generated)
            for name in (*manifest, "manifest.json"): self.assertEqual((generated / name).read_bytes(), (OUT / name).read_bytes())


if __name__ == "__main__": unittest.main()
