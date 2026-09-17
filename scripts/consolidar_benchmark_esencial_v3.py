"""Consolida el benchmark mínimo que justifica TF-IDF y preserva sus parámetros."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/benchmark_esencial_v3_v1"
SPECS = [
    ("C+89", "v3_desarrollo_793", "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/metricas.json", "fase_c_mas_89", "ancla_formal"),
    ("W+C inicial", "v3_desarrollo_793", "data/evaluacion/palabras_caracteres_tfidf_v3_v1/metricas.json", "palabras_caracteres", "rechazado_en_ronda"),
    ("C+pre2000", "v3_desarrollo_793", "data/evaluacion/ampliacion_pre2000_tfidf_v3_v1/metricas.json", "c_mas_pre2000", "rechazado"),
    ("Jerarquía W+C", "v3_desarrollo_793", "data/evaluacion/jerarquia_direccional_v3_v1/metricas.json", "jerarquia", "rechazado"),
    ("TF-IDF adaptado L0", "v3_desarrollo_793", "data/evaluacion/adaptacion_dominio_bcch_v3_v1/metricas.json", "adaptado_l0", "rechazado"),
    ("NB-SVM", "v3_desarrollo_793", "data/evaluacion/extension_representaciones_v3_v1/metricas.json", "extension", "rechazado"),
    ("Ensamble calibrado", "v3_desarrollo_793", "data/evaluacion/ensamble_calibrado_v3_v1/metricas.json", "ensamble", "rechazado"),
    ("C+600", "v3_desarrollo_793", "data/evaluacion/reestimacion_600_c_wc_v3_v1/metricas.json", "c_mas_600", "no_adoptado"),
    ("W+C+600", "v3_desarrollo_793", "data/evaluacion/reestimacion_600_c_wc_v3_v1/metricas.json", "wc_mas_600", "mejor_numerico_challenger"),
]
BETO_SOURCE = ROOT / "data/auditoria/recepcion_beto_v1/auditoria.json"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))


def flatten(name, group, source, key, decision):
    m = read_json(ROOT / source)[key]
    return {"modelo": name, "grupo_comparabilidad": group, "accuracy": m["accuracy"], "macro_f1": m["macro_f1"], "f1_hd": m["f1_hd"],
        "f1_h": m["por_clase"]["hawkish"]["f1"], "f1_d": m["por_clase"]["dovish"]["f1"], "recall_d": m["por_clase"]["dovish"]["recall"],
        "f1_n": m["por_clase"]["neutral"]["f1"], "errores": m["errores"], "inversiones_hd": m["h_d_cruzados"],
        "omisiones_direccion": m["direccion_a_neutral"], "falsas_direcciones": m["neutral_a_direccion"], "decision": decision, "fuente": source, "clave": key}


def run(out=OUT):
    out = Path(out)
    if out.exists(): raise FileExistsError("No sobrescribir benchmark")
    rows = [flatten(*spec) for spec in SPECS]
    legacy = read_json(BETO_SOURCE)["comparacion"]["condiciones"]
    for name, key, decision in [("TF-IDF legado", "tfidf", "ganador_controlado"), ("BETO", "beto", "rechazado_controlado")]:
        m = legacy[key]["conjunto"]
        rows.append({"modelo": name, "grupo_comparabilidad": "legado_v2_793", "accuracy": m["accuracy"], "macro_f1": m["macro_f1"], "f1_hd": m["f1_hd"],
            "f1_h": m["f1_hawkish"], "f1_d": m["f1_dovish"], "recall_d": m["recall_dovish"], "f1_n": m["f1_neutral"], "errores": m["errores"],
            "inversiones_hd": m["h_a_d"] + m["d_a_h"], "omisiones_direccion": m["hd_a_n"], "falsas_direcciones": m["n_a_hd"], "decision": decision,
            "fuente": str(BETO_SOURCE.relative_to(ROOT)), "clave": f"comparacion.condiciones.{key}.conjunto"})
    params = {"arquitectura": "dos etapas: A relevancia; B H/D/N entre relevantes", "clasificador": "LogisticRegression",
        "logistic_regression": {"class_weight": "balanced", "max_iter": 2000, "random_state": 20260915, "C": 2.0},
        "tfidf_palabras_A": {"strip_accents": "unicode", "lowercase": True, "ngram_range": [1, 1], "min_df": 3, "max_df": 0.9, "sublinear_tf": True},
        "tfidf_palabras_B": {"strip_accents": "unicode", "lowercase": True, "ngram_range": [1, 4], "min_df": 3, "max_df": 0.9, "sublinear_tf": True},
        "tfidf_caracteres": {"analyzer": "char_wb", "ngram_range": [3, 5], "min_df": 3, "max_df": 0.98, "sublinear_tf": True, "strip_accents": "unicode", "lowercase": True, "max_features": 120000},
        "pesos_char_congelados_por_outer_fold": {"1": 1.0, "2": 0.5, "3": 1.0, "4": 1.0, "5": 1.0},
        "validacion": {"outer": "5 folds agrupados por meeting_id", "inner": "GroupKFold(3) solo para selección permitida", "purga": "reunión y texto normalizado", "n_validacion": 793}}
    sources = sorted({ROOT / row["fuente"] for row in rows} | {ROOT / "scripts/entrenar_tfidf_supervision_v3.py", ROOT / "scripts/evaluar_palabras_caracteres_v3.py"})
    registry = {"version": "benchmark_esencial_v3_v1", "objetivo": "preservar evidencia, parámetros y decisiones para defender elección TF-IDF",
        "mejor_numerico_v3": "W+C+600", "modelo_formal_vigente": "C+89", "mrbert_estado": "pendiente de ejecución Colab",
        "advertencias": ["793 casos son desarrollo abierto, no test final", "no comparar directamente grupos v3 y legado v2", "una arquitectura rechazada no prueba inferioridad universal"],
        "parametros_tfidf": params, "modelos": rows, "fuentes_sha256": {str(path.relative_to(ROOT)): sha(path) for path in sources}}
    out.mkdir(parents=True); (out / "registro.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "tabla_modelos.csv").open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    (out / "manifest.json").write_text(json.dumps({"sha256_salidas": {name: sha(out / name) for name in ["registro.json", "tabla_modelos.csv"]}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return registry


if __name__ == "__main__": print(json.dumps(run(), ensure_ascii=False, indent=2))
