import csv
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/mrbert_600_v3_v1"


class TestRecepcionMrBert600V3(unittest.TestCase):
    def test_manifest_interno(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        self.assertEqual(len(manifest), 19)
        for name, expected in manifest.items():
            self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), expected)

    def test_predicciones_y_metricas_recalculadas(self):
        with (OUT / "predicciones.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 793)
        self.assertEqual(len({r["intervencion_id"] for r in rows}), 793)
        labels = ["hawkish", "dovish", "neutral"]
        cm = [[sum(r["etiqueta_v3"] == a and r["pred_mrbert"] == b for r in rows) for b in labels] for a in labels]
        f1 = []
        for i in range(3):
            tp = cm[i][i]; fp = sum(cm[j][i] for j in range(3) if j != i); fn = sum(cm[i][j] for j in range(3) if j != i)
            f1.append(2 * tp / (2 * tp + fp + fn))
        metrics = json.loads((OUT / "metricas.json").read_text(encoding="utf-8"))["mrbert_600"]
        self.assertEqual(cm, metrics["matriz_orden_h_d_n"])
        self.assertAlmostEqual(sum(cm[i][i] for i in range(3)) / 793, metrics["accuracy"])
        self.assertAlmostEqual(sum(f1) / 3, metrics["macro_f1"])
        self.assertAlmostEqual(sum(f1[:2]) / 2, metrics["f1_hd"])

    def test_protocolo_congelado(self):
        p = json.loads((OUT / "protocolo.json").read_text(encoding="utf-8"))
        self.assertEqual(p["revision_huggingface"], "34a7cc86e0d0a2b77e802d07a189db1c0ef2e7d4")
        self.assertEqual((p["max_length"], p["epochs"], p["learning_rate"]), (1024, 2, 2e-5))
        self.assertFalse(p["evaluacion_independiente"])


if __name__ == "__main__": unittest.main()
