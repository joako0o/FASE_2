"""Reestimación preregistrada única C versus W+C con dos tandas humanas cerradas."""
import argparse
import hashlib
import json
import platform
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.exceptions import ConvergenceWarning

from entrenar_tfidf_supervision_v3 import RAIZ, ajustar_predecir, cargar_datos, clave_texto, metricas_completas, sha256
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import fit_predict, multicriteria
from reestimar_c_wc_con_300_v3 import load_300, audited_extra

OUT = RAIZ / "data/evaluacion/reestimacion_600_c_wc_v3_v1"
SECOND_PATH = RAIZ / "data/evaluacion/anotacion_dirigida_300_v3_cerrada_v1/referencia_300_v3.csv"
ANCHOR89 = RAIZ / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv"
ANCHOR300 = RAIZ / "data/evaluacion/reestimacion_300_c_wc_v3_v1/predicciones.csv"
PREREG = RAIZ / "docs/PROTOCOLO_REESTIMACION_600_C_WC_V3.md"
WEIGHTS = {1: 1.0, 2: 0.5, 3: 1.0, 4: 1.0, 5: 1.0}


def save(path, obj): path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
def load_second():
    data = pd.read_csv(SECOND_PATH, dtype=str, keep_default_na=False)
    if len(data) != 300 or not data.intervencion_id.is_unique or set(data.estado_revision_v3) != {"cerrado"}: raise ValueError("Segunda tanda no cerrada")
    if data.etiqueta_v3.value_counts().to_dict() != {"neutral": 198, "dovish": 66, "hawkish": 36}: raise ValueError("Distribución segunda tanda inesperada")
    if not data.texto.map(lambda x: hashlib.sha256(x.encode()).hexdigest()).equals(data.sha256_texto): raise ValueError("Hash de segunda tanda inválido")
    data["meeting_id"] = data.intervencion_id.str.rsplit(":", n=2).str[0]; data["relevancia_v3"] = data.es_relevante_v3
    return data[["meeting_id", "texto", "etiqueta_v3", "relevancia_v3", "intervencion_id"]].copy()


def run(out=OUT):
    out = Path(out)
    if out.exists(): raise FileExistsError("No sobrescribir reestimación")
    base, _, base_sources = cargar_datos(); ia89, ia_sources = cargar_nuevos(); first, second = load_300(), load_second()
    if set(first.intervencion_id) & set(second.intervencion_id) or (set(first.intervencion_id) | set(second.intervencion_id)) & set(base.intervencion_id): raise ValueError("Solapamiento de IDs")
    anchor89 = pd.read_csv(ANCHOR89, dtype=str, keep_default_na=False).set_index("intervencion_id")
    anchor300 = pd.read_csv(ANCHOR300, dtype=str, keep_default_na=False).set_index("intervencion_id")
    predictions, audits, executions = [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy(); keys = set(val.texto.map(clave_texto))
            train = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(keys)].copy()
            ai = audited_extra(ia89, val, fold, "ia89"); h1 = audited_extra(first, val, fold, "humana300_primera"); h2 = audited_extra(second, val, fold, "humana300_dirigida")
            audits.extend([ai, h1, h2]); ai_in, h1_in, h2_in = ai[ai.incluido], h1[h1.incluido], h2[h2.incluido]
            prior89 = pd.concat([train, ai_in.reindex(columns=train.columns)], ignore_index=True)
            prior300 = pd.concat([prior89, h1_in.reindex(columns=train.columns)], ignore_index=True)
            augmented = pd.concat([prior300, h2_in.reindex(columns=train.columns)], ignore_index=True)
            if set(augmented.meeting_id) & set(val.meeting_id) or set(augmented.texto.map(clave_texto)) & keys: raise ValueError(f"Contaminación fold {fold}")
            a89, b89, p89, _ = ajustar_predecir(prior89, val, "v3"); fixed89 = anchor89.loc[val.index]
            if not (np.array_equal(a89.astype(str), fixed89.pred_a_fase_c.to_numpy()) and np.array_equal(b89.astype(str), fixed89.pred_b_fase_c.to_numpy()) and np.array_equal(p89.astype(str), fixed89.pred_fase_c.to_numpy())): raise ValueError(f"No reproduce C+89 fold {fold}")
            _, _, p300, _ = ajustar_predecir(prior300, val, "v3"); fixed300 = anchor300.loc[val.index]
            if not np.array_equal(p300.astype(str), fixed300.pred_c_300.to_numpy()): raise ValueError(f"No reproduce C+300 fold {fold}")
            ac, bc, pc, dc = ajustar_predecir(augmented, val, "v3"); aw, bw, pw, dw = fit_predict(augmented, val, WEIGHTS[fold])
            executions.append({"fold": fold, "peso_char": WEIGHTS[fold], "n_train_base": len(train), "n_ia89": len(ai_in), "n_primera300": len(h1_in), "n_dirigida300": len(h2_in), "dirigida_por_clase": h2_in.etiqueta_v3.value_counts().to_dict(), "dimensiones_c": dc, "dimensiones_wc": dw})
            for i, (_, row) in enumerate(val.iterrows()): predictions.append({"intervencion_id": row.intervencion_id, "meeting_id": row.meeting_id, "fold": fold, "etiqueta_v3": row.etiqueta_v3, "es_relevante_v3": row.relevancia_v3, "pred_c_ancla89": p89[i], "pred_c_primera300": p300[i], "pred_c_600": pc[i], "pred_wc_600": pw[i], "pred_a_c_600": str(ac[i]), "pred_b_c_600": bc[i], "pred_a_wc_600": str(aw[i]), "pred_b_wc_600": bw[i]})
            print(f"Fold {fold}: segunda tanda incluida={len(h2_in)}, peso={WEIGHTS[fold]}", flush=True)
    table = pd.DataFrame(predictions).sort_values(["fold", "intervencion_id"]).reset_index(drop=True)
    specs = [("ancla_c_89", "pred_c_ancla89"), ("c_primera_300", "pred_c_primera300"), ("c_mas_600", "pred_c_600"), ("wc_mas_600", "pred_wc_600")]
    metrics_by = {name: metricas_completas(table.rename(columns={column: "pred"}), "pred") for name, column in specs}
    checks_wc, folds_wc, accept_wc = multicriteria(metrics_by["c_mas_600"], metrics_by["wc_mas_600"])
    selected = "wc_mas_600" if accept_wc else "c_mas_600"; selected_col = "pred_wc_600" if accept_wc else "pred_c_600"
    checks_anchor, folds_anchor, accept_anchor = multicriteria(metrics_by["ancla_c_89"], metrics_by[selected])
    table["pred_seleccionada"] = table[selected_col]; table["acierto_seleccionada"] = table.pred_seleccionada.eq(table.etiqueta_v3)
    metrics = {"version": out.name, **metrics_by, "comparacion_wc_vs_c600": {"controles": checks_wc, "folds_f1_hd_mejorados": folds_wc, "decision": "aceptar_wc" if accept_wc else "retener_c"}, "representacion_seleccionada": selected,
        "comparacion_seleccionada_vs_ancla_c89": {"controles": checks_anchor, "folds_f1_hd_mejorados": folds_anchor, "decision": "adoptar_reestimacion" if accept_anchor else "retener_ancla_c89"}, "modelo_de_desarrollo_resultante": selected if accept_anchor else "ancla_c_89", "evaluacion_independiente": False, "busqueda_hiperparametros": False}
    audit = pd.concat(audits, ignore_index=True); out.mkdir(parents=True)
    table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n"); audit[["fold", "origen", "intervencion_id", "meeting_id", "etiqueta_v3", "excluir_reunion", "excluir_texto", "incluido"]].to_csv(out / "inclusion_por_fold.csv", index=False, lineterminator="\n")
    table[~table.acierto_seleccionada].to_csv(out / "errores_seleccionada.csv", index=False, lineterminator="\n"); save(out / "metricas.json", metrics); save(out / "ejecucion_folds.json", executions)
    sources = {**base_sources, **ia_sources, "primera300": RAIZ / "data/evaluacion/anotacion_adicional_300_v3_cerrada_v1/referencia_300_v3.csv", "dirigida300": SECOND_PATH, "ancla89": ANCHOR89, "ancla300": ANCHOR300, "prerregistro": PREREG, "script": Path(__file__)}
    save(out / "protocolo.json", {"prerregistro": str(PREREG.relative_to(RAIZ)), "operacion": "C versus W+C con idéntico train +600, purgado por reunión/texto", "pesos_char": WEIGHTS, "fuentes_sha256": {k: sha256(v) for k, v in sources.items()}, "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "sklearn": sklearn.__version__}})
    included2 = audit[audit.origen.eq("humana300_dirigida")]
    save(out / "verificacion.json", {"ancla_c89_reproducida": True, "ancla_c_primera300_reproducida": True, "filas_validacion": len(table), "ids_validacion_unicos": table.intervencion_id.nunique(), "segunda_tanda_ids": second.intervencion_id.nunique(), "inclusion_segunda_por_fold": included2.groupby("fold").incluido.sum().astype(int).tolist(), "copias_textuales_incluidas": int((audit.incluido & audit.excluir_texto).sum()), "reuniones_validacion_incluidas": int((audit.incluido & audit.excluir_reunion).sum())})
    lines = ["# Reestimación C versus W+C con 600 humanas v3", "", "Apertura histórica de desarrollo; no evaluación independiente.", "", "| Condición | Macro-F1 | F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for key, label in [("ancla_c_89", "C+89"), ("c_primera_300", "C+89+300"), ("c_mas_600", "C+89+600"), ("wc_mas_600", "W+C+89+600")]:
        m = metrics_by[key]; d = m["por_clase"]["dovish"]; lines.append(f"| {label} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {d['f1']:.6f} | {d['recall']:.6f} | {m['por_clase']['hawkish']['f1']:.6f} | {m['por_clase']['neutral']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |")
    lines += ["", f"**C vs W+C:** {metrics['comparacion_wc_vs_c600']['decision']}.", f"**Frente al ancla:** {metrics['comparacion_seleccionada_vs_ancla_c89']['decision']}.", f"**Modelo resultante:** `{metrics['modelo_de_desarrollo_resultante']}`.", ""]
    (out / "resumen.md").write_text("\n".join(lines), encoding="utf-8")
    outputs = ["predicciones.csv", "inclusion_por_fold.csv", "errores_seleccionada.csv", "metricas.json", "ejecucion_folds.json", "protocolo.json", "verificacion.json", "resumen.md"]
    save(out / "manifest.json", {"sha256_salidas": {name: sha256(out / name) for name in outputs}}); return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--salida", type=Path, default=OUT); print(json.dumps(run(parser.parse_args().salida), ensure_ascii=False, indent=2))
