"""Cierra segunda revisión v3 de 100 casos prioritarios y consolida las 300 filas."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data/recepcion/anotacion_adicional_300_v3_v1"
SOURCE = SOURCE_DIR / "anotaciones_canonicas.csv"
QUEUE = SOURCE_DIR / "revision_semantica_prioritaria_100.csv"
OUT = ROOT / "data/evaluacion/anotacion_adicional_300_v3_cerrada_v1"

# Correcciones tras lectura de unidad completa bajo dirección monetaria propia respaldada.
CORRECTIONS = {
"RPM-2006-10-12:935:1": ("neutral", "Retirar el sesgo al alza y mencionar que el próximo cambio podría ser a la baja no adopta un sesgo bajista; mantener sin nueva dirección es N."),
"RPM-2008-07-10:1962:1": ("neutral", "Afirma que se requeriría una respuesta monetaria, pero no identifica su dirección; la inflación no permite inferir H por sí sola."),
"RPM-2006-09-07:871:1": ("neutral", "Señalar que la normalización estaría llegando a su fin no respalda expansión ni recorte; termina un sesgo restrictivo sin adoptar uno bajista."),
"RPM-2008-04-10:1780:1": ("neutral", "Vota mantener y reafirma un compromiso antiinflacionario general, sin alza, restricción explícita ni sesgo futuro direccional."),
"RPM-2009-11-12:2793:1": ("hawkish", "Recomienda anunciar el acortamiento gradual y término de la FLAP. La acción propia retira una facilidad expansiva documentada; evitar sobrerreacciones no cambia su signo."),
"RPM-2008-10-09:2127:1": ("neutral", "Mantiene la TPM y habla de ajustes adicionales sin indicar su signo, condicionando decisiones a nueva información; no se infiere alza desde la inflación."),
"RPM-2007-11-13:1562:1": ("neutral", "Recomienda mantener y solo dice que habría que actuar si empeoran expectativas, sin especificar acción o dirección."),
"RPM-2007-08-09:1365:2": ("neutral", "Describe inflación y expectativas de mercado de futuras alzas, pero no adopta ni recomienda esa trayectoria como propia."),
"RPM-2007-02-08:1092:2": ("neutral", "Recomienda mantener y observar para resolver contradicciones; materializar recortes queda como alternativa, no como orientación propia respaldada."),
"RPM-2009-05-07:2510:4": ("neutral", "Es un cálculo descriptivo de Regla de Taylor solicitado por el Presidente; no recomienda bajar la TPM."),
"RPM-2008-05-08:1849:1": ("neutral", "El acuerdo mantiene la TPM y deja cualquier cambio futuro sujeto a nueva información, sin dirección explícita."),
"RPM-2012-02-14:4612:1": ("neutral", "Diagnostica menor probabilidad de holguras y menciona implicancias, pero no formula una acción ni dirección monetaria."),
"RPM-2011-04-12:3962:1": ("neutral", "Describe presiones inflacionarias internas y normalización en economías extranjeras, sin adoptar una recomendación para la TPM chilena."),
"RPM-2010-02-11:2940:1": ("neutral", "Señala un riesgo para percepción de inflación, sin conectar ese diagnóstico con una acción o sesgo monetario propio."),
"RPM-2015-08-13:6957:1": ("neutral", "Cualifica un riesgo de desanclaje y excluye una acción inminente; discutir el riesgo no equivale a respaldar endurecimiento."),
"RPM-2007-02-08:1090:7": ("neutral", "Considera que una reducción adicional no es urgente y que los antecedentes no apuntan en dirección evidente; no respalda un recorte futuro."),
"RPM-2009-07-09:2631:1": ("neutral", "Afirma que la tasa no está donde debería, pero no dice si debe subir o bajar; inferir baja desde el output gap añadiría dirección invisible."),
"RPM-2008-02-07:1685:1": ("neutral", "Mantiene la TPM y no descarta ajustarla nuevamente, pero no especifica el signo del eventual ajuste; el diagnóstico inflacionario no asigna H."),
}
FLAP_ID = "RPM-2009-11-12:2793:1"
FLAP_MARKER = "su recomendación al Consejo es que en la presente Reunión se pronuncie sobre dos aspectos: en primer término, sobre un acortamiento gradual de la FLAP"


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with Path(path).open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def flap_quote(text):
    start = text.find(FLAP_MARKER)
    if start < 0: raise ValueError("No se encontró recomendación FLAP")
    return text[start:start + 300].rstrip()


def run(out=OUT):
    out = Path(out)
    names = ["adjudicacion_prioritaria_100.csv", "cambios_semanticos.csv", "referencia_300_v3.csv",
             "resumen.json", "protocolo.json", "manifest.json"]
    if out.exists(): raise FileExistsError("No sobrescribir cierre semántico")
    source, queue = read(SOURCE), read(QUEUE)
    by_id = {r["intervencion_id"]: r for r in source}; queue_ids = [r["intervencion_id"] for r in queue]
    if len(source) != 300 or len(queue_ids) != 100 or len(set(queue_ids)) != 100:
        raise ValueError("Cobertura inesperada")
    if not set(CORRECTIONS) <= set(queue_ids) or len(CORRECTIONS) != 18:
        raise ValueError("Correcciones fuera de cola")

    reviews, changes = [], []
    for identity in queue_ids:
        row = by_id[identity]; previous = row["etiqueta_v3"]
        if identity in CORRECTIONS:
            label, rationale = CORRECTIONS[identity]
            quote = flap_quote(row["texto"]) if identity == FLAP_ID else row["cita_literal"]
            confidence, result = ("media", "corregida_v3") if identity == FLAP_ID else ("alta", "corregida_v3")
            changes.append({"intervencion_id": identity, "etiqueta_humana": previous,
                            "etiqueta_adjudicada_v3": label, "fundamento_adjudicacion": rationale})
        else:
            label, rationale, quote = previous, "Ratificada tras lectura completa: " + row["fundamento_humano"], row["cita_literal"]
            confidence, result = row["confianza_humana"], "ratificada_v3"
        if quote not in row["texto"] or len(quote) > 300:
            raise ValueError(f"Cita de revisión inválida: {identity}")
        reviews.append({"intervencion_id": identity, "etiqueta_humana": previous,
            "etiqueta_adjudicada_v3": label, "es_relevante_adjudicada_v3": row["es_relevante_v3"],
            "confianza_adjudicacion": confidence, "cita_literal_adjudicacion": quote,
            "fundamento_adjudicacion": rationale, "resultado_revision": result, "estado_revision": "cerrado"})
    review_by_id = {r["intervencion_id"]: r for r in reviews}
    final = []
    for row in source:
        identity = row["intervencion_id"]
        if identity in review_by_id:
            rev = review_by_id[identity]
            label, relevance = rev["etiqueta_adjudicada_v3"], rev["es_relevante_adjudicada_v3"]
            confidence, quote, rationale = rev["confianza_adjudicacion"], rev["cita_literal_adjudicacion"], rev["fundamento_adjudicacion"]
            source_decision = rev["resultado_revision"]
        else:
            label, relevance = row["etiqueta_v3"], row["es_relevante_v3"]
            confidence, quote, rationale = row["confianza_humana"], row["cita_literal"], row["fundamento_humano"]
            source_decision = "aceptada_fuera_cola_prioritaria"
        if relevance == "0" and label != "neutral": raise ValueError(f"Incoherencia final: {identity}")
        if relevance == "1" and (not quote or quote not in row["texto"] or len(quote) > 300):
            raise ValueError(f"Evidencia final inválida: {identity}")
        final.append({"intervencion_id": identity, "fecha_reunion": row["fecha_reunion"],
            "actor": row["actor"], "cargo": row["cargo"], "texto": row["texto"],
            "etiqueta_humana": row["etiqueta_v3"], "etiqueta_v3": label,
            "es_relevante_v3": relevance, "confianza_v3": confidence, "cita_literal": quote,
            "fundamento_v3": rationale, "resultado_revision": source_decision,
            "estado_revision_v3": "cerrado", "sha256_texto": row["sha256_texto"]})

    out.mkdir(parents=True)
    write_csv(out / names[0], reviews); write_csv(out / names[1], changes); write_csv(out / names[2], final)
    from collections import Counter
    summary = {"filas": 300, "ids_unicos": 300, "segunda_revision": 100,
        "ratificadas_en_segunda_revision": 82, "corregidas_en_segunda_revision": 18,
        "aceptadas_fuera_cola_prioritaria": 200,
        "cambios": dict(Counter(f"{r['etiqueta_humana']}→{r['etiqueta_adjudicada_v3']}" for r in changes)),
        "etiquetas_finales": dict(Counter(r["etiqueta_v3"] for r in final)),
        "relevancia_final": dict(Counter(r["es_relevante_v3"] for r in final)),
        "filas_cerradas": 300, "lista_para_entrenamiento": True,
        "predicciones_modelo_consultadas": False, "evaluacion_independiente": False}
    (out / names[3]).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    protocol = {"codebook": "docs/codebook_v3.md", "fuente_sha256": sha(SOURCE),
        "cola_sha256": sha(QUEUE), "operacion": "segunda lectura 80 H/D y 20 N de riesgo sin predicciones",
        "reglas": ["dirección propia respaldada", "diagnóstico no asigna signo", "expectativa ajena no asigna signo",
                   "mantener sin sesgo es N", "acción actual explícita prima"],
        "uso": "ampliación de train con purga por reunión/texto en cada fold; nunca test final"}
    (out / names[4]).write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / names[5]).write_text(json.dumps({"sha256_salidas": {n: sha(out/n) for n in names[:-1]}},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__": print(json.dumps(run(), ensure_ascii=False, indent=2))
