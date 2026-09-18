import csv
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestProyectoEsencial(unittest.TestCase):
    def test_inventario_reducido(self):
        scripts = list((ROOT / "scripts").glob("*.py"))
        tests = list((ROOT / "tests").glob("test_*.py"))
        self.assertEqual([p.name for p in scripts], ["modelo_final.py"])
        self.assertEqual([p.name for p in tests], ["test_proyecto_esencial.py"])
        self.assertLessEqual(len(list((ROOT / "docs").glob("*.md"))), 7)

    def test_integridad(self):
        manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))["sha256"]
        for name, expected in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_entrenamiento_final(self):
        with (ROOT / "data/entrenamiento_wc600.csv").open(encoding="utf-8", newline="") as f: rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1596)
        self.assertEqual(len({r["intervencion_id"] for r in rows}), 1596)
        expected = {1: 1494, 2: 1450, 3: 1453, 4: 1473, 5: 1466}
        self.assertEqual({i: sum(str(i) in r["miembros"].split("|") for r in rows) for i in range(1, 6)}, expected)
        with (ROOT / "data/evaluacion_ciega_gold.csv").open(encoding="utf-8", newline="") as f: gold = list(csv.DictReader(f))
        self.assertEqual(len(gold), 300)
        self.assertFalse({r["meeting_id"] for r in rows} & {r["meeting_id"] for r in gold})

    def test_resultado_y_benchmark(self):
        result = json.loads((ROOT / "data/resultados_evaluacion_ciega.json").read_text(encoding="utf-8"))
        self.assertEqual(result["decision"], "adoptar_wc_600")
        self.assertEqual(result["filas_evaluadas"], 299)
        self.assertAlmostEqual(result["modelos"]["wc_600"]["macro_f1"], 0.7462588094167041)
        benchmark = json.loads((ROOT / "data/benchmark_modelos.json").read_text(encoding="utf-8"))
        self.assertEqual(len(benchmark["modelos"]), 14)
        self.assertEqual(benchmark["modelo_formal_vigente"], "W+C+600")

    def test_clasificacion_completa(self):
        with (ROOT / "resultados/clasificacion_wc600_9725.csv").open(encoding="utf-8", newline="") as f: rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9725)
        self.assertEqual(len({r["intervencion_id"] for r in rows}), 9725)
        self.assertEqual(len({r["topico_humano"] for r in rows}), 13)
        self.assertTrue(all(r["keywords_humano"] for r in rows))
        self.assertEqual({label: sum(r["prediccion_v3"] == label for r in rows) for label in ["hawkish", "dovish", "neutral"]}, {"hawkish": 513, "dovish": 380, "neutral": 8832})
        self.assertEqual(sum(r["acuerdo_miembros"] == "desacuerdo" for r in rows), 169)
        manifest = json.loads((ROOT / "resultados/manifest.json").read_text(encoding="utf-8"))["sha256"]
        for name, expected in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT / "resultados" / name).read_bytes()).hexdigest(), expected)

    def test_script_verifica(self):
        spec = importlib.util.spec_from_file_location("modelo_final", ROOT / "scripts/modelo_final.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual(module.verificar()["estado"], "íntegro")
        self.assertEqual(module.CHAR["ngram_range"], (3, 5))
        self.assertEqual(module.LR["C"], 2.0)


if __name__ == "__main__": unittest.main()
