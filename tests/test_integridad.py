"""Regresiones de indexación OOF, validación, importación y fuentes protegidas.

Ejecutar: python -m unittest discover -s tests -v
No se escribe sobre datos del proyecto; todas las salidas de pruebas son temporales.
"""
import csv
from datetime import date
import io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import config
import fusionar_gold_llenado as gold
from utilidades import cargar_script, errores_anotacion, asignar_tandas, sha256


# ---- 1. Reglas de anotación compartidas ----
class ReglasAnotacion(unittest.TestCase):
    def test_normaliza_solo_espacios(self):
        self.assertEqual(errores_anotacion("hawkish", "alta", 1, "", "subir la tasa", "Vamos a subir\n la tasa."), [])

    def test_no_acepta_elipsis(self):
        self.assertIn("frase no verbatim", errores_anotacion("hawkish", "alta", 1, "", "subir...tasa", "subir la tasa"))

    def test_irrelevante_debe_ser_neutral(self):
        self.assertIn("irrelevante no neutral", errores_anotacion("dovish", "alta", 0, "trámite", "", "cierre"))

    def test_nota_blanca_no_vale(self):
        self.assertIn("falta nota", errores_anotacion("neutral", "alta", 0, " \n ", "", "cierre"))

    def test_frase_blanca_en_neutral_relevante_no_vale(self):
        self.assertIn("falta frase", errores_anotacion("neutral", "alta", 1, "", "  ", "diagnóstico"))

    def test_cita_opcional_tambien_es_literal(self):
        self.assertIn("frase no verbatim", errores_anotacion("neutral", "alta", 0, "trámite", "abrir", "cerrar"))

    def test_limite_frase(self):
        self.assertEqual(errores_anotacion("neutral", "alta", 1, "", "x" * 300, "x" * 301), [])
        self.assertIn("frase excede 300 caracteres", errores_anotacion("neutral", "alta", 1, "", "x" * 301, "x" * 301))

    def test_probabilidades_invalidas_detectadas(self):
        validador = cargar_script("05_validar_etiquetas.py")
        datos = pd.read_csv(config.RUTA_ETIQUETAS / "etiquetas_piloto_r1.csv")
        datos.loc[0, "prob_hawkish"] = np.inf
        with self.assertRaises(AssertionError):
            validador.validar(datos)

    def test_tandas_con_textos_mayores_al_presupuesto(self):
        self.assertEqual(asignar_tandas([2, 3, 11, 2, 10], 10), [1, 1, 2, 3, 4])

    def test_presupuesto_invalido(self):
        with self.assertRaises(AssertionError):
            asignar_tandas([1], 0)


# ---- 2. Instrumento gold de prueba y controles de importación ----
class ImportacionGold(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.cabecera = ["orden", "intervencion_id", "fecha_reunion", "actor", "cargo", "texto",
                         "etiqueta", "confianza", "es_relevante", "nota", "frase_justificante",
                         "metodo", "ronda", "version_codebook", "fecha", "etiquetador"]
        self.canonico = []
        for i in range(2):
            fila = dict.fromkeys(self.cabecera, "")
            fila.update(orden=str(i + 1), intervencion_id=f"RPM-2010-01-14:{i}:1", fecha_reunion="2010-01-14",
                        actor="Actor", cargo="Consejero", texto='Propone subir\nla tasa, "hoy"; sí.',
                        metodo="humano_gold", ronda="gold_ciego", version_codebook="v2", etiquetador="usuario")
            self.canonico.append(fila)
        self.lleno = [{**f, "etiqueta": "hawkish", "confianza": "alta", "es_relevante": "1",
                       "frase_justificante": "subir la tasa", "fecha": "2026-09-15"} for f in self.canonico]

    def escribir(self, nombre, filas, separador=","):
        ruta = self.raiz / nombre
        with ruta.open("w", encoding="utf-8-sig", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=self.cabecera, delimiter=separador)
            escritor.writeheader(); escritor.writerows(filas)
        return ruta

    def analizar(self, **kwargs):
        return gold.analizar(self.cabecera, self.canonico, self.cabecera, self.lleno,
                             corte=date(2026, 9, 16), **kwargs)

    def test_caso_valido(self):
        nuevas, errores, pendientes = self.analizar()
        self.assertFalse(errores or pendientes)
        self.assertEqual(nuevas[0]["texto"], self.canonico[0]["texto"])
        self.assertEqual(nuevas[0]["fecha"], "2026-09-15")

    def test_orden_filas_distinto_se_alinea_por_id(self):
        self.lleno.reverse()
        nuevas, errores, _ = self.analizar()
        self.assertFalse(errores)
        self.assertEqual([f["intervencion_id"] for f in nuevas], [f["intervencion_id"] for f in self.canonico])

    def test_ids_duplicados(self):
        self.lleno[1]["intervencion_id"] = self.lleno[0]["intervencion_id"]
        with self.assertRaises(AssertionError):
            self.analizar()

    def test_id_faltante(self):
        self.lleno.pop()
        with self.assertRaises(AssertionError):
            self.analizar()

    def test_texto_alterado(self):
        self.lleno[0]["texto"] = "otro texto"
        self.assertIn("columna protegida modificada: texto", [e["problema"] for e in self.analizar()[1]])

    def test_metadatos_protegidos(self):
        self.lleno[0]["actor"] = "Otro"
        self.assertIn("columna protegida modificada: actor", [e["problema"] for e in self.analizar()[1]])

    def test_fecha_futura_rechazada(self):
        self.lleno[0]["fecha"] = "2027-01-01"
        self.assertTrue(self.analizar()[1])

    def test_fecha_ausente_rechazada(self):
        self.lleno[0]["fecha"] = ""
        self.assertTrue(self.analizar()[1])

    def test_fecha_confirmada_explicita_se_conserva(self):
        self.lleno[0]["fecha"] = "2027-01-01"
        nuevas, errores, _ = self.analizar(fecha_anotacion="2026-09-15")
        self.assertFalse(errores)
        self.assertEqual(nuevas[0]["fecha"], "2026-09-15")

    def test_fecha_confirmada_futura_no_vale(self):
        with self.assertRaises(AssertionError):
            self.analizar(fecha_anotacion="2027-01-01")

    def test_csv_multilinea_coma_y_punto_coma(self):
        for separador in [",", ";"]:
            with self.subTest(separador=separador):
                ruta = self.escribir("lleno.csv", self.lleno, separador)
                _, filas = gold.registros(ruta)
                self.assertEqual(filas, self.lleno)

    def test_cabeceras_duplicadas_rechazadas(self):
        ruta = self.raiz / "mal.csv"
        ruta.write_text("intervencion_id,intervencion_id\na,a\n")
        with self.assertRaises(AssertionError):
            gold.registros(ruta)

    def test_filas_irregulares_rechazadas(self):
        ruta = self.raiz / "mal.csv"
        ruta.write_text("intervencion_id,texto\na,x,y\n")
        with self.assertRaises(AssertionError):
            gold.registros(ruta)

    def test_xlsx_formulas_rechazadas(self):
        libro = Workbook(); hoja = libro.active; hoja.title = "etiquetar"
        hoja.append(self.cabecera); hoja.append([self.lleno[0][c] for c in self.cabecera])
        hoja["G2"] = '=IF(1=1,"hawkish","neutral")'
        ruta = self.raiz / "formula.xlsx"; libro.save(ruta); libro.close()
        with self.assertRaises(AssertionError):
            gold.registros(ruta)

    def test_normalizacion_se_persiste_y_no_sobrescribe(self):
        self.lleno[0]["etiqueta"] = " HAWKISH "
        self.lleno[0]["confianza"] = " ALTA "
        canonico = self.escribir("canonico.csv", self.canonico)
        entrada = self.escribir("entrada.csv", self.lleno)
        salida = self.raiz / "salida.csv"
        huellas = sha256(canonico), sha256(entrada)
        with patch.object(gold, "CANONICO", canonico), redirect_stdout(io.StringIO()):
            self.assertEqual(gold.main([str(entrada), "--salida", str(salida)]), 0)
            self.assertEqual(gold.main([str(entrada), "--salida", str(salida)]), 1)
        _, filas = gold.registros(salida)
        self.assertEqual(filas[0]["etiqueta"], "hawkish")
        self.assertEqual(filas[0]["confianza"], "alta")
        self.assertTrue(salida.with_suffix(".provenance.json").exists())
        self.assertEqual(huellas, (sha256(canonico), sha256(entrada)))

    def test_errores_nunca_escriben_salida(self):
        self.lleno[0]["frase_justificante"] = "frase inventada"
        canonico = self.escribir("canonico.csv", self.canonico)
        entrada = self.escribir("entrada.csv", self.lleno)
        salida = self.raiz / "salida.csv"
        with patch.object(gold, "CANONICO", canonico), redirect_stdout(io.StringIO()):
            self.assertEqual(gold.main([str(entrada), "--salida", str(salida)]), 1)
        self.assertFalse(salida.exists())

    def test_parcial_requiere_opcion_explicita(self):
        self.lleno[1] = self.canonico[1].copy()
        canonico = self.escribir("canonico.csv", self.canonico)
        entrada = self.escribir("entrada.csv", self.lleno)
        with patch.object(gold, "CANONICO", canonico), redirect_stdout(io.StringIO()):
            self.assertEqual(gold.main([str(entrada), "--validar"]), 1)
            self.assertEqual(gold.main([str(entrada), "--validar", "--permitir-parcial"]), 0)

    def test_solo_nota_no_es_fila_vacia(self):
        self.lleno[1] = {**self.canonico[1], "nota": "falta completar"}
        self.assertTrue(self.analizar()[1])
        self.assertFalse(self.analizar()[2])

    def test_no_existe_forzar(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            gold.main(["entrada.csv", "--forzar"])
        self.assertEqual(error.exception.code, 2)


# ---- 3. Regresión del bug OOF con identificadores sintéticos ----
class BaselineOOF(unittest.TestCase):
    def test_predicciones_se_escriben_en_indices_test(self):
        baseline = cargar_script("15_baseline_tfidf.py")
        etiquetas = np.array(["hawkish", "dovish", "neutral"] * 10)
        relevancia = np.array([0 if i % 6 == 2 else 1 for i in range(30)])
        ajustes = []

        class Vectorizador:
            def __init__(self, **kwargs):
                pass

            def fit_transform(self, textos):
                self.train = set(map(int, textos)); ajustes.append(self.train)
                return self.transform(textos, training=True)

            def transform(self, textos, training=False):
                ids = np.array(list(map(int, textos)))
                if not training:
                    assert self.train.isdisjoint(ids), "vocabulario ajustado sobre test"
                return ids.reshape(-1, 1)

        class Clasificador:
            def __init__(self, **kwargs):
                pass

            def fit(self, x, y):
                self.classes_ = np.unique(y)
                return self

            def predict(self, x):
                return relevancia[x[:, 0]]

            def predict_proba(self, x):
                return np.array([[1.0 if c == etiquetas[i] else 0.0 for c in self.classes_] for i in x[:, 0]])

        datos = pd.DataFrame({"texto": list(map(str, range(30))), "es_relevante": relevancia.astype(str),
                              "etiqueta": etiquetas, "meeting_id": [f"m{i // 3}" for i in range(30)]})
        with patch.object(baseline, "TfidfVectorizer", Vectorizador), patch.object(baseline, "LogisticRegression", Clasificador):
            resultado = baseline.evaluar_oof(datos)
        self.assertEqual(resultado.pred.tolist(), etiquetas.tolist())
        self.assertTrue(resultado.groupby("meeting_id").fold.nunique().eq(1).all())
        self.assertEqual(len(ajustes), baseline.N_FOLDS * 2)
        self.assertEqual(resultado.score_pred.astype(float).tolist(), [1.0, -1.0, 0.0] * 10)

    def test_baseline_guardado_tiene_metadatos_coherentes(self):
        datos = pd.read_csv(config.RUTA_L2 / "baseline_tfidf_oof.csv")
        self.assertTrue(datos.intervencion_id.is_unique)
        self.assertTrue(datos.groupby("fecha").fold.nunique().eq(1).all())
        self.assertEqual(cargar_script("15_baseline_tfidf.py").calcular_metricas(datos)["macro_f1"], 0.7173)


# ---- 4. Todos los generadores congelados se niegan a sobrescribir ----
class FuentesProtegidas(unittest.TestCase):
    def test_generadores_protegidos(self):
        nombres = ["01_excel_a_capa_l0.py", "02_metadata_actores.py", "03_muestra_piloto.py",
                   "04_tandas_por_presupuesto.py", "06_tandas_escalado.py", "07_macro_desde_excel.py",
                   "08_muestra_estrato_fases.py", "09_muestra_gold_ciego.py",
                   "10_muestra_enriquecida.py", "10_muestra_tanda9_stance.py"]
        for nombre in nombres:
            with self.subTest(script=nombre), self.assertRaises(FileExistsError):
                cargar_script(nombre).main()


if __name__ == "__main__":
    unittest.main()
