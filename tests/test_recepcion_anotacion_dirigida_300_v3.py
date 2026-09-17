import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.recibir_anotacion_dirigida_300_v3 import BLIND, OUT, SOURCE, run


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))


class TestRecepcionAnotacionDirigida300V3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read(OUT / "anotaciones_canonicas.csv"); cls.blind = {r["intervencion_id"]: r for r in read(BLIND)}
        cls.incidents = read(OUT / "incidencias_reparadas.csv"); cls.review = read(OUT / "revision_semantica_300.csv")
        cls.summary = json.loads((OUT / "resumen.json").read_text(encoding="utf-8"))

    def test_origen_cobertura_y_campos_inmutables(self):
        self.assertEqual(len(self.rows), 300); self.assertEqual(len({r["intervencion_id"] for r in self.rows}), 300)
        self.assertEqual(set(self.blind), {r["intervencion_id"] for r in self.rows})
        for row in self.rows:
            original = self.blind[row["intervencion_id"]]
            for field in ("orden", "fecha_reunion", "actor", "cargo", "texto"):
                self.assertEqual(" ".join(str(row[field]).split()), " ".join(str(original[field]).split()))
            self.assertEqual(hashlib.sha256(row["texto"].encode()).hexdigest(), row["sha256_texto"])
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "ce1f6794e5d7fe971428089c17d7b12acd262496644826835270fa44130dd895")

    def test_distribuciones_y_estado(self):
        self.assertEqual(self.summary["etiquetas_v3"], {"neutral": 191, "hawkish": 42, "dovish": 67})
        self.assertEqual(self.summary["relevancia_v3"], {"1": 295, "0": 5})
        self.assertEqual(self.summary["confianza"], {"alta": 248, "media": 51, "baja": 1})
        self.assertFalse(self.summary["lista_para_entrenamiento"])
        self.assertEqual({r["estado_semantico"] for r in self.rows}, {"pendiente_segunda_revision"})

    def test_citas_y_coherencia(self):
        for row in self.rows:
            if row["es_relevante_v3"] == "1":
                self.assertTrue(row["cita_literal"]); self.assertLessEqual(len(row["cita_literal"]), 300); self.assertIn(row["cita_literal"], row["texto"])
            else: self.assertEqual((row["etiqueta_v3"], row["cita_literal"]), ("neutral", ""))

    def test_incidencias_solo_reextraccion(self):
        self.assertEqual(len(self.incidents), 15)
        self.assertEqual({r["tipo"] for r in self.incidents}, {"capitalizacion_repuesta_desde_texto", "elipsis_no_literal_retirada", "transcripcion_repuesta_desde_texto"})
        by_id = {r["intervencion_id"]: r for r in self.rows}
        for incident in self.incidents: self.assertIn(incident["cita_reparada"], by_id[incident["intervencion_id"]]["texto"])

    def test_revision_cubre_las_300_sin_predicciones(self):
        self.assertEqual(len(self.review), 300)
        self.assertEqual([r["intervencion_id"] for r in self.review], [r["intervencion_id"] for r in self.rows])
        for row in self.review:
            self.assertTrue(all(not row[key] for key in row if key.startswith("revision_")))
            self.assertNotIn("pred", " ".join(row).lower())

    def test_manifest_y_reproducibilidad(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        for name, expected in manifest.items(): self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), expected)
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "recepcion"; generated.mkdir()
            (generated / "anotacion_original.xlsx").write_bytes(SOURCE.read_bytes()); run(generated)
            for name in (*manifest, "manifest.json"): self.assertEqual((generated / name).read_bytes(), (OUT / name).read_bytes())


if __name__ == "__main__": unittest.main()
