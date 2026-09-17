import csv
import hashlib
import json
import subprocess
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/recepcion/anotacion_adicional_300_v3_v1"
CANONICAL = OUT / "anotaciones_canonicas.csv"
QUEUE = OUT / "revision_semantica_prioritaria_100.csv"


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class TestRecepcionAnotacion300V3(unittest.TestCase):
    def test_origen_y_cobertura(self):
        self.assertEqual("5a4951360c61c8e6e7752706af7880771e9d4399a3e4bf325df628aa5b78dbfa",
                         sha(OUT / "anotacion_original.xlsx"))
        rows = read(CANONICAL)
        self.assertEqual(300, len(rows))
        self.assertEqual(300, len({r["intervencion_id"] for r in rows}))
        self.assertEqual(Counter({"neutral": 220, "hawkish": 45, "dovish": 35}),
                         Counter(r["etiqueta_v3"] for r in rows))
        self.assertEqual(Counter({"1": 268, "0": 32}), Counter(r["es_relevante_v3"] for r in rows))

    def test_citas_y_coherencia(self):
        rows = read(CANONICAL)
        for row in rows:
            quote = " ".join(row["cita_literal"].split())
            text = " ".join(row["texto"].split())
            if row["es_relevante_v3"] == "1":
                self.assertTrue(quote, row["intervencion_id"])
                self.assertLessEqual(len(quote), 300, row["intervencion_id"])
                self.assertIn(quote, text, row["intervencion_id"])
            else:
                self.assertEqual("", quote)
                self.assertEqual("neutral", row["etiqueta_v3"])
            self.assertEqual("valido", row["estado_estructural"])
            self.assertEqual("pendiente_segunda_revision", row["estado_semantico"])

    def test_incidencias_reparadas(self):
        incidents = read(OUT / "incidencias_reparadas.csv")
        self.assertEqual(31, len(incidents))
        self.assertEqual(Counter({"elipsis_no_literal_retirada": 21,
                                  "capitalizacion_repuesta_desde_texto": 8,
                                  "transcripcion_repuesta_desde_texto": 2}),
                         Counter(r["tipo"] for r in incidents))

    def test_cola_prioritaria_ciega(self):
        rows = read(QUEUE)
        self.assertEqual(100, len(rows))
        self.assertEqual(80, sum(r["etiqueta_v3"] in {"hawkish", "dovish"} for r in rows))
        self.assertFalse(any("pred" in c.lower() for c in rows[0]))
        revision = [c for c in rows[0] if c.startswith("revision_")]
        self.assertTrue(revision)
        self.assertTrue(all(not r[c] for r in rows for c in revision))

    def test_manifest_y_estado_no_entrenable(self):
        summary = json.loads((OUT / "resumen.json").read_text(encoding="utf-8"))
        protocol = json.loads((OUT / "protocolo.json").read_text(encoding="utf-8"))
        self.assertFalse(summary["lista_para_entrenamiento"])
        self.assertFalse(protocol["entrenamiento_permitido"])
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
        for name, digest in manifest["sha256_salidas"].items():
            self.assertEqual(digest, sha(OUT / name))

    def test_reproducibilidad_canonica(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = ("import sys; from pathlib import Path; sys.path.insert(0, 'scripts'); "
                    f"import recibir_anotacion_300_v3 as m; m.run(Path(r'{tmp}')/'salida')")
            subprocess.run([str(ROOT / ".venv/bin/python"), "-c", code], cwd=ROOT, check=True)
            self.assertEqual(CANONICAL.read_bytes(), (Path(tmp) / "salida/anotaciones_canonicas.csv").read_bytes())


if __name__ == "__main__":
    unittest.main()
