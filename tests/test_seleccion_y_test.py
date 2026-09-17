"""Regresiones de selección IA y evaluación humana separadas; sin tocar el test real."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from utilidades import cargar_script

seleccion = cargar_script("18_seleccionar_tfidf.py")
evaluacion = cargar_script("19_evaluar_tfidf_gold.py")


# ---- 1. Selección prefijada y sin contaminación de parámetros ----
class SeleccionIA(unittest.TestCase):
    def test_rejilla_acotada_incluye_baseline(self):
        candidatos = seleccion.configuraciones()
        self.assertEqual(len(candidatos), 12)
        self.assertIn({"candidato": 11, "ngram_max": 2, "min_df": 3, "C": 1.0}, candidatos)

    def test_parametros_no_mutan_defaults(self):
        original_tfidf = deepcopy(seleccion.BASELINE.PARAMS_TFIDF)
        original_lr = deepcopy(seleccion.BASELINE.PARAMS_LR)
        tfidf, lr = seleccion.parametrizar({"ngram_max": 1, "min_df": 2, "C": 0.5})
        self.assertEqual(tfidf["ngram_range"], (1, 1))
        self.assertEqual(lr["C"], 0.5)
        self.assertEqual(seleccion.BASELINE.PARAMS_TFIDF, original_tfidf)
        self.assertEqual(seleccion.BASELINE.PARAMS_LR, original_lr)

    def test_seleccion_usa_media_no_oof(self):
        datos = pd.DataFrame([{"candidato": 1, "macro_f1_media": 0.6, "macro_f1_oof_conjunto": 0.9, "ngram_max": 1, "min_df": 3, "C": 0.5},
                              {"candidato": 2, "macro_f1_media": 0.7, "macro_f1_oof_conjunto": 0.8, "ngram_max": 2, "min_df": 2, "C": 2.0}])
        self.assertEqual(seleccion.elegir_configuracion(datos).candidato, 2)

    def test_desempate_prefijado(self):
        datos = pd.DataFrame(seleccion.configuraciones())
        datos["macro_f1_media"] = 0.5
        ganador = seleccion.elegir_configuracion(datos)
        self.assertEqual((ganador.ngram_max, ganador.min_df, ganador.C), (1, 3, 0.5))

    def test_no_sobrescribe_experimento(self):
        with tempfile.TemporaryDirectory() as temporal, self.assertRaises(FileExistsError):
            seleccion.ejecutar(Path(temporal), Path(temporal) / "modelo.joblib")

    def test_usa_los_mismos_folds(self):
        # Emula CV; una reasignación de folds entre candidatos debe detenerse.
        datos = pd.DataFrame({"intervencion_id": ["a", "b", "c"], "meeting_id": ["m1", "m2", "m3"],
                              "etiqueta": ["hawkish", "dovish", "neutral"], "pred": ["hawkish", "dovish", "neutral"], "fold": [1, 2, 3]})
        alterado = datos.assign(fold=[2, 1, 3])
        with patch.object(seleccion.BASELINE, "evaluar_oof", side_effect=[datos, alterado]), redirect_stdout(io.StringIO()):
            with self.assertRaises(AssertionError):
                seleccion.buscar_configuracion(datos, seleccion.configuraciones()[:2])

    def test_textos_reservados_no_abren_excel(self):
        filas = pd.DataFrame({"orden": range(306), "intervencion_id": [f"id{i}" for i in range(306)]})
        corpus = filas.assign(texto="Texto de prueba", meeting_id="m1")
        train = pd.DataFrame({"intervencion_id": ["train"], "texto": ["otro"], "meeting_id": ["m2"]})
        leidos = []
        def leer(ruta, **kwargs):
            leidos.append(Path(ruta).name)
            return filas if Path(ruta).name == "gold_ciego_300.csv" else corpus.drop(columns="orden")
        with patch.object(seleccion.pd, "read_csv", side_effect=leer), patch.object(seleccion.pd, "read_excel", side_effect=AssertionError("no abrir humano")):
            test = seleccion.cargar_textos_reservados(train)
        self.assertEqual(leidos, ["gold_ciego_300.csv", "corpus.csv"])
        self.assertEqual(len(test), 306)
        self.assertNotIn("etiqueta", test.columns)


# ---- 2. Métricas y emparejamiento de decisiones ----
class EvaluacionHumana(unittest.TestCase):
    def test_metricas_perfectas(self):
        clases = ["hawkish", "dovish", "neutral"]
        m = evaluacion.metricas_clasificacion(clases, clases)
        self.assertEqual(m["macro_f1"], 1)
        self.assertEqual(m["kappa"], 1)
        self.assertEqual(m["errores"], 0)

    def test_siempre_neutral_no_equivale_a_buen_macro_f1(self):
        m = evaluacion.metricas_clasificacion(["hawkish", "dovish", "neutral", "neutral"], ["neutral"] * 4)
        self.assertEqual(m["accuracy"], 0.5)
        self.assertAlmostEqual(m["macro_f1"], 2 / 9)
        self.assertEqual(m["kappa"], 0)

    def test_matriz_filas_humanas(self):
        m = evaluacion.metricas_clasificacion(["hawkish", "dovish", "neutral"], ["neutral", "dovish", "neutral"])
        self.assertEqual(m["matriz_confusion"]["valores"], [[0, 0, 1], [0, 1, 0], [0, 0, 1]])

    def test_kappa_monoclase_indefinido(self):
        self.assertIsNone(evaluacion.metricas_clasificacion(["neutral"], ["neutral"])["kappa"])

    def test_empareja_por_id_no_por_orden(self):
        pred = pd.DataFrame({"intervencion_id": ["b", "a"], "pred": ["neutral", "hawkish"]})
        ref = pd.DataFrame({"intervencion_id": ["a", "b"], "etiqueta": ["hawkish", "neutral"], "es_relevante": ["1", "0"], "fecha_reunion": ["2010-01-14"] * 2})
        unido = evaluacion.unir_referencia(pred, ref)
        self.assertTrue(unido.pred.eq(unido.etiqueta_humana).all())

    def test_rechaza_duplicados_antes_merge(self):
        pred = pd.DataFrame({"intervencion_id": ["a", "a"]})
        ref = pd.DataFrame({"intervencion_id": ["a"]})
        with self.assertRaises(AssertionError):
            evaluacion.unir_referencia(pred, ref)

    def test_citas_no_bloquean_clases_pero_no_se_ocultan(self):
        cab = ["orden", "intervencion_id", "texto", "etiqueta", "confianza", "es_relevante", "nota", "frase_justificante", "fecha"]
        base = {c: "" for c in cab}
        base.update(orden="1", intervencion_id="a", texto="Subir la tasa")
        llena = {**base, "etiqueta": "hawkish", "confianza": "alta", "es_relevante": "1", "frase_justificante": "subir...tasa"}
        ref, errores = evaluacion.preparar_referencia(cab, [base], cab, [llena], "2026-09-16")
        self.assertEqual(ref.etiqueta.tolist(), ["hawkish"])
        self.assertEqual([e["problema"] for e in errores], ["frase no verbatim"])
        llena["etiqueta"] = "incorrecta"
        with self.assertRaises(AssertionError):
            evaluacion.preparar_referencia(cab, [base], cab, [llena], "2026-09-16")


# ---- 3. Integración sobre el examen congelado, sin reoptimizar ----
class ExamenCongelado(unittest.TestCase):
    def test_manifiestos_y_seleccion_consistentes(self):
        predicciones, protocolo, elegida, manifiesto = evaluacion.verificar_experimento(seleccion.RUTA_EXPERIMENTO)
        self.assertEqual(len(predicciones), 306)
        self.assertEqual(elegida["candidato"], 6)
        self.assertFalse(manifiesto["respuestas_humanas_leidas"])
        self.assertEqual(protocolo["entrada_modelo"], ["texto"])

    def test_recalculo_independiente_metricas_guardadas(self):
        import json
        ruta = seleccion.RUTA_EXPERIMENTO
        comparacion = pd.read_csv(ruta / "comparacion_gold.csv")
        guardadas = json.loads((ruta / "metricas_gold.json").read_text())
        recalculadas = evaluacion.metricas_clasificacion(comparacion.etiqueta_humana, comparacion.pred)
        self.assertEqual(recalculadas, guardadas["principal"])
        self.assertEqual(recalculadas["aciertos"], 260)
        self.assertEqual(recalculadas["errores"], 46)
        self.assertEqual(int(comparacion.texto_repetido_training.sum()), 12)

    def test_evaluador_no_sobrescribe_examen(self):
        with self.assertRaises(FileExistsError):
            evaluacion.ejecutar()


if __name__ == "__main__":
    unittest.main()
