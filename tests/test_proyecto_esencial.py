import csv
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestProyectoEsencial(unittest.TestCase):
    def test_inventario_reducido(self):
        scripts = list((ROOT / "scripts").glob("*.py"))
        tests = list((ROOT / "tests").glob("test_*.py"))
        self.assertEqual({p.name for p in scripts}, {"modelo_final.py", "analisis_resultados.py"})
        self.assertEqual([p.name for p in tests], ["test_proyecto_esencial.py"])
        self.assertLessEqual(len(list((ROOT / "docs").glob("*.md"))), 7)

    def test_integridad(self):
        manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))["sha256"]
        for name, expected in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_entrenamiento_final(self):
        with (ROOT / "data/entrenamiento_wc600.csv").open(encoding="utf-8", newline="") as f: rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1596)
        self.assertEqual(len({r["intervencion_id"] for r in rows}), 1596)
        expected = {1: 1494, 2: 1450, 3: 1453, 4: 1473, 5: 1466}
        self.assertEqual({i: sum(str(i) in r["miembros"].split("|") for r in rows) for i in range(1, 6)}, expected)
        with (ROOT / "data/evaluacion_ciega_gold.csv").open(encoding="utf-8", newline="") as f: gold = list(csv.DictReader(f))
        self.assertEqual(len(gold), 300)
        self.assertFalse({r["meeting_id"] for r in rows} & {r["meeting_id"] for r in gold})

    def test_resultado_y_benchmark(self):
        result = json.loads((ROOT / "data/resultados_evaluacion_ciega.json").read_text(encoding="utf-8"))
        self.assertEqual(result["decision"], "adoptar_wc_600")
        self.assertEqual(result["filas_evaluadas"], 299)
        self.assertAlmostEqual(result["modelos"]["wc_600"]["macro_f1"], 0.7462588094167041)
        benchmark = json.loads((ROOT / "data/benchmark_modelos.json").read_text(encoding="utf-8"))
        self.assertEqual(len(benchmark["modelos"]), 14)
        self.assertEqual(benchmark["modelo_formal_vigente"], "W+C+600")

    def test_clasificacion_completa(self):
        with (ROOT / "resultados/clasificacion_wc600_9725.csv").open(encoding="utf-8", newline="") as f: rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9725)
        self.assertEqual(len({r["intervencion_id"] for r in rows}), 9725)
        self.assertEqual(len({r["topico_humano"] for r in rows}), 13)
        self.assertTrue(all(r["keywords_humano"] for r in rows))
        self.assertEqual({label: sum(r["prediccion_v3"] == label for r in rows) for label in ["hawkish", "dovish", "neutral"]}, {"hawkish": 513, "dovish": 380, "neutral": 8832})
        self.assertEqual(sum(r["acuerdo_miembros"] == "desacuerdo" for r in rows), 169)
        for r in rows[:100]: self.assertAlmostEqual(sum(float(r[c]) for c in ["prob_h_no_calibrada", "prob_d_no_calibrada", "prob_n_no_calibrada"]), 1.0)
        manifest = json.loads((ROOT / "resultados/manifest.json").read_text(encoding="utf-8"))["sha256"]
        for name, expected in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT / "resultados" / name).read_bytes()).hexdigest(), expected)

    def test_analisis_y_modelos_persistidos(self):
        summary = json.loads((ROOT / "resultados/analisis_descriptivo/resumen.json").read_text(encoding="utf-8"))
        self.assertEqual((summary["filas_validas"], summary["no_decidibles"], summary["reuniones"]), (9724, 1, 132))
        self.assertEqual((summary["decisiones_institucionales_proxy"], summary["casos_convergencia_proxy"]), (132, 39))
        self.assertEqual((summary["topicos_humanos"], summary["topicos_modelo_nmf"], summary["oraciones_ajuste_topicos_modelo"]), (13, 14, 57452))
        self.assertEqual((summary["ejes_radar_tematico"], summary["actores_aptos_radar"]), (6, 9))
        self.assertEqual(summary["pares_reunion_actor_con_candidato_voto"], 560)
        self.assertEqual((summary["acuerdos_consejo_extraidos"], summary["filas_base_votos_acta_actor"]), (132, 649))
        self.assertEqual((summary["votos_con_accion_extraida"], summary["votos_inferidos_por_unanimidad"], summary["votos_revisados_textualmente"], summary["votos_no_extraidos"], summary["votos_finales_con_magnitud_y_tpm"]), (516, 87, 45, 1, 648))
        self.assertFalse(summary["embeddings_generados"])
        with (ROOT / "resultados/analisis_descriptivo/tabla_maestra.csv").open(encoding="utf-8", newline="") as f: master = list(csv.DictReader(f))
        self.assertEqual(len(master), 9725)
        self.assertTrue(all(r["orden_habla"] and r["subindice"] and r["tipo_actor"] for r in master))
        self.assertEqual({r["tipo_actor"] for r in master}, {"miembro_consejo", "staff_tecnico", "hacienda_gobierno", "consejo_institucional"})
        topic_method = json.loads((ROOT / "resultados/analisis_descriptivo/topicos_modelo_metodo.json").read_text(encoding="utf-8"))
        self.assertEqual((topic_method["metodo"], topic_method["n_topicos"], topic_method["columnas_humanas_usadas"]), ("NMF sobre TF-IDF de oraciones", 14, []))
        radar_method = json.loads((ROOT / "resultados/analisis_descriptivo/radar_tematico_metodo.json").read_text(encoding="utf-8"))
        self.assertEqual(len(radar_method["ejes_componentes_nmf"]), 6)
        self.assertTrue({"tema_nmf_05", "tema_nmf_14"}.issubset(radar_method["componentes_excluidos"]))
        for name in ["indices_actor_por_anio.csv", "topicos_por_actor.csv", "topicos_modelo_nmf.csv", "asignacion_topicos_modelo_nmf.csv", "topicos_modelo_por_reunion.csv", "radar_tematico_actores.csv", "radar_tematico_actores_ancho.csv", "radar_tematico_metodo.json", "vocabulario_frecuente_por_actor.csv", "vocabulario_distintivo_por_actor.csv", "matriz_votos_candidatos.csv", "acuerdo_consejo_por_reunion.csv", "base_votos_acta_actor.csv", "convergencia_actor_reunion_proxy.csv"]:
            self.assertTrue((ROOT / "resultados/analisis_descriptivo" / name).is_file())
        with (ROOT / "resultados/analisis_descriptivo/base_votos_acta_actor.csv").open(encoding="utf-8", newline="") as f: votes = list(csv.DictReader(f))
        self.assertEqual(len(votes), 649)
        self.assertEqual(len({r["meeting_id"] for r in votes}), 132)
        self.assertEqual({r["acuerdo_accion"] for r in votes}, {"subir", "bajar", "mantener"})
        self.assertTrue(all(r["voto_accion"] and r["voto_accion_con_inferencia"] and r["voto_accion_final"] and r["fuente_voto_final"] for r in votes))
        self.assertEqual(sum(r["voto_accion_final"] == "no_extraido" for r in votes), 1)
        self.assertTrue(all(r["voto_magnitud_pb_final"] and r["voto_tpm_objetivo_final"] for r in votes if r["voto_accion_final"] != "no_extraido"))
        self.assertEqual(sum(r["fuente_voto_final"] == "revision_textual_asistida" for r in votes), 45)
        self.assertEqual(sum(r["coincide_final_con_acuerdo"] == "no" for r in votes), 9)
        with (ROOT / "data/revision_votos_actores.csv").open(encoding="utf-8", newline="") as f: reviewed_votes = list(csv.DictReader(f))
        self.assertEqual((len(reviewed_votes), sum(r["voto_accion_revision"] == "no_extraido" for r in reviewed_votes)), (46, 1))
        with (ROOT / "resultados/analisis_descriptivo/acuerdo_consejo_por_reunion.csv").open(encoding="utf-8", newline="") as f: agreements = list(csv.DictReader(f))
        self.assertEqual(len(agreements), 132)
        self.assertTrue(all(r["acuerdo_accion"] in {"subir", "bajar", "mantener"} and r["acuerdo_tpm_objetivo"] for r in agreements))
        model_manifest = json.loads((ROOT / "modelos/wc600/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(model_manifest["archivos_sha256"]), 5)
        for name, expected in model_manifest["archivos_sha256"].items(): self.assertEqual(hashlib.sha256((ROOT / "modelos/wc600" / name).read_bytes()).hexdigest(), expected)
        analysis_manifest = json.loads((ROOT / "resultados/analisis_descriptivo/manifest.json").read_text(encoding="utf-8"))["sha256_salidas"]
        for name, expected in analysis_manifest.items(): self.assertEqual(hashlib.sha256((ROOT / "resultados/analisis_descriptivo" / name).read_bytes()).hexdigest(), expected)

    def test_readme_documenta_formulas(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for formula in ["operatorname{tfidf}", "MacroF1", "F1_{HD}", "tono neto general", "balance direccional", "cobertura direccional", "log-odds", "bootstrap", "Convergencia_{it}", "Disenso_{it}", "s_{it}=\\alpha_i"]:
            self.assertIn(formula, text)
        with (ROOT / "data/actores_metadata.csv").open(encoding="utf-8", newline="") as f: actors = list(csv.DictReader(f))
        self.assertEqual(len(actors), 55)
        self.assertEqual(sum(r["verificado"] == "True" for r in actors), 3)

    def test_script_verifica(self):
        spec = importlib.util.spec_from_file_location("modelo_final", ROOT / "scripts/modelo_final.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual(module.verificar()["estado"], "íntegro")
        self.assertEqual(module.CHAR["ngram_range"], (3, 5))
        self.assertEqual(module.LR["C"], 2.0)


if __name__ == "__main__": unittest.main()
