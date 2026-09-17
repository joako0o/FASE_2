"""Cierra la revisión semántica completa de la segunda entrega dirigida de 300 v3."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data/recepcion/anotacion_dirigida_300_v3_v1"
SOURCE = SOURCE_DIR / "anotaciones_canonicas.csv"
QUEUE = SOURCE_DIR / "revision_semantica_300.csv"
OUT = ROOT / "data/evaluacion/anotacion_dirigida_300_v3_cerrada_v1"

CORRECTIONS = {
"RPM-2008-11-13:2173:1": ("neutral", "Mantiene la TPM y reafirma el compromiso general de convergencia de la inflación, sin alza, restricción explícita ni sesgo futuro direccional."),
"RPM-2009-09-08:2711:1": ("dovish", "Vota mantener explícitamente el estímulo monetario inalterado, la TPM mínima y la FLAP; sostener una postura declarada expansiva es D aunque no añada sesgo futuro."),
"RPM-2007-02-08:1090:6": ("neutral", "Elige mantener la TPM. El diagnóstico de mayor inflación no permite convertir la mantención en H sin restricción o sesgo al alza explícito."),
"RPM-2005-08-11:314:1": ("hawkish", "La exposición respalda una progresiva normalización del estímulo monetario vigente como ingrediente central de las proyecciones; es retiro de expansión respaldado."),
"RPM-2008-12-11:2248:1": ("dovish", "Vota mantener e incorporar explícitamente un sesgo a la baja, anticipando relajamiento monetario; el sesgo futuro respaldado determina D."),
"RPM-2014-06-12:6292:1": ("dovish", "Vota mantener una TPM que la propia unidad declara expansiva, comparte que podrían requerirse nuevos estímulos y conserva el comunicado; sostiene expansión explícita."),
"RPM-2007-10-11:1484:1": ("neutral", "Reporta expectativas de mercado de futuras alzas, sin adoptarlas ni recomendarlas como orientación propia."),
"RPM-2007-05-10:1259:1": ("neutral", "Vota mantener sin sesgo direccional; crecimiento e inflación son diagnóstico y no autorizan inferir H."),
"RPM-2006-08-10:825:1": ("neutral", "Vota mantener y pausar el ciclo de alzas. Terminar o pausar un sesgo restrictivo, sin adoptar uno bajista, es N."),
"RPM-2007-02-08:1093:1": ("neutral", "Menciona ajustes adicionales de hasta 75 puntos base, pero no especifica su signo; la dirección no se completa desde brechas o contexto histórico."),
"RPM-2015-02-12:6628:2": ("neutral", "Afirma que hay espacio para una política expansiva, pero no adopta ni recomienda una acción o trayectoria; capacidad de actuar no equivale a orientación respaldada."),
"RPM-2009-01-08:2285:1": ("neutral", "Formula una consulta e ilustra trayectorias hipotéticas del modelo, aclarando que no afirma si el ejercicio está bien o mal; no respalda una baja propia."),
"RPM-2006-08-10:827:1": ("neutral", "El acuerdo mantiene la TPM y habla de ajustes pausados sin indicar su signo. Inflación y condiciones expansivas no permiten completar una dirección invisible."),
"RPM-2011-08-18:4268:1": ("neutral", "Recomienda mantener, eliminar el sesgo restrictivo y adoptar orientación neutral. Retirar el sesgo al alza sin adoptar sesgo a la baja es N."),
"RPM-2006-10-12:940:1": ("neutral", "Vota mantener y prolongar la tasa inalterada, sin declarar que esa tasa sea expansiva ni adoptar sesgo a la baja; menor inflación no asigna dirección por inferencia."),
}
NEW_QUOTES = {
"RPM-2009-09-08:2711:1": "la opción que mejor se acomoda a esta trayectoria en esta Reunión es la de mantener el estímulo monetario inalterado en su nivel actual, lo que significa mantener la TPM en 0,50% y la vigencia de la FLAP a 6 meses",
"RPM-2014-06-12:6292:1": "Manifiesta que la TPM se ha recortado en 100 puntos base y ha alcanzado un nivel que es más bien expansivo; las tasas de interés en el mercado monetario han reaccionado en la misma línea y las tasas largas han alcanzado mínimos históricos.",
}


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with path.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def run(out=OUT):
    out = Path(out); names = ["adjudicacion_300.csv", "cambios_semanticos.csv", "referencia_300_v3.csv", "resumen.json", "protocolo.json", "manifest.json"]
    if out.exists(): raise FileExistsError("No sobrescribir cierre")
    source, queue = read(SOURCE), read(QUEUE); by_id = {r["intervencion_id"]: r for r in source}
    if len(source) != 300 or len(queue) != 300 or len(by_id) != 300 or len(CORRECTIONS) != 15: raise ValueError("Cobertura inesperada")
    if [r["intervencion_id"] for r in source] != [r["intervencion_id"] for r in queue] or not set(CORRECTIONS) <= set(by_id): raise ValueError("Cola o correcciones inválidas")
    reviews, changes, final = [], [], []
    for row in source:
        identity, previous = row["intervencion_id"], row["etiqueta_v3"]
        if identity in CORRECTIONS:
            label, rationale = CORRECTIONS[identity]; quote = NEW_QUOTES.get(identity, row["cita_literal"])
            confidence, result = ("media", "corregida_v3") if identity in {"RPM-2005-08-11:314:1", "RPM-2014-06-12:6292:1"} else ("alta", "corregida_v3")
            changes.append({"intervencion_id": identity, "etiqueta_recibida": previous, "etiqueta_adjudicada_v3": label, "fundamento_adjudicacion": rationale})
        else:
            label, quote, rationale = previous, row["cita_literal"], "Ratificada tras lectura de la unidad completa: " + row["fundamento_humano"]
            confidence, result = row["confianza_humana"], "ratificada_v3"
        if row["es_relevante_v3"] == "1" and (not quote or len(quote) > 300 or quote not in row["texto"]): raise ValueError(f"Evidencia inválida: {identity}")
        reviews.append({"intervencion_id": identity, "etiqueta_recibida": previous, "etiqueta_adjudicada_v3": label,
            "es_relevante_adjudicada_v3": row["es_relevante_v3"], "confianza_adjudicacion": confidence,
            "cita_literal_adjudicacion": quote, "fundamento_adjudicacion": rationale, "resultado_revision": result, "estado_revision": "cerrado"})
        final.append({"intervencion_id": identity, "fecha_reunion": row["fecha_reunion"], "actor": row["actor"], "cargo": row["cargo"], "texto": row["texto"],
            "etiqueta_recibida": previous, "etiqueta_v3": label, "es_relevante_v3": row["es_relevante_v3"], "confianza_v3": confidence,
            "cita_literal": quote, "fundamento_v3": rationale, "resultado_revision": result, "estado_revision_v3": "cerrado", "sha256_texto": row["sha256_texto"]})
    out.mkdir(parents=True); write_csv(out / names[0], reviews); write_csv(out / names[1], changes); write_csv(out / names[2], final)
    summary = {"filas": 300, "ids_unicos": 300, "segunda_revision": 300, "ratificadas": 285, "corregidas": 15,
        "cambios": dict(Counter(f"{r['etiqueta_recibida']}→{r['etiqueta_adjudicada_v3']}" for r in changes)),
        "etiquetas_finales": dict(Counter(r["etiqueta_v3"] for r in final)), "relevancia_final": dict(Counter(r["es_relevante_v3"] for r in final)),
        "filas_cerradas": 300, "lista_para_entrenamiento": True, "predicciones_modelo_consultadas": False, "evaluacion_independiente": False}
    (out / names[3]).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    protocol = {"codebook": "docs/codebook_v3.md", "fuente_sha256": sha(SOURCE), "cola_sha256": sha(QUEUE),
        "operacion": "segunda lectura completa de 300 unidades sin predicciones", "reglas": ["dirección propia respaldada", "acción actual explícita prima", "diagnóstico no asigna signo", "expectativa ajena no asigna signo", "mantener sin sesgo es N"],
        "uso": "ampliación de train con purga por reunión y texto; nunca test final"}
    (out / names[4]).write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / names[5]).write_text(json.dumps({"sha256_salidas": {name: sha(out / name) for name in names[:-1]}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__": print(json.dumps(run(), ensure_ascii=False, indent=2))
