"""Pruebas léxicas y de aislamiento IA; nunca abre respuestas humanas."""
# ---- 1. Dependencias y ejemplos sintéticos ----
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lexico_ngramas as L
from utilidades import cargar_script, sha256

E = cargar_script("21_evaluar_lexico.py")


def diccionario_prueba():
    return pd.DataFrame({"ngrama": ["subir la tpm", "bajar la tasa", "recorte", "recorte de gastos"],
                         "senal": ["restrictiva", "expansiva", "expansiva", "contextual"]})


class Extraccion(unittest.TestCase):
    def test_normalizacion_y_limites(self):
        self.assertEqual(L.normalizar("Acordó SUBIR la TPM"), "acordo subir la tpm")
        gramos = L.ngramas("Vota a favor. No subir; la TPM")
        self.assertIn("vota a favor", gramos)
        self.assertNotIn("favor no", gramos)
        self.assertNotIn("subir la tpm", gramos)
        self.assertTrue(all(1 <= len(g.split()) <= 4 for g in gramos))
        self.assertIn("subir la tpm", L.ngramas("subir\nla TPM"))

    def test_umbrales_documentos_no_apariciones_y_reuniones(self):
        textos = ["frecuente repetida repetida local", "frecuente repetida local", "frecuente repetida local",
                  "frecuente repetida local", "frecuente repetida", "frecuente", "frecuente", "frecuente"]
        datos = pd.DataFrame({"texto": textos, "meeting_id": ["a", "a", "b", "b", "c", "c", "d", "d"],
                              "etiqueta": ["hawkish", "dovish", "neutral", "neutral"] * 2})
        tabla = L.construir_catalogo(datos).set_index("ngrama")
        self.assertNotIn("local", tabla.index)
        self.assertEqual(tabla.loc["repetida", "intervenciones"], 5)
        self.assertEqual(tabla.loc["repetida", "apariciones"], 6)
        self.assertEqual(tabla.loc["repetida", "reuniones"], 3)
        datos["meeting_id"] = "una"
        self.assertEqual(len(L.construir_catalogo(datos)), 0)

    def test_contextos_solo_reciben_descubrimiento(self):
        datos, mascara, _, _ = E.cargar_insumos(L.RUTA_LEXICO)
        contextos = pd.read_csv(L.RUTA_LEXICO / "contextos_revision.csv")
        self.assertTrue(set(contextos.intervencion_id) <= set(datos.loc[mascara, "intervencion_id"]))
        self.assertEqual(len(contextos), 219)
        self.assertTrue(contextos.groupby("ngrama").size().eq(3).all())


# ---- 2. Señales, negación y solapamientos ----
class Coincidencias(unittest.TestCase):
    def test_afirmacion_y_negacion_separadas(self):
        textos = ["SUBIR la TPM", "No propone subir la TPM", "bajar la tasa", "sin recorte"]
        np.testing.assert_array_equal(L.matriz_senales(textos, diccionario_prueba()), np.eye(4))

    def test_no_solo_y_oraciones(self):
        textos = ["no solo subir la TPM", "no solamente subir la TPM", "no. subir la TPM"]
        np.testing.assert_array_equal(L.matriz_senales(textos, diccionario_prueba()), [[1, 0, 0, 0]] * 3)

    def test_limites_de_tokens_y_solapamiento_contextual(self):
        textos = ["recortes", "subir. la TPM", "recorte de gastos", "recorte y recorte"]
        np.testing.assert_array_equal(L.matriz_senales(textos, diccionario_prueba()),
                                      [[0, 0, 0, 0]] * 3 + [[0, 0, 1, 0]])

    def test_negacion_derecha_limitacion_declarada(self):
        # No fingir que la heurística comprende una negación posterior.
        np.testing.assert_array_equal(L.matriz_senales(["subir la TPM no es recomendable"], diccionario_prueba()), [[1, 0, 0, 0]])

    def test_vacios(self):
        self.assertEqual(L.matriz_senales([], diccionario_prueba()).shape, (0, 4))
        self.assertFalse(L.matriz_senales([""], diccionario_prueba()).any())


# ---- 3. Separación, manifiestos y ajuste por fold ----
class Validacion(unittest.TestCase):
    def test_particion_y_cinco_folds_aislados(self):
        datos, mascara, _, _ = E.cargar_insumos(L.RUTA_LEXICO)
        self.assertEqual(int(mascara.sum()), 559)
        visitas = np.zeros(len(datos), dtype=int)
        for _, train, val in E.particiones_validacion(datos, mascara):
            self.assertTrue(set(np.flatnonzero(mascara)) <= set(train))
            self.assertFalse(set(datos.iloc[train].meeting_id) & set(datos.iloc[val].meeting_id))
            visitas[val] += 1
        np.testing.assert_array_equal(visitas, (~mascara).astype(int))

    def test_manifiestos_y_diccionario_completo(self):
        with patch.object(pd, "read_excel", side_effect=AssertionError("no abrir humano")):
            _, _, diccionario, _ = E.cargar_insumos(L.RUTA_LEXICO)
        self.assertEqual(len(diccionario), 73)
        candidatos = pd.read_csv(L.RUTA_LEXICO / "candidatos_revision.csv")
        for roto in [diccionario.iloc[:-1], diccionario.assign(senal="hawkish"), diccionario.assign(justificacion=" ")]:
            with self.assertRaises(AssertionError):
                L.validar_diccionario(roto, candidatos)

    def test_rechaza_diccionario_alterado(self):
        with tempfile.TemporaryDirectory() as temporal:
            copia = Path(temporal) / "lexico"
            shutil.copytree(L.RUTA_LEXICO, copia)
            with (copia / "diccionario_v1.csv").open("a") as archivo:
                archivo.write("\n")
            with self.assertRaises(AssertionError):
                E.cargar_insumos(copia)

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as temporal, self.assertRaises(FileExistsError):
            E.ejecutar(salida=temporal)

    def test_vocabulario_no_ve_validacion_y_baseline_equivalente(self):
        filas = []
        for i in range(5):
            for texto, clase, relevante in [("subir la tpm presiones", "hawkish", "1"),
                                             ("bajar la tasa recorte", "dovish", "1"),
                                             ("analisis escenario informe", "neutral", "1"),
                                             ("saludos gracias despedida", "neutral", "0")]:
                filas.append({"texto": texto, "etiqueta": clase, "es_relevante": relevante})
        train = pd.DataFrame(filas)
        val = pd.DataFrame({"texto": ["exclusivovalidacion subir la tpm", "saludos gracias despedida"]})
        original = TfidfVectorizer.fit_transform
        vistos = []
        def ajustar(vector, documentos, *args, **kwargs):
            documentos = list(documentos)
            self.assertFalse(any("exclusivovalidacion" in t for t in documentos))
            matriz = original(vector, documentos, *args, **kwargs)
            vistos.append(set(vector.vocabulary_))
            return matriz
        original_fit = TfidfVectorizer.fit
        def ajustar_fit(vector, documentos, *args, **kwargs):
            documentos = list(documentos)
            self.assertFalse(any("exclusivovalidacion" in t for t in documentos))
            resultado = original_fit(vector, documentos, *args, **kwargs)
            vistos.append(set(vector.vocabulary_))
            return resultado
        with patch.object(TfidfVectorizer, "fit_transform", new=ajustar), patch.object(TfidfVectorizer, "fit", new=ajustar_fit):
            pred = E.predecir_variantes(train, val, diccionario_prueba())
        self.assertEqual(set(pred), {v[2] for v in E.VARIANTES})
        self.assertEqual(len(vistos), 3)
        modelo = E.BASELINE.entrenar_modelo(train, E.PARAMETROS_TFIDF, E.PARAMETROS_LR)
        np.testing.assert_array_equal(pred["unigramas"], E.BASELINE.predecir_textos(modelo, val.texto).pred)
        for salida in pred.values():
            self.assertEqual(salida[1], "neutral")
        self.assertEqual(E.BASELINE.PARAMS_TFIDF["ngram_range"], (1, 2))

    def test_metricas_clases_fijas(self):
        resultado = E.metricas(["neutral"] * 3, ["neutral"] * 3)
        self.assertEqual(resultado["accuracy"], 1)
        self.assertEqual(resultado["macro_f1"], 1 / 3)
        self.assertEqual(resultado["n_hawkish"], 0)

    @unittest.skipUnless((L.RUTA_VALIDACION / "metricas.json").exists(), "evaluación aún no ejecutada")
    def test_artefactos_evaluados_y_pares(self):
        ruta = L.RUTA_VALIDACION
        resumen = json.loads((ruta / "metricas.json").read_text())
        for nombre, huella in resumen["sha256_salidas"].items():
            self.assertEqual(sha256(ruta / nombre), huella)
        protocolo = json.loads((ruta / "protocolo_validacion.json").read_text())
        self.assertEqual(sha256(Path(E.__file__)), protocolo["sha256_evaluador"])
        for nombre, huella in protocolo["sha256_dependencias"].items():
            self.assertEqual(sha256(L.config.RUTA_REPO / nombre), huella)
        oof = pd.read_csv(ruta / "predicciones_validacion.csv")
        self.assertEqual(len(oof), 793 * 4)
        self.assertTrue(oof.groupby("intervencion_id").fold.nunique().eq(1).all())
        self.assertTrue(oof.groupby("meeting_id").fold.nunique().eq(1).all())
        folds = pd.read_csv(ruta / "resultados_folds.csv")
        tabla = pd.read_csv(ruta / "comparacion_variantes.csv").set_index("variante")
        for variante, sub in oof.groupby("variante"):
            for clave, valor in E.metricas(sub.etiqueta, sub.pred).items():
                self.assertAlmostEqual(tabla.loc[variante, clave], valor)
        pares = folds.pivot(index="fold", columns="variante", values="macro_f1")
        for nombre, diferencia in resumen["diferencias_pareadas"].items():
            self.assertAlmostEqual(diferencia["delta_macro_f1_media"], (pares[nombre + "_lexico"] - pares[nombre]).mean())
        self.assertFalse(resumen["gold_leido_o_predicho"])
        self.assertFalse(resumen["modelo_vigente_reemplazado"])


if __name__ == "__main__":
    unittest.main()
