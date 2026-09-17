import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cerrar_revision_semantica_300_v3 import CORRECTIONS, OUT, QUEUE, SOURCE, run


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class TestCierreRevisionSemantica300V3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = read(SOURCE)
        cls.queue = read(QUEUE)
        cls.review = read(OUT / "adjudicacion_prioritaria_100.csv")
        cls.changes = read(OUT / "cambios_semanticos.csv")
        cls.final = read(OUT / "referencia_300_v3.csv")
        cls.summary = json.loads((OUT / "resumen.json").read_text(encoding="utf-8"))

    def test_cobertura_y_cierre(self):
        self.assertEqual((len(self.review), len(self.changes), len(self.final)), (100, 18, 300))
        self.assertEqual(len({r["intervencion_id"] for r in self.final}), 300)
        self.assertEqual({r["estado_revision"] for r in self.review}, {"cerrado"})
        self.assertEqual({r["estado_revision_v3"] for r in self.final}, {"cerrado"})

    def test_segunda_revision_es_exactamente_la_cola_congelada(self):
        self.assertEqual([r["intervencion_id"] for r in self.review],
                         [r["intervencion_id"] for r in self.queue])
        self.assertEqual(sum(r["resultado_revision"] == "corregida_v3" for r in self.review), 18)
        self.assertEqual(sum(r["resultado_revision"] == "ratificada_v3" for r in self.review), 82)
        self.assertEqual({r["intervencion_id"] for r in self.changes}, set(CORRECTIONS))

    def test_conteos_finales(self):
        self.assertEqual(self.summary["etiquetas_finales"], {"neutral": 237, "hawkish": 35, "dovish": 28})
        self.assertEqual(self.summary["cambios"], {"dovish→neutral": 6, "hawkish→neutral": 11,
                                                   "dovish→hawkish": 1})
        self.assertEqual(self.summary["relevancia_final"], {"0": 32, "1": 268})
        self.assertTrue(self.summary["lista_para_entrenamiento"])
        self.assertFalse(self.summary["predicciones_modelo_consultadas"])
        self.assertFalse(self.summary["evaluacion_independiente"])

    def test_campos_inmutables_y_hash_de_texto(self):
        original = {r["intervencion_id"]: r for r in self.source}
        for row in self.final:
            before = original[row["intervencion_id"]]
            for field in ("fecha_reunion", "actor", "cargo", "texto", "sha256_texto"):
                self.assertEqual(row[field], before[field])
            self.assertEqual(hashlib.sha256(row["texto"].encode()).hexdigest(), row["sha256_texto"])

    def test_evidencia_exacta_y_coherencia(self):
        for row in self.final:
            if row["es_relevante_v3"] == "1":
                self.assertTrue(row["cita_literal"])
                self.assertLessEqual(len(row["cita_literal"]), 300)
                self.assertIn(row["cita_literal"], row["texto"])
            else:
                self.assertEqual(row["etiqueta_v3"], "neutral")

    def test_correccion_flap_es_hawkish_y_cita_accion(self):
        row = next(r for r in self.final if r["intervencion_id"] == "RPM-2009-11-12:2793:1")
        self.assertEqual((row["etiqueta_humana"], row["etiqueta_v3"]), ("dovish", "hawkish"))
        self.assertIn("acortamiento gradual de la FLAP", row["cita_literal"])

    def test_manifest_y_reproducibilidad(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        for name, expected in manifest.items():
            self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), expected)
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "cierre"
            run(generated)
            for name in (*manifest, "manifest.json"):
                self.assertEqual((generated / name).read_bytes(), (OUT / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
