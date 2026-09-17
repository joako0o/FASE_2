"""Ronda jerárquica: relevancia -> presencia de dirección -> signo H/D."""
import json
from collections import Counter
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from entrenar_tfidf_supervision_v3 import RAIZ, PARAMETROS_A, PARAMETROS_B, PARAMETROS_LR, cargar_datos, clave_texto, metricas_completas, sha256
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import vectorizer, multicriteria

OUT = RAIZ / "data/evaluacion/jerarquia_direccional_v3_v1"


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def fit_binary(train_text, train_y, val_text, word_params, weight):
    vec = vectorizer(word_params, weight)
    model = LogisticRegression(**PARAMETROS_LR).fit(vec.fit_transform(train_text), train_y)
    pred = model.predict(vec.transform(val_text))
    return pred, {"features": int(sum(len(t.vocabulary_) for _, t in vec.transformer_list)),
                  "iteraciones": model.n_iter_.tolist(), "n_train": len(train_y),
                  "clases_train": pd.Series(train_y).value_counts().to_dict()}


def fit_hierarchy(train, val, weight):
    pred_rel, dim_a = fit_binary(train.texto, train.relevancia_v3.astype(int), val.texto, PARAMETROS_A, weight)
    relevant = train.relevancia_v3.eq("1")
    direction_y = train.loc[relevant, "etiqueta_v3"].isin(["hawkish", "dovish"]).astype(int)
    pred_dir, dim_dir = fit_binary(train.loc[relevant, "texto"], direction_y, val.texto, PARAMETROS_B, weight)
    directional = relevant & train.etiqueta_v3.isin(["hawkish", "dovish"])
    pred_sign, dim_sign = fit_binary(train.loc[directional, "texto"], train.loc[directional, "etiqueta_v3"],
                                     val.texto, PARAMETROS_B, weight)
    final = np.where((pred_rel == 1) & (pred_dir == 1), pred_sign, "neutral")
    return pred_rel, pred_dir, pred_sign, final, {"relevancia": dim_a, "direccion": dim_dir, "signo": dim_sign}


def run(out=OUT):
    out = Path(out)
    if out.exists():
        raise FileExistsError("No sobrescribir ronda jerárquica")
    base, _, base_sources = cargar_datos(); ia89, ia_sources = cargar_nuevos()
    wc_path = RAIZ / "data/evaluacion/palabras_caracteres_tfidf_v3_v1/predicciones.csv"
    selection_path = RAIZ / "data/evaluacion/palabras_caracteres_tfidf_v3_v1/seleccion_interna.json"
    wc = pd.read_csv(wc_path, dtype=str, keep_default_na=False).set_index("intervencion_id")
    selected = {int(x["outer_fold"]): float(x["peso_seleccionado"])
                for x in json.loads(selection_path.read_text(encoding="utf-8"))}
    predictions, executions = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy()
            keys, meetings = set(val.texto.map(clave_texto)), set(val.meeting_id)
            train = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(keys)].copy()
            ia = ia89[~ia89.meeting_id.isin(meetings) & ~ia89.texto.map(clave_texto).isin(keys)].copy()
            train = pd.concat([train, ia.reindex(columns=train.columns)], ignore_index=True)
            weight = selected[fold]
            pa, pdirection, psign, final, dims = fit_hierarchy(train, val, weight)
            anchor = wc.loc[val.index]
            if not np.array_equal(pa.astype(str), anchor.pred_a_word_char.to_numpy()):
                raise ValueError(f"No se reprodujo puerta A palabra+carácter en fold {fold}")
            executions.append({"fold": fold, "char_weight_reutilizado": weight, "n_ia89": len(ia), **dims})
            for i, (_, row) in enumerate(val.iterrows()):
                predictions.append({"intervencion_id": row.intervencion_id, "meeting_id": row.meeting_id,
                    "fold": fold, "etiqueta_v3": row.etiqueta_v3, "es_relevante_v3": row.relevancia_v3,
                    "pred_c": anchor.iloc[i].pred_c, "pred_multiclase_wc": anchor.iloc[i].pred_word_char,
                    "pred_relevancia": str(pa[i]), "pred_presencia_direccion": str(pdirection[i]),
                    "pred_signo": psign[i], "pred_jerarquia": final[i]})
            print(f"Fold {fold}: jerarquía entrenada; peso={weight}", flush=True)
    table = pd.DataFrame(predictions).sort_values(["fold", "intervencion_id"])
    metrics_by = {}
    for col in ["pred_c", "pred_multiclase_wc", "pred_jerarquia"]:
        metrics_by[col] = metricas_completas(table.rename(columns={col: "pred"}), "pred")
    checks, improved, accepted = multicriteria(metrics_by["pred_c"], metrics_by["pred_jerarquia"])
    table["cambio_vs_c"] = table.pred_c.ne(table.pred_jerarquia)
    table["cambio_arquitectura"] = table.pred_multiclase_wc.ne(table.pred_jerarquia)
    table["efecto_vs_c"] = np.select(
        [table.pred_c.eq(table.etiqueta_v3) & table.pred_jerarquia.ne(table.etiqueta_v3),
         table.pred_c.ne(table.etiqueta_v3) & table.pred_jerarquia.eq(table.etiqueta_v3)],
        ["acierto_a_error", "error_a_acierto"], default="sin_cambio")
    metrics = {"version": out.name, "candidato_c": metrics_by["pred_c"],
               "multiclase_palabra_caracter": metrics_by["pred_multiclase_wc"],
               "jerarquia": metrics_by["pred_jerarquia"],
               "delta_jerarquia_menos_c": {k: metrics_by["pred_jerarquia"][k]-metrics_by["pred_c"][k]
                   for k in ["accuracy", "macro_f1", "f1_hd", "media_folds_f1_hd", "errores"]},
               "delta_jerarquia_menos_multiclase": {k: metrics_by["pred_jerarquia"][k]-metrics_by["pred_multiclase_wc"][k]
                   for k in ["accuracy", "macro_f1", "f1_hd", "media_folds_f1_hd", "errores"]},
               "folds_f1_hd_mejorados_vs_c": improved, "controles_multicriterio_vs_c": checks,
               "decision": "aceptar" if accepted else "rechazar", "efecto_vs_c": dict(Counter(table.efecto_vs_c)),
               "evaluacion_independiente": False, "hiperparametros_nuevos": False}
    out.mkdir(parents=True)
    table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n")
    save_json(out / "metricas.json", metrics); save_json(out / "ejecucion_folds.json", executions)
    sources = {**base_sources, **ia_sources, "predicciones_word_char": wc_path,
               "seleccion_interna_word_char": selection_path, "script": Path(__file__)}
    save_json(out / "protocolo.json", {"arquitectura": "A relevancia; B presencia H/D; C signo H/D",
        "entrenamiento": "todas las puertas se ajustan solo dentro de cada outer train",
        "representacion": "misma palabra+char y pesos elegidos previamente por CV interna",
        "seleccion_adicional": False, "fuentes_sha256": {k: sha256(v) for k, v in sources.items()}})
    summary = "# Ronda jerárquica direccional\n\nTres etapas: relevancia, presencia de dirección y signo H/D. Se reutiliza sin cambios la representación y el peso seleccionados internamente en la ronda anterior.\n\n"
    summary += "| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for name, key in [("C", "pred_c"), ("Multiclase W+C", "pred_multiclase_wc"), ("Jerarquía", "pred_jerarquia")]:
        m=metrics_by[key]; pc=m["por_clase"]
        summary += f"| {name} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {pc['dovish']['f1']:.6f} | {pc['dovish']['recall']:.6f} | {pc['hawkish']['f1']:.6f} | {pc['neutral']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    summary += "\n| Fold | F1-HD C | F1-HD jerarquía | Delta |\n|---:|---:|---:|---:|\n"
    for i in range(1,6):
        a,b=metrics_by["pred_c"]["por_fold"][str(i)]["f1_hd"],metrics_by["pred_jerarquia"]["por_fold"][str(i)]["f1_hd"]
        summary += f"| {i} | {a:.6f} | {b:.6f} | {b-a:+.6f} |\n"
    summary += f"\n**Decisión multicriterio vs C: {'ACEPTAR' if accepted else 'RECHAZAR'}.** `{json.dumps(checks, ensure_ascii=False)}`\n"
    (out / "resumen.md").write_text(summary, encoding="utf-8")
    save_json(out / "manifest.json", {"sha256_salidas": {p.name: sha256(p) for p in out.iterdir() if p.name != "manifest.json"}})
    return metrics


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
