import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cerrar_revision_semantica_dirigida_300_v3 import CORRECTIONS, OUT, SOURCE, run


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))


class TestCierreSemanticoDirigida300V3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = {r["intervencion_id"]: r for r in read(SOURCE)}
        cls.review = read(OUT / "adjudicacion_300.csv"); cls.changes = read(OUT / "cambios_semanticos.csv"); cls.final = read(OUT / "referencia_300_v3.csv")
        cls.summary = json.loads((OUT / "resumen.json").read_text(encoding="utf-8"))

    def test_cobertura_y_cierre_total(self):
        self.assertEqual((len(self.review), len(self.changes), len(self.final)), (300, 15, 300))
        self.assertEqual(len({r["intervencion_id"] for r in self.final}), 300)
        self.assertEqual({r["estado_revision"] for r in self.review}, {"cerrado"})
        self.assertEqual({r["estado_revision_v3"] for r in self.final}, {"cerrado"})
        self.assertEqual(sum(r["resultado_revision"] == "ratificada_v3" for r in self.review), 285)

    def test_correcciones_exactas_y_conteos(self):
        self.assertEqual({r["intervencion_id"] for r in self.changes}, set(CORRECTIONS))
        self.assertEqual(self.summary["cambios"], {"hawkish→neutral": 7, "neutral→dovish": 3, "neutral→hawkish": 1, "dovish→neutral": 4})
        self.assertEqual(self.summary["etiquetas_finales"], {"neutral": 198, "hawkish": 36, "dovish": 66})
        self.assertTrue(self.summary["lista_para_entrenamiento"]); self.assertFalse(self.summary["predicciones_modelo_consultadas"])

    def test_campos_fuente_y_hashes_inmutables(self):
        for row in self.final:
            before = self.source[row["intervencion_id"]]
            for field in ("fecha_reunion", "actor", "cargo", "texto", "sha256_texto"): self.assertEqual(row[field], before[field])
            self.assertEqual(hashlib.sha256(row["texto"].encode()).hexdigest(), row["sha256_texto"])

    def test_evidencia_literal(self):
        for row in self.final:
            if row["es_relevante_v3"] == "1":
                self.assertTrue(row["cita_literal"]); self.assertLessEqual(len(row["cita_literal"]), 300); self.assertIn(row["cita_literal"], row["texto"])
            else: self.assertEqual((row["etiqueta_v3"], row["cita_literal"]), ("neutral", ""))

    def test_casos_regla_accion_y_no_inferencia(self):
        by = {r["intervencion_id"]: r for r in self.final}
        self.assertEqual(by["RPM-2009-09-08:2711:1"]["etiqueta_v3"], "dovish")
        self.assertIn("mantener el estímulo monetario inalterado", by["RPM-2009-09-08:2711:1"]["cita_literal"])
        self.assertEqual(by["RPM-2008-11-13:2173:1"]["etiqueta_v3"], "neutral")
        self.assertEqual(by["RPM-2007-10-11:1484:1"]["etiqueta_v3"], "neutral")
        self.assertEqual(by["RPM-2011-08-18:4268:1"]["etiqueta_v3"], "neutral")

    def test_manifest_y_reproducibilidad(self):
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        for name, expected in manifest.items(): self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), expected)
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / "cierre"; run(generated)
            for name in (*manifest, "manifest.json"): self.assertEqual((generated / name).read_bytes(), (OUT / name).read_bytes())


if __name__ == "__main__": unittest.main()
