import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "colab/FASE_2_experimentos.ipynb"


class TestColabExperimentos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        cls.code = "\n".join("".join(c.get("source", [])) for c in cls.nb["cells"] if c["cell_type"] == "code")

    def test_formato_y_codigo(self):
        self.assertEqual(4, self.nb["nbformat"])
        self.assertGreaterEqual(len(self.nb["cells"]), 5)
        for i, cell in enumerate(self.nb["cells"]):
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), f"cell_{i}", "exec")

    def test_rama_entorno_y_opciones(self):
        self.assertIn('RAMA = "arena/01a0b014-fase-2"', self.code)
        self.assertIn("scripts/40_gestionar_proyecto.py", self.code)
        for option in ["suite_pruebas", "diagnostico_gpu", "palabras_caracteres",
                       "extension_representaciones", "ensamble_calibrado"]:
            self.assertIn(option, self.code)

    def test_salida_auditable(self):
        self.assertIn("checksums_colab.json", self.code)
        self.assertIn("make_archive", self.code)
        self.assertIn("colab_files.download", self.code)
        self.assertIn("OPENBLAS_NUM_THREADS", self.code)

    def test_no_credenciales(self):
        lower = self.code.lower()
        self.assertNotIn("github_token", lower)
        self.assertNotIn("personal_access_token", lower)
        self.assertNotIn("ghp_", lower)
        self.assertNotIn("git push", lower)


if __name__ == "__main__":
    unittest.main()
