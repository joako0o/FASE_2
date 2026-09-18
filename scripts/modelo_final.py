"""Entrena, guarda y aplica el modelo formal W+C+600 exactamente como fue evaluado."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
GOLD = ROOT / "data/evaluacion_ciega_gold.csv"
MANIFEST = ROOT / "data/manifest.json"
ORDER = ["hawkish", "dovish", "neutral"]
WEIGHTS = {1: 1.0, 2: 0.5, 3: 1.0, 4: 1.0, 5: 1.0}
WORD_A = {"strip_accents": "unicode", "lowercase": True, "ngram_range": (1, 1), "min_df": 3, "max_df": 0.9, "sublinear_tf": True}
WORD_B = {**WORD_A, "ngram_range": (1, 4)}
CHAR = {"analyzer": "char_wb", "ngram_range": (3, 5), "min_df": 3, "max_df": 0.98, "sublinear_tf": True, "strip_accents": "unicode", "lowercase": True, "max_features": 120000}
LR = {"class_weight": "balanced", "C": 2.0, "max_iter": 2000, "random_state": 20260915}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def vectorizer(words, weight): return FeatureUnion([("word", TfidfVectorizer(**words)), ("char", TfidfVectorizer(**CHAR))], transformer_weights={"word": 1.0, "char": weight}, n_jobs=1)
def vote(values):
    counts = Counter(values)
    return max(ORDER, key=lambda label: (counts[label], -ORDER.index(label)))


def verificar():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["sha256"]
    failures = [name for name, expected in manifest.items() if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    if failures: raise ValueError("Archivos ausentes o alterados: " + ", ".join(failures))
    data = pd.read_csv(TRAIN, dtype=str, keep_default_na=False)
    if len(data) != 1596 or not data.intervencion_id.is_unique: raise ValueError("Entrenamiento final inválido")
    expected = {1: 1494, 2: 1450, 3: 1453, 4: 1473, 5: 1466}
    observed = {i: int(data.miembros.str.split("|").map(lambda x: str(i) in x).sum()) for i in range(1, 6)}
    if observed != expected: raise ValueError(f"Miembros distintos: {observed}")
    return {"estado": "íntegro", "filas_entrenamiento": len(data), "filas_por_miembro": observed}


def ajustar(train, weight):
    va = vectorizer(WORD_A, weight); ma = LogisticRegression(**LR).fit(va.fit_transform(train.texto), train.relevancia_v3.astype(int))
    relevant = train.relevancia_v3.eq("1"); vb = vectorizer(WORD_B, weight)
    mb = LogisticRegression(**LR).fit(vb.fit_transform(train.loc[relevant, "texto"]), train.loc[relevant, "etiqueta_v3"])
    return {"vector_a": va, "modelo_a": ma, "vector_b": vb, "modelo_b": mb, "peso_char": weight}


def inferir(bundle, texts):
    xa = bundle["vector_a"].transform(texts); xb = bundle["vector_b"].transform(texts)
    ma, mb = bundle["modelo_a"], bundle["modelo_b"]
    pa = ma.predict_proba(xa)[:, list(ma.classes_).index(1)]
    pb = mb.predict_proba(xb); class_index = {label: i for i, label in enumerate(mb.classes_)}
    probs = np.column_stack([pa * pb[:, class_index["hawkish"]], pa * pb[:, class_index["dovish"]], (1 - pa) + pa * pb[:, class_index["neutral"]]])
    hard_b = mb.predict(xb); hard = np.where(ma.predict(xa) == 0, "neutral", hard_b)
    return hard, probs


def predecir(input_path, output_path, models_dir=None, load_dir=None):
    verificar(); source = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if "texto" not in source or not len(source): raise ValueError("La entrada requiere una columna texto y al menos una fila")
    output_path = Path(output_path)
    if output_path.exists(): raise FileExistsError(f"No sobrescribir: {output_path}")
    if models_dir is not None and load_dir is not None: raise ValueError("Usar guardar o cargar modelos, no ambos")
    if models_dir is not None:
        models_dir = Path(models_dir)
        if models_dir.exists(): raise FileExistsError(f"No sobrescribir: {models_dir}")
        models_dir.mkdir(parents=True)
    if load_dir is not None:
        load_dir = Path(load_dir); stored = json.loads((load_dir / "manifest.json").read_text(encoding="utf-8"))
        if stored["entrenamiento_sha256"] != sha(TRAIN): raise ValueError("Modelos corresponden a otro entrenamiento")
        for name, expected in stored["archivos_sha256"].items():
            if sha(load_dir / name) != expected: raise ValueError(f"Modelo alterado: {name}")
    train = pd.read_csv(TRAIN, dtype=str, keep_default_na=False); members, probabilities, model_hashes = [], [], {}
    for member, weight in WEIGHTS.items():
        subset = train[train.miembros.str.split("|").map(lambda x: str(member) in x)]
        bundle = joblib.load(load_dir / f"miembro_{member}.joblib") if load_dir is not None else ajustar(subset, weight)
        prediction, probs = inferir(bundle, source.texto)
        members.append(prediction); probabilities.append(probs); source[f"pred_miembro_{member}"] = prediction
        if models_dir is not None:
            path = models_dir / f"miembro_{member}.joblib"; joblib.dump(bundle, path, compress=3); model_hashes[path.name] = sha(path)
    mean_probs = np.mean(probabilities, axis=0)
    source["prediccion_v3"] = [vote(values) for values in zip(*members)]
    source["prob_h_no_calibrada"], source["prob_d_no_calibrada"], source["prob_n_no_calibrada"] = mean_probs.T
    source["score_hd_continuo"] = source.prob_h_no_calibrada - source.prob_d_no_calibrada
    source["acuerdo_miembros"] = np.where(source[[f"pred_miembro_{i}" for i in WEIGHTS]].nunique(axis=1).eq(1), "unanime", "desacuerdo")
    if "intervencion_id" in source:
        train_ids = set(train.intervencion_id); gold_ids = set(pd.read_csv(GOLD, dtype=str, keep_default_na=False).intervencion_id)
        source["usado_en_entrenamiento"] = source.intervencion_id.isin(train_ids)
        source["rol"] = source.intervencion_id.map(lambda x: "entrenamiento" if x in train_ids else ("evaluacion_ciega" if x in gold_ids else "inferencia_no_etiquetada"))
    output_path.parent.mkdir(parents=True, exist_ok=True); source.to_csv(output_path, index=False, lineterminator="\n")
    if models_dir is not None:
        metadata = {"modelo": "W+C+600", "archivos_sha256": model_hashes, "entrenamiento_sha256": sha(TRAIN), "parametros": {"word_a": WORD_A, "word_b": WORD_B, "char": CHAR, "lr": LR, "pesos": WEIGHTS}}
        (models_dir / "manifest.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"filas": len(source), "salida": str(output_path), "predicciones": source.prediccion_v3.value_counts().to_dict(), "modelos_guardados": str(models_dir) if models_dir else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest="comando", required=True)
    commands.add_parser("verificar", help="Comprobar datos y checksums sin entrenar")
    predict = commands.add_parser("predecir", help="Entrenar los cinco miembros y clasificar un CSV")
    predict.add_argument("entrada", type=Path); predict.add_argument("salida", type=Path); predict.add_argument("--guardar-modelos", type=Path); predict.add_argument("--cargar-modelos", type=Path)
    args = parser.parse_args(); result = verificar() if args.comando == "verificar" else predecir(args.entrada, args.salida, args.guardar_modelos, args.cargar_modelos)
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == "__main__": main()
