"""Ronda lineal: palabras + caracteres con selección interna agrupada por reunión."""
import hashlib
import json
import platform
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

from entrenar_tfidf_supervision_v3 import (
    RAIZ, PARAMETROS_A, PARAMETROS_B, PARAMETROS_LR, cargar_datos,
    clave_texto, ajustar_predecir, medir, metricas_completas, sha256)
from evaluar_ampliacion_ia89_v3 import cargar_nuevos

OUT = RAIZ / "data/evaluacion/palabras_caracteres_tfidf_v3_v1"
CHAR_WEIGHTS = (0.5, 1.0)
CHAR_PARAMS = {"analyzer": "char_wb", "ngram_range": (3, 5), "min_df": 3,
               "max_df": 0.98, "sublinear_tf": True, "strip_accents": "unicode",
               "lowercase": True, "max_features": 120000}


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def vectorizer(word_params, char_weight):
    return FeatureUnion(
        [("word", TfidfVectorizer(**word_params)), ("char", TfidfVectorizer(**CHAR_PARAMS))],
        transformer_weights={"word": 1.0, "char": char_weight}, n_jobs=1)


def fit_predict(train, val, char_weight):
    va = vectorizer(PARAMETROS_A, char_weight)
    ma = LogisticRegression(**PARAMETROS_LR).fit(
        va.fit_transform(train.texto), train.relevancia_v3.astype(int))
    pa = ma.predict(va.transform(val.texto))
    relevant = train.relevancia_v3.eq("1")
    vb = vectorizer(PARAMETROS_B, char_weight)
    mb = LogisticRegression(**PARAMETROS_LR).fit(
        vb.fit_transform(train.loc[relevant, "texto"]), train.loc[relevant, "etiqueta_v3"])
    pb = mb.predict(vb.transform(val.texto))
    final = np.where(pa == 0, "neutral", pb)
    dimensions = {"n_train": len(train), "n_relevante": int(relevant.sum()),
                  "features_a": int(sum(len(t.vocabulary_) for _, t in va.transformer_list)),
                  "features_b": int(sum(len(t.vocabulary_) for _, t in vb.transformer_list)),
                  "iteraciones_a": ma.n_iter_.tolist(), "iteraciones_b": mb.n_iter_.tolist()}
    return pa, pb, final, dimensions


def inner_select(train):
    groups = train.meeting_id.astype(str).to_numpy()
    splitter = GroupKFold(n_splits=3)
    audit, scores = [], []
    for weight in CHAR_WEIGHTS:
        fold_metrics, true_all, pred_all = [], [], []
        for inner_fold, (ti, vi) in enumerate(splitter.split(train, groups=groups), 1):
            tr, val = train.iloc[ti].copy(), train.iloc[vi].copy()
            val_keys = set(val.texto.map(clave_texto))
            tr = tr[~tr.texto.map(clave_texto).isin(val_keys)].copy()
            if set(tr.meeting_id) & set(val.meeting_id) or set(tr.texto.map(clave_texto)) & val_keys:
                raise ValueError("Contaminación en CV interna")
            _, _, pred, _ = fit_predict(tr, val, weight)
            m = medir(val.etiqueta_v3.tolist(), pred.tolist())
            fold_metrics.append(m); true_all.extend(val.etiqueta_v3); pred_all.extend(pred)
            audit.append({"char_weight": weight, "inner_fold": inner_fold,
                          "n_train": len(tr), "n_validacion": len(val),
                          "reuniones_train": tr.meeting_id.nunique(),
                          "reuniones_validacion": val.meeting_id.nunique(), "metricas": m})
        aggregate = medir(true_all, pred_all)
        mean_hd = sum(m["f1_hd"] for m in fold_metrics) / 3
        mean_macro = sum(m["macro_f1"] for m in fold_metrics) / 3
        score = (mean_hd, aggregate["por_clase"]["dovish"]["recall"], mean_macro, -weight)
        scores.append((score, weight, {"media_folds_f1_hd": mean_hd,
                                      "media_folds_macro_f1": mean_macro,
                                      "agregadas": aggregate}))
    selected = max(scores, key=lambda x: x[0])
    return selected[1], {"candidatos": {str(w): m for _, w, m in scores},
                         "peso_seleccionado": selected[1], "detalle_folds": audit,
                         "regla": "max media F1-HD; desempate recall D, macro-F1 y menor peso"}


def multicriteria(base, candidate):
    better = [candidate["por_fold"][str(i)]["f1_hd"] > base["por_fold"][str(i)]["f1_hd"] for i in range(1, 6)]
    checks = {"media_f1_hd_mejora": candidate["media_folds_f1_hd"] > base["media_folds_f1_hd"],
              "al_menos_3_folds": sum(better) >= 3,
              "f1_d_no_baja": candidate["por_clase"]["dovish"]["f1"] >= base["por_clase"]["dovish"]["f1"],
              "recall_d_no_baja": candidate["por_clase"]["dovish"]["recall"] >= base["por_clase"]["dovish"]["recall"],
              "inversiones_no_aumentan": candidate["h_d_cruzados"] <= base["h_d_cruzados"],
              "omisiones_no_aumentan": candidate["direccion_a_neutral"] <= base["direccion_a_neutral"],
              "macro_f1_no_baja": candidate["macro_f1"] >= base["macro_f1"],
              "f1_n_no_baja": candidate["por_clase"]["neutral"]["f1"] >= base["por_clase"]["neutral"]["f1"]}
    return checks, sum(better), all(checks.values())


def run(out=OUT):
    out = Path(out)
    if out.exists():
        raise FileExistsError("No sobrescribir ronda")
    base, _, base_sources = cargar_datos(); ia89, ia_sources = cargar_nuevos()
    anchor_path = RAIZ / "data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv"
    anchor = pd.read_csv(anchor_path, dtype=str, keep_default_na=False).set_index("intervencion_id")
    predictions, selections, executions = [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy()
            keys, meetings = set(val.texto.map(clave_texto)), set(val.meeting_id)
            train = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(keys)].copy()
            ia = ia89[~ia89.meeting_id.isin(meetings) & ~ia89.texto.map(clave_texto).isin(keys)].copy()
            train = pd.concat([train, ia.reindex(columns=train.columns)], ignore_index=True)
            a0, b0, p0, _ = ajustar_predecir(train, val, "v3")
            fixed = anchor.loc[val.index]
            if not (np.array_equal(a0.astype(str), fixed.pred_a_fase_c.to_numpy()) and
                    np.array_equal(b0.astype(str), fixed.pred_b_fase_c.to_numpy()) and
                    np.array_equal(p0.astype(str), fixed.pred_fase_c.to_numpy())):
                raise ValueError(f"No se reprodujo candidato C en fold {fold}")
            weight, selection = inner_select(train)
            a1, b1, p1, dims = fit_predict(train, val, weight)
            selection["outer_fold"] = fold; selections.append(selection)
            executions.append({"outer_fold": fold, "char_weight": weight, "n_ia89": len(ia), **dims})
            for i, (_, row) in enumerate(val.iterrows()):
                predictions.append({"intervencion_id": row.intervencion_id, "meeting_id": row.meeting_id,
                    "fold": fold, "etiqueta_v3": row.etiqueta_v3, "es_relevante_v3": row.relevancia_v3,
                    "pred_c": p0[i], "pred_word_char": p1[i], "pred_a_c": str(a0[i]),
                    "pred_a_word_char": str(a1[i]), "pred_b_c": b0[i], "pred_b_word_char": b1[i]})
            print(f"Fold {fold}: peso interno={weight}; train={len(train)}", flush=True)
    table = pd.DataFrame(predictions).sort_values(["fold", "intervencion_id"])
    bmet = metricas_completas(table.rename(columns={"pred_c": "pred"}), "pred")
    cmet = metricas_completas(table.rename(columns={"pred_word_char": "pred"}), "pred")
    checks, improved, accepted = multicriteria(bmet, cmet)
    table["cambio"] = table.pred_c.ne(table.pred_word_char)
    table["efecto"] = np.select(
        [table.pred_c.eq(table.etiqueta_v3) & table.pred_word_char.ne(table.etiqueta_v3),
         table.pred_c.ne(table.etiqueta_v3) & table.pred_word_char.eq(table.etiqueta_v3)],
        ["acierto_a_error", "error_a_acierto"], default="sin_cambio")
    metrics = {"version": out.name, "candidato_c": bmet, "palabras_caracteres": cmet,
               "delta": {k: cmet[k]-bmet[k] for k in ["accuracy", "macro_f1", "f1_hd", "media_folds_f1_hd", "errores"]},
               "folds_f1_hd_mejorados": improved, "controles_multicriterio": checks,
               "decision": "aceptar" if accepted else "rechazar", "cambios_prediccion": int(table.cambio.sum()),
               "evaluacion_independiente": False, "seleccion_externa_hiperparametros": False}
    out.mkdir(parents=True)
    table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n")
    save_json(out / "metricas.json", metrics); save_json(out / "seleccion_interna.json", selections)
    save_json(out / "ejecucion_folds.json", executions)
    sources = {**base_sources, **ia_sources, "ancla_c": anchor_path, "script": Path(__file__)}
    save_json(out / "protocolo.json", {"familia": "TF-IDF palabra + char_wb con regresión logística",
        "pesos_char_prefijados": CHAR_WEIGHTS, "parametros_char": CHAR_PARAMS,
        "seleccion": "CV interna GroupKFold(3) por meeting_id en cada outer train",
        "fuentes_sha256": {k: sha256(v) for k, v in sources.items()},
        "versiones": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                       "scipy": scipy.__version__, "sklearn": sklearn.__version__}})
    summary = "# Ronda lineal — palabras + caracteres\n\nPesos de caracteres elegidos solo mediante CV interna agrupada por reunión. Evaluación de desarrollo abierta, no test final.\n\n"
    summary += "| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for name, m in [("C", bmet), ("Palabra+carácter", cmet)]:
        pc=m["por_clase"]; summary += f"| {name} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {pc['dovish']['f1']:.6f} | {pc['dovish']['recall']:.6f} | {pc['hawkish']['f1']:.6f} | {pc['neutral']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    summary += "\n| Fold | F1-HD C | F1-HD palabra+carácter | Delta | Peso char interno |\n|---:|---:|---:|---:|---:|\n"
    for i in range(1,6):
        a,b=bmet["por_fold"][str(i)]["f1_hd"],cmet["por_fold"][str(i)]["f1_hd"]
        summary += f"| {i} | {a:.6f} | {b:.6f} | {b-a:+.6f} | {selections[i-1]['peso_seleccionado']} |\n"
    summary += f"\n**Decisión multicriterio: {'ACEPTAR' if accepted else 'RECHAZAR'}.** Controles: `{json.dumps(checks, ensure_ascii=False)}`.\n"
    (out / "resumen.md").write_text(summary, encoding="utf-8")
    save_json(out / "manifest.json", {"sha256_salidas": {p.name: sha256(p) for p in out.iterdir() if p.name != "manifest.json"}})
    return metrics


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
