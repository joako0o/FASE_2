"""Empaqueta resultados reproducibles y compactos para el scrollytelling.

No entrena modelos ni cambia resultados canónicos. Separa datos agregados de actas
por año para permitir carga diferida en un sitio estático.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "resultados/analisis_descriptivo"
CORPUS = ROOT / "data/corpus_bcch_2005_2015.csv"
DEFAULT_OUT = ROOT / "datos_web"
TOPIC_IDS = [f"tema_nmf_{i:02d}" for i in range(1, 15)]
RADAR_AXES = {
    "actividad_demanda_ciclo": ["tema_nmf_01"],
    "mercado_laboral_empleo": ["tema_nmf_02"],
    "inflacion_expectativas_meta": ["tema_nmf_09"],
    "entorno_externo_commodities_economias": ["tema_nmf_03", "tema_nmf_08", "tema_nmf_13"],
    "tipo_cambio_real_nominal": ["tema_nmf_10"],
    "tasas_interes_plazos": ["tema_nmf_12"],
}
LABEL_CODE = {"hawkish": "H", "dovish": "D", "neutral": "N", "no_puedo_decidir": "ND"}


def scalar(value):
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return None
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,)): return round(float(value), 6)
    if isinstance(value, (np.bool_,)): return bool(value)
    return value


def rounded(value, digits=5):
    return None if pd.isna(value) else round(float(value), digits)


def records(frame):
    return [{key: scalar(value) for key, value in row.items()} for row in frame.to_dict("records")]


def write_json(path, value, pretty=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2 if pretty else None, separators=None if pretty else (",", ":"), allow_nan=False) + "\n", encoding="utf-8")


def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(out=DEFAULT_OUT, overwrite=False):
    out = Path(out)
    if out.exists():
        if not overwrite: raise FileExistsError(f"Ya existe {out}; usar --sobrescribir")
        shutil.rmtree(out)
    out.mkdir(parents=True)

    master = pd.read_csv(ANALYSIS / "tabla_maestra.csv", keep_default_na=False)
    corpus = pd.read_csv(CORPUS, keep_default_na=False, usecols=["intervencion_id", "texto"])
    master = master.merge(corpus, on="intervencion_id", how="left", validate="one_to_one")
    assignments = pd.read_csv(ANALYSIS / "asignacion_topicos_modelo_nmf.csv", keep_default_na=False)
    assignments = assignments.rename(columns={f"peso_{topic}": topic for topic in TOPIC_IDS})
    data = master.merge(assignments[["intervencion_id", "topico_modelo_1", "peso_topico_1", "topico_modelo_2", "peso_topico_2", "entropia_topicos"] + TOPIC_IDS], on="intervencion_id", how="left", validate="one_to_one")
    for column in ["orden_habla", "subindice", "anio", "relevancia_analisis", "pred_relevancia_v3"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    for column in ["prob_h_no_calibrada", "prob_d_no_calibrada", "prob_n_no_calibrada", "prob_relevancia_no_calibrada", "score_hd_continuo"] + TOPIC_IDS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Catálogo de tópicos: nombres auditados y cruce blando tópico × postura.
    topic_audit = pd.read_csv(ANALYSIS / "auditoria_nombres_topicos_nmf.csv", keep_default_na=False)
    topic_cross = []
    for topic in TOPIC_IDS:
        weights = data[topic]
        by_label = {code: float(weights[data.etiqueta_analisis.eq(label)].sum()) for label, code in LABEL_CODE.items()}
        total = sum(by_label.values()); directional = by_label["H"] + by_label["D"]
        topic_cross.append({"topico_modelo": topic, "masa_por_orientacion": {key: round(value, 6) for key, value in by_label.items()},
            "proporcion_por_orientacion": {key: round(value / total, 6) if total else None for key, value in by_label.items()},
            "balance_direccional": round((by_label["H"] - by_label["D"]) / directional, 6) if directional else None,
            "masa_relevante": round(float(weights[data.relevancia_analisis.eq(1)].sum()) / float(weights.sum()), 6) if weights.sum() else None})
    topic_cross = {row["topico_modelo"]: row for row in topic_cross}
    topics = []
    for row in topic_audit.to_dict("records"):
        topic = row["topico_modelo"]
        topics.append({**{key: scalar(value) for key, value in row.items()}, **topic_cross[topic],
            "eje_radar": next((axis for axis, members in RADAR_AXES.items() if topic in members), None)})
    write_json(out / "topicos.json", {"advertencia": "Los nombres son glosas auditadas posteriores a NMF. La orientación proviene de W+C+600 o de etiquetas humanas identificadas por procedencia.", "topicos": topics}, pretty=True)

    # Estructura documental por quintiles de posición; no equivale a tiempo de habla.
    ordered = data.sort_values(["meeting_id", "orden_habla", "subindice", "intervencion_id"]).copy()
    ordered["posicion_relativa"] = ordered.groupby("meeting_id").cumcount() / ordered.groupby("meeting_id").intervencion_id.transform("size").sub(1).clip(lower=1)
    ordered["fase_documental"] = pd.cut(ordered.posicion_relativa, [-0.001, .2, .4, .6, .8, 1.001], labels=["inicio", "tramo_2", "centro", "tramo_4", "cierre"])
    phases = []
    for phase, group in ordered.groupby("fase_documental", observed=True):
        labels = group.etiqueta_analisis.map(LABEL_CODE).value_counts()
        phases.append({"fase_documental": str(phase), "n_intervenciones": len(group), "proporcion_orientacion": {label: round(int(labels.get(label, 0)) / len(group), 6) for label in ["H", "D", "N", "ND"]},
            "peso_medio_topicos": {topic: round(float(group[topic].mean()), 6) for topic in TOPIC_IDS}})
    write_json(out / "estructura_actas.json", {"metodo": "Quintiles de la posición ordenada dentro de cada acta; describen el documento publicado, no duración, turnos literales ni influencia.", "fases": phases}, pretty=True)

    # Catálogo de actores y perfiles disponibles.
    actor_index = pd.read_csv(ANALYSIS / "indices_por_tipo_y_actor.csv", keep_default_na=False)
    actor_topics = pd.read_csv(ANALYSIS / "topicos_modelo_por_actor.csv").query("ranking <= 5")
    actor_words = pd.read_csv(ANALYSIS / "vocabulario_distintivo_por_actor.csv").query("ranking <= 10")
    radar = pd.read_csv(ANALYSIS / "radar_tematico_actores.csv")
    actor_year = pd.read_csv(ANALYSIS / "indices_actor_por_anio.csv")
    actors = []
    for actor_number, row in enumerate(actor_index.to_dict("records"), 1):
        actor = row["actor"]
        actors.append({"actor_id": actor_number, **{key: scalar(value) for key, value in row.items()},
            "topicos_principales": records(actor_topics[actor_topics.actor.eq(actor)].sort_values("ranking")),
            "vocabulario_distintivo": records(actor_words[actor_words.actor.eq(actor)].sort_values("ranking")),
            "radar": records(radar[radar.actor.eq(actor)].sort_values("eje_radar")),
            "serie_anual": records(actor_year[actor_year.actor.eq(actor)].sort_values("anio"))})
    actor_ids = {row["actor"]: row["actor_id"] for row in actors}
    write_json(out / "actores.json", {"advertencia": "Volumen y énfasis textual no miden habilidad, influencia ni tiempo efectivo de palabra.", "actores": actors})

    # Resumen por reunión con decisión, tópicos, ejes, dispersión entre consejeros y votos trazables.
    meeting_indices = pd.read_csv(ANALYSIS / "indices_por_reunion.csv")
    agreements = pd.read_csv(ANALYSIS / "acuerdo_consejo_por_reunion.csv")
    meeting_topics = pd.read_csv(ANALYSIS / "topicos_modelo_por_reunion.csv").query("ranking <= 5")
    meeting_axes = pd.read_csv(ANALYSIS / "evolucion_topicos_modelo_por_reunion.csv")
    votes = pd.read_csv(ANALYSIS / "base_votos_acta_actor.csv")
    council = data[data.tipo_actor.eq("miembro_consejo")]
    actor_meeting = council.groupby(["meeting_id", "actor"], as_index=False).agg(score_actor=("score_hd_continuo", "mean"), n_intervenciones=("intervencion_id", "size"))
    dispersion = actor_meeting.groupby("meeting_id").agg(n_actores_consejo=("actor", "nunique"), dispersion_score_actores=("score_actor", "std"), rango_score_actores=("score_actor", lambda values: values.max() - values.min())).reset_index()
    relevance = data.groupby("meeting_id").relevancia_analisis.agg(n_relevantes="sum", n_total="size").reset_index(); relevance["proporcion_relevante"] = relevance.n_relevantes / relevance.n_total
    meeting_table = meeting_indices.merge(agreements, on=["meeting_id", "fecha", "anio"], how="left", validate="one_to_one").merge(dispersion, on="meeting_id", how="left", validate="one_to_one").merge(relevance, on="meeting_id", how="left", validate="one_to_one")
    meetings = []
    for row in meeting_table.sort_values(["fecha", "meeting_id"]).to_dict("records"):
        meeting = row["meeting_id"]
        vote_columns = ["actor", "voto_accion_final", "fuente_voto_final", "voto_magnitud_pb_final", "voto_tpm_objetivo_final", "coincide_final_con_acuerdo", "confianza_revision", "nota_revision"]
        meetings.append({**{key: scalar(value) for key, value in row.items()},
            "topicos_principales": records(meeting_topics[meeting_topics.meeting_id.eq(meeting)].sort_values("ranking")),
            "ejes": records(meeting_axes[meeting_axes.meeting_id.eq(meeting)].sort_values("eje_tematico")),
            "votos": records(votes[votes.meeting_id.eq(meeting)][vote_columns])})
    write_json(out / "reuniones.json", {"advertencia": "La dispersión es textual. Los votos conservan fuente y confianza; revisión asistida no equivale a validación humana.", "reuniones": meetings})

    # Series generales para el primer bloque narrativo.
    annual = pd.read_csv(ANALYSIS / "indices_por_anio.csv")
    annual_topics = pd.read_csv(ANALYSIS / "evolucion_topicos_modelo_anual.csv")
    decision_year = agreements.groupby(["anio", "acuerdo_accion"]).size().rename("n").reset_index()
    write_json(out / "series_generales.json", {"orientacion_anual": records(annual), "topicos_anuales": records(annual_topics), "decisiones_por_anio": records(decision_year)}, pretty=True)

    # Índice y actas por año: carga diferida para el explorador.
    meeting_lookup = {row["meeting_id"]: row for row in meetings}
    act_index = []
    for year, year_data in ordered.groupby("anio", sort=True):
        year_meetings = []
        for meeting, group in year_data.groupby("meeting_id", sort=False):
            header = meeting_lookup[meeting]
            turns = []
            for row in group.to_dict("records"):
                human = None
                if row.get("topico_humano") or row.get("keywords_humano"):
                    human = {"topico": row.get("topico_humano") or None, "keywords": row.get("keywords_humano") or None, "origen": "anotacion_humana_historica"}
                turns.append({"id": row["intervencion_id"], "orden": scalar(row["orden_habla"]), "subindice": scalar(row["subindice"]), "actor_id": actor_ids[row["actor"]], "actor": row["actor"], "cargo": row["cargo"], "tipo_actor": row["tipo_actor"], "texto": row["texto"],
                    "relevancia": int(row["relevancia_analisis"]), "procedencia_relevancia": row["procedencia_relevancia"], "orientacion": LABEL_CODE[row["etiqueta_analisis"]], "procedencia_orientacion": row["procedencia_etiqueta"],
                    "modelo_wc600": {"prediccion": LABEL_CODE.get(row["prediccion_v3"], row["prediccion_v3"]), "prob_h": rounded(row["prob_h_no_calibrada"]), "prob_d": rounded(row["prob_d_no_calibrada"]), "prob_n": rounded(row["prob_n_no_calibrada"]), "score_hd": rounded(row["score_hd_continuo"]), "acuerdo_postura": row["acuerdo_miembros"], "pred_relevancia": int(row["pred_relevancia_v3"]), "prob_relevancia": rounded(row["prob_relevancia_no_calibrada"]), "acuerdo_relevancia": row["acuerdo_relevancia_miembros"]},
                    "nmf": {"principal": scalar(row["topico_modelo_1"]), "peso_principal": rounded(row["peso_topico_1"]), "secundario": scalar(row["topico_modelo_2"]), "peso_secundario": rounded(row["peso_topico_2"]), "entropia": rounded(row["entropia_topicos"]), "pesos": [rounded(row[topic]) for topic in TOPIC_IDS]}, "anotacion_humana_historica": human})
            year_meetings.append({"meeting_id": meeting, "fecha": header["fecha"], "decision": {key: header.get(key) for key in ["acuerdo_accion", "acuerdo_magnitud_pb_final", "acuerdo_tpm_previa", "acuerdo_tpm_objetivo", "acuerdo_tipo_textual"]}, "intervenciones": turns})
            act_index.append({"meeting_id": meeting, "fecha": header["fecha"], "anio": int(year), "n_intervenciones": len(turns), "archivo": f"actas/{int(year)}.json"})
        write_json(out / "actas" / f"{int(year)}.json", {"anio": int(year), "reuniones": year_meetings})
    write_json(out / "actas" / "index.json", {"reuniones": act_index}, pretty=True)

    summary = json.loads((ANALYSIS / "resumen.json").read_text(encoding="utf-8"))
    methodology = {"periodo": [2005, 2015], "modelo_postura": "W+C+600", "unidad_explorador": "intervencion registrada en el acta", "modelo_topicos": "NMF K=14 ajustado sobre oraciones y proyectado a intervenciones", "etiquetas_orientacion": {"H": "respalda dirección relativamente más restrictiva", "D": "respalda dirección relativamente más expansiva", "N": "sin dirección respaldada", "ND": "no puedo decidir"}, "advertencias": ["Las actas son registros institucionales, no transcripciones estenográficas.", "H/D/N describe evidencia textual, no identidad política permanente.", "Los nombres NMF son glosas auditadas posteriores al modelo.", "El radar mide énfasis relativo, no habilidad.", "Asociación y secuencia no demuestran influencia ni causalidad."]}
    write_json(out / "metodologia.json", methodology, pretty=True)
    write_json(out / "resumen.json", summary, pretty=True)

    readme = """# Datos para el scrollytelling

Paquete generado por `scripts/preparar_datos_web.py`. No editar los JSON manualmente.

- `resumen.json`: cifras canónicas del corpus.
- `metodologia.json`: definiciones y advertencias obligatorias.
- `series_generales.json`: orientación, tópicos y decisiones por año.
- `topicos.json`: 14 componentes auditados y cruce blando con H/D/N.
- `estructura_actas.json`: distribución por quintil documental.
- `actores.json`: perfiles, radar, tópicos, léxico y serie anual.
- `reuniones.json`: 132 fichas agregadas, acuerdos, dispersión y votos trazables.
- `actas/index.json`: selector de reuniones.
- `actas/2005.json` … `actas/2015.json`: intervenciones para carga diferida.
- `manifest.json`: tamaños y SHA-256.

El frontend debe cargar primero `resumen`, `metodologia`, `series_generales`, `topicos` y `actas/index`; los años se cargan solo al abrir una reunión. No llamar “transcripción” a `intervenciones`: son secuencias reconstruidas desde el acta publicada.
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    files = sorted(path for path in out.rglob("*") if path.is_file())
    manifest = {"version": "datos_web_v1", "generado_desde": "resultados/analisis_descriptivo", "periodo": [2005, 2015], "archivos": {str(path.relative_to(out)): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in files}}
    write_json(out / "manifest.json", manifest, pretty=True)
    return {"salida": str(out), "archivos": len(files) + 1, "bytes": sum(path.stat().st_size for path in out.rglob("*") if path.is_file()), "reuniones": len(meetings), "intervenciones": len(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sobrescribir", action="store_true")
    args = parser.parse_args()
    print(json.dumps(prepare(args.salida, args.sobrescribir), ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
