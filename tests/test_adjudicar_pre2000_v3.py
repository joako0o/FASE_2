import csv
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/pre2000_adjudicacion_v3_v1"
CSV_PATH = OUT / "adjudicacion_pre2000_v3.csv"


def rows(path=CSV_PATH):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def norm(text):
    return " ".join(text.split())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestAdjudicarPre2000V3(unittest.TestCase):
    def test_cobertura_estados_y_coherencia(self):
        data = rows()
        self.assertEqual(257, len(data))
        self.assertEqual(257, len({x["frag_id"] for x in data}))
        self.assertEqual(7, sum(x["estado_revision_v3"] == "pendiente" for x in data))
        self.assertEqual(18, sum(x["resultado_revision"] == "corregido_v3" for x in data))
        for row in data:
            self.assertIn(row["estado_revision_v3"], {"cerrado", "pendiente"})
            if row["estado_revision_v3"] == "cerrado":
                self.assertIn(row["etiqueta_v3"], {"hawkish", "dovish", "neutral"})
            else:
                self.assertEqual("", row["etiqueta_v3"])
            if row["es_relevante_v3"] == "0":
                self.assertEqual("neutral", row["etiqueta_v3"])

    def test_citas_literales_continuas(self):
        for row in rows():
            quote, text = norm(row["cita_literal"]), norm(row["texto_original"])
            self.assertTrue(quote, row["frag_id"])
            self.assertLessEqual(len(quote), 300, row["frag_id"])
            self.assertIn(quote, text, row["frag_id"])

    def test_hash_texto_y_manifest(self):
        for row in rows():
            expected = hashlib.sha256(norm(row["texto_original"]).encode()).hexdigest()
            self.assertEqual(expected, row["sha256_texto"])
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))

    def test_reproducibilidad_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "audit"
            code = (
                "import scripts.adjudicar_pre2000_v3 as m; "
                f"m.run(r'{output}')"
            )
            subprocess.run([str(ROOT / ".venv/bin/python"), "-c", code], cwd=ROOT, check=True)
            self.assertEqual(CSV_PATH.read_bytes(), (output / CSV_PATH.name).read_bytes())

    def test_correcciones_clave(self):
        by_id = {int(x["frag_id"]): x for x in rows()}
        self.assertEqual("dovish", by_id[21889]["etiqueta_v3"])
        self.assertEqual("neutral", by_id[33261]["etiqueta_v3"])
        self.assertEqual("0", by_id[33261]["es_relevante_v3"])
        self.assertEqual("neutral", by_id[22418]["etiqueta_v3"])
        self.assertEqual("pendiente", by_id[27869]["estado_revision_v3"])


if __name__ == "__main__":
    unittest.main()
