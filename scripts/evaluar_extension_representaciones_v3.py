"""Ejecuta la extensión preregistrada de tokenización, NB-SVM, LSA y suavizado."""
import json
from pathlib import Path
import re
import warnings

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer, strip_accents_unicode
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import Normalizer

from entrenar_tfidf_supervision_v3 import (
    RAIZ, PARAMETROS_A, PARAMETROS_B, PARAMETROS_LR, cargar_datos,
    clave_texto, medir, metricas_completas, sha256)
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from evaluar_palabras_caracteres_v3 import vectorizer, multicriteria

OUT = RAIZ / "data/evaluacion/extension_representaciones_v3_v1"
METHODS = ("token_monetario", "nbsvm", "lsa128", "suavizado_oraciones")
CLASSES = np.array(["hawkish", "dovish", "neutral"])
TOKEN_RE = re.compile(r"uf\+?\d*(?:[.,]\d+)?%?|\d+(?:[.,]\d+)?%?|[a-záéíóúüñ]+", re.I)
PHRASES = {("politica", "monetaria"): "politica_monetaria",
           ("tasa", "instancia"): "tasa_instancia", ("tasa", "de", "instancia"): "tasa_instancia",
           ("tasa", "politica"): "tasa_politica", ("tasa", "de", "politica"): "tasa_politica",
           ("puntos", "base"): "puntos_base", ("linea", "credito", "liquidez"): "linea_credito_liquidez",
           ("linea", "de", "credito", "de", "liquidez"): "linea_credito_liquidez"}


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def monetary_tokenizer(text):
    tokens = TOKEN_RE.findall(strip_accents_unicode(text.lower()))
    extra = []
    for phrase, joined in PHRASES.items():
        n = len(phrase)
        if any(tuple(tokens[i:i+n]) == phrase for i in range(len(tokens)-n+1)):
            extra.append(joined)
    directional = {"subir", "sube", "suba", "alza", "elevar", "bajar", "baja", "rebajar", "reducir", "relajar"}
    for i, tok in enumerate(tokens):
        if tok in directional and "no" in tokens[max(0, i-3):i]:
            extra.append("neg_" + tok)
    return tokens + extra


def monetary_vectorizer(stage):
    word = dict(PARAMETROS_A if stage == "a" else PARAMETROS_B)
    word.update({"tokenizer": monetary_tokenizer, "token_pattern": None,
                 "ngram_range": (1, 2) if stage == "a" else (1, 3), "max_features": 120000})
    from sklearn.pipeline import FeatureUnion
    from evaluar_palabras_caracteres_v3 import CHAR_PARAMS
    return FeatureUnion([("word", TfidfVectorizer(**word)), ("char", TfidfVectorizer(**CHAR_PARAMS))],
                        transformer_weights={"word": 1.0, "char": 1.0}, n_jobs=1)


def align_proba(proba, model_classes):
    out = np.zeros((len(proba), 3))
    for j, c in enumerate(model_classes):
        out[:, int(np.where(CLASSES == str(c))[0][0])] = proba[:, j]
    return out


def compose(p_rel, p_class):
    out = p_class * p_rel[:, None]
    out[:, 2] += 1.0 - p_rel
    return out / out.sum(axis=1, keepdims=True)


def standard_prob(train, texts, vec_a, vec_b):
    xa = vec_a.fit_transform(train.texto)
    ma = LogisticRegression(**PARAMETROS_LR).fit(xa, train.relevancia_v3.astype(int))
    p_rel = ma.predict_proba(vec_a.transform(texts))[:, list(ma.classes_).index(1)]
    relevant = train.relevancia_v3.eq("1")
    xb = vec_b.fit_transform(train.loc[relevant, "texto"])
    mb = LogisticRegression(**PARAMETROS_LR).fit(xb, train.loc[relevant, "etiqueta_v3"])
    p_class = align_proba(mb.predict_proba(vec_b.transform(texts)), mb.classes_)
    return compose(p_rel, p_class), (vec_a, ma, vec_b, mb)


def predict_standard_fitted(fitted, texts):
    va, ma, vb, mb = fitted
    p_rel = ma.predict_proba(va.transform(texts))[:, list(ma.classes_).index(1)]
    p_class = align_proba(mb.predict_proba(vb.transform(texts)), mb.classes_)
    return compose(p_rel, p_class)


def ratio(x, y):
    pos, neg = y == 1, y == 0
    p = (np.asarray(x[pos].sum(axis=0)).ravel() + 1) / (pos.sum() + 1)
    q = (np.asarray(x[neg].sum(axis=0)).ravel() + 1) / (neg.sum() + 1)
    return np.log(p / q)


def nbsvm_binary(x, y, xv):
    y = np.asarray(y).astype(int); r = ratio(x, y)
    model = LogisticRegression(**PARAMETROS_LR).fit(x.multiply(r), y)
    return model.predict_proba(xv.multiply(r))[:, list(model.classes_).index(1)]


def nbsvm_prob(train, texts):
    va = vectorizer(PARAMETROS_A, 1.0); xa = va.fit_transform(train.texto); xva = va.transform(texts)
    p_rel = nbsvm_binary(xa, train.relevancia_v3.astype(int), xva)
    relevant = train.relevancia_v3.eq("1")
    vb = vectorizer(PARAMETROS_B, 1.0); xb = vb.fit_transform(train.loc[relevant, "texto"]); xvb = vb.transform(texts)
    y = train.loc[relevant, "etiqueta_v3"].to_numpy(); scores=[]
    for c in CLASSES:
        scores.append(nbsvm_binary(xb, y == c, xvb))
    p_class = np.column_stack(scores); p_class /= p_class.sum(axis=1, keepdims=True)
    return compose(p_rel, p_class)


def lsa_stage(train_text, y, val_text):
    vec = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1, 2), min_df=3,
                          max_df=.98, sublinear_tf=True, max_features=50000)
    x = vec.fit_transform(train_text); xv = vec.transform(val_text)
    n = min(128, x.shape[0]-1, x.shape[1]-1)
    svd = TruncatedSVD(n_components=n, random_state=20260917)
    normalizer = Normalizer(copy=False)
    z = normalizer.fit_transform(svd.fit_transform(x)); zv = normalizer.transform(svd.transform(xv))
    model = LogisticRegression(**PARAMETROS_LR).fit(z, y)
    return model.predict_proba(zv), model.classes_


def lsa_prob(train, texts):
    pa, ca = lsa_stage(train.texto, train.relevancia_v3.astype(int), texts)
    p_rel = pa[:, list(ca).index(1)]
    relevant = train.relevancia_v3.eq("1")
    pb, cb = lsa_stage(train.loc[relevant, "texto"], train.loc[relevant, "etiqueta_v3"], texts)
    return compose(p_rel, align_proba(pb, cb))


def split_sentences(text):
    parts = [x.strip() for x in re.split(r"(?<=[.!?;])\s+|\n+", str(text)) if x.strip()]
    return parts or [str(text)]


def sentence_smooth_prob(train, texts):
    full, fitted = standard_prob(train, texts, vectorizer(PARAMETROS_A, 1.0), vectorizer(PARAMETROS_B, 1.0))
    sentences, owners = [], []
    for i, text in enumerate(texts):
        for sentence in split_sentences(text):
            sentences.append(sentence); owners.append(i)
    sentence_prob = predict_standard_fitted(fitted, pd.Series(sentences))
    averaged = np.zeros_like(full); counts = np.zeros(len(full))
    for owner, prob in zip(owners, sentence_prob):
        averaged[owner] += prob; counts[owner] += 1
    averaged /= counts[:, None]
    return 0.75 * full + 0.25 * averaged


def method_prob(method, train, texts):
    if method == "token_monetario":
        return standard_prob(train, texts, monetary_vectorizer("a"), monetary_vectorizer("b"))[0]
    if method == "nbsvm": return nbsvm_prob(train, texts)
    if method == "lsa128": return lsa_prob(train, texts)
    if method == "suavizado_oraciones": return sentence_smooth_prob(train, list(texts))
    raise ValueError(method)


def labels(prob):
    return CLASSES[np.argmax(prob, axis=1)]


def select_method(core):
    splitter = GroupKFold(n_splits=3); groups = core.meeting_id.to_numpy()
    details, scores = {}, []
    for order, method in enumerate(METHODS):
        fold_metrics=[]; all_true=[]; all_pred=[]
        for fold, (ti, vi) in enumerate(splitter.split(core, groups=groups), 1):
            train, val = core.iloc[ti].copy(), core.iloc[vi].copy()
            keys = set(val.texto.map(clave_texto)); train = train[~train.texto.map(clave_texto).isin(keys)]
            if set(train.meeting_id) & set(val.meeting_id) or set(train.texto.map(clave_texto)) & keys:
                raise ValueError("Contaminación interna")
            pred = labels(method_prob(method, train, val.texto))
            m = medir(val.etiqueta_v3.tolist(), pred.tolist()); fold_metrics.append(m)
            all_true.extend(val.etiqueta_v3); all_pred.extend(pred)
        agg=medir(all_true, all_pred); mean_hd=sum(x["f1_hd"] for x in fold_metrics)/3
        details[method]={"media_folds_f1_hd":mean_hd,"agregadas":agg,"por_fold":fold_metrics}
        scores.append(((mean_hd,agg["por_clase"]["dovish"]["recall"],agg["macro_f1"],-order),method))
        print(f"Selección interna {method}: F1-HD={mean_hd:.6f}",flush=True)
    return max(scores)[1], details


def run(out=OUT):
    out=Path(out)
    if out.exists(): raise FileExistsError("No sobrescribir extensión")
    base,_,base_sources=cargar_datos(); ia89,ia_sources=cargar_nuevos()
    core=base[base.fold_validacion.eq(0)].copy()
    if len(core)!=559 or core.meeting_id.nunique()+sum(core.meeting_id.duplicated())<1: raise ValueError("Núcleo interno inválido")
    winner,internal=select_method(core)
    anchor_path=RAIZ/"data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c/predicciones.csv"
    anchor=pd.read_csv(anchor_path,dtype=str,keep_default_na=False).set_index("intervencion_id")
    predictions=[]
    with warnings.catch_warnings():
        warnings.simplefilter("error",ConvergenceWarning)
        for fold in range(1,6):
            val=base[base.fold_validacion.eq(fold)].copy(); keys=set(val.texto.map(clave_texto)); meetings=set(val.meeting_id)
            train=base[~base.fold_validacion.eq(fold)&~base.texto.map(clave_texto).isin(keys)].copy()
            ia=ia89[~ia89.meeting_id.isin(meetings)&~ia89.texto.map(clave_texto).isin(keys)].copy()
            train=pd.concat([train,ia.reindex(columns=train.columns)],ignore_index=True)
            pred=labels(method_prob(winner,train,val.texto)); fixed=anchor.loc[val.index]
            for i,(_,row) in enumerate(val.iterrows()):
                predictions.append({"intervencion_id":row.intervencion_id,"meeting_id":row.meeting_id,"fold":fold,
                    "etiqueta_v3":row.etiqueta_v3,"es_relevante_v3":row.relevancia_v3,"pred_c":fixed.iloc[i].pred_fase_c,
                    "metodo_ganador_interno":winner,"pred_extension":pred[i]})
            print(f"Outer fold {fold}: método fijado={winner}",flush=True)
    table=pd.DataFrame(predictions).sort_values(["fold","intervencion_id"])
    base_m=metricas_completas(table.rename(columns={"pred_c":"pred"}),"pred")
    ext_m=metricas_completas(table.rename(columns={"pred_extension":"pred"}),"pred")
    checks,improved,accepted=multicriteria(base_m,ext_m)
    result={"version":out.name,"ganador_interno":winner,"seleccion_interna":internal,"candidato_c":base_m,
            "extension":ext_m,"delta":{k:ext_m[k]-base_m[k] for k in ["accuracy","macro_f1","f1_hd","media_folds_f1_hd","errores"]},
            "folds_f1_hd_mejorados":improved,"controles_multicriterio":checks,"decision":"aceptar" if accepted else "rechazar",
            "metodos_no_ganadores_evaluados_externamente":False,"evaluacion_independiente":False}
    out.mkdir(parents=True);table.to_csv(out/"predicciones.csv",index=False,lineterminator="\n");save_json(out/"metricas.json",result)
    protocol=RAIZ/"docs/PROTOCOLO_EXTENSION_REPRESENTACIONES_V3.md"
    sources={**base_sources,**ia_sources,"ancla_c":anchor_path,"preregistro":protocol,"script":Path(__file__)}
    save_json(out/"protocolo.json",{"ganador_fijado_antes_evaluacion_externa":winner,"n_core_seleccion":559,
        "outer_no_usado_para_seleccion":True,"fuentes_sha256":{k:sha256(v) for k,v in sources.items()}})
    summary="# Extensión de representaciones v3\n\nSelección exclusiva mediante CV agrupada en las 559 filas `fold=0`; solo el ganador se evaluó externamente.\n\n"
    summary+="| Método interno | Media F1-HD | Recall D | Macro-F1 |\n|---|---:|---:|---:|\n"
    for method in METHODS:
        m=internal[method];summary+=f"| {method} | {m['media_folds_f1_hd']:.6f} | {m['agregadas']['por_clase']['dovish']['recall']:.6f} | {m['agregadas']['macro_f1']:.6f} |\n"
    summary+=f"\n**Ganador interno fijado: `{winner}`.**\n\n| Condición | Accuracy | Macro-F1 | F1-HD | Media folds F1-HD | F1 D | Recall D | F1 H | F1 N | Errores | H↔D | H/D→N | N→H/D |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n"
    for name,m in [("C",base_m),(winner,ext_m)]:
        pc=m["por_clase"];summary+=f"| {name} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['f1_hd']:.6f} | {m['media_folds_f1_hd']:.6f} | {pc['dovish']['f1']:.6f} | {pc['dovish']['recall']:.6f} | {pc['hawkish']['f1']:.6f} | {pc['neutral']['f1']:.6f} | {m['errores']} | {m['h_d_cruzados']} | {m['direccion_a_neutral']} | {m['neutral_a_direccion']} |\n"
    summary+=f"\n**Decisión multicriterio: {'ACEPTAR' if accepted else 'RECHAZAR'}.** `{json.dumps(checks,ensure_ascii=False)}`\n"
    (out/"resumen.md").write_text(summary,encoding="utf-8")
    save_json(out/"manifest.json",{"sha256_salidas":{p.name:sha256(p) for p in out.iterdir() if p.name!="manifest.json"}})
    return result


if __name__=="__main__": print(json.dumps(run(),ensure_ascii=False,indent=2))
