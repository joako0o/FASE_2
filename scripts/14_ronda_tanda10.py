"""Ronda 14 (tanda 10 del estrato enriquecido, decision 10).

Genera data/etiquetas/etiquetas_r14_tanda10.csv en el formato largo canonico
(PLAN.md §4.2, el mismo que exige scripts/05_validar_etiquetas.py).

Tanda 10 = segundo corte de estrato_enriquecido.csv: 36 intervenciones /
19.361 palabras, fases 2007_mixto (cierre) + 2008_crisis_alza,
pools A_consejo y B_opciones.

Convenciones heredadas vigentes ademas de las de r13:
- "Vota mantener" cuando el staff ofrecia {disminuir 25, mantener} y el sesgo
  previo era a la baja = hawkish relativo (contra la corriente de la fase),
  p.ej. enero-2007 y abril-2007 (mirrores de la regla de pausas en alzas).
- Mantener descartando explicitamente ambas direcciones = neutral pura.
- Acuerdo+comunicado con alza y reafirmacion de alzas futuras = hawkish 0.95.

Idempotente y append-only: re-ejecutar reescribe el mismo contenido; los
archivos de rondas anteriores quedan intactos (verificacion por hash).
"""

import hashlib
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parent.parent
OUT = R / "data" / "etiquetas" / "etiquetas_r14_tanda10.csv"
ESTRATO = R / "data" / "muestras" / "estrato_enriquecido.csv"
FECHA = "2026-09-16"
ETIQUETADOR = "ia_agente"
RONDA = "enriquecido_t10_r14"

# (intervencion_id, etiqueta, score, confianza, es_relevante, frase, nota)
ROWS = [
    # --- cierre fase 2007_mixto ---
    ("RPM-2007-01-11:1043:1", "neutral", 0.0, "alta", 1,
     "las proyecciones están construidas mecánicamente con una regla de política que incluye una baja de tasas de entre 50 y 55 puntos base en los próximos meses",
     "explica supuestos clave de las proyecciones (regla mecánica con bajas próximas)"),
    ("RPM-2007-01-11:1045:1", "neutral", 0.0, "alta", 1,
     "las cifras de desempleo del INE desde el punto de vista nacional son una muy buena noticia",
     "defiende la medición del INE; no hay antecedentes de sesgo en el desempleo"),
    ("RPM-2007-01-11:1054:1", "hawkish", 0.70, "alta", 1,
     "vota por la mantención de la tasa de política monetaria en su nivel actual de 5,25%",
     "voto contra el recorte de enero-2007 (opciones -25/mantener): esperar más información"),
    ("RPM-2007-02-08:1090:4", "neutral", 0.0, "alta", 1,
     "parecería más adecuado mantener el sesgo neutral",
     "opciones del staff (feb-2007): -25 o mantener sin inclinación; expectativa unánime de mantención"),
    ("RPM-2007-02-08:1102:1", "hawkish", 0.65, "alta", 1,
     "la opción de política de mantener la tasa de política monetaria sea la más apropiada",
     "vota mantener contra recorte en feb-2007; comunicado neutral similar a enero"),
    ("RPM-2007-03-15:1117:1", "neutral", 0.0, "alta", 1,
     "pivotea desde 62% para arriba y es una de las razones para tenerlo como escenario de riesgo",
     "curvas de cobre y WTI; motivo del escenario de riesgo del petróleo"),
    ("RPM-2007-03-15:1123:1", "neutral", 0.0, "alta", 1,
     "los riesgos hoy en día están hacia abajo con respecto a la actividad, que también existe preocupación en los mercados accionarios",
     "lectura: subprime y desaceleración USA vs inflación, riesgos en ambas direcciones"),
    ("RPM-2007-03-15:1134:1", "neutral", 0.0, "alta", 1,
     "no le hace sentido la información que se está entregando",
     "cuestiona lectura de IMACEC/manufactura e importaciones de consumo"),
    ("RPM-2007-03-15:1161:1", "dovish", 0.85, "alta", 1,
     "hay razones y espacio suficientes para justificar un recorte de 25 puntos base",
     "Ministro Velasco: argumentos del staff a favor de la baja le parecen abrumadores"),
    ("RPM-2007-04-12:1218:1", "hawkish", 0.70, "alta", 1,
     "vota por la mantención de la tasa de política monetaria en su nivel actual",
     "vota mantener contra recorte (abr-2007): riesgos al alza consolidándose; esperar al IPoM"),
    ("RPM-2007-05-10:1246:1", "neutral", 0.0, "alta", 1,
     "constituye para él uno de los aspectos más significativos de la coyuntura internacional",
     "términos de intercambio: Perú/Colombia se fortalecen sin shocks equivalentes"),
    ("RPM-2007-05-10:1251:3", "neutral", 0.0, "alta", 0,
     None, "trámite: solicita presentación de opciones"),
    ("RPM-2007-08-09:1394:1", "hawkish", 0.80, "alta", 1,
     "lo que le lleva a recomendar un incremento de 25 puntos base en la tasa de política monetaria",
     "Velasco: +25 moderado evitando sobrerreacción; fenómeno de costos, no de demanda"),
    ("RPM-2007-09-13:1469:1", "hawkish", 0.95, "alta", 1,
     "acordó aumentar la Tasa de Interés de Política Monetaria en 25 puntos base, a 5,75% anual",
     "acuerdo+comunicado: alza +25 unánime; atención a propagación de shocks"),
    ("RPM-2007-10-11:1508:3", "neutral", 0.0, "alta", 0,
     None, "trámite: solicita presentación de opciones"),
    # --- fase 2008_crisis_alza ---
    ("RPM-2008-01-10:1629:1", "hawkish", 0.85, "alta", 1,
     "un incremento de 25 puntos base probablemente sea el adecuado para enfrentar el escenario de mayor inflación contenido en el IPoM",
     "opciones del staff (ene-2008): +25 o +50; descarta mantención como incongruente"),
    ("RPM-2008-03-13:1694:1", "neutral", 0.0, "alta", 1,
     "no es que la expectativa de baja de tasa en el corto plazo le haya significado un efecto fallido a la Reserva Federal en términos de credibilidad",
     "precisión: las tasas largas no han subido; la curva pivotea desde un nivel más bajo"),
    ("RPM-2008-03-13:1703:1", "neutral", 0.0, "alta", 1,
     "se puede tener legítimas dudas respecto a la utilidad de la política monetaria",
     "crisis financiera: provisión de liquidez sin precedentes; incertidumbre gigantesca"),
    ("RPM-2008-03-13:1709:1", "neutral", 0.0, "alta", 1,
     "efectivamente es así y que lo han atribuido a primas por riesgo que hoy día, debido a la incertidumbre que existe, son más sensibles a las noticias",
     "explicación técnica: sobrerreacción de mercado y baja de enero por primas por riesgo"),
    ("RPM-2008-03-13:1711:1", "neutral", 0.0, "alta", 1,
     "se está proyectando también una inflación más alta para adelante porque se trata de un shock que no estaba metido en las expectativas",
     "defiende el tratamiento de shocks de oferta en las proyecciones del Banco"),
    ("RPM-2008-03-13:1721:1", "neutral", 0.0, "alta", 1,
     "se considera que las opciones más plausibles para esta ocasión son un incremento de la Tasa de Política Monetaria en 25 puntos base o su mantención en el nivel actual",
     "opciones del staff (mar-2008): +25 o mantener sin inclinación; mercado inusualmente dividido"),
    ("RPM-2008-03-13:1737:2", "hawkish", 0.85, "alta", 1,
     "mantiene su votación consistente en subir la Tasa de Política Monetaria a 6,50%",
     "voto alza +25 a 6,50% (contra la mantención mayoritaria de mar-2008)"),
    ("RPM-2008-03-13:1739:1", "neutral", 0.0, "alta", 0,
     None, "trámite: negociación de la redacción de la Minuta sobre referencia a intervención"),
    ("RPM-2008-05-08:1818:4", "neutral", 0.0, "alta", 1,
     "puede tener como explicación alguna relación con la subcontratación",
     "desacople empleo/actividad: composición sectorial y subcontratación"),
    ("RPM-2008-05-08:1837:1", "neutral", 0.0, "alta", 1,
     "la forma como se lee el gráfico de Expectativas de Política Monetaria va a cambiar con el tiempo",
     "metodología: lectura condicional de la curva de expectativas (prima por liquidez)"),
    ("RPM-2008-05-08:1848:1", "dovish", 0.65, "alta", 1,
     "se inclina por una mantención de la Tasa de Política Monetaria en 6,25%",
     "mantiene con opción de alza viva; destaca como mayor riesgo la persistencia inflacionaria"),
    ("RPM-2008-06-10:1902:1", "hawkish", 0.80, "alta", 1,
     "lo que lleva a descartar la opción de mantener la Tasa de Política Monetaria en esta ocasión",
     "opciones del staff (jun-2008): +25 o +50; shock alimentario-combustibles con consecuencias persistentes"),
    ("RPM-2008-07-10:1923:7", "neutral", 0.0, "alta", 1,
     "el mercado tiene incorporado de todas formas una probabilidad casi completa de un aumento final hacia fin de año en su Tasa de Política Monetaria",
     "contrapunto: expectativas de mercado por el alza; ajuste de tasas largas en USA"),
    ("RPM-2008-07-10:1945:1", "neutral", 0.0, "alta", 1,
     "consulta si este mayor aumento significa que habrá más inflación o si se trata de un aumento razonable",
     "pregunta técnica: salarios reales al alza vs trayectoria de inflación"),
    ("RPM-2008-08-14:2044:1", "hawkish", 0.95, "alta", 1,
     "vota por un alza de 50 puntos base",
     "voto +50pb con sesgo al alza: expectativas sugieren necesidad de ajuste significativo"),
    ("RPM-2008-09-04:2100:1", "neutral", 0.0, "alta", 0,
     None, "trámite: aprueba texto del comunicado y levanta la sesión"),
    ("RPM-2008-11-13:2159:1", "neutral", 0.0, "alta", 1,
     "es difícil contemplar una opción distinta a mantener la Tasa de Política Monetaria en esta oportunidad",
     "opciones del staff (nov-2008): solo mantención (aumento requiere escenario distinto; recorte apresurado)"),
    ("RPM-2008-11-13:2169:1", "neutral", 0.0, "alta", 1,
     "su voto es por mantener la Tasa de Política Monetaria, manteniendo un sesgo neutral en el Comunicado",
     "descarta ambas direcciones: recorte imprudente (inflación y TCR desalineados) y alza descartada"),
    ("RPM-2008-12-11:2238:1", "neutral", 0.0, "alta", 1,
     "la inclusión de un sesgo en el comunicado parece ser necesaria y natural, cualquiera sea la decisión de esta Reunión",
     "opciones del staff (dic-2008): iniciar ciclo de relajamiento ahora o mantener con sesgo; ambas plausibles"),
    ("RPM-2008-12-11:2249:1", "neutral", 0.0, "media", 1,
     "las expectativas de los analistas para el plazo de 2 años, por primera vez en varios meses, se han ubicado nuevamente en torno a la meta",
     "diagnóstico de crisis: riesgos claramente negativos; abre espacio al relajamiento (sin voto en el fragmento)"),
    ("RPM-2008-12-11:2251:1", "dovish", 0.60, "media", 1,
     "su voto es por mantener la Tasa de Política Monetaria en esta ocasión, en su nivel actual",
     "vota mantener pero declara que lo estándar apuntaría a bajas rápidas y bruscas (50pb+); espera alinear el TC"),
]


def a_probs(etiqueta: str, score: float):
    """Score s en [-1,1] -> probabilidades coherentes con el formato L1."""
    if etiqueta == "hawkish":
        return score, 0.0, round(1.0 - score, 6)
    if etiqueta == "dovish":
        return 0.0, score, round(1.0 - score, 6)
    h = max(score, 0.0)
    d = max(-score, 0.0)
    return h, d, round(1.0 - h - d, 6)


def main():
    filas = []
    for iid, et, sc, conf, rel, frase, nota in ROWS:
        fecha = iid.split(":")[0].replace("RPM-", "")
        ph, pdv, pn = a_probs(et, sc)
        filas.append({
            "intervencion_id": iid, "metodo": "ia_ronda", "etiqueta": et,
            "prob_hawkish": ph, "prob_dovish": pdv, "prob_neutral": pn,
            "score": round(ph - pdv, 6),
            "frase_justificante": frase, "confianza": conf, "es_relevante": rel,
            "nota": nota, "ronda": RONDA, "version_codebook": "v2",
            "fecha": FECHA, "etiquetador": ETIQUETADOR,
        })
    r14 = pd.DataFrame(filas)
    assert not r14.duplicated("intervencion_id").any(), "duplicados internos"

    muestra = pd.read_csv(ESTRATO)
    muestra["subindice"] = muestra.subindice.astype(int)
    t10 = muestra[muestra.tanda == 10]
    assert len(t10) == 36 and t10.largo_palabras.sum() == 19361, \
        "la muestra tanda 10 no coincide con la del script 10"
    assert sorted(r14.intervencion_id) == sorted(t10.intervencion_id), \
        "cobertura de la ronda != tanda 10 de la muestra"

    textos = {}
    uni = pd.read_csv(R / "data" / "muestras" / "escalado_tandas.csv",
                      usecols=["intervencion_id", "texto"])
    for row in uni.itertuples():
        textos[row.intervencion_id] = " ".join(str(row.texto).split())

    for row in r14.itertuples():
        texto = textos[row.intervencion_id]
        assert row.nota, f"{row.intervencion_id}: nota vacía"
        if row.es_relevante == 1:
            frase = " ".join(str(row.frase_justificante).split())
            assert frase and frase in texto, f"frase no verbatim: {row.intervencion_id}"
        else:
            assert row.etiqueta == "neutral" and pd.isna(row.frase_justificante), \
                f"flag 0 mal formado: {row.intervencion_id}"
        assert row.confianza in {"alta", "media"}
        assert row.etiqueta in {"hawkish", "dovish", "neutral"}

    dist = r14[r14.es_relevante == 1].etiqueta.value_counts().to_dict()

    archivos_previos = [f for f in sorted((R / "data" / "etiquetas").glob("etiquetas_*.csv"))
                        if f.name != OUT.name]
    total_antes = sum(len(pd.read_csv(f)) for f in archivos_previos)
    assert total_antes == 1066, f"rondas previas != 1.066: {total_antes}"
    hashes = {f.name: hashlib.md5(f.read_bytes()).hexdigest() for f in archivos_previos}

    r14.to_csv(OUT, index=False)
    r14c = pd.read_csv(OUT)
    assert len(r14c) == len(r14), "salida inconsistente tras escritura"
    hashes2 = {f.name: hashlib.md5(f.read_bytes()).hexdigest() for f in archivos_previos}
    assert hashes == hashes2, "archivos de rondas anteriores modificados (append-only roto)"

    print(f"tanda 10 ({RONDA}): {len(r14)} int / 19.361 palabras | relevantes: {dist} | flag0: {len(r14) - sum(dist.values())}")
    print(f"acumulado: {total_antes} + {len(r14)} = {total_antes + len(r14)}")
    print(f"OK -> {OUT}")


if __name__ == "__main__":
    main()
