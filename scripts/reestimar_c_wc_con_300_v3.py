"""Reestimación preregistrada única de C versus W+C con 300 humanas v3."""
import argparse
import hashlib
import json
import platform
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.exceptions import ConvergenceWarning

from entrenar_tfidf_supervision_v3 import (RAIZ, ajustar_predecir, cargar_datos,
    clave_texto, metricas_completas, sha256)
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import fit_predict, multicriteria

OUT = RAIZ / "data/evaluacion/reestimacion_300_c_wc_v3_v1"
NEW_PATH = RAIZ / "data/evaluacion/anotacion_adicional_300_v3_cerrada_v1/referencia_300_v3.csv"
ANCHOR_PATH = RAIZ / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv"
PREREG_PATH = RAIZ / "docs/PROTOCOLO_REESTIMACION_300_C_WC_V3.md"
WEIGHTS = {1: 1.0, 2: 0.5, 3: 1.0, 4: 1.0, 5: 1.0}


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def load_300():
    data = pd.read_csv(NEW_PATH, dtype=str, keep_default_na=False)
    required = {"intervencion_id", "texto", "etiqueta_v3", "es_relevante_v3", "estado_revision_v3", "sha256_texto"}
    if not required <= set(data) or len(data) != 300 or not data.intervencion_id.is_unique:
        raise ValueError("Referencia humana cerrada inválida")
    if set(data.estado_revision_v3) != {"cerrado"}:
        raise ValueError("Existen filas humanas no cerradas")
    if Counter(data.etiqueta_v3) != Counter({"neutral": 237, "hawkish": 35, "dovish": 28}):
        raise ValueError("Distribución humana final inesperada")
    hashes = data.texto.map(lambda x: hashlib.sha256(x.encode()).hexdigest())
    if not hashes.equals(data.sha256_texto):
        raise ValueError("Hash de texto humano inválido")
    data["meeting_id"] = data.intervencion_id.str.rsplit(":", n=2).str[0]
    data["relevancia_v3"] = data.es_relevante_v3
    return data[["meeting_id", "texto", "etiqueta_v3", "relevancia_v3", "intervencion_id"]].copy()


def audited_extra(extra, val, fold, origin):
    result = extra.copy()
    meetings, keys = set(val.meeting_id), set(val.texto.map(clave_texto))
    result["excluir_reunion"] = result.meeting_id.isin(meetings)
    result["excluir_texto"] = result.texto.map(clave_texto).isin(keys)
    result["incluido"] = ~(result.excluir_reunion | result.excluir_texto)
    result["fold"] = fold; result["origen"] = origin
    return result


def run(out=OUT):
    out = Path(out)
    if out.exists(): raise FileExistsError("No sobrescribir reestimación única")
    base, _, base_sources = cargar_datos(); ia89, ia_sources = cargar_nuevos(); human = load_300()
    if set(human.intervencion_id) & set(base.intervencion_id):
        raise ValueError("IDs humanos ya presentes en base histórica")
    anchor = pd.read_csv(ANCHOR_PATH, dtype=str, keep_default_na=False).set_index("intervencion_id")
    predictions, audits, executions = [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy()
            val_keys = set(val.texto.map(clave_texto))
            train_base = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(val_keys)].copy()
            ai = audited_extra(ia89, val, fold, "ia89")
            hu = audited_extra(human, val, fold, "humana300")
            audits.extend([ai, hu])
            ia_in = ai[ai.incluido].copy(); hu_in = hu[hu.incluido].copy()
            prior = pd.concat([train_base, ia_in.reindex(columns=train_base.columns)], ignore_index=True)
            augmented = pd.concat([prior, hu_in.reindex(columns=train_base.columns)], ignore_index=True)
            if set(augmented.meeting_id) & set(val.meeting_id) or set(augmented.texto.map(clave_texto)) & val_keys:
                raise ValueError(f"Contaminación en fold {fold}")
            a_old, b_old, p_old, _ = ajustar_predecir(prior, val, "v3")
            fixed = anchor.loc[val.index]
            if not (np.array_equal(a_old.astype(str), fixed.pred_a_fase_c.to_numpy()) and
                    np.array_equal(b_old.astype(str), fixed.pred_b_fase_c.to_numpy()) and
                    np.array_equal(p_old.astype(str), fixed.pred_fase_c.to_numpy())):
                raise ValueError(f"No se reprodujo ancla C+89 en fold {fold}")
            ac, bc, pc, dc = ajustar_predecir(augmented, val, "v3")
            aw, bw, pw, dw = fit_predict(augmented, val, WEIGHTS[fold])
            executions.append({"fold": fold, "peso_char": WEIGHTS[fold], "n_train_base": len(train_base),
                "n_ia89_incluida": len(ia_in), "n_humana300_incluida": len(hu_in),
                "humana_por_clase": hu_in.etiqueta_v3.value_counts().to_dict(),
                "dimensiones_c": dc, "dimensiones_wc": dw})
            for i, (_, row) in enumerate(val.iterrows()):
                predictions.append({"intervencion_id": row.intervencion_id, "meeting_id": row.meeting_id,
                    "fold": fold, "etiqueta_v3": row.etiqueta_v3, "es_relevante_v3": row.relevancia_v3,
                    "pred_c_ancla_89": p_old[i], "pred_c_300": pc[i], "pred_wc_300": pw[i],
                    "pred_a_c_300": str(ac[i]), "pred_b_c_300": bc[i],
                    "pred_a_wc_300": str(aw[i]), "pred_b_wc_300": bw[i]})
            print(f"Fold {fold}: IA={len(ia_in)}, humanas={len(hu_in)}, peso_char={WEIGHTS[fold]}", flush=True)
    table = pd.DataFrame(predictions).sort_values(["fold", "intervencion_id"]).reset_index(drop=True)
    metrics_by = {name: metricas_completas(table.rename(columns={column: "pred"}), "pred") for name, column in
                  [("ancla_c_89", "pred_c_ancla_89"), ("c_mas_300", "pred_c_300"), ("wc_mas_300", "pred_wc_300")]}
    checks_wc, folds_wc, accepted_wc = multicriteria(metrics_by["c_mas_300"], metrics_by["wc_mas_300"])
    selected_name = "wc_mas_300" if accepted_wc else "c_mas_300"
    selected_column = "pred_wc_300" if accepted_wc else "pred_c_300"
    checks_anchor, folds_anchor, accepted_anchor = multicriteria(metrics_by["ancla_c_89"], metrics_by[selected_name])
    table["pred_seleccionada"] = table[selected_column]
    table["cambio_c_por_300"] = table.pred_c_ancla_89.ne(table.pred_c_300)
    table["cambio_c_vs_wc"] = table.pred_c_300.ne(table.pred_wc_300)
    table["acierto_seleccionada"] = table.pred_seleccionada.eq(table.etiqueta_v3)
    metrics = {"version": out.name, **metrics_by,
        "comparacion_wc_vs_c300": {"controles": checks_wc, "folds_f1_hd_mejorados": folds_wc,
            "decision": "aceptar_wc" if accepted_wc else "retener_c"},
        "representacion_seleccionada": selected_name,
        "comparacion_seleccionada_vs_ancla_c89": {"controles": checks_anchor,
            "folds_f1_hd_mejorados": folds_anchor,
            "decision": "adoptar_reestimacion" if accepted_anchor else "retener_ancla_c89"},
        "modelo_de_desarrollo_resultante": selected_name if accepted_anchor else "ancla_c_89",
        "cambios_prediccion_c_por_300": int(table.cambio_c_por_300.sum()),
        "diferencias_prediccion_c_vs_wc": int(table.cambio_c_vs_wc.sum()),
        "evaluacion_independiente": False, "busqueda_hiperparametros": False}
    audit = pd.concat(audits, ignore_index=True)
    out.mkdir(parents=True)
    table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n")
    audit[["fold", "origen", "intervencion_id", "meeting_id", "etiqueta_v3", "excluir_reunion",
           "excluir_texto", "incluido"]].to_csv(out / "inclusion_por_fold.csv", index=False, lineterminator="\n")
    errors = table[~table.acierto_seleccionada].copy()
    errors.to_csv(out / "errores_seleccionada.csv", index=False, lineterminator="\n")
    save_json(out / "metricas.json", metrics); save_json(out / "ejecucion_folds.json", executions)
    sources = {**base_sources, **ia_sources, "humanas300": NEW_PATH, "ancla_c89": ANCHOR_PATH,
               "prerregistro": PREREG_PATH, "script": Path(__file__)}
    save_json(out / "protocolo.json", {"prerregistro": str(PREREG_PATH.relative_to(RAIZ)),
        "operacion": "C versus W+C con idéntico train +300, purgado por reunión y texto",
        "pesos_char_congelados": WEIGHTS, "fuentes_sha256": {k: sha256(v) for k, v in sources.items()},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                       "scipy": scipy.__version__, "sklearn": sklearn.__version__}})
    save_json(out / "verificacion.json", {"ancla_c89_reproducida_exactamente": True,
        "filas_validacion": len(table), "ids_validacion_unicos": table.intervencion_id.nunique(),
        "filas_humanas": len(human), "ids_humanos_unicos": human.intervencion_id.nunique(),
        "inclusion_humana_por_fold": audit[audit.origen.eq("humana300")].groupby("fold").incluido.sum().astype(int).tolist(),
        "copias_textuales_incluidas": int((audit.incluido & audit.excluir_texto).sum()),
        "reuniones_validacion_incluidas": int((audit.incluido & audit.excluir_reunion).sum()),
        "humanas_fuera_validacion": True})
    lines = ["# Reestimación única C versus W+C con 300 humanas v3", "",
        "Las 300 referencias entraron solo al train permitido, con exclusión por reunión y texto. Esta apertura histórica no es evaluación independiente.", "",
        "| Condición | Macro-F1 | F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for key, label in [("ancla_c_89", "C+89 (ancla)"), ("c_mas_300", "C+89+300"), ("wc_mas_300", "W+C+89+300")]:
        m = metrics_by[key]; d = m["por_clase"]["dovish"]
        lines.append(f"| {label} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {d['f1']:.6f} | {d['recall']:.6f} | {m['por_clase']['hawkish']['f1']:.6f} | {m['por_clase']['neutral']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |")
    lines += ["", f"**C vs W+C:** {metrics['comparacion_wc_vs_c300']['decision']}.",
              f"**Frente al ancla:** {metrics['comparacion_seleccionada_vs_ancla_c89']['decision']}.",
              f"**Modelo de desarrollo resultante:** `{metrics['modelo_de_desarrollo_resultante']}`.", ""]
    (out / "resumen.md").write_text("\n".join(lines), encoding="utf-8")
    outputs = ["predicciones.csv", "inclusion_por_fold.csv", "errores_seleccionada.csv", "metricas.json",
               "ejecucion_folds.json", "protocolo.json", "verificacion.json", "resumen.md"]
    save_json(out / "manifest.json", {"sha256_salidas": {n: sha256(out/n) for n in outputs}})
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--salida", type=Path, default=OUT)
    print(json.dumps(run(parser.parse_args().salida), ensure_ascii=False, indent=2))
