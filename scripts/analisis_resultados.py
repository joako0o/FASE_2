"""Construye vistas H/D/N, agregados, tópicos, actores y léxico del corpus clasificado."""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer, strip_accents_unicode

ROOT = Path(__file__).resolve().parents[1]
CLASSIFIED = ROOT / "resultados/clasificacion_wc600_9725.csv"
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
GOLD = ROOT / "data/evaluacion_ciega_gold.csv"
OUT = ROOT / "resultados/analisis_descriptivo"
LABELS = ["hawkish", "dovish", "neutral"]
STOP = set("de la el que en y los las del se por un una con para su al lo como es no más mas ha sus este esta sobre son fue han si ya entre le les o e a ante desde hasta durante mediante señor senor señora senora consejero consejera presidente vicepresidente gerente banco central chile senala indica menciona manifiesta expresa agrega hace presente ano respecto tambien".split())


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save_json(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
def safe_div(a, b): return a / b if b else np.nan

def add_indices(group):
    counts = group.etiqueta_analisis.value_counts()
    h, d, n = (int(counts.get(x, 0)) for x in LABELS); total = h + d + n
    return pd.Series({"n_intervenciones": total, "n_hawkish": h, "n_dovish": d, "n_neutral": n,
        "proporcion_hawkish": safe_div(h, total), "proporcion_dovish": safe_div(d, total), "proporcion_neutral": safe_div(n, total),
        "tono_neto_general": safe_div(h-d, total), "balance_direccional": safe_div(h-d, h+d), "cobertura_direccional": safe_div(h+d, total),
        "score_hd_continuo_medio": group.score_hd_continuo.astype(float).mean()})

def grouped(data, columns): return data.groupby(columns, dropna=False, sort=True).apply(add_indices, include_groups=False).reset_index()

def log_odds(matrix, mask_a, mask_b, names, label_a, label_b, top=500):
    ca = np.asarray(matrix[mask_a].sum(axis=0)).ravel(); cb = np.asarray(matrix[mask_b].sum(axis=0)).ravel(); corpus = ca + cb
    alpha0 = 1000.0; alpha = alpha0 * (corpus + 1) / (corpus.sum() + len(corpus)); aa, ab = alpha.sum(), alpha.sum()
    delta = np.log((ca + alpha) / (ca.sum() + aa - ca - alpha)) - np.log((cb + alpha) / (cb.sum() + ab - cb - alpha))
    variance = 1/(ca+alpha) + 1/(cb+alpha); z = delta / np.sqrt(variance)
    frame = pd.DataFrame({"ngram": names, f"conteo_{label_a}": ca.astype(int), f"conteo_{label_b}": cb.astype(int), "log_odds": delta, "z_score": z})
    positive = frame.nlargest(top, "z_score").assign(distintivo_de=label_a); negative = frame.nsmallest(top, "z_score").assign(distintivo_de=label_b)
    return pd.concat([positive, negative], ignore_index=True)

def run(out=OUT):
    out = Path(out)
    if out.exists(): raise FileExistsError(f"No sobrescribir: {out}")
    data = pd.read_csv(CLASSIFIED, dtype=str, keep_default_na=False); train = pd.read_csv(TRAIN, dtype=str, keep_default_na=False); gold = pd.read_csv(GOLD, dtype=str, keep_default_na=False)
    train_labels = train.set_index("intervencion_id").etiqueta_v3.to_dict(); gold_labels = gold.set_index("intervencion_id").etiqueta_v3.to_dict(); gold_include = gold.set_index("intervencion_id").incluir_evaluacion.to_dict()
    def best(row):
        iid = row.intervencion_id
        if iid in train_labels: return train_labels[iid], "etiqueta_validada_entrenamiento"
        if iid in gold_labels: return (gold_labels[iid], "gold_evaluacion_ciega") if gold_include[iid] == "true" else ("no_puedo_decidir", "gold_no_decidible")
        return row.prediccion_v3, "prediccion_wc600"
    assigned = data.apply(best, axis=1, result_type="expand"); data["etiqueta_analisis"], data["procedencia_etiqueta"] = assigned[0], assigned[1]
    valid = data[data.etiqueta_analisis.isin(LABELS)].copy(); out.mkdir(parents=True)
    data.to_csv(out / "tabla_maestra.csv", index=False, lineterminator="\n")
    grouped(valid, ["meeting_id", "fecha", "anio"]).to_csv(out / "indices_por_reunion.csv", index=False, lineterminator="\n")
    grouped(valid, ["anio"]).to_csv(out / "indices_por_anio.csv", index=False, lineterminator="\n")
    grouped(valid, ["topico_humano"]).to_csv(out / "indices_por_topico.csv", index=False, lineterminator="\n")
    grouped(valid, ["keywords_humano"]).to_csv(out / "indices_por_keywords.csv", index=False, lineterminator="\n")
    grouped(valid, ["actor"]).sort_values("n_intervenciones", ascending=False).to_csv(out / "indices_por_actor.csv", index=False, lineterminator="\n")
    grouped(valid, ["anio", "topico_humano"]).to_csv(out / "mix_topicos_por_anio.csv", index=False, lineterminator="\n")
    vector = CountVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1,4), min_df=5)
    matrix = vector.fit_transform(valid.texto); names = vector.get_feature_names_out(); binary = matrix.copy(); binary.data[:] = 1
    meeting_frequency = np.zeros(len(names), dtype=int)
    meetings = valid.meeting_id.to_numpy()
    for meeting in np.unique(meetings): meeting_frequency += np.asarray(binary[meetings == meeting].sum(axis=0)).ravel() > 0
    global_freq = pd.DataFrame({"ngram": names, "n_palabras": [x.count(" ")+1 for x in names], "ocurrencias": np.asarray(matrix.sum(axis=0)).ravel().astype(int), "intervenciones": np.asarray(binary.sum(axis=0)).ravel().astype(int), "reuniones": meeting_frequency})
    global_freq = global_freq[global_freq.reuniones.ge(3)].sort_values(["ocurrencias","intervenciones"], ascending=False)
    global_freq.head(5000).to_csv(out / "lexico_frecuencia_global.csv", index=False, lineterminator="\n")
    content = global_freq[global_freq.ngram.map(lambda term: any(token not in STOP for token in term.split()))].head(2000)
    content.to_csv(out / "lexico_frecuencia_contenido.csv", index=False, lineterminator="\n")
    y = valid.etiqueta_analisis.to_numpy(); hd = log_odds(matrix, y=="hawkish", y=="dovish", names, "hawkish", "dovish"); hd.to_csv(out / "lexico_distintivo_h_vs_d.csv", index=False, lineterminator="\n")
    directional = np.isin(y,["hawkish","dovish"]); dn = log_odds(matrix, directional, y=="neutral", names, "direccional", "neutral"); dn.to_csv(out / "lexico_direccional_vs_neutral.csv", index=False, lineterminator="\n")
    contexts=[]; normalized=valid.texto.map(lambda x: strip_accents_unicode(" ".join(str(x).lower().split())))
    chosen=pd.concat([hd.head(50),hd.tail(50)]).drop_duplicates("ngram")
    for _, term in chosen.iterrows():
        pattern=re.compile(r"(?<!\w)"+re.escape(term.ngram)+r"(?!\w)")
        hits=valid[normalized.map(lambda x: bool(pattern.search(x)))].head(3)
        for _, row in hits.iterrows(): contexts.append({"ngram":term.ngram,"distintivo_de":term.distintivo_de,"intervencion_id":row.intervencion_id,"meeting_id":row.meeting_id,"etiqueta_analisis":row.etiqueta_analisis,"texto":row.texto})
    pd.DataFrame(contexts).to_csv(out / "lexico_contextos_h_d.csv", index=False, lineterminator="\n")
    outputs = sorted(p.name for p in out.iterdir() if p.is_file())
    summary = {"filas":len(data),"filas_validas":len(valid),"no_decidibles":len(data)-len(valid),"procedencia":data.procedencia_etiqueta.value_counts().to_dict(),"distribucion_etiqueta_analisis":valid.etiqueta_analisis.value_counts().to_dict(),"reuniones":valid.meeting_id.nunique(),"actores":valid.actor.nunique(),"topicos":valid.topico_humano.nunique(),"vocabulario_1_a_4_min_df_5":len(names),"nota_neutrales":"Se conservan en tono general y cobertura; balance direccional usa solo H/D.","embeddings_generados":False,"razon_embeddings":"No son parte de W+C+600; se reservan para una hipótesis temática posterior."}
    save_json(out / "resumen.json", summary); outputs.append("resumen.json")
    sources = [CLASSIFIED, TRAIN, GOLD, Path(__file__)]
    save_json(out / "manifest.json", {"fuentes_sha256":{str(p.relative_to(ROOT)):sha(p) for p in sources},"sha256_salidas":{name:sha(out/name) for name in outputs}})
    return summary
if __name__ == "__main__": print(json.dumps(run(), ensure_ascii=False, indent=2))
