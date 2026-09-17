"""Ronda de adaptación no supervisada: ajusta TF-IDF con L0 sin reuniones de validación."""
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from entrenar_tfidf_supervision_v3 import RAIZ, PARAMETROS_A, PARAMETROS_B, PARAMETROS_LR, cargar_datos, clave_texto, metricas_completas, sha256
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import vectorizer, multicriteria

OUT = RAIZ / "data/evaluacion/adaptacion_dominio_bcch_v3_v1"


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def fit_adapted(train, val, domain_texts, weight):
    va = vectorizer(PARAMETROS_A, weight); va.fit(domain_texts)
    ma = LogisticRegression(**PARAMETROS_LR).fit(va.transform(train.texto), train.relevancia_v3.astype(int))
    pa = ma.predict(va.transform(val.texto))
    relevant = train.relevancia_v3.eq("1")
    vb = vectorizer(PARAMETROS_B, weight); vb.fit(domain_texts)
    mb = LogisticRegression(**PARAMETROS_LR).fit(vb.transform(train.loc[relevant, "texto"]), train.loc[relevant, "etiqueta_v3"])
    pb = mb.predict(vb.transform(val.texto))
    final = np.where(pa == 0, "neutral", pb)
    dims = {"n_dominio_sin_etiquetas": len(domain_texts),
            "features_a": int(sum(len(t.vocabulary_) for _, t in va.transformer_list)),
            "features_b": int(sum(len(t.vocabulary_) for _, t in vb.transformer_list)),
            "iteraciones_a": ma.n_iter_.tolist(), "iteraciones_b": mb.n_iter_.tolist()}
    return pa, pb, final, dims


def run(out=OUT):
    out = Path(out)
    if out.exists():
        raise FileExistsError("No sobrescribir adaptación")
    base, _, base_sources = cargar_datos(); ia89, ia_sources = cargar_nuevos()
    corpus_path = RAIZ / "data/L0/corpus.csv"
    corpus = pd.read_csv(corpus_path, dtype=str, keep_default_na=False)
    wc_path = RAIZ / "data/evaluacion/palabras_caracteres_tfidf_v3_v1/predicciones.csv"
    selection_path = RAIZ / "data/evaluacion/palabras_caracteres_tfidf_v3_v1/seleccion_interna.json"
    wc = pd.read_csv(wc_path, dtype=str, keep_default_na=False).set_index("intervencion_id")
    weights = {int(x["outer_fold"]): float(x["peso_seleccionado"])
               for x in json.loads(selection_path.read_text(encoding="utf-8"))}
    predictions, runs = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        for fold in range(1, 6):
            val = base[base.fold_validacion.eq(fold)].copy()
            val_keys, val_meetings = set(val.texto.map(clave_texto)), set(val.meeting_id)
            train = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(val_keys)].copy()
            ia = ia89[~ia89.meeting_id.isin(val_meetings) & ~ia89.texto.map(clave_texto).isin(val_keys)].copy()
            train = pd.concat([train, ia.reindex(columns=train.columns)], ignore_index=True)
            domain = corpus[~corpus.meeting_id.isin(val_meetings)].copy()
            domain = domain[~domain.texto.map(clave_texto).isin(val_keys)].copy()
            if set(domain.meeting_id) & val_meetings or set(domain.texto.map(clave_texto)) & val_keys:
                raise ValueError("Contaminación textual o de reunión en adaptación")
            weight = weights[fold]
            pa, pb, pred, dims = fit_adapted(train, val, domain.texto, weight)
            anchor = wc.loc[val.index]
            runs.append({"fold": fold, "peso_char_reutilizado": weight,
                         "reuniones_dominio": int(domain.meeting_id.nunique()),
                         "ids_train_supervisado": len(train), **dims})
            for i, (_, row) in enumerate(val.iterrows()):
                predictions.append({"intervencion_id": row.intervencion_id, "meeting_id": row.meeting_id,
                    "fold": fold, "etiqueta_v3": row.etiqueta_v3, "es_relevante_v3": row.relevancia_v3,
                    "pred_c": anchor.iloc[i].pred_c, "pred_wc": anchor.iloc[i].pred_word_char,
                    "pred_adaptado": pred[i], "pred_a_adaptado": str(pa[i]), "pred_b_adaptado": pb[i]})
            print(f"Fold {fold}: dominio={len(domain)} textos/{domain.meeting_id.nunique()} reuniones", flush=True)
    table = pd.DataFrame(predictions).sort_values(["fold", "intervencion_id"])
    metrics = {col: metricas_completas(table.rename(columns={col: "pred"}), "pred")
               for col in ["pred_c", "pred_wc", "pred_adaptado"]}
    checks, improved, accepted = multicriteria(metrics["pred_c"], metrics["pred_adaptado"])
    table["cambio_vs_c"] = table.pred_c.ne(table.pred_adaptado)
    result = {"version": out.name, "candidato_c": metrics["pred_c"], "palabra_caracter": metrics["pred_wc"],
              "adaptado_l0": metrics["pred_adaptado"],
              "delta_adaptado_menos_c": {k: metrics["pred_adaptado"][k]-metrics["pred_c"][k]
                  for k in ["accuracy", "macro_f1", "f1_hd", "media_folds_f1_hd", "errores"]},
              "folds_f1_hd_mejorados": improved, "controles_multicriterio": checks,
              "decision": "aceptar" if accepted else "rechazar", "evaluacion_independiente": False,
              "etiquetas_dominio_usadas": False, "reuniones_validacion_en_dominio": 0}
    out.mkdir(parents=True)
    table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n")
    save_json(out / "metricas.json", result); save_json(out / "ejecucion_folds.json", runs)
    sources = {**base_sources, **ia_sources, "corpus_dominio": corpus_path, "predicciones_wc": wc_path,
               "seleccion_interna_wc": selection_path, "script": Path(__file__)}
    save_json(out / "protocolo.json", {"adaptacion": "vocabulario e IDF TF-IDF ajustados sin etiquetas sobre L0",
        "purga": "se excluye toda reunión y copia textual de outer validation antes de ajustar representación",
        "clasificadores": "ajustados solo con train supervisado permitido", "seleccion_nueva": False,
        "fuentes_sha256": {k: sha256(v) for k, v in sources.items()}})
    summary = "# Adaptación no supervisada al dominio BCCh\n\nVocabulario e IDF se ajustan con textos L0 sin etiquetas y excluyendo íntegramente las reuniones de validación externa.\n\n"
    summary += "| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for name,key in [("C","pred_c"),("W+C","pred_wc"),("Adaptado L0","pred_adaptado")]:
        m=metrics[key]; pc=m["por_clase"]
        summary += f"| {name} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {pc['dovish']['f1']:.6f} | {pc['dovish']['recall']:.6f} | {pc['hawkish']['f1']:.6f} | {pc['neutral']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    summary += "\n| Fold | F1-HD C | F1-HD adaptado | Delta |\n|---:|---:|---:|---:|\n"
    for i in range(1,6):
        a,b=metrics["pred_c"]["por_fold"][str(i)]["f1_hd"],metrics["pred_adaptado"]["por_fold"][str(i)]["f1_hd"]
        summary += f"| {i} | {a:.6f} | {b:.6f} | {b-a:+.6f} |\n"
    summary += f"\n**Decisión multicriterio: {'ACEPTAR' if accepted else 'RECHAZAR'}.** `{json.dumps(checks, ensure_ascii=False)}`\n"
    (out / "resumen.md").write_text(summary, encoding="utf-8")
    save_json(out / "manifest.json", {"sha256_salidas": {p.name: sha256(p) for p in out.iterdir() if p.name != "manifest.json"}})
    return result


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
