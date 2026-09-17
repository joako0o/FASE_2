"""Regresiones de márgenes, máscaras y diagnóstico IA sin respuestas humanas."""
# ---- 1. Dependencias y ejemplos sintéticos ----
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from utilidades import cargar_script, sha256
E = cargar_script("23_diagnosticar_influencias.py")


class Influencias(unittest.TestCase):
    def test_descomposicion_con_intercepto_y_residuo(self):
        fila = csr_matrix([[0.2, 0, 0.4, 0.1]])
        resumen, detalle = E.descomponer(fila, np.array([2, 9, -3, 1]), 0.7, np.array(list("abcd")), np.array([3, 4, 5, 6]))
        self.assertAlmostEqual(resumen["margen"], 0)
        self.assertEqual({d["termino"] for d in detalle}, {"a", "c", "d"})
        self.assertEqual(next(d for d in detalle if d["termino"] == "c")["sentido"], "en_contra")
        with patch.object(E, "TOP_LOCAL", 1):
            resumen, detalle = E.descomponer(fila, np.array([2, 9, -3, 1]), 0.7, np.array(list("abcd")), np.array([3, 4, 5, 6]))
        self.assertEqual(len(detalle), 2)
        self.assertAlmostEqual(resumen["residuo_no_mostrado"], 0.1)
        self.assertAlmostEqual(resumen["margen"], resumen["intercepto"] + resumen["residuo_no_mostrado"] + sum(d["aporte"] for d in detalle))

    def test_texto_sin_vocabulario_solo_intercepto(self):
        resumen, detalle = E.descomponer(csr_matrix((1, 3)), np.ones(3), -0.4, np.array(list("abc")), np.ones(3))
        self.assertEqual(detalle, [])
        self.assertEqual(resumen["margen"], -0.4)

    def test_contrastes_no_confunden_binario_y_multiclase(self):
        class Modelo:
            classes_ = np.array([0, 1])
            coef_ = np.array([[2., -3.]])
        c = E.contrastes(Modelo(), "A")
        np.testing.assert_array_equal(c["irrelevante_vs_relevante"], [-2, 3])
        Modelo.classes_ = np.array(["dovish", "hawkish", "neutral"])
        Modelo.coef_ = np.array([[1., -1.], [3., 2.], [-4., -1.]])
        c = E.contrastes(Modelo(), "B")
        np.testing.assert_array_equal(c["hawkish_vs_dovish"], [2, 3])
        np.testing.assert_array_equal(c["hawkish_vs_resto"], [4.5, 3])

    def test_estabilidad_incluye_folds_fuera_del_top_y_ausencia(self):
        tablas = []
        for etapa in ["A", "B"]:
            for fold, terminos, pesos in [(1, ["x", "y"], [3, 2]), (2, ["x", "y"], [-2, 4]), (3, ["y"], [5])]:
                tablas.append(pd.DataFrame({"etapa": etapa, "fold": fold, "termino": terminos, "df_train": 3, "reuniones_train": 2, "contraste": pesos}))
        with patch.object(E, "TOP_GLOBAL", 1):
            _, _, estabilidad = E.resumir_coeficientes(tablas)
        fila = estabilidad[estabilidad.etapa.eq("A") & estabilidad.termino.eq("x")].iloc[0]
        self.assertEqual(fila.folds_presente, 2)
        self.assertEqual(fila.folds_positivo, 1)
        self.assertEqual(fila.folds_negativo, 1)
        self.assertEqual(fila.coef_medio, 0.5)

    def test_ajuste_solo_train_y_mascara_explicita(self):
        filas = []
        for _ in range(5):
            for texto, clase, rel in [("subir la tpm presiones", "hawkish", "1"), ("bajar la tasa recorte", "dovish", "1"),
                                       ("analisis escenario informe", "neutral", "1"), ("saludos gracias despedida", "neutral", "0")]:
                filas.append({"texto": texto, "etiqueta": clase, "es_relevante": rel, "meeting_id": "m1"})
        train = pd.DataFrame(filas)
        val = pd.DataFrame({"texto": ["exclusivovalidacion subir la tpm", "saludos gracias despedida"],
                            "intervencion_id": ["a", "b"], "meeting_id": ["m2"] * 2,
                            "etiqueta": ["hawkish", "neutral"], "es_relevante": ["1", "0"]})
        original = TfidfVectorizer.fit
        def ajustar(vector, textos, *args, **kwargs):
            textos = list(textos)
            self.assertFalse(any("exclusivovalidacion" in t for t in textos))
            return original(vector, textos, *args, **kwargs)
        with patch.object(TfidfVectorizer, "fit", new=ajustar):
            tablas, casos, margenes, detalles = E.diagnosticar_fold(train, val, 1)
        self.assertTrue(all("exclusivovalidacion" not in set(t.termino) for t in tablas))
        self.assertEqual(casos[1]["pred_a"], 0)
        self.assertEqual(casos[1]["pred"], "neutral")
        self.assertEqual(len(margenes), 6)
        self.assertTrue(all(not d["b_activa"] for d in margenes if d["intervencion_id"] == "b"))

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal, self.assertRaises(FileExistsError):
            E.ejecutar(temporal)

    @unittest.skipUnless((E.RUTA_SALIDA / "manifest.json").exists(), "aún sin diagnóstico")
    def test_artefactos_y_margenes(self):
        ruta = E.RUTA_SALIDA
        resumen = json.loads((ruta / "manifest.json").read_text())
        protocolo = json.loads((ruta / "protocolo.json").read_text())
        for nombre, huella in resumen["sha256_salidas"].items():
            self.assertEqual(sha256(ruta / nombre), huella)
        for nombre, huella in protocolo["sha256_insumos"].items():
            self.assertEqual(sha256(E.config.RUTA_REPO / nombre), huella)
        casos = pd.read_csv(ruta / "casos_validacion.csv")
        self.assertTrue(casos.intervencion_id.is_unique)
        self.assertEqual(len(casos), 793)
        self.assertTrue(casos.loc[casos.pred_a.eq(0), "pred"].eq("neutral").all())
        margenes = pd.read_csv(ruta / "margenes.csv")
        aportes = pd.read_csv(ruta / "aportes_locales.csv")
        claves = ["intervencion_id", "etapa"]
        suma = aportes.groupby(claves).aporte.sum().rename("top_suma")
        tabla = margenes.join(suma, on=claves).fillna({"top_suma": 0})
        np.testing.assert_allclose(tabla.margen, tabla.intercepto + tabla.residuo_no_mostrado + tabla.top_suma, atol=1e-9)
        self.assertEqual(len(tabla), 793 * 3)
        self.assertFalse(resumen["hibrido_entrenado"])
        self.assertFalse(resumen["gold_abierto_o_predicho"])

    @unittest.skipUnless((E.RUTA_SALIDA / "revision_manifest.json").exists(), "aún sin revisión")
    def test_revision_trazable_sin_cambiar_etiquetas(self):
        from utilidades import norm
        ruta = E.RUTA_SALIDA
        manifest = json.loads((ruta / "revision_manifest.json").read_text())
        revision = pd.read_csv(ruta / "revision_17_confusiones_hd.csv")
        casos = pd.read_csv(ruta / "casos_validacion.csv").set_index("intervencion_id")
        self.assertEqual(sha256(ruta / "revision_17_confusiones_hd.csv"), manifest["sha256_revision"])
        self.assertEqual(set(revision.intervencion_id), set(casos[casos.confusion_hd].index))
        for fila in revision.itertuples():
            self.assertIn(norm(fila.extracto_verificado), norm(casos.loc[fila.intervencion_id, "texto"]))
            self.assertEqual(fila.etiqueta_ia, casos.loc[fila.intervencion_id, "etiqueta_ia"])
            self.assertFalse(fila.etiqueta_modificada)
        informe = json.loads((ruta / "informe_manifest.json").read_text())
        self.assertEqual(sha256(E.config.RUTA_REPO / "docs/INFLUENCIAS_NGRAMAS.md"), informe["sha256_informe"])


if __name__ == "__main__":
    unittest.main()
