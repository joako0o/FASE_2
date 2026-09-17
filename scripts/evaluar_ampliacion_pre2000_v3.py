"""Compara candidato C real contra C + 250 adjudicaciones pre-2000 cerradas."""
import json
from collections import Counter
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning

from entrenar_tfidf_supervision_v3 import RAIZ, ajustar_predecir, cargar_datos, clave_texto, metricas_completas, sha256
from evaluar_ampliacion_ia89_v3 import cargar_nuevos

OUT = RAIZ / "data/evaluacion/ampliacion_pre2000_tfidf_v3_v1"


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def load_pre2000():
    path = RAIZ / "data/evaluacion/pre2000_adjudicacion_v3_v1/adjudicacion_pre2000_v3.csv"
    data = pd.read_csv(path, dtype=str, keep_default_na=False)
    data = data[data.estado_revision_v3.eq("cerrado")].copy()
    if len(data) != 250 or data.frag_id.nunique() != 250:
        raise ValueError("Se esperaban 250 filas pre-2000 cerradas")
    data["intervencion_id"] = "PRE2000-" + data.frag_id
    data["meeting_id"] = "PRE2000-" + data.fecha
    data["texto"] = data.texto_original
    data["relevancia_v3"] = data.es_relevante_v3
    return data[["intervencion_id", "meeting_id", "texto", "etiqueta_v3", "relevancia_v3"]], path


def run(out=OUT):
    out = Path(out)
    if out.exists():
        raise FileExistsError("No sobrescribir experimento")
    base, _, base_sources = cargar_datos()
    ia89, ia_sources = cargar_nuevos()
    pre, pre_path = load_pre2000()
    anchor_path = RAIZ / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv"
    anchor = pd.read_csv(anchor_path, dtype=str, keep_default_na=False).set_index("intervencion_id")
    predictions, executions = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy()
            keys = set(val.texto.map(clave_texto))
            meetings = set(val.meeting_id)
            train = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(keys)].copy()
            ia = ia89[~ia89.meeting_id.isin(meetings) & ~ia89.texto.map(clave_texto).isin(keys)].copy()
            pre_fold = pre[~pre.texto.map(clave_texto).isin(keys)].copy()
            candidate_c = pd.concat([train, ia.reindex(columns=train.columns)], ignore_index=True)
            candidate_pre = pd.concat([candidate_c, pre_fold.reindex(columns=train.columns)], ignore_index=True)
            results = {}
            for name, dataset in [("candidato_c", candidate_c), ("c_mas_pre2000", candidate_pre)]:
                a, b, final, dimensions = ajustar_predecir(dataset, val, "v3")
                results[name] = (a, b, final)
                executions.append({"fold": fold, "condicion": name, "n_ia89": len(ia),
                                   "n_pre2000": 0 if name == "candidato_c" else len(pre_fold), **dimensions})
            a0, b0, p0 = results["candidato_c"]
            fixed = anchor.loc[val.index]
            if not (np.array_equal(a0.astype(str), fixed.pred_a_fase_c.to_numpy()) and
                    np.array_equal(b0.astype(str), fixed.pred_b_fase_c.to_numpy()) and
                    np.array_equal(p0.astype(str), fixed.pred_fase_c.to_numpy())):
                raise ValueError(f"No se reprodujo candidato C en fold {fold}")
            a1, b1, p1 = results["c_mas_pre2000"]
            for i, (_, row) in enumerate(val.iterrows()):
                predictions.append({"intervencion_id": row.intervencion_id, "meeting_id": row.meeting_id,
                    "fold": fold, "etiqueta_v3": row.etiqueta_v3, "es_relevante_v3": row.relevancia_v3,
                    "pred_c": p0[i], "pred_pre2000": p1[i], "pred_a_c": str(a0[i]),
                    "pred_a_pre2000": str(a1[i]), "pred_b_c": b0[i], "pred_b_pre2000": b1[i]})
            print(f"Fold {fold}: C reproducido; +{len(pre_fold)} pre-2000", flush=True)
    table = pd.DataFrame(predictions).sort_values(["fold", "intervencion_id"])
    cmet = metricas_completas(table.rename(columns={"pred_c": "pred"}), "pred")
    pmet = metricas_completas(table.rename(columns={"pred_pre2000": "pred"}), "pred")
    table["cambio"] = table.pred_c.ne(table.pred_pre2000)
    table["efecto"] = np.select(
        [table.pred_c.eq(table.etiqueta_v3) & table.pred_pre2000.ne(table.etiqueta_v3),
         table.pred_c.ne(table.etiqueta_v3) & table.pred_pre2000.eq(table.etiqueta_v3)],
        ["acierto_a_error", "error_a_acierto"], default="sin_cambio")
    improved_folds = sum(pmet["por_fold"][str(i)]["f1_hd"] > cmet["por_fold"][str(i)]["f1_hd"] for i in range(1, 6))
    metrics = {"version": out.name, "candidato_c": cmet, "c_mas_pre2000": pmet,
        "delta": {k: pmet[k] - cmet[k] for k in ["accuracy", "macro_f1", "f1_hd", "media_folds_f1_hd", "errores"]},
        "folds_f1_hd_mejorados": improved_folds,
        "cambios_prediccion": int(table.cambio.sum()), "efecto": dict(Counter(table.efecto)),
        "evaluacion_independiente": False, "hiperparametros_buscados": False,
        "decision": "rechazar_dosis_pre2000" if improved_folds < 3 or pmet["errores"] > cmet["errores"] else "aceptar"}
    out.mkdir(parents=True)
    table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n")
    save_json(out / "metricas.json", metrics); save_json(out / "ejecucion_folds.json", executions)
    sources = {**base_sources, **ia_sources, "pre2000": pre_path, "ancla_c": anchor_path, "script": Path(__file__)}
    save_json(out / "protocolo.json", {"operacion": "única comparación predefinida C vs C+pre2000; sin búsqueda",
        "purga": "reunión y texto para IA89; texto para pre-2000, cuyas fechas no solapan 2005-2015",
        "fuentes_sha256": {k: sha256(v) for k, v in sources.items()}})
    summary = "# Ampliación real con pre-2000\n\nComparación de desarrollo reutilizada; no es evaluación independiente.\n\n"
    summary += "| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for name, m in [("C", cmet), ("C + 250 pre-2000", pmet)]:
        summary += f"| {name} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {m['por_clase']['dovish']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    summary += "\n| Fold | F1-HD C | F1-HD C+pre-2000 | Delta |\n|---:|---:|---:|---:|\n"
    for i in range(1, 6):
        a, b = cmet["por_fold"][str(i)]["f1_hd"], pmet["por_fold"][str(i)]["f1_hd"]
        summary += f"| {i} | {a:.6f} | {b:.6f} | {b-a:+.6f} |\n"
    summary += "\n**Decisión: rechazar la dosis completa pre-2000.** Mejora la media por fold y F1 D, pero solo mejora 2/5 folds, aumenta los errores de 57 a 59, reduce F1 H y deteriora levemente accuracy. No se incorpora al candidato congelado.\n"
    (out / "resumen.md").write_text(summary, encoding="utf-8")
    save_json(out / "manifest.json", {"sha256_salidas": {p.name: sha256(p) for p in out.iterdir() if p.name != "manifest.json"}})
    return metrics


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
