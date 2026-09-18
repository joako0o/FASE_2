"""Entrena y aplica el modelo formal W+C+600 exactamente como fue evaluado."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
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


def fit_predict(train, texts, weight):
    va = vectorizer(WORD_A, weight); ma = LogisticRegression(**LR).fit(va.fit_transform(train.texto), train.relevancia_v3.astype(int))
    pred_a = ma.predict(va.transform(texts)); relevant = train.relevancia_v3.eq("1")
    vb = vectorizer(WORD_B, weight); mb = LogisticRegression(**LR).fit(vb.fit_transform(train.loc[relevant, "texto"]), train.loc[relevant, "etiqueta_v3"])
    pred_b = mb.predict(vb.transform(texts))
    return np.where(pred_a == 0, "neutral", pred_b)


def predecir(input_path, output_path):
    verificar(); source = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if "texto" not in source or not len(source): raise ValueError("La entrada requiere una columna texto y al menos una fila")
    train = pd.read_csv(TRAIN, dtype=str, keep_default_na=False); members = []
    for member, weight in WEIGHTS.items():
        subset = train[train.miembros.str.split("|").map(lambda x: str(member) in x)]
        prediction = fit_predict(subset, source.texto, weight); members.append(prediction); source[f"pred_miembro_{member}"] = prediction
    source["prediccion_v3"] = [vote(values) for values in zip(*members)]
    if "intervencion_id" in source: source["usado_en_entrenamiento"] = source.intervencion_id.isin(set(train.intervencion_id))
    output_path = Path(output_path)
    if output_path.exists(): raise FileExistsError(f"No sobrescribir: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True); source.to_csv(output_path, index=False, lineterminator="\n")
    return {"filas": len(source), "salida": str(output_path), "predicciones": source.prediccion_v3.value_counts().to_dict()}


def main():
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest="comando", required=True)
    commands.add_parser("verificar", help="Comprobar datos y checksums sin entrenar")
    predict = commands.add_parser("predecir", help="Entrenar los cinco miembros y clasificar un CSV")
    predict.add_argument("entrada", type=Path); predict.add_argument("salida", type=Path)
    args = parser.parse_args(); result = verificar() if args.comando == "verificar" else predecir(args.entrada, args.salida)
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == "__main__": main()
