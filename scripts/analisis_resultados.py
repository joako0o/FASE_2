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
CORPUS = ROOT / "data/corpus_bcch_2005_2015.csv"
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
GOLD = ROOT / "data/evaluacion_ciega_gold.csv"
VOTE_REVIEW = ROOT / "data/revision_votos_actores.csv"
OUT = ROOT / "resultados/analisis_descriptivo"
LABELS = ["hawkish", "dovish", "neutral"]
STOP = set("de la el que en y los las del se por un una con para su al lo como es no más mas ha sus este esta sobre son fue han si ya entre le les o e a ante desde hasta durante mediante señor senor señora senora consejero consejera presidente vicepresidente gerente banco central chile senala indica menciona manifiesta expresa agrega hace presente ano respecto tambien intervencion inicia continua continuacion prosigue aludido referido ofrece palabra agradece comentarios concede consulta opinion tiene porque pero hay ello ser muy puede pueden parte caso punto forma manera bien solo dado reunion sesion".split())


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save_json(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
def safe_div(a, b): return a / b if b else np.nan

def normalize_text(text): return strip_accents_unicode(" ".join(str(text).lower().split()))

ACTION_TERMS = {
    "subir": r"\b(?:subir|aumentar|elevar|incrementar|alza|aumento)\b",
    "bajar": r"\b(?:bajar|rebajar|reducir|disminuir|recortar|rebaja|reduccion|recorte)\b",
    "mantener": r"\b(?:mantener|mantencion|mantenimiento|no innovar|hacer una pausa|dejar(?:la|lo)?\s+(?:la\s+)?tpm\s+en\s+su\s+actual|dejar(?:la|lo)?\s+en\s+su\s+actual)\b",
}

def action_after(text, anchor_pattern, max_distance=500):
    """Extrae la primera acción TPM posterior al último ancla; no interpreta referencias vagas."""
    normalized = normalize_text(text); anchors = list(re.finditer(anchor_pattern, normalized))
    for anchor in reversed(anchors):
        window = normalized[anchor.start():anchor.start()+max_distance]
        found = [(match.start(), action, match) for action, pattern in ACTION_TERMS.items() for match in re.finditer(pattern, window)]
        if not found: continue
        _, action, match = min(found, key=lambda item: item[0]); tail = window[match.start():match.start()+350]
        pb = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:puntos?\s+base|pb)\b", tail)
        percent_change = re.search(r"\b(?:en|de)\s*(0[.,]\d+)\s*%", tail)
        rate = re.search(r"\ben\s*(\d+(?:[.,]\d+)?)\s*%", tail) if action == "mantener" else re.search(r"(?:hasta|a|nivel\s+de|para\s+quedar\s+en|situar(?:la|lo)?\s+en|ubicar(?:la|lo)?\s+en|establecer(?:la|lo)?\s+en)\s*(\d+(?:[.,]\d+)?)\s*%", tail)
        if not rate: rate = re.search(r"\ben\s*(\d+(?:[.,]\d+)?)\s*%", tail)
        bias = re.search(r"sesgo\s+(?:de\s+politica\s+)?(?:al\s+alza|a\s+la\s+baja|expansivo|contractivo|negativo|positivo|neutral)", tail)
        snippet = normalized[max(0,anchor.start()-80):min(len(normalized),anchor.start()+500)]
        linkage = re.search(r"\b(?:por|a favor de|en orden a|en consecuencia|es|seria|tambien)\b", window[:match.start()])
        confidence = "alta" if match.start() <= 35 or (match.start() <= 140 and linkage) else "media"
        return {"accion":action,"magnitud_pb":float(pb.group(1).replace(",",".")) if pb else (100*float(percent_change.group(1).replace(",",".")) if percent_change else (0.0 if action=="mantener" else np.nan)),"tpm_objetivo":float(rate.group(1).replace(",",".")) if rate else np.nan,"sesgo":bias.group(0).replace("sesgo ","") if bias else "","fragmento":snippet,"confianza":confidence}
    return {"accion":"no_extraido","magnitud_pb":np.nan,"tpm_objetivo":np.nan,"sesgo":"","fragmento":"","confianza":"no_resuelto"}

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
    order = pd.read_csv(CORPUS, dtype=str, keep_default_na=False, usecols=["intervencion_id", "orden_habla", "subindice"])
    if len(order) != len(data) or order.intervencion_id.nunique() != len(order): raise ValueError("Orden del corpus incompleto o duplicado")
    data = data.merge(order, on="intervencion_id", how="left", validate="one_to_one")
    if data[["orden_habla", "subindice"]].eq("").any().any(): raise ValueError("Faltan campos de orden tras unir el corpus")
    train_labels = train.set_index("intervencion_id").etiqueta_v3.to_dict(); gold_labels = gold.set_index("intervencion_id").etiqueta_v3.to_dict(); gold_include = gold.set_index("intervencion_id").incluir_evaluacion.to_dict()
    def best(row):
        iid = row.intervencion_id
        if iid in train_labels: return train_labels[iid], "etiqueta_validada_entrenamiento"
        if iid in gold_labels: return (gold_labels[iid], "gold_evaluacion_ciega") if gold_include[iid] == "true" else ("no_puedo_decidir", "gold_no_decidible")
        return row.prediccion_v3, "prediccion_wc600"
    assigned = data.apply(best, axis=1, result_type="expand"); data["etiqueta_analisis"], data["procedencia_etiqueta"] = assigned[0], assigned[1]
    cargo_lower = data.cargo.str.lower(); data["tipo_actor"] = "staff_tecnico"
    data.loc[cargo_lower.str.contains(r"ministro|ministerio|subsecretario", regex=True), "tipo_actor"] = "hacienda_gobierno"
    data.loc[cargo_lower.str.contains(r"consejer|presidente del banco central|vicepresidente del banco central", regex=True), "tipo_actor"] = "miembro_consejo"
    data.loc[data.actor.eq("Consejo del Banco Central de Chile"), "tipo_actor"] = "consejo_institucional"
    valid = data[data.etiqueta_analisis.isin(LABELS)].copy(); out.mkdir(parents=True)
    data.to_csv(out / "tabla_maestra.csv", index=False, lineterminator="\n")
    grouped(valid, ["meeting_id", "fecha", "anio"]).to_csv(out / "indices_por_reunion.csv", index=False, lineterminator="\n")
    grouped(valid, ["anio"]).to_csv(out / "indices_por_anio.csv", index=False, lineterminator="\n")
    grouped(valid, ["topico_humano"]).to_csv(out / "indices_por_topico.csv", index=False, lineterminator="\n")
    grouped(valid, ["keywords_humano"]).to_csv(out / "indices_por_keywords.csv", index=False, lineterminator="\n")
    grouped(valid, ["actor"]).sort_values("n_intervenciones", ascending=False).to_csv(out / "indices_por_actor.csv", index=False, lineterminator="\n")
    grouped(valid, ["tipo_actor", "actor"]).sort_values(["tipo_actor", "n_intervenciones"], ascending=[True, False]).to_csv(out / "indices_por_tipo_y_actor.csv", index=False, lineterminator="\n")
    actor_year = grouped(valid, ["tipo_actor", "actor", "anio"]); actor_year.to_csv(out / "indices_actor_por_anio.csv", index=False, lineterminator="\n")
    annual_variation = []
    for (actor_type, actor), group in actor_year.groupby(["tipo_actor", "actor"]):
        group = group.sort_values("anio"); total_n = int(group.n_intervenciones.sum())
        if len(group) < 2 or total_n < 20: continue
        years = group.anio.astype(int).to_numpy(); scores = group.score_hd_continuo_medio.to_numpy()
        slope = float(np.polyfit(years, scores, 1)[0]) if len(group) >= 3 else np.nan
        annual_variation.append({"tipo_actor":actor_type,"actor":actor,"anios_observados":len(group),"n_intervenciones":total_n,"anio_inicial":int(years[0]),"score_inicial":float(scores[0]),"anio_final":int(years[-1]),"score_final":float(scores[-1]),"cambio_primero_ultimo":float(scores[-1]-scores[0]),"min_score_anual":float(scores.min()),"max_score_anual":float(scores.max()),"rango_score_anual":float(scores.max()-scores.min()),"pendiente_anual":slope})
    pd.DataFrame(annual_variation).sort_values(["tipo_actor", "n_intervenciones"], ascending=[True,False]).to_csv(out / "variacion_anual_por_actor.csv", index=False, lineterminator="\n")
    grouped(valid, ["anio", "topico_humano"]).to_csv(out / "mix_topicos_por_anio.csv", index=False, lineterminator="\n")
    actor_topic = valid.groupby(["actor", "topico_humano"]).size().rename("n").reset_index()
    actor_topic["proporcion_actor"] = actor_topic.n / actor_topic.groupby("actor").n.transform("sum")
    actor_topic["ranking_actor"] = actor_topic.groupby("actor").n.rank(method="first", ascending=False).astype(int)
    actor_topic.sort_values(["actor", "ranking_actor"]).to_csv(out / "topicos_por_actor.csv", index=False, lineterminator="\n")
    # Convergencia rápida: usa postura direccional y decisión institucional clasificadas como proxies, no votos certificados.
    valid["orden_habla_num"] = pd.to_numeric(valid.orden_habla, errors="coerce")
    valid["subindice_num"] = pd.to_numeric(valid.subindice, errors="coerce").fillna(0)
    comparable = valid.tipo_actor.eq("miembro_consejo")
    institutional = valid[valid.actor.eq("Consejo del Banco Central de Chile")].sort_values(["meeting_id", "orden_habla_num", "subindice_num"]).copy()
    agreement_records = []
    for _, row in institutional.iterrows():
        extracted = action_after(row.texto, r"\b(?:acord(?:o|a|aron)|acuerd(?:a|an)|resolvio)\b")
        if extracted["accion"] == "no_extraido" and "tasa de politica monetaria" in normalize_text(row.texto):
            extracted = action_after(row.texto, r"\b(?:subir|aumentar|elevar|incrementar|bajar|rebajar|reducir|disminuir|recortar|mantener|mantencion)\b")
        if extracted["accion"] == "no_extraido": continue
        normalized = normalize_text(row.texto)
        agreement_records.append({"meeting_id":row.meeting_id,"fecha":row.fecha,"anio":row.anio,"acuerdo_accion":extracted["accion"],"acuerdo_magnitud_pb":extracted["magnitud_pb"],"acuerdo_tpm_objetivo":extracted["tpm_objetivo"],"acuerdo_sesgo":extracted["sesgo"],"acuerdo_tipo_textual":"unanimidad" if "por unanimidad" in normalized else ("mayoria" if "por la mayoria" in normalized or "por mayoria" in normalized else "no_indicado"),"acuerdo_intervencion_id":row.intervencion_id,"acuerdo_orden_habla":row.orden_habla,"acuerdo_subindice":row.subindice,"acuerdo_fragmento":extracted["fragmento"],"acuerdo_texto":row.texto,"prioridad":int("adopta el siguiente acuerdo" in normalized)})
    agreements = pd.DataFrame(agreement_records).sort_values(["meeting_id", "prioridad", "acuerdo_orden_habla"], ascending=[True,False,True]).groupby("meeting_id").head(1).drop(columns="prioridad")
    meeting_institutional_text = institutional.groupby("meeting_id").texto.apply(lambda values: normalize_text(" ".join(values)))
    agreement_type = meeting_institutional_text.map(lambda text: "unanimidad" if "unanimidad" in text or "unanime" in text else ("mayoria" if "mayoria" in text else "no_indicado"))
    agreements["acuerdo_tipo_textual"] = agreements.meeting_id.map(agreement_type)
    if len(agreements) != valid.meeting_id.nunique(): raise ValueError(f"Acuerdos extraídos: {len(agreements)}; esperados: {valid.meeting_id.nunique()}")
    agreements.to_csv(out / "acuerdo_consejo_por_reunion.csv", index=False, lineterminator="\n")
    # Se mantiene además el proxy de tono institucional usado en el análisis exploratorio de convergencia.
    decision_rows = institutional[institutional.topico_humano.isin(["decision_tpm", "acuerdo_comunicado"])].groupby("meeting_id").tail(1)
    sign = {"hawkish": 1.0, "dovish": -1.0, "neutral": 0.0}; decision_index = decision_rows.set_index("meeting_id"); decisions = decision_index.etiqueta_analisis.map(sign).to_dict()
    decision_rows[["meeting_id", "intervencion_id", "etiqueta_analisis", "score_hd_continuo", "orden_habla", "subindice", "texto"]].to_csv(out / "decision_institucional_proxy.csv", index=False, lineterminator="\n")
    vote_pattern = r"\b(?:vota|voto|votaria|votaría|votara|votará)\b|\bsu voto\b|\bmi voto\b"
    votes = valid[comparable & valid.texto.str.lower().str.contains(vote_pattern, regex=True)].copy().sort_values(["meeting_id", "actor", "orden_habla_num", "subindice_num"])
    votes.to_csv(out / "candidatos_votos_explicitos.csv", index=False, lineterminator="\n")
    vote_records = []
    for _, row in votes.iterrows():
        extracted = action_after(row.texto, r"\b(?:su voto|mi voto|vota|voto)\b")
        accepted = extracted["confianza"] == "alta"
        vote_records.append({**row.to_dict(),"voto_accion":extracted["accion"] if accepted else "no_extraido","voto_accion_sugerida":extracted["accion"] if not accepted else "","voto_magnitud_pb":extracted["magnitud_pb"] if accepted else np.nan,"voto_tpm_objetivo":extracted["tpm_objetivo"] if accepted else np.nan,"voto_sesgo":extracted["sesgo"] if accepted else "","voto_fragmento":extracted["fragmento"],"confianza_extraccion":extracted["confianza"]})
    extracted_votes = pd.DataFrame(vote_records); extracted_votes["n_fragmentos_candidatos"] = extracted_votes.groupby(["meeting_id", "actor"]).meeting_id.transform("size")
    selected_votes = []
    for _, group in extracted_votes.groupby(["meeting_id", "actor"]):
        resolved = group[group.voto_accion.ne("no_extraido")]
        selected_votes.append((resolved if len(resolved) else group).iloc[-1])
    vote_matrix = pd.DataFrame(selected_votes); vote_matrix["estado_validacion"] = np.where(vote_matrix.voto_accion.eq("no_extraido"), "candidato_no_resuelto", "extraido_automaticamente_no_validado")
    vote_columns = ["meeting_id", "fecha", "anio", "actor", "cargo", "intervencion_id", "orden_habla", "subindice", "voto_accion", "voto_accion_sugerida", "voto_magnitud_pb", "voto_tpm_objetivo", "voto_sesgo", "confianza_extraccion", "etiqueta_analisis", "score_hd_continuo", "n_fragmentos_candidatos", "estado_validacion", "voto_fragmento", "texto"]
    vote_matrix[vote_columns].to_csv(out / "matriz_votos_candidatos.csv", index=False, lineterminator="\n")
    participants = valid[comparable].groupby(["meeting_id", "actor"], as_index=False).agg(fecha=("fecha","first"),anio=("anio","first"),cargo=("cargo","first"),n_intervenciones_actor=("intervencion_id","size"))
    base_votes = participants.merge(vote_matrix[["meeting_id","actor","intervencion_id","orden_habla","subindice","voto_accion","voto_accion_sugerida","voto_magnitud_pb","voto_tpm_objetivo","voto_sesgo","confianza_extraccion","etiqueta_analisis","score_hd_continuo","estado_validacion","voto_fragmento","texto"]], on=["meeting_id","actor"], how="left", validate="one_to_one")
    base_votes = base_votes.merge(agreements, on=["meeting_id","fecha","anio"], how="left", validate="many_to_one")
    base_votes["estado_validacion"] = base_votes.estado_validacion.fillna("sin_fragmento_de_voto_detectado")
    base_votes["voto_accion"] = base_votes.voto_accion.fillna("no_extraido")
    infer_unanimous = base_votes.voto_accion.eq("no_extraido") & base_votes.acuerdo_tipo_textual.eq("unanimidad")
    base_votes["voto_accion_con_inferencia"] = base_votes.voto_accion
    base_votes.loc[infer_unanimous, "voto_accion_con_inferencia"] = base_votes.loc[infer_unanimous, "acuerdo_accion"]
    base_votes["fuente_voto"] = np.where(base_votes.voto_accion.ne("no_extraido"), "texto_explicito_extraido", np.where(infer_unanimous, "inferido_de_unanimidad_textual", "no_extraido"))
    review = pd.read_csv(VOTE_REVIEW, dtype=str, keep_default_na=False)
    if review.duplicated(["meeting_id","actor"]).any(): raise ValueError("Revisión de votos duplicada")
    if len(base_votes.merge(review[["meeting_id","actor"]], on=["meeting_id","actor"], how="inner")) != len(review): raise ValueError("Revisión contiene pares ajenos a la base")
    base_votes = base_votes.merge(review, on=["meeting_id","actor"], how="left", validate="one_to_one")
    reviewed = base_votes.voto_accion_revision.fillna("").isin(["subir","bajar","mantener"])
    base_votes["voto_accion_final"] = base_votes.voto_accion_con_inferencia
    base_votes.loc[reviewed, "voto_accion_final"] = base_votes.loc[reviewed, "voto_accion_revision"]
    base_votes["fuente_voto_final"] = base_votes.fuente_voto
    base_votes.loc[reviewed, "fuente_voto_final"] = "revision_textual_asistida"
    base_votes["coincide_con_acuerdo"] = np.where(base_votes.voto_accion.eq("no_extraido"), "no_determinado", np.where(base_votes.voto_accion.eq(base_votes.acuerdo_accion), "si", "no"))
    base_votes["coincide_final_con_acuerdo"] = np.where(base_votes.voto_accion_final.eq("no_extraido"), "no_determinado", np.where(base_votes.voto_accion_final.eq(base_votes.acuerdo_accion), "si", "no"))
    base_votes.sort_values(["fecha","orden_habla","actor"]).to_csv(out / "base_votos_acta_actor.csv", index=False, lineterminator="\n")
    convergence = []
    directional_rows = valid[comparable & valid.etiqueta_analisis.isin(["hawkish", "dovish"]) & valid.meeting_id.isin(decisions)].copy()
    for (meeting, actor), group in directional_rows.groupby(["meeting_id", "actor"]):
        d_order, d_sub = decision_index.at[meeting, "orden_habla_num"], decision_index.at[meeting, "subindice_num"]
        before = group.orden_habla_num.lt(d_order) | (group.orden_habla_num.eq(d_order) & group.subindice_num.le(d_sub))
        group = group[before].sort_values(["orden_habla_num", "subindice_num"])
        if len(group) < 2: continue
        first, last, target = group.iloc[0], group.iloc[-1], decisions[meeting]
        s_first, s_last = float(first.score_hd_continuo), float(last.score_hd_continuo)
        convergence.append({"meeting_id": meeting, "anio": str(first.anio), "actor": actor, "n_intervenciones_direccionales": len(group), "etiqueta_decision_proxy": decision_index.at[meeting, "etiqueta_analisis"], "score_primera": s_first, "score_ultima": s_last, "cambio_score": s_last-s_first, "distancia_inicial": abs(s_first-target), "distancia_final": abs(s_last-target), "convergencia": abs(s_first-target)-abs(s_last-target), "id_primera": first.intervencion_id, "id_ultima": last.intervencion_id})
    convergence = pd.DataFrame(convergence)
    convergence.to_csv(out / "convergencia_actor_reunion_proxy.csv", index=False, lineterminator="\n")
    if len(convergence):
        convergence.groupby("actor").agg(reuniones=("meeting_id","nunique"), convergencia_media=("convergencia","mean"), mediana=("convergencia","median"), proporcion_acercamiento=("convergencia",lambda x: float((x>0).mean())), cambio_score_medio=("cambio_score","mean")).reset_index().sort_values(["reuniones","convergencia_media"], ascending=[False,False]).to_csv(out / "convergencia_resumen_actor_proxy.csv", index=False, lineterminator="\n")
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
    actor_vocab = []; actor_frequency = []
    substantive_mask = ~valid.topico_humano.isin(["apertura_cierre", "acuerdo_comunicado", "decision_tpm"]).to_numpy()
    actors_substantive = valid.actor.to_numpy()[substantive_mask]; matrix_substantive = matrix[substantive_mask]
    for actor, n_actor in pd.Series(actors_substantive).value_counts().items():
        if n_actor < 20: continue
        contrast = log_odds(matrix_substantive, actors_substantive==actor, actors_substantive!=actor, names, "actor", "resto", top=300)
        actor_tokens = set(strip_accents_unicode(actor.lower()).split())
        meaningful = lambda term: not any(token in actor_tokens for token in term.split()) and any(token not in STOP for token in term.split())
        contrast = contrast[contrast.distintivo_de.eq("actor") & contrast.ngram.map(meaningful)].head(20)
        for rank, (_, term) in enumerate(contrast.iterrows(), 1): actor_vocab.append({"actor":actor,"n_intervenciones_sustantivas":int(n_actor),"ranking":rank,"ngram":term.ngram,"conteo_actor":int(term.conteo_actor),"conteo_resto":int(term.conteo_resto),"log_odds":term.log_odds,"z_score":term.z_score})
        counts = np.asarray(matrix_substantive[actors_substantive==actor].sum(axis=0)).ravel().astype(int)
        frequent = pd.DataFrame({"ngram":names,"ocurrencias":counts}); frequent = frequent[frequent.ocurrencias.ge(3) & frequent.ngram.map(meaningful)].nlargest(20, "ocurrencias")
        for rank, (_, term) in enumerate(frequent.iterrows(), 1): actor_frequency.append({"actor":actor,"n_intervenciones_sustantivas":int(n_actor),"ranking":rank,"ngram":term.ngram,"ocurrencias":int(term.ocurrencias)})
    pd.DataFrame(actor_vocab).to_csv(out / "vocabulario_distintivo_por_actor.csv", index=False, lineterminator="\n")
    pd.DataFrame(actor_frequency).to_csv(out / "vocabulario_frecuente_por_actor.csv", index=False, lineterminator="\n")
    contexts=[]; normalized=valid.texto.map(lambda x: strip_accents_unicode(" ".join(str(x).lower().split())))
    chosen=pd.concat([hd.head(50),hd.tail(50)]).drop_duplicates("ngram")
    for _, term in chosen.iterrows():
        pattern=re.compile(r"(?<!\w)"+re.escape(term.ngram)+r"(?!\w)")
        hits=valid[normalized.map(lambda x: bool(pattern.search(x)))].head(3)
        for _, row in hits.iterrows(): contexts.append({"ngram":term.ngram,"distintivo_de":term.distintivo_de,"intervencion_id":row.intervencion_id,"meeting_id":row.meeting_id,"etiqueta_analisis":row.etiqueta_analisis,"texto":row.texto})
    pd.DataFrame(contexts).to_csv(out / "lexico_contextos_h_d.csv", index=False, lineterminator="\n")
    outputs = sorted(p.name for p in out.iterdir() if p.is_file())
    summary = {"filas":len(data),"filas_validas":len(valid),"no_decidibles":len(data)-len(valid),"procedencia":data.procedencia_etiqueta.value_counts().to_dict(),"distribucion_etiqueta_analisis":valid.etiqueta_analisis.value_counts().to_dict(),"reuniones":valid.meeting_id.nunique(),"actores":valid.actor.nunique(),"topicos":valid.topico_humano.nunique(),"vocabulario_1_a_4_min_df_5":len(names),"actores_con_vocabulario_distintivo":len(set(x["actor"] for x in actor_vocab)),"decisiones_institucionales_proxy":len(decision_rows),"candidatos_votos_explicitos":len(votes),"pares_reunion_actor_con_candidato_voto":len(vote_matrix),"acuerdos_consejo_extraidos":len(agreements),"filas_base_votos_acta_actor":len(base_votes),"votos_con_accion_extraida":int(base_votes.voto_accion.ne("no_extraido").sum()),"votos_inferidos_por_unanimidad":int(base_votes.fuente_voto.eq("inferido_de_unanimidad_textual").sum()),"votos_revisados_textualmente":int(base_votes.fuente_voto_final.eq("revision_textual_asistida").sum()),"votos_no_extraidos":int(base_votes.voto_accion_final.eq("no_extraido").sum()),"casos_convergencia_proxy":len(convergence),"nota_convergencia":"Exploratoria: decisión institucional y postura son etiquetas/scores del sistema; candidatos de voto requieren validación textual humana.","nota_neutrales":"Se conservan en tono general y cobertura; balance direccional usa solo H/D.","embeddings_generados":False,"razon_embeddings":"No son parte de W+C+600; se reservan para una hipótesis temática posterior."}
    save_json(out / "resumen.json", summary); outputs.append("resumen.json")
    sources = [CLASSIFIED, CORPUS, TRAIN, GOLD, VOTE_REVIEW, Path(__file__)]
    save_json(out / "manifest.json", {"fuentes_sha256":{str(p.relative_to(ROOT)):sha(p) for p in sources},"sha256_salidas":{name:sha(out/name) for name in outputs}})
    return summary
if __name__ == "__main__": print(json.dumps(run(), ensure_ascii=False, indent=2))
