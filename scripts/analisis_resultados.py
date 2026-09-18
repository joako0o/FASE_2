"""Construye vistas H/D/N, agregados, tópicos, actores y léxico del corpus clasificado."""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import (
    CountVectorizer,
    TfidfVectorizer,
    strip_accents_unicode,
)
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
CLASSIFIED = ROOT / "resultados/clasificacion_wc600_9725.csv"
CORPUS = ROOT / "data/corpus_bcch_2005_2015.csv"
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
GOLD = ROOT / "data/evaluacion_ciega_gold.csv"
VOTE_REVIEW = ROOT / "data/revision_votos_actores.csv"
OUT = ROOT / "resultados/analisis_descriptivo"
LABELS = ["hawkish", "dovish", "neutral"]
STOP = set("de la el que en y los las del se por un una con para su al lo como es no más mas ha sus este esta sobre son fue han si ya entre le les o e a ante desde hasta durante mediante señor senor señora senora consejero consejera presidente vicepresidente gerente banco central chile senala indica menciona manifiesta expresa agrega hace presente ano respecto tambien intervencion inicia continua continuacion prosigue aludido referido ofrece palabra agradece comentarios concede consulta opinion tiene porque pero hay ello ser muy puede pueden parte caso punto forma manera bien solo dado reunion sesion".split())
TOPIC_STOP = STOP | set("asimismo estos estas ese esa esos esas esto cual cuales cada otro otra otros otras luego aun tanto todo toda todos todas mismo misma dentro fuera vez dos tras segun siendo hacer hecho hacia donde cuando quienes quien mientras aunque embargo cuanto encuentra considera sostiene plantea parece juicio terminos general actual oportunidad antecedentes informacion analisis situacion contexto escenario don doña dona horas staff".split())


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
    data = data.drop(columns=["orden_habla", "subindice"], errors="ignore").merge(order, on="intervencion_id", how="left", validate="one_to_one")
    if data[["orden_habla", "subindice"]].eq("").any().any(): raise ValueError("Faltan campos de orden tras unir el corpus")
    train_labels = train.set_index("intervencion_id").etiqueta_v3.to_dict(); gold_labels = gold.set_index("intervencion_id").etiqueta_v3.to_dict(); gold_include = gold.set_index("intervencion_id").incluir_evaluacion.to_dict()
    train_relevance = train.set_index("intervencion_id").relevancia_v3.astype(int).to_dict(); gold_relevance = gold.set_index("intervencion_id").es_relevante_v3.astype(int).to_dict()
    def best(row):
        iid = row.intervencion_id
        if iid in train_labels: return train_labels[iid], "etiqueta_validada_entrenamiento"
        if iid in gold_labels: return (gold_labels[iid], "gold_evaluacion_ciega") if gold_include[iid] == "true" else ("no_puedo_decidir", "gold_no_decidible")
        return row.prediccion_v3, "prediccion_wc600"
    assigned = data.apply(best, axis=1, result_type="expand"); data["etiqueta_analisis"], data["procedencia_etiqueta"] = assigned[0], assigned[1]
    data["relevancia_analisis"] = data.apply(lambda row: train_relevance.get(row.intervencion_id, gold_relevance.get(row.intervencion_id, int(row.pred_relevancia_v3))), axis=1)
    data["procedencia_relevancia"] = data.apply(lambda row: "etiqueta_validada_entrenamiento" if row.intervencion_id in train_relevance else ("gold_evaluacion_ciega" if row.intervencion_id in gold_relevance else "prediccion_wc600"), axis=1)
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
    # Tópicos descubiertos solo desde texto: NMF no recibe topico_humano ni keywords_humano.
    sentence_texts = [sentence for text in valid.texto for sentence in re.split(r"(?<=[.!?;])\s+", str(text)) if len(sentence) >= 80]
    actor_terms = set(re.findall(r"(?u)\b\w\w+\b", strip_accents_unicode(" ".join(valid.actor.unique()).lower())))
    topic_stop = sorted(TOPIC_STOP | actor_terms)
    topic_vector = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1,2), min_df=12, max_df=0.5, max_features=20000, stop_words=topic_stop, sublinear_tf=True)
    sentence_tfidf = topic_vector.fit_transform(sentence_texts); topic_names = topic_vector.get_feature_names_out(); sentence_binary = sentence_tfidf.copy(); sentence_binary.data[:] = 1
    sentence_df = np.asarray(sentence_binary.sum(axis=0)).ravel(); candidate_ks=[6,8,10,12,14,16,18,20,22,24]; benchmark_models={}; benchmark_rows=[]; benchmark_topics=[]
    def topic_quality(model, matrix, binary, document_frequency, feature_names):
        weights=model.transform(matrix); totals=weights.sum(axis=1,keepdims=True); normalized=np.divide(weights,totals,out=np.zeros_like(weights),where=totals>0); prevalence=normalized.mean(axis=0)
        similarity=cosine_similarity(model.components_); k=len(model.components_); redundancy=float((similarity.sum()-k)/(k*(k-1)))
        top_indices=[component.argsort()[-10:] for component in model.components_]; diversity=len(set(np.concatenate(top_indices)))/(10*k); npmi=[]; n_docs=matrix.shape[0]
        for indices in top_indices:
            for left_pos,left in enumerate(indices):
                for right in indices[left_pos+1:]:
                    cooccurrence=binary[:,left].multiply(binary[:,right]).getnnz()
                    if cooccurrence:
                        p_pair=cooccurrence/n_docs; npmi.append(np.log(p_pair/((document_frequency[left]/n_docs)*(document_frequency[right]/n_docs)))/(-np.log(p_pair)))
                    else: npmi.append(-1.0)
        p=prevalence/prevalence.sum(); effective=float(np.exp(-(p*np.log(p+1e-15)).sum()))
        return {"error_reconstruccion":float(model.reconstruction_err_),"coherencia_npmi_top10":float(np.mean(npmi)),"diversidad_top10":float(diversity),"redundancia_coseno_media":redundancy,"prevalencia_minima":float(prevalence.min()),"prevalencia_maxima":float(prevalence.max()),"numero_efectivo_topicos":effective,"filas_vector_cero":int((totals.ravel()==0).sum())}
    for k in candidate_ks:
        model=NMF(n_components=k,init="nndsvda",random_state=20260918,max_iter=500,alpha_W=0.00005,alpha_H=0.00005).fit(sentence_tfidf); benchmark_models[k]=model
        metrics=topic_quality(model,sentence_tfidf,sentence_binary,sentence_df,topic_names); stability=[]
        for seed in [20260919,20260920]:
            alternate=NMF(n_components=k,init="nndsvdar",random_state=seed,max_iter=500,alpha_W=0.00005,alpha_H=0.00005).fit(sentence_tfidf)
            similarity=cosine_similarity(model.components_,alternate.components_); rows_match,cols_match=linear_sum_assignment(-similarity); stability.append(float(similarity[rows_match,cols_match].mean()))
        metrics.update({"unidad":"oracion_min_80","k":k,"estabilidad_media":float(np.mean(stability)),"n_unidades":len(sentence_texts),"vocabulario":len(topic_names)}); benchmark_rows.append(metrics)
        sentence_weights=model.transform(sentence_tfidf); sums=sentence_weights.sum(axis=1,keepdims=True); sentence_weights=np.divide(sentence_weights,sums,out=np.zeros_like(sentence_weights),where=sums>0); prevalence=sentence_weights.mean(axis=0)
        for local_id,(component,share) in enumerate(zip(model.components_, prevalence, strict=True), 1):
            terms=topic_names[component.argsort()[::-1][:20]]; benchmark_topics.append({"k":k,"topico_local":f"k{k}_tema_{local_id:02d}","terminos_top5":" | ".join(terms[:5]),"terminos_top20":" | ".join(terms),"prevalencia":float(share)})
    benchmark=pd.DataFrame(benchmark_rows); error_k6=float(benchmark.loc[benchmark.k.eq(6),"error_reconstruccion"].iloc[0]); benchmark["reduccion_error_vs_k6"]=(error_k6-benchmark.error_reconstruccion)/error_k6
    benchmark.to_csv(out / "segmentacion_nmf_benchmark.csv",index=False,lineterminator="\n"); pd.DataFrame(benchmark_topics).to_csv(out / "segmentacion_nmf_topicos_candidatos.csv",index=False,lineterminator="\n")
    n_topics=14; topic_model=benchmark_models[n_topics]
    doc_weights = topic_model.transform(topic_vector.transform(valid.texto)); row_sums = doc_weights.sum(axis=1, keepdims=True)
    doc_weights = np.divide(doc_weights, row_sums, out=np.zeros_like(doc_weights), where=row_sums>0)
    prevalence_order = np.argsort(doc_weights.mean(axis=0))[::-1]; doc_weights = doc_weights[:,prevalence_order]; components = topic_model.components_[prevalence_order]
    topic_ids = [f"tema_nmf_{i:02d}" for i in range(1,n_topics+1)]; topic_names = topic_vector.get_feature_names_out(); topic_rows=[]
    topic_audit = {
        "tema_nmf_01":("Actividad, demanda y crecimiento trimestral","economico","alta","Ciclo interno de corto plazo","Los términos y ejemplos cubren actividad, demanda, consumo, inversión, PIB y velocidades trimestrales."),
        "tema_nmf_02":("Mercado laboral, empleo y salarios","economico","alta","Condiciones del mercado laboral","Empleo, desempleo, salarios y trabajo dominan; 'mercado' aislado puede ser ambiguo."),
        "tema_nmf_03":("Precios de commodities: petróleo, cobre y alimentos","economico","alta","Precios de materias primas","Los términos y ejemplos son específicos de petróleo, cobre, gasolina, alimentos y commodities."),
        "tema_nmf_04":("Proceso técnico del staff y opciones de política","institucional_documental","media","Interacciones con divisiones técnicas","Mezcla División Estudios, opciones, minuta y divisiones financiera/operaciones; no es un dominio económico único."),
        "tema_nmf_05":("Decisión, mantención y acuerdo de TPM","decision_formal","alta","Formalización de la decisión monetaria","Los ejemplos principales son votos, acuerdos y mantención de la TPM, no política monetaria en sentido temático amplio."),
        "tema_nmf_06":("Participación de Hacienda y secuencia de sesión","institucional_documental","alta","Intervenciones del Ministro de Hacienda","Combina Ministro/Hacienda con incorporación, exposición, votación y reanudación de la sesión."),
        "tema_nmf_07":("Coyuntura reciente y comparación con el último IPoM","temporal_documental","media","Actualización mensual de antecedentes","Meses, último mes, registros e IPoM indican actualización temporal; no identifica un sector económico."),
        "tema_nmf_08":("Economías emergentes, desarrolladas y mercados globales","economico","alta","Entorno económico internacional comparado","Contrasta emergentes y desarrolladas e incluye mercados, riesgo, monedas, Europa, América Latina y China."),
        "tema_nmf_09":("Inflación, expectativas y meta","economico","alta","Dinámica y expectativas de inflación","Inflación, expectativas, meta, subyacente, IPC y horizonte de política son coherentes entre términos y ejemplos."),
        "tema_nmf_10":("Tipo de cambio real y nominal","economico","alta","Apreciación y depreciación cambiaria","Tipo de cambio, apreciación, depreciación, dólar y peso aparecen de forma consistente."),
        "tema_nmf_11":("Transición de presentaciones macroeconómicas","institucional_documental","alta","Presentaciones y apertura de comentarios","Los ejemplos son agradecimientos, transición de exposiciones y apertura de consultas, no contenido internacional sustantivo."),
        "tema_nmf_12":("Plazos y tasas de interés","economico_financiero","media","Estructura temporal de tasas y deuda","Incluye tasas cortas/largas y vencimientos de bonos; también menciona horizontes de inflación, por lo que el nombre debe ser amplio."),
        "tema_nmf_13":("Estados Unidos, zona euro y economías avanzadas","economico","alta","Entorno internacional avanzado","Estados Unidos domina, acompañado por zona euro, Europa, Japón y China; no representa todo el escenario internacional."),
        "tema_nmf_14":("Magnitudes en puntos base: TPM y diferenciales","decision_financiero_mixto","media","Cambios de TPM y spreads en puntos base","Aunque predominan 25/50 pb y TPM, los ejemplos también incluyen CDS y spreads; llamarlo solo magnitud de TPM sería incorrecto.")}
    for topic_id, component, prevalence in zip(topic_ids, components, doc_weights.mean(axis=0), strict=True):
        ordered = component.argsort()[::-1]; terms = topic_names[ordered[:20]]; audited=topic_audit[topic_id]
        topic_rows.append({"topico_modelo":topic_id,"nombre_auditado":audited[0],"tipo_componente":audited[1],"confianza_nombre":audited[2],"etiqueta_automatica_top5":" | ".join(terms[:5]),"terminos_top20":" | ".join(terms),"peso_medio_corpus":float(prevalence),"origen":"NMF_solo_texto_sin_topico_humano_ni_keywords"})
    pd.DataFrame(topic_rows).to_csv(out / "topicos_modelo_nmf.csv", index=False, lineterminator="\n")
    top_order = np.argsort(doc_weights, axis=1)[:,::-1]; topic_assignment = valid[["intervencion_id","meeting_id","fecha","anio","actor","tipo_actor"]].reset_index(drop=True).copy()
    topic_assignment["topico_modelo_1"] = [topic_ids[i] for i in top_order[:,0]]; topic_assignment["peso_topico_1"] = doc_weights[np.arange(len(valid)),top_order[:,0]]
    topic_assignment["topico_modelo_2"] = [topic_ids[i] for i in top_order[:,1]]; topic_assignment["peso_topico_2"] = doc_weights[np.arange(len(valid)),top_order[:,1]]
    topic_assignment["entropia_topicos"] = -(np.where(doc_weights>0, doc_weights*np.log(doc_weights+1e-15), 0).sum(axis=1))/np.log(n_topics)
    for index, topic_id in enumerate(topic_ids): topic_assignment[f"peso_{topic_id}"] = doc_weights[:,index]
    topic_assignment.to_csv(out / "asignacion_topicos_modelo_nmf.csv", index=False, lineterminator="\n")
    audit_rows=[]; valid_reset=valid.reset_index(drop=True); topic_table=pd.DataFrame(topic_rows).set_index("topico_modelo")
    for idx,topic_id in enumerate(topic_ids):
        representative=np.argsort(doc_weights[:,idx])[::-1][:5]; audited=topic_audit[topic_id]
        audit_rows.append({"topico_modelo":topic_id,"nombre_auditado":audited[0],"tipo_componente":audited[1],"confianza_nombre":audited[2],"nombre_alternativo":audited[3],"justificacion_y_limite":audited[4],"etiqueta_automatica_top5":topic_table.at[topic_id,"etiqueta_automatica_top5"],"terminos_top20":topic_table.at[topic_id,"terminos_top20"],"ids_representativos":" | ".join(valid_reset.iloc[representative].intervencion_id),"textos_representativos":" || ".join(valid_reset.iloc[representative].texto.str.replace(r"\s+"," ",regex=True).str.slice(0,500))})
    pd.DataFrame(audit_rows).to_csv(out / "auditoria_nombres_topicos_nmf.csv",index=False,lineterminator="\n")
    # Prueba directa K=6 solicitada para el radar: se conserva aunque no sea la solución recomendada.
    k6_model=benchmark_models[6]; k6_weights=k6_model.transform(topic_vector.transform(valid.texto)); k6_sums=k6_weights.sum(axis=1,keepdims=True); k6_weights=np.divide(k6_weights,k6_sums,out=np.zeros_like(k6_weights),where=k6_sums>0)
    k6_order=np.argsort(k6_weights.mean(axis=0))[::-1]; k6_weights=k6_weights[:,k6_order]; k6_components=k6_model.components_[k6_order]; k6_ids=[f"tema_k6_{i:02d}" for i in range(1,7)]; k6_labels={}; k6_rows=[]
    for topic_id,component,share in zip(k6_ids, k6_components, k6_weights.mean(axis=0), strict=True):
        terms=topic_names[component.argsort()[::-1][:20]]; label=" | ".join(terms[:5]); k6_labels[topic_id]=label; k6_rows.append({"topico_k6":topic_id,"etiqueta_automatica_top5":label,"terminos_top20":" | ".join(terms),"peso_medio_corpus":float(share)})
    pd.DataFrame(k6_rows).to_csv(out / "segmentacion_nmf_k6_topicos.csv",index=False,lineterminator="\n")
    k6_documents=valid[["tipo_actor","actor"]].reset_index(drop=True).copy()
    for idx,topic_id in enumerate(k6_ids): k6_documents[topic_id]=k6_weights[:,idx]
    k6_actor=k6_documents.groupby(["tipo_actor","actor"],as_index=False)[k6_ids].mean().merge(valid.groupby(["tipo_actor","actor"]).size().rename("n_intervenciones").reset_index(),on=["tipo_actor","actor"],validate="one_to_one")
    k6_long=k6_actor.melt(id_vars=["tipo_actor","actor","n_intervenciones"],value_vars=k6_ids,var_name="topico_k6",value_name="peso_medio"); k6_long["muestra_apta_radar"]=k6_long.tipo_actor.eq("miembro_consejo")&k6_long.n_intervenciones.ge(100); k6_long["percentil_0_100"]=np.nan
    for _topic_id,group in k6_long[k6_long.muestra_apta_radar].groupby("topico_k6"):
        ranks=group.peso_medio.rank(method="average"); k6_long.loc[group.index,"percentil_0_100"]=100*(ranks-1)/(len(group)-1)
    k6_long["etiqueta_automatica_top5"]=k6_long.topico_k6.map(k6_labels); k6_long.to_csv(out / "radar_nmf_k6_prueba.csv",index=False,lineterminator="\n")
    k6_long.pivot(index=["tipo_actor","actor","n_intervenciones","muestra_apta_radar"],columns="topico_k6",values="percentil_0_100").reset_index().to_csv(out / "radar_nmf_k6_prueba_ancho.csv",index=False,lineterminator="\n")
    # Sensibilidad a la unidad documental con K=14.
    unit_rows=[benchmark[benchmark.k.eq(14)].iloc[0].to_dict()]; unit_topics=[row for row in benchmark_topics if row["k"]==14]
    unit_topics=[{"unidad":"oracion_min_80",**row} for row in unit_topics]
    unit_sets={"intervencion":(valid.texto.tolist(),12),"actor_reunion":(valid.groupby(["meeting_id","actor"]).texto.apply(lambda values:" ".join(values)).tolist(),5)}
    for unit,(texts,min_df_unit) in unit_sets.items():
        vector_unit=TfidfVectorizer(strip_accents="unicode",lowercase=True,ngram_range=(1,2),min_df=min_df_unit,max_df=0.5,max_features=20000,stop_words=topic_stop,sublinear_tf=True); matrix_unit=vector_unit.fit_transform(texts); names_unit=vector_unit.get_feature_names_out(); binary_unit=matrix_unit.copy(); binary_unit.data[:]=1; df_unit=np.asarray(binary_unit.sum(axis=0)).ravel()
        model_unit=NMF(n_components=14,init="nndsvda",random_state=20260918,max_iter=500,alpha_W=0.00005,alpha_H=0.00005).fit(matrix_unit); metrics=topic_quality(model_unit,matrix_unit,binary_unit,df_unit,names_unit); stability=[]
        for seed in [20260919,20260920]:
            alternate=NMF(n_components=14,init="nndsvdar",random_state=seed,max_iter=500,alpha_W=0.00005,alpha_H=0.00005).fit(matrix_unit); similarity=cosine_similarity(model_unit.components_,alternate.components_); row_match,col_match=linear_sum_assignment(-similarity); stability.append(float(similarity[row_match,col_match].mean()))
        metrics.update({"unidad":unit,"k":14,"estabilidad_media":float(np.mean(stability)),"n_unidades":len(texts),"vocabulario":len(names_unit),"reduccion_error_vs_k6":np.nan}); unit_rows.append(metrics)
        weights_unit=model_unit.transform(matrix_unit); totals_unit=weights_unit.sum(axis=1,keepdims=True); weights_unit=np.divide(weights_unit,totals_unit,out=np.zeros_like(weights_unit),where=totals_unit>0)
        for local_id,(component,share) in enumerate(zip(model_unit.components_, weights_unit.mean(axis=0), strict=True), 1):
            terms=names_unit[component.argsort()[::-1][:20]]; unit_topics.append({"unidad":unit,"k":14,"topico_local":f"{unit}_tema_{local_id:02d}","terminos_top5":" | ".join(terms[:5]),"terminos_top20":" | ".join(terms),"prevalencia":float(share)})
    pd.DataFrame(unit_rows).to_csv(out / "segmentacion_nmf_unidades.csv",index=False,lineterminator="\n"); pd.DataFrame(unit_topics).to_csv(out / "segmentacion_nmf_unidades_topicos.csv",index=False,lineterminator="\n")
    k6_metrics=benchmark[benchmark.k.eq(6)].iloc[0]; k14_metrics=benchmark[benchmark.k.eq(14)].iloc[0]; k18_metrics=benchmark[benchmark.k.eq(18)].iloc[0]; k20_metrics=benchmark[benchmark.k.eq(20)].iloc[0]; k22_metrics=benchmark[benchmark.k.eq(22)].iloc[0]; k24_metrics=benchmark[benchmark.k.eq(24)].iloc[0]
    save_json(out / "segmentacion_nmf_seleccion.json", {"k_evaluados":candidate_ks,"k_seleccionado":14,"k6_probado":True,"k_hasta_24_probado":True,"conclusion_k6":"Alta coherencia y estabilidad, pero un componente concentra cerca de 46% y solo tres de seis componentes son dominios económicos sustantivos; los demás capturan estructura/decisión. No se recomienda usar sus seis componentes como seis habilidades FIFA.","razon_k14":"Mantiene estabilidad prácticamente perfecta y diversidad alta, reduce la prevalencia máxima a cerca de 15%, y es el primer candidato que separa actividad, trabajo, inflación, commodities, tipo de cambio y tasas. K=20/22/24 fragmentan actividad, inflación, tasas y escenario externo, y pierden diversidad sin aportar ejes necesarios al radar.","comparacion_clave":{"k6":{"coherencia_npmi":float(k6_metrics.coherencia_npmi_top10),"prevalencia_maxima":float(k6_metrics.prevalencia_maxima),"estabilidad":float(k6_metrics.estabilidad_media)},"k14":{"coherencia_npmi":float(k14_metrics.coherencia_npmi_top10),"prevalencia_maxima":float(k14_metrics.prevalencia_maxima),"diversidad":float(k14_metrics.diversidad_top10),"estabilidad":float(k14_metrics.estabilidad_media)},"k18":{"coherencia_npmi":float(k18_metrics.coherencia_npmi_top10),"diversidad":float(k18_metrics.diversidad_top10),"estabilidad":float(k18_metrics.estabilidad_media)},"k20":{"diversidad":float(k20_metrics.diversidad_top10),"estabilidad":float(k20_metrics.estabilidad_media)},"k22":{"diversidad":float(k22_metrics.diversidad_top10),"estabilidad":float(k22_metrics.estabilidad_media)},"k24":{"coherencia_npmi":float(k24_metrics.coherencia_npmi_top10),"diversidad":float(k24_metrics.diversidad_top10),"estabilidad":float(k24_metrics.estabilidad_media),"prevalencia_maxima":float(k24_metrics.prevalencia_maxima)}},"unidad_seleccionada":"oracion_min_80","razon_unidad":"Intervención y actor-reunión mezclan contenido económico con fórmulas procedimentales; la oración separa mejor dominios semánticos. La asignación final se proyecta luego a cada intervención.","criterio":"Selección multicriterio: coherencia, estabilidad, diversidad, redundancia, balance de prevalencia e interpretación; el error de reconstrucción no se usa solo porque siempre mejora al aumentar K."})
    def aggregate_model_topics(columns, filename):
        weights = topic_assignment[columns].join(pd.DataFrame(doc_weights, columns=topic_ids)); long = weights.melt(id_vars=columns, var_name="topico_modelo", value_name="peso")
        dominant = topic_assignment.groupby(columns+["topico_modelo_1"]).size().rename("n_dominante").reset_index().rename(columns={"topico_modelo_1":"topico_modelo"})
        result = long.groupby(columns+["topico_modelo"], as_index=False).agg(peso_medio=("peso","mean"),peso_total=("peso","sum")).merge(dominant, on=columns+["topico_modelo"], how="left")
        result["n_dominante"] = result.n_dominante.fillna(0).astype(int); result["ranking"] = result.groupby(columns).peso_medio.rank(method="first", ascending=False).astype(int)
        result.sort_values(columns+["ranking"]).to_csv(out / filename, index=False, lineterminator="\n")
    aggregate_model_topics(["meeting_id","fecha","anio"], "topicos_modelo_por_reunion.csv")
    aggregate_model_topics(["anio"], "topicos_modelo_por_anio.csv")
    aggregate_model_topics(["actor"], "topicos_modelo_por_actor.csv")
    radar_axes = {
        "actividad_demanda_ciclo":["tema_nmf_01"], "mercado_laboral_empleo":["tema_nmf_02"], "inflacion_expectativas_meta":["tema_nmf_09"],
        "entorno_externo_commodities_economias":["tema_nmf_03","tema_nmf_08","tema_nmf_13"], "tipo_cambio_real_nominal":["tema_nmf_10"], "tasas_interes_plazos":["tema_nmf_12"]}
    radar_documents = topic_assignment[["actor","tipo_actor"]].copy()
    for axis, topics in radar_axes.items(): radar_documents[axis] = topic_assignment[[f"peso_{topic}" for topic in topics]].sum(axis=1)
    radar_actor = radar_documents.groupby(["tipo_actor","actor"], as_index=False)[list(radar_axes)].mean()
    actor_counts = valid.groupby(["tipo_actor","actor"]).size().rename("n_intervenciones").reset_index(); radar_actor = actor_counts.merge(radar_actor, on=["tipo_actor","actor"], how="left", validate="one_to_one")
    radar_long = radar_actor.melt(id_vars=["tipo_actor","actor","n_intervenciones"], value_vars=list(radar_axes), var_name="eje_radar", value_name="peso_medio_bruto")
    totals = radar_long.groupby(["tipo_actor","actor"]).peso_medio_bruto.transform("sum"); radar_long["proporcion_seis_ejes"] = radar_long.peso_medio_bruto / totals
    corpus_axes = {axis:float(radar_documents[axis].mean()) for axis in radar_axes}; corpus_total=sum(corpus_axes.values()); corpus_share={axis:value/corpus_total for axis,value in corpus_axes.items()}
    radar_long["proporcion_corpus"] = radar_long.eje_radar.map(corpus_share); radar_long["indice_especializacion_base100"] = 100*radar_long.proporcion_seis_ejes/radar_long.proporcion_corpus
    radar_long["muestra_apta_radar"] = radar_long.tipo_actor.eq("miembro_consejo") & radar_long.n_intervenciones.ge(100); radar_long["puntaje_fifa_percentil_0_100"] = np.nan
    for _axis, group in radar_long[radar_long.muestra_apta_radar].groupby("eje_radar"):
        ranks=group.indice_especializacion_base100.rank(method="average"); radar_long.loc[group.index,"puntaje_fifa_percentil_0_100"] = 100*(ranks-1)/(len(group)-1)
    radar_long["componentes_nmf"] = radar_long.eje_radar.map(lambda axis:"|".join(radar_axes[axis])); radar_long.sort_values(["actor","eje_radar"]).to_csv(out / "radar_tematico_actores.csv", index=False, lineterminator="\n")
    radar_wide = radar_long.pivot(index=["tipo_actor","actor","n_intervenciones","muestra_apta_radar"], columns="eje_radar", values="puntaje_fifa_percentil_0_100").reset_index(); radar_wide.to_csv(out / "radar_tematico_actores_ancho.csv", index=False, lineterminator="\n")
    # Evolución de los mismos seis ejes, para que el tiempo y las tarjetas sean comparables.
    temporal_documents = topic_assignment[["meeting_id","fecha","anio"]].copy()
    for axis, topics in radar_axes.items(): temporal_documents[axis] = topic_assignment[[f"peso_{topic}" for topic in topics]].sum(axis=1)
    def temporal_axis_table(columns):
        aggregations = {"n_intervenciones":("meeting_id","size"), **{axis:(axis,"mean") for axis in radar_axes}}
        grouped_time = temporal_documents.groupby(columns, as_index=False).agg(**aggregations)
        long = grouped_time.melt(id_vars=columns+["n_intervenciones"], value_vars=list(radar_axes), var_name="eje_tematico", value_name="peso_medio_bruto")
        total = long.groupby(columns).peso_medio_bruto.transform("sum"); long["proporcion_seis_ejes"] = long.peso_medio_bruto/total
        long["proporcion_corpus"] = long.eje_tematico.map(corpus_share); long["indice_vs_corpus_base100"] = 100*long.proporcion_seis_ejes/long.proporcion_corpus
        long["ranking_periodo"] = long.groupby(columns).proporcion_seis_ejes.rank(method="first", ascending=False).astype(int)
        return long
    evolution_meeting = temporal_axis_table(["meeting_id","fecha","anio"]).sort_values(["fecha","eje_tematico"])
    evolution_meeting["media_movil_12_reuniones"] = evolution_meeting.groupby("eje_tematico").proporcion_seis_ejes.transform(lambda values:values.rolling(12,min_periods=6).mean())
    evolution_meeting["cambio_12_reuniones"] = evolution_meeting.groupby("eje_tematico").proporcion_seis_ejes.diff(12)
    evolution_meeting.to_csv(out / "evolucion_topicos_modelo_por_reunion.csv", index=False, lineterminator="\n")
    evolution_year = temporal_axis_table(["anio"]).sort_values(["anio","eje_tematico"]); evolution_year["cambio_anual"] = evolution_year.groupby("eje_tematico").proporcion_seis_ejes.diff()
    evolution_year.to_csv(out / "evolucion_topicos_modelo_anual.csv", index=False, lineterminator="\n")
    trend_rows=[]
    for axis, group in evolution_year.groupby("eje_tematico"):
        group=group.sort_values("anio"); years=group.anio.astype(int).to_numpy(); shares=group.proporcion_seis_ejes.to_numpy(); maximum=group.loc[group.proporcion_seis_ejes.idxmax()]; minimum=group.loc[group.proporcion_seis_ejes.idxmin()]
        trend_rows.append({"eje_tematico":axis,"proporcion_2005":shares[0],"proporcion_2015":shares[-1],"cambio_2005_2015":shares[-1]-shares[0],"pendiente_anual":float(np.polyfit(years,shares,1)[0]),"anio_maximo":int(maximum.anio),"proporcion_maxima":maximum.proporcion_seis_ejes,"anio_minimo":int(minimum.anio),"proporcion_minima":minimum.proporcion_seis_ejes})
    pd.DataFrame(trend_rows).sort_values("cambio_2005_2015", ascending=False).to_csv(out / "evolucion_topicos_modelo_resumen.csv", index=False, lineterminator="\n")
    save_json(out / "evolucion_topicos_modelo_metodo.json", {"unidad":"Acta/reunión y año", "ejes_componentes_nmf":radar_axes, "serie_principal":"proporcion_seis_ejes", "suavizado":"media móvil retrospectiva de 12 reuniones; disponible desde 6 observaciones", "cambio":"diferencia contra 12 reuniones antes o año anterior", "advertencia":"Cambios descriptivos en atención textual; no miden por sí solos importancia económica ni causalidad."})
    save_json(out / "radar_tematico_metodo.json", {"objetivo":"Tarjeta tipo FIFA de énfasis temático relativo, no habilidad ni calidad", "ejes_componentes_nmf":radar_axes, "alternativa_k6_evaluada":"radar_nmf_k6_prueba.csv; descartada como principal porque mezcla tres ejes económicos con estructura/decisión y tiene concentración excesiva", "componentes_excluidos":["tema_nmf_04","tema_nmf_05","tema_nmf_06","tema_nmf_07","tema_nmf_11","tema_nmf_14"], "razon_exclusion":"Los temas 04/06/07/11 son estructura documental; 05 es decisión común de TPM; 14 mezcla magnitudes de TPM con spreads y CDS. Usarlos como especialización sería circular, heterogéneo o ambiguo.", "universo_percentiles":"Solo miembros del Consejo con al menos 100 intervenciones", "calculo":["sumar pesos NMF por eje", "promediar por actor", "renormalizar entre seis ejes", "dividir por proporción corpus (base 100)", "convertir a percentil 0-100 entre actores elegibles"], "advertencia":"Un valor alto indica énfasis relativo. No mide competencia, influencia ni desempeño."})
    save_json(out / "topicos_modelo_metodo.json", {"metodo":"NMF sobre TF-IDF de oraciones", "n_topicos":n_topics, "seleccion":"Benchmark K=6,8,10,12,14,16,18,20,22,24; se selecciona K=14 por balance multicriterio", "benchmark":"segmentacion_nmf_benchmark.csv", "sensibilidad_unidad":"segmentacion_nmf_unidades.csv", "auditoria_nombres":"auditoria_nombres_topicos_nmf.csv: 20 términos + 5 intervenciones representativas, alternativa, confianza y límite", "n_oraciones_ajuste":len(sentence_texts), "longitud_minima_oracion":80, "ngram_range":[1,2], "min_df":12, "max_df":0.5, "max_features":20000, "semilla":20260918, "columnas_humanas_usadas":[], "advertencia":"Los IDs y términos son patrones estadísticos exploratorios, no categorías humanas ni salida de W+C+600."})
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
    agreements = agreements.sort_values("fecha"); agreements["acuerdo_tpm_previa"] = agreements.acuerdo_tpm_objetivo.shift(1)
    delta_pb = agreements.acuerdo_tpm_objetivo.diff().abs() * 100
    agreements["acuerdo_magnitud_pb_final"] = agreements.acuerdo_magnitud_pb.fillna(delta_pb)
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
    base_votes["voto_magnitud_pb_final"] = base_votes.voto_magnitud_pb
    base_votes["voto_tpm_objetivo_final"] = base_votes.voto_tpm_objetivo
    revision_magnitude = pd.to_numeric(base_votes.magnitud_pb_revision, errors="coerce"); revision_target = pd.to_numeric(base_votes.tpm_objetivo_revision, errors="coerce")
    base_votes.loc[reviewed & revision_magnitude.notna(), "voto_magnitud_pb_final"] = revision_magnitude
    base_votes.loc[reviewed & revision_target.notna(), "voto_tpm_objetivo_final"] = revision_target
    same_as_agreement = base_votes.voto_accion_final.eq(base_votes.acuerdo_accion)
    base_votes.loc[same_as_agreement & base_votes.voto_magnitud_pb_final.isna(), "voto_magnitud_pb_final"] = base_votes.acuerdo_magnitud_pb_final
    base_votes.loc[same_as_agreement & base_votes.voto_tpm_objetivo_final.isna(), "voto_tpm_objetivo_final"] = base_votes.acuerdo_tpm_objetivo
    base_votes.loc[base_votes.voto_accion_final.eq("mantener") & base_votes.voto_magnitud_pb_final.isna(), "voto_magnitud_pb_final"] = 0.0
    meeting_magnitude = base_votes.groupby("meeting_id").voto_magnitud_pb_final.transform("median")
    base_votes.loc[same_as_agreement & base_votes.voto_magnitud_pb_final.isna(), "voto_magnitud_pb_final"] = meeting_magnitude
    missing_target = base_votes.voto_tpm_objetivo_final.isna() & base_votes.voto_accion_final.ne("no_extraido") & base_votes.acuerdo_tpm_previa.notna()
    direction = base_votes.voto_accion_final.map({"subir":1.0,"bajar":-1.0,"mantener":0.0})
    base_votes.loc[missing_target, "voto_tpm_objetivo_final"] = base_votes.loc[missing_target, "acuerdo_tpm_previa"] + direction[missing_target] * base_votes.loc[missing_target, "voto_magnitud_pb_final"] / 100
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
        meaningful = lambda term, own_tokens=actor_tokens: not any(token in own_tokens for token in term.split()) and any(token not in STOP for token in term.split())
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
        hits=valid[normalized.map(lambda x, current=pattern: bool(current.search(x)))].head(3)
        for _, row in hits.iterrows(): contexts.append({"ngram":term.ngram,"distintivo_de":term.distintivo_de,"intervencion_id":row.intervencion_id,"meeting_id":row.meeting_id,"etiqueta_analisis":row.etiqueta_analisis,"texto":row.texto})
    pd.DataFrame(contexts).to_csv(out / "lexico_contextos_h_d.csv", index=False, lineterminator="\n")
    outputs = sorted(p.name for p in out.iterdir() if p.is_file())
    summary = {"filas":len(data),"filas_validas":len(valid),"no_decidibles":len(data)-len(valid),"relevantes":int(data.relevancia_analisis.sum()),"irrelevantes":int((data.relevancia_analisis==0).sum()),"procedencia":data.procedencia_etiqueta.value_counts().to_dict(),"distribucion_etiqueta_analisis":valid.etiqueta_analisis.value_counts().to_dict(),"reuniones":valid.meeting_id.nunique(),"actores":valid.actor.nunique(),"topicos":valid.topico_humano.nunique(),"topicos_humanos":valid.topico_humano.nunique(),"topicos_modelo_nmf":n_topics,"topicos_nombres_auditados":len(topic_audit),"topicos_nombre_confianza_media":sum(values[2]=="media" for values in topic_audit.values()),"segmentacion_k_evaluados":candidate_ks,"segmentacion_k_seleccionado":n_topics,"segmentacion_k6_probado":True,"segmentacion_k_hasta24_probado":True,"oraciones_ajuste_topicos_modelo":len(sentence_texts),"ejes_radar_tematico":len(radar_axes),"actores_aptos_radar":int(radar_long[radar_long.muestra_apta_radar].actor.nunique()),"filas_evolucion_topicos_reunion":len(evolution_meeting),"filas_evolucion_topicos_anual":len(evolution_year),"vocabulario_1_a_4_min_df_5":len(names),"actores_con_vocabulario_distintivo":len({x["actor"] for x in actor_vocab}),"decisiones_institucionales_proxy":len(decision_rows),"candidatos_votos_explicitos":len(votes),"pares_reunion_actor_con_candidato_voto":len(vote_matrix),"acuerdos_consejo_extraidos":len(agreements),"filas_base_votos_acta_actor":len(base_votes),"votos_con_accion_extraida":int(base_votes.voto_accion.ne("no_extraido").sum()),"votos_inferidos_por_unanimidad":int(base_votes.fuente_voto.eq("inferido_de_unanimidad_textual").sum()),"votos_revisados_textualmente":int(base_votes.fuente_voto_final.eq("revision_textual_asistida").sum()),"votos_no_extraidos":int(base_votes.voto_accion_final.eq("no_extraido").sum()),"votos_finales_con_magnitud_y_tpm":int((base_votes.voto_accion_final.ne("no_extraido") & base_votes.voto_magnitud_pb_final.notna() & base_votes.voto_tpm_objetivo_final.notna()).sum()),"casos_convergencia_proxy":len(convergence),"nota_convergencia":"Exploratoria: decisión institucional y postura son etiquetas/scores del sistema; candidatos de voto requieren validación textual humana.","nota_neutrales":"Se conservan en tono general y cobertura; balance direccional usa solo H/D.","embeddings_generados":False,"razon_embeddings":"No son parte de W+C+600 ni necesarios para NMF, que usa TF-IDF disperso; se reservan para otra hipótesis."}
    save_json(out / "resumen.json", summary); outputs.append("resumen.json")
    sources = [CLASSIFIED, CORPUS, TRAIN, GOLD, VOTE_REVIEW, Path(__file__)]
    save_json(out / "manifest.json", {"fuentes_sha256":{str(p.relative_to(ROOT)):sha(p) for p in sources},"sha256_salidas":{name:sha(out/name) for name in outputs}})
    return summary
if __name__ == "__main__": print(json.dumps(run(), ensure_ascii=False, indent=2))
