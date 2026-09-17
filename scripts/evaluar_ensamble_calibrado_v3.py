"""Ejecuta el ensamble C + W+C preregistrado con calibración solo interna."""
import json
from pathlib import Path
import re
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

from entrenar_tfidf_supervision_v3 import (
    RAIZ, PARAMETROS_A, PARAMETROS_B, PARAMETROS_LR, cargar_datos,
    clave_texto, medir, metricas_completas, sha256)
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import vectorizer

OUT = RAIZ / "data/evaluacion/ensamble_calibrado_v3_v1"
CLASSES = np.array(["hawkish", "dovish", "neutral"])
CHAR_WEIGHTS = (0.5, 1.0)
POLICIES = {
    "blend_50": {"alpha": 0.50, "d_mult": 1.00, "margin": 0.00, "maxsent": False},
    "blend_50_d115": {"alpha": 0.50, "d_mult": 1.15, "margin": 0.00, "maxsent": False},
    "blend_75wc_d115": {"alpha": 0.75, "d_mult": 1.15, "margin": 0.00, "maxsent": False},
    "blend_75wc_d115_margin05": {"alpha": 0.75, "d_mult": 1.15, "margin": 0.05, "maxsent": False},
    "blend_50_maxsent_d115": {"alpha": 0.50, "d_mult": 1.15, "margin": 0.00, "maxsent": True},
}


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def align(proba, model_classes):
    out = np.zeros((len(proba), 3))
    for j, cls in enumerate(model_classes):
        out[:, int(np.where(CLASSES == str(cls))[0][0])] = proba[:, j]
    return out


def gated(p_rel, p_class):
    out = p_class.copy()
    irrelevant = p_rel < 0.5
    out[irrelevant] = np.array([0.0, 0.0, 1.0])
    return out


def fit_component(train, texts, vec_a, vec_b):
    xa = vec_a.fit_transform(train.texto)
    ma = LogisticRegression(**PARAMETROS_LR).fit(xa, train.relevancia_v3.astype(int))
    relevant = train.relevancia_v3.eq("1")
    xb = vec_b.fit_transform(train.loc[relevant, "texto"])
    mb = LogisticRegression(**PARAMETROS_LR).fit(xb, train.loc[relevant, "etiqueta_v3"])
    fitted = (vec_a, ma, vec_b, mb)
    return predict_component(fitted, texts), fitted


def predict_component(fitted, texts):
    va, ma, vb, mb = fitted
    p_rel = ma.predict_proba(va.transform(texts))[:, list(ma.classes_).index(1)]
    p_class = align(mb.predict_proba(vb.transform(texts)), mb.classes_)
    return gated(p_rel, p_class)


def split_sentences(text):
    parts = [x.strip() for x in re.split(r"(?<=[.!?;])\s+|\n+", str(text)) if x.strip()]
    return parts or [str(text)]


def max_sentence_component(fitted, texts, full_prob):
    sentences, owners = [], []
    for owner, text in enumerate(texts):
        for sentence in split_sentences(text):
            sentences.append(sentence); owners.append(owner)
    sentence_prob = predict_component(fitted, pd.Series(sentences))
    maxima = np.zeros_like(full_prob)
    for owner, prob in zip(owners, sentence_prob):
        maxima[owner] = np.maximum(maxima[owner], prob)
    maxima /= maxima.sum(axis=1, keepdims=True)
    combined = 0.75 * full_prob + 0.25 * maxima
    return combined / combined.sum(axis=1, keepdims=True)


def labels(prob):
    return CLASSES[np.argmax(prob, axis=1)]


def apply_policy(name, p_c, p_wc, p_max):
    cfg = POLICIES[name]; component = p_max if cfg["maxsent"] else p_wc
    prob = (1.0 - cfg["alpha"]) * p_c + cfg["alpha"] * component
    prob[:, 1] *= cfg["d_mult"]
    prob /= prob.sum(axis=1, keepdims=True)
    pred = labels(prob)
    if cfg["margin"]:
        low_margin = np.abs(prob[:, 0] - prob[:, 1]) < cfg["margin"]
        pred = np.where(low_margin & np.isin(pred, ["hawkish", "dovish"]), "neutral", pred)
    return pred, prob


def grouped_metrics(table, pred_col, n_folds):
    result = medir(table.etiqueta_v3.tolist(), table[pred_col].tolist())
    result["por_fold"] = {str(i): medir(table.loc[table.fold.eq(i), "etiqueta_v3"].tolist(),
                                            table.loc[table.fold.eq(i), pred_col].tolist())
                           for i in range(1, n_folds + 1)}
    result["media_folds_f1_hd"] = sum(x["f1_hd"] for x in result["por_fold"].values()) / n_folds
    result["media_folds_macro_f1"] = sum(x["macro_f1"] for x in result["por_fold"].values()) / n_folds
    return result


def controls(base, candidate, n_folds):
    improved = sum(candidate["por_fold"][str(i)]["f1_hd"] > base["por_fold"][str(i)]["f1_hd"]
                   for i in range(1, n_folds + 1))
    checks = {"media_f1_hd_mejora": candidate["media_folds_f1_hd"] > base["media_folds_f1_hd"],
              "mayoria_folds": improved >= (n_folds // 2 + 1),
              "f1_d_no_baja": candidate["por_clase"]["dovish"]["f1"] >= base["por_clase"]["dovish"]["f1"],
              "recall_d_no_baja": candidate["por_clase"]["dovish"]["recall"] >= base["por_clase"]["dovish"]["recall"],
              "inversiones_no_aumentan": candidate["h_d_cruzados"] <= base["h_d_cruzados"],
              "omisiones_no_aumentan": candidate["direccion_a_neutral"] <= base["direccion_a_neutral"],
              "macro_f1_no_baja": candidate["macro_f1"] >= base["macro_f1"],
              "f1_n_no_baja": candidate["por_clase"]["neutral"]["f1"] >= base["por_clase"]["neutral"]["f1"]}
    return checks, improved


def internal_splits(core):
    splitter = GroupKFold(n_splits=3)
    result = []
    for fold, (ti, vi) in enumerate(splitter.split(core, groups=core.meeting_id), 1):
        train, val = core.iloc[ti].copy(), core.iloc[vi].copy()
        keys = set(val.texto.map(clave_texto)); train = train[~train.texto.map(clave_texto).isin(keys)]
        if set(train.meeting_id) & set(val.meeting_id) or set(train.texto.map(clave_texto)) & keys:
            raise ValueError("Contaminación interna")
        result.append((fold, train, val))
    return result


def select_char_weight(splits):
    candidates = {}
    for weight in CHAR_WEIGHTS:
        rows = []
        for fold, train, val in splits:
            prob, _ = fit_component(train, val.texto, vectorizer(PARAMETROS_A, weight), vectorizer(PARAMETROS_B, weight))
            rows.extend({"fold": fold, "etiqueta_v3": true, "pred": pred}
                        for true, pred in zip(val.etiqueta_v3, labels(prob)))
        table = pd.DataFrame(rows); m = grouped_metrics(table, "pred", 3)
        candidates[str(weight)] = m
    chosen = max(CHAR_WEIGHTS, key=lambda w: (candidates[str(w)]["media_folds_f1_hd"],
        candidates[str(w)]["por_clase"]["dovish"]["recall"], candidates[str(w)]["macro_f1"], -w))
    return chosen, candidates


def select_policy(splits, weight):
    rows = []
    for fold, train, val in splits:
        p_c, _ = fit_component(train, val.texto, TfidfVectorizer(**PARAMETROS_A), TfidfVectorizer(**PARAMETROS_B))
        p_wc, fitted_wc = fit_component(train, val.texto, vectorizer(PARAMETROS_A, weight), vectorizer(PARAMETROS_B, weight))
        p_max = max_sentence_component(fitted_wc, list(val.texto), p_wc)
        base_pred = labels(p_c)
        for i, true in enumerate(val.etiqueta_v3):
            row = {"fold": fold, "etiqueta_v3": true, "pred_c": base_pred[i]}
            for name in POLICIES:
                row[name] = apply_policy(name, p_c[i:i+1].copy(), p_wc[i:i+1].copy(), p_max[i:i+1].copy())[0][0]
            rows.append(row)
    table = pd.DataFrame(rows); base = grouped_metrics(table, "pred_c", 3)
    results = {}; scored = []
    for order, name in enumerate(POLICIES):
        m = grouped_metrics(table, name, 3); checks, improved = controls(base, m, 3)
        results[name] = {"metricas": m, "controles": checks, "folds_mejorados": improved}
        score = (sum(checks.values()), m["media_folds_f1_hd"], m["por_clase"]["dovish"]["recall"], -order)
        scored.append((score, name))
    return max(scored)[1], base, results


def run(out=OUT):
    out = Path(out)
    if out.exists(): raise FileExistsError("No sobrescribir ensamble")
    base, _, base_sources = cargar_datos(); ia89, ia_sources = cargar_nuevos()
    core = base[base.fold_validacion.eq(0)].copy(); splits = internal_splits(core)
    weight, weight_results = select_char_weight(splits)
    winner, internal_base, policy_results = select_policy(splits, weight)
    print(f"Selección interna: peso char={weight}; política={winner}", flush=True)
    anchor_path = RAIZ / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv"
    anchor = pd.read_csv(anchor_path, dtype=str, keep_default_na=False).set_index("intervencion_id")
    output = []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy(); keys = set(val.texto.map(clave_texto)); meetings = set(val.meeting_id)
            train = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(keys)].copy()
            ia = ia89[~ia89.meeting_id.isin(meetings) & ~ia89.texto.map(clave_texto).isin(keys)].copy()
            train = pd.concat([train, ia.reindex(columns=train.columns)], ignore_index=True)
            p_c, _ = fit_component(train, val.texto, TfidfVectorizer(**PARAMETROS_A), TfidfVectorizer(**PARAMETROS_B))
            p_wc, fitted_wc = fit_component(train, val.texto, vectorizer(PARAMETROS_A, weight), vectorizer(PARAMETROS_B, weight))
            p_max = max_sentence_component(fitted_wc, list(val.texto), p_wc)
            pred, _ = apply_policy(winner, p_c.copy(), p_wc.copy(), p_max.copy())
            fixed = anchor.loc[val.index]
            if not np.array_equal(labels(p_c), fixed.pred_fase_c.to_numpy()):
                raise ValueError(f"No se reprodujo C probabilístico en fold {fold}")
            for i, (_, row) in enumerate(val.iterrows()):
                output.append({"intervencion_id": row.intervencion_id, "meeting_id": row.meeting_id, "fold": fold,
                    "etiqueta_v3": row.etiqueta_v3, "es_relevante_v3": row.relevancia_v3,
                    "pred_c": fixed.iloc[i].pred_fase_c, "politica_ganadora": winner, "pred_ensamble": pred[i]})
            print(f"Outer fold {fold}: {winner}", flush=True)
    table = pd.DataFrame(output).sort_values(["fold", "intervencion_id"])
    base_m = metricas_completas(table.rename(columns={"pred_c": "pred"}), "pred")
    ensemble_m = metricas_completas(table.rename(columns={"pred_ensamble": "pred"}), "pred")
    checks, improved = controls(base_m, ensemble_m, 5); accepted = all(checks.values())
    result = {"version": out.name, "peso_char_interno": weight, "seleccion_peso_char": weight_results,
              "politica_ganadora_interna": winner, "baseline_interno": internal_base,
              "seleccion_politicas": policy_results, "candidato_c": base_m, "ensamble": ensemble_m,
              "delta": {k: ensemble_m[k]-base_m[k] for k in ["accuracy", "macro_f1", "f1_hd", "media_folds_f1_hd", "errores"]},
              "folds_f1_hd_mejorados": improved, "controles_multicriterio": checks,
              "decision": "aceptar" if accepted else "rechazar", "politicas_perdedoras_abiertas_externamente": False,
              "evaluacion_independiente": False}
    out.mkdir(parents=True); table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n")
    save_json(out / "metricas.json", result)
    prereg = RAIZ / "docs/PROTOCOLO_ENSAMBLE_CALIBRADO_V3.md"
    sources = {**base_sources, **ia_sources, "ancla_c": anchor_path, "preregistro": prereg, "script": Path(__file__)}
    save_json(out / "protocolo.json", {"seleccion_solo_fold0": True, "n_seleccion": 559,
        "peso_char_fijado_antes_outer": weight, "politica_fijada_antes_outer": winner,
        "fuentes_sha256": {k: sha256(v) for k, v in sources.items()}})
    summary = "# Ensamble calibrado C + W+C\n\nSelección íntegra en 559 filas fold=0; una sola política se abrió externamente.\n\n"
    summary += f"Peso W+C elegido: `{weight}`. Política ganadora: `{winner}`.\n\n"
    summary += "| Política interna | Controles (de 8) | Media F1-HD | Recall D | F1 D |\n|---|---:|---:|---:|---:|\n"
    for name in POLICIES:
        r = policy_results[name]; m = r["metricas"]
        summary += f"| {name} | {sum(r['controles'].values())} | {m['media_folds_f1_hd']:.6f} | {m['por_clase']['dovish']['recall']:.6f} | {m['por_clase']['dovish']['f1']:.6f} |\n"
    summary += "\n| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for name, m in [("C", base_m), (winner, ensemble_m)]:
        pc=m["por_clase"]; summary += f"| {name} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {pc['dovish']['f1']:.6f} | {pc['dovish']['recall']:.6f} | {pc['hawkish']['f1']:.6f} | {pc['neutral']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    summary += f"\n**Decisión: {'ACEPTAR' if accepted else 'RECHAZAR'}.** `{json.dumps(checks, ensure_ascii=False)}`\n"
    (out / "resumen.md").write_text(summary, encoding="utf-8")
    save_json(out / "manifest.json", {"sha256_salidas": {p.name: sha256(p) for p in out.iterdir() if p.name != "manifest.json"}})
    return result


if __name__ == "__main__": print(json.dumps(run(), ensure_ascii=False, indent=2))
