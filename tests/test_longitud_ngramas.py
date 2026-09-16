"""Selección de seis longitudes: pruebas sintéticas y de linaje IA solamente."""
# ---- 1. Dependencias y fixtures sin anotaciones humanas ----
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from utilidades import cargar_script, sha256
E = cargar_script("22_seleccionar_longitud_ngramas.py")


class LongitudNgramas(unittest.TestCase):
    def test_rejilla_acotada_y_defaults_conservados(self):
        self.assertEqual(E.LONGITUDES, (1, 2, 3, 4, 5, 6))
        self.assertEqual(E.ANTERIOR.PARAMETROS_TFIDF["ngram_range"], (1, 1))
        self.assertEqual(E.ANTERIOR.PARAMETROS_LR["C"], 2)
        self.assertEqual(E.ANTERIOR.BASELINE.PARAMS_TFIDF["ngram_range"], (1, 2))

    def test_seleccion_media_no_redondeada_no_oof(self):
        tabla = pd.DataFrame({"ngram_max": [1, 2], "macro_f1_media": [0.750001, 0.750002], "macro_f1": [0.9, 0.7]})
        self.assertEqual(E.elegir(tabla), 2)

    def test_empate_exacto_favorece_menor_longitud(self):
        tabla = pd.DataFrame({"ngram_max": [6, 4, 3, 1], "macro_f1_media": [0.8, 0.8, 0.8, 0.7]})
        self.assertEqual(E.elegir(tabla), 3)

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal, self.assertRaises(FileExistsError):
            E.ejecutar(salida=temporal)

    def test_ajuste_no_ve_validacion_y_a_fija(self):
        filas = []
        for _ in range(5):
            for texto, etiqueta, relevante in [
                ("subir la tpm presiones monetarias persistentes futuras", "hawkish", "1"),
                ("bajar la tasa actividad economica debil ahora", "dovish", "1"),
                ("analisis escenario informe variables externas otras perspectivas", "neutral", "1"),
                ("saludos gracias despedida", "neutral", "0")]:
                filas.append({"texto": texto, "etiqueta": etiqueta, "es_relevante": relevante})
        train = pd.DataFrame(filas)
        val = pd.DataFrame({"texto": ["exclusivovalidacion subir la tpm", "saludos gracias despedida"]})
        vistos = []
        def espia(original):
            def ajustar(vector, documentos, *args, **kwargs):
                documentos = list(documentos)
                self.assertFalse(any("exclusivovalidacion" in t for t in documentos))
                resultado = original(vector, documentos, *args, **kwargs)
                vistos.append(vector.ngram_range)
                self.assertNotIn("exclusivovalidacion", vector.vocabulary_)
                return resultado
            return ajustar
        with patch.object(TfidfVectorizer, "fit_transform", new=espia(TfidfVectorizer.fit_transform)), patch.object(TfidfVectorizer, "fit", new=espia(TfidfVectorizer.fit)), patch.object(E.ANTERIOR.L, "matriz_senales", side_effect=AssertionError("sin diccionario")):
            resultado = E.evaluar_fold(train, val)
        self.assertEqual(vistos, [(1, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)])
        self.assertEqual(set(resultado), set(E.LONGITUDES))
        vocabularios = []
        for pred, dimensiones in resultado.values():
            self.assertEqual(pred[1], "neutral")
            self.assertGreater(dimensiones["terminos_longitud_maxima_b"], 0)
            vocabularios.append(dimensiones["vocabulario_b"])
        self.assertEqual(vocabularios, sorted(vocabularios))
        base = E.ANTERIOR.BASELINE.entrenar_modelo(train, E.ANTERIOR.PARAMETROS_TFIDF, E.ANTERIOR.PARAMETROS_LR)
        np.testing.assert_array_equal(resultado[1][0], E.ANTERIOR.BASELINE.predecir_textos(base, val.texto).pred)

    def test_carga_y_folds_no_abren_humano_ni_catalogo(self):
        original = pd.read_csv
        def leer(ruta, *args, **kwargs):
            self.assertNotIn("comparacion_gold", str(ruta))
            self.assertNotIn("catalogo_training_completo", str(ruta))
            self.assertNotIn("diccionario_v1", str(ruta))
            return original(ruta, *args, **kwargs)
        with patch.object(pd, "read_excel", side_effect=AssertionError("no abrir humano")), patch.object(pd, "read_csv", side_effect=leer):
            datos, mascara, anteriores, _ = E.cargar_insumos()
            folds, asignacion = E.asignar_folds(datos, mascara)
        self.assertEqual(asignacion.fold_validacion.eq(0).sum(), 559)
        self.assertEqual(asignacion.texto_identico_en_train.sum(), 34)
        for numero, tr, va in folds:
            self.assertFalse(set(datos.iloc[tr].meeting_id) & set(datos.iloc[va].meeting_id))
            esperado = anteriores[anteriores.fold.eq(numero) & anteriores.variante.eq("unigramas")]
            self.assertEqual(set(datos.iloc[va].intervencion_id), set(esperado.intervencion_id))

    def test_rechaza_cambio_en_anclas(self):
        actual = pd.DataFrame({"intervencion_id": ["a", "a"], "meeting_id": ["m", "m"],
                               "etiqueta": ["hawkish"] * 2, "fold": [1, 1], "pred": ["hawkish"] * 2,
                               "ngram_max": [1, 4]})
        previo = actual.drop(columns="ngram_max").assign(variante=["unigramas", "ngramas_1_4"])
        E.verificar_anclas(actual, previo)
        actual.loc[0, "pred"] = "neutral"
        with self.assertRaises(AssertionError):
            E.verificar_anclas(actual, previo)

    @unittest.skipUnless((E.RUTA_SALIDA / "manifest.json").exists(), "aún sin evaluación")
    def test_artefactos_metricas_y_seleccion_recalculables(self):
        ruta = E.RUTA_SALIDA
        manifest = json.loads((ruta / "manifest.json").read_text())
        for nombre, huella in manifest["sha256_salidas"].items():
            self.assertEqual(sha256(ruta / nombre), huella)
        self.assertEqual(sha256(E.RUTA_INFORME), manifest["sha256_informe"])
        protocolo = json.loads((ruta / "protocolo.json").read_text())
        for nombre, huella in protocolo["sha256_insumos"].items():
            self.assertEqual(sha256(E.config.RUTA_REPO / nombre), huella)
        pred = pd.read_csv(ruta / "predicciones_validacion.csv")
        folds = pd.read_csv(ruta / "resultados_folds.csv")
        self.assertEqual(len(pred), 793 * 6)
        self.assertEqual(len(folds), 30)
        self.assertFalse(pred.duplicated(["intervencion_id", "ngram_max"]).any())
        self.assertTrue(pred.groupby("meeting_id").fold.nunique().eq(1).all())
        recalculado = E.resumir(pred, folds)
        pd.testing.assert_frame_equal(recalculado, pd.read_csv(ruta / "comparacion_longitudes.csv"))
        for fila in folds.itertuples():
            sub = pred[pred.fold.eq(fila.fold) & pred.ngram_max.eq(fila.ngram_max)]
            for nombre, valor in E.ANTERIOR.metricas(sub.etiqueta, sub.pred).items():
                self.assertAlmostEqual(getattr(fila, nombre), valor)
        seleccion = json.loads((ruta / "seleccion.json").read_text())
        self.assertEqual(seleccion["ngram_max_b"], E.elegir(recalculado))
        anterior = pd.read_csv(E.ANTERIOR.L.RUTA_VALIDACION / "predicciones_validacion.csv")
        E.verificar_anclas(pred, anterior)


if __name__ == "__main__":
    unittest.main()
