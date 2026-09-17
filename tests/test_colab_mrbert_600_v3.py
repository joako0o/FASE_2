import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "colab/FASE_2_MrBERT_600_v3.ipynb"
SCRIPT = ROOT / "scripts/evaluar_mrbert_600_v3.py"
DOCS = ROOT / "docs/COLAB_EXPERIMENTOS.md"


class TestColabMrBert600V3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb = json.loads(NOTEBOOK.read_text(encoding="utf-8")); cls.code = "\n".join("".join(c.get("source", [])) for c in cls.nb["cells"] if c["cell_type"] == "code")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_notebook_valido_y_gpu(self):
        self.assertEqual(self.nb["nbformat"], 4); self.assertEqual(self.nb["metadata"]["accelerator"], "GPU")
        self.assertIn("nvidia-smi", self.code); self.assertIn("torch.cuda.is_available", self.script)

    def test_modelo_y_revision_congelados(self):
        self.assertIn('MODEL_ID = "BSC-LT/MrBERT-es"', self.script)
        self.assertIn('MODEL_REVISION = "34a7cc86e0d0a2b77e802d07a189db1c0ef2e7d4"', self.script)
        self.assertIn('MAX_LENGTH = 1024', self.script); self.assertIn('EPOCHS = 2', self.script)

    def test_clona_solo_rama_y_no_solicita_credenciales(self):
        self.assertIn('BRANCH = "arena/01a0b014-fase-2"', self.code); self.assertIn('"--branch", BRANCH', self.code)
        forbidden = ["ghp_", "github_token", "personal access token", "oauth"]
        self.assertFalse(any(value in self.code.lower() for value in forbidden))

    def test_reanudacion_y_zip(self):
        self.assertIn("drive.mount", self.code); self.assertIn("MyDrive/FASE_2/resultados_mrbert_600_v3", self.code)
        self.assertIn("if target.exists()", self.script); self.assertIn("files.download", self.code)

    def test_purga_y_predictores_permitidos(self):
        self.assertIn("audited_extra", self.script); self.assertIn("set(train.meeting_id) & set(val.meeting_id)", self.script)
        self.assertIn('self.items = [head_tail(tokenizer, text) for text in frame.texto]', self.script)
        self.assertIn("citas, fundamentos, confianza, estratos", self.script)

    def test_salida_auditable_y_documentacion(self):
        for name in ("protocolo.json", "predicciones.csv", "metricas.json", "entorno.json", "manifest.json"):
            self.assertIn(name, self.script)
        docs = DOCS.read_text(encoding="utf-8")
        self.assertIn("FASE_2_MrBERT_600_v3.ipynb", docs); self.assertIn("colab.research.google.com", docs)


if __name__ == "__main__": unittest.main()
