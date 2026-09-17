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

    def test_rejecucion_sale_del_checkout_antes_de_borrarlo(self):
        setup = "".join(self.nb["cells"][2]["source"])
        self.assertLess(setup.index("os.chdir(BASE)"), setup.index("shutil.rmtree(PROYECTO)"))
        self.assertLess(setup.index("shutil.rmtree(PROYECTO)"), setup.index('"git", "clone"'))
        self.assertIn("PROYECTO)], BASE)", setup)
        self.assertIn('"--single-branch"', setup)

    def test_python_313_colab_usa_requisitos_fijados(self):
        setup = "".join(self.nb["cells"][2]["source"])
        self.assertIn("version == (3, 13)", setup)
        self.assertIn("requirements-preparacion.txt", setup)
        self.assertIn('"pip", "check"', setup)
        self.assertIn('"virtualenv"', setup)
        self.assertIn('PROYECTO / ".venv/bin/python"', setup)
        self.assertIn("virtualenv_colab_python_3.13_requisitos_fijados", setup)

    def test_errores_de_instalacion_quedan_visibles(self):
        setup = "".join(self.nb["cells"][2]["source"])
        self.assertIn("stderr=subprocess.STDOUT", setup)
        self.assertIn("proceso.stdout", setup)
        self.assertIn("proceso.returncode", setup)

    def test_no_credenciales(self):
        lower = self.code.lower()
        self.assertNotIn("github_token", lower)
        self.assertNotIn("personal_access_token", lower)
        self.assertNotIn("ghp_", lower)
        self.assertNotIn("git push", lower)


if __name__ == "__main__":
    unittest.main()
