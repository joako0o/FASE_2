"""Ronda 13 (tanda 9 del estrato enriquecido, decision 10).

Genera data/etiquetas/etiquetas_r13_tanda09.csv en el formato largo canonico
(PLAN.md §4.2, el mismo que exige scripts/05_validar_etiquetas.py).

Tanda 9 = primer corte de estrato_enriquecido.csv: 41 intervenciones /
19.734 palabras, fases 2006_alza_fin + 2007_mixto, pools A_consejo y
B_opciones (Gerente de Division Estudios).

Convenciones vigentes (codebook v2 + heredadas de sesiones anteriores):
- Opciones del staff con recomendacion explicita reciben la clase de la opcion
  recomendada (igual que en tandas previas, p.ej. id 214:4); frases tipo
  "dificil justificar otra opcion" = recomendacion (score 0.70-0.80).
- Acuerdo+comunicado con alza = hawkish 0.85-0.95.
- Voto/pausa explicita dentro de un ciclo de alzas con opcion de alza viva
  = dovish (contra la corriente de fase), 0.65-0.75.
- Mantencion de TPM reafirmando "ajustes pausados" pendientes = hawkish media
  (convencion sesion 8c).
- Voto "mantener" cuando el staff ofrecia {disminuir, mantener} sin
  recomendacion = neutral con nota.
- Tramite (solicitar opciones, aprobar comunicado, levantar sesion) = flag 0.

Incidencia de esta sesion (documentada en docs/AVANCE.md): una primera
extraccion en directorio efimero no correspondio al corte oficial tanda=9
del archivo de muestra y fue descartada antes de etiquetar; esta ronda usa la
extraccion regenerada y verificada por (id, palabras) contra el archivo.

Idempotente: re-ejecutar reescribe el mismo contenido determinista sin tocar
los archivos de rondas anteriores (append-only).
"""

import hashlib
from pathlib import Path

import pandas as pd

R = Path(__file__).resolve().parent.parent
OUT = R / "data" / "etiquetas" / "etiquetas_r13_tanda09.csv"
ESTRATO = R / "data" / "muestras" / "estrato_enriquecido.csv"
FECHA = "2026-09-16"
ETIQUETADOR = "ia_agente"
RONDA = "enriquecido_t09_r13"

# (intervencion_id, etiqueta, score, confianza, es_relevante, frase, nota)
# score = prob_hawkish - prob_dovish; neutros con lean documentado en nota.
ROWS = [
    # --- fase 2006_alza_fin (sep-2005 a dic-2006) ---
    ("RPM-2005-09-08:390:1", "hawkish", 0.80, "alta", 1,
     "es difícil justificar una opción distinta a aumentar la tasa de política monetaria en 25 puntos base",
     "opciones del staff (sep-2005): recomienda +25 explícito; descarta mantención y +50"),
    ("RPM-2005-11-10:474:1", "neutral", 0.0, "alta", 1,
     "la evaluación de la tasa neutral ha ido cambiando en el tiempo, lo que está también detrás de estos cálculos",
     "metodología del impulso monetario (tasa corta/larga, expectativas)"),
    ("RPM-2005-11-10:482:1", "neutral", 0.0, "alta", 1,
     "puede obedecer a problemas de liquidez de algunos bancos por el calce",
     "explicación técnica de movimientos de tasas cortas"),
    ("RPM-2005-11-10:492:1", "hawkish", 0.80, "alta", 1,
     "se puede justificar un aumento de 25 puntos base, considerando que es un movimiento coherente con continuar normalizando la política monetaria",
     "opciones del staff (nov-2005): justifica +25 para continuar la normalización"),
    ("RPM-2005-11-10:499:1", "hawkish", 0.90, "alta", 1,
     "la opción que considera apropiada para esta oportunidad, es elevar la Tasa de Política Monetaria en 25 puntos base",
     "voto +25 quinta alza consecutiva para evitar desanclaje de expectativas"),
    ("RPM-2005-11-10:503:1", "hawkish", 0.90, "alta", 1,
     "su voto también es por subir la tasa de política monetaria en 25 puntos base",
     "voto alza: producto sobre potencial, riesgo de desanclaje; seguir normalizando"),
    ("RPM-2005-12-13:525:1", "dovish", 0.70, "alta", 1,
     "vota por mantener inalterada la tasa de política monetaria",
     "pausa tras 5 alzas: presiones inflacionarias cesando levemente; riesgo de sobrepasar"),
    ("RPM-2006-02-09:582:1", "neutral", 0.0, "alta", 1,
     "le llama la atención un alza de 10%, por cuanto se esperaba para estas semanas una caída bastante brusca",
     "sorpresa por alza de 10% (dato de coyuntura)"),
    ("RPM-2006-02-09:583:1", "neutral", 0.0, "alta", 1,
     "el alza de los inventarios de cobre es producto de la acumulación de stocks de los consumidores",
     "explicación del alza de inventarios de cobre (China)"),
    ("RPM-2006-02-09:595:1", "neutral", 0.0, "alta", 0,
     None, "trámite: aprueba texto del comunicado y levanta la sesión"),
    ("RPM-2006-04-13:649:3", "neutral", 0.0, "alta", 1,
     "el tipo de cambio estuviera en una trayectoria preocupante, entonces ése es un elemento que se debería también considerar",
     "reflexión metodológica: rol de expectativas de mercado y del tipo de cambio en decisiones"),
    ("RPM-2006-05-11:672:1", "dovish", 0.70, "alta", 1,
     "vota, en consecuencia, por mantener la tasa de política monetaria en 5%",
     "vota pausa: dos alzas consecutivas alterarían la estrategia de normalización pausada"),
    ("RPM-2006-06-15:722:1", "neutral", 0.0, "alta", 1,
     "hacer uno ahora es bueno internamente, pero esperar dos años es demasiado",
     "debate metodológico sobre empalme de series con el INE"),
    ("RPM-2006-06-15:737:1", "dovish", 0.75, "alta", 1,
     "vota en esta oportunidad por mantener la tasa de política monetaria en el nivel actual",
     "vota mantener por error de tipo 2: costo de mantener errado menor que el de elevar"),
    ("RPM-2006-07-13:762:2", "neutral", 0.0, "alta", 1,
     "si ese efecto tendería a desaparecer en términos significativos dentro del horizonte habitual de proyecciones",
     "consulta técnica: persistencia del efecto de la política sobre el tipo de cambio"),
    ("RPM-2006-07-13:769:2", "neutral", 0.0, "alta", 1,
     "el Gobierno se ceñirá tajantemente a la regla fiscal ya anunciada sin cambio alguno",
     "política fiscal (regla, gasto próximo año) y proyecciones de cobre/Codelco"),
    ("RPM-2006-07-13:770:3", "neutral", 0.0, "alta", 0,
     None, "trámite: solicita presentación de opciones"),
    ("RPM-2006-07-13:780:4", "hawkish", 0.85, "alta", 1,
     "acordó aumentar la tasa de interés de política monetaria en 25 puntos base hasta 5,25% anual",
     "acuerdo+comunicado: alza +25; ajustes pausados necesarios pero menos frecuentes"),
    ("RPM-2006-08-10:816:1", "neutral", 0.0, "alta", 0,
     None, "trámite: solicita presentación de opciones"),
    ("RPM-2006-08-10:826:1", "hawkish", 0.55, "media", 1,
     "lo prudente es reafirmar la política de ajustes más pausados en la Tasa de Política Monetaria",
     "vota mantener reafirmando retiro pausado pendiente (convención sesión 8c)"),
    ("RPM-2006-09-07:866:1", "neutral", 0.0, "alta", 0,
     None, "trámite: solicita presentación de opciones"),
    ("RPM-2006-09-07:867:1", "dovish", 0.70, "alta", 1,
     "se justifica solamente la opción de mantener la tasa de política monetaria en esta reunión",
     "opciones del staff (sep-2006): solo mantención; proyección con mantención prolongada"),
    ("RPM-2006-10-12:922:1", "neutral", 0.0, "alta", 1,
     "se está viendo la inflación algo por debajo de lo proyectado",
     "lectura de coyuntura: actividad débil e inflación bajo lo proyectado"),
    ("RPM-2006-10-12:936:1", "dovish", 0.75, "alta", 1,
     "a su parecer hay todas las razones del mundo para mantener la tasa",
     "mantener + cambiar el sesgo comunicacional desde 'más alzas' a 'mantención'"),
    ("RPM-2006-11-16:975:2", "neutral", 0.0, "alta", 0,
     None, "trámite: solicita presentación de opciones"),
    ("RPM-2006-11-16:976:1", "dovish", 0.75, "alta", 1,
     "es difícil justificar una opción distinta a la de mantener la tasa de política monetaria en esta reunión",
     "opciones del staff (nov-2006): mantención; evaluar eliminar sesgo al alza"),
    ("RPM-2006-11-16:984:1", "dovish", 0.65, "alta", 1,
     "vota por mantener la tasa de política monetaria en 5,25%",
     "vota mantener; desenfatizar signo de futuros movimientos en el comunicado"),
    ("RPM-2006-12-14:1001:1", "neutral", 0.0, "alta", 1,
     "el mercado, al esperar baja de tasa, puede haber generado esta depreciación reciente",
     "interpretación de la Reserva Federal: expectativa de baja y depreciación"),
    # --- fase 2007_mixto ---
    ("RPM-2007-01-11:1058:1", "neutral", 0.0, "alta", 0,
     None, "trámite: aprueba texto del comunicado y levanta la sesión"),
    ("RPM-2007-02-08:1066:1", "neutral", 0.0, "alta", 1,
     "a lo mejor hay otros factores importantes que están influyendo en el precio",
     "diagnóstico del precio del petróleo (restricción OPEP, clima)"),
    ("RPM-2007-03-15:1149:1", "dovish", 0.65, "media", 1,
     "es de actuar de modo simétrico hacia arriba o por debajo del 3%",
     "argumento de simetría: estamos por debajo de la meta, apoya mayor impulso"),
    ("RPM-2007-04-12:1209:4", "neutral", 0.0, "alta", 1,
     "las opciones más plausibles para esta reunión son disminuir la Tasa de Política Monetaria en 25 puntos base, o mantenerla en su nivel actual",
     "opciones del staff (abr-2007): -25 o mantener, sin recomendación explícita"),
    ("RPM-2007-04-12:1214:1", "neutral", 0.0, "media", 1,
     "su lectura es que más bien no se materializaron",
     "cuestionamiento metodológico a la selección de riesgos; lee que los riesgos de inflación no se materializaron"),
    ("RPM-2007-05-10:1260:1", "neutral", 0.0, "alta", 1,
     "la decisión más adecuada es mantener la Tasa de Política Monetaria en 5%",
     "vota mantener: antecedentes en ambas direcciones tras quitar sesgo a la baja"),
    ("RPM-2007-08-09:1367:2", "neutral", 0.0, "alta", 1,
     "se debió haber pensado en la posibilidad de una baja de un punto a lo menos con respecto de la tasa neutral",
     "consulta metodológica: desempleo bajo vs tasa neutral y medición de brecha"),
    ("RPM-2007-08-09:1387:1", "hawkish", 0.75, "alta", 1,
     "un aumento de 25 puntos base y reforzar el sesgo de las últimas reuniones",
     "opciones del staff (ago-2007): +25 o +50; inclina +25 reforzando sesgo"),
    ("RPM-2007-08-09:1402:1", "hawkish", 0.95, "alta", 1,
     "acordó aumentar la tasa de interés de política monetaria en 25 puntos base a 5,5% anual",
     "acuerdo+comunicado: alza +25; necesario seguir aumentando la TPM"),
    ("RPM-2007-09-13:1415:1", "neutral", 0.0, "alta", 1,
     "cuando se incluya habrá comunicacionalmente un alza en el spread completamente predecible y explicable",
     "técnica: bono Codelco y su efecto medible en el EMBI"),
    ("RPM-2007-09-13:1465:1", "hawkish", 0.85, "alta", 1,
     "vota por elevar la tasa de política en 25 puntos base",
     "vota alza +25; propone en paralelo eliminar el sesgo de futuros movimientos"),
    ("RPM-2007-12-13:1596:2", "neutral", 0.0, "alta", 1,
     "los métodos no están haciendo un buen trabajo, limpiando los componentes de días estacionales",
     "metodología: volatilidad irregular de la demanda interna"),
    ("RPM-2007-12-13:1602:1", "neutral", 0.0, "alta", 1,
     "las opciones que parecen plausibles son mantener la Tasa de Política Monetaria en su nivel actual",
     "opciones del staff (dic-2007): mantener o +25; sesgo neutro previo; prudente esperar al IPoM"),
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
    r13 = pd.DataFrame(filas)
    assert not r13.duplicated("intervencion_id").any(), "duplicados internos"

    muestra = pd.read_csv(ESTRATO)
    muestra["subindice"] = muestra.subindice.astype(int)
    t9 = muestra[muestra.tanda == 9]
    assert len(t9) == 41 and t9.largo_palabras.sum() == 19734, \
        "la muestra tanda 9 no coincide con la del script 10"
    assert sorted(r13.intervencion_id) == sorted(t9.intervencion_id), \
        "cobertura de la ronda != tanda 9 de la muestra"

    textos = {}
    uni = pd.read_csv(R / "data" / "muestras" / "escalado_tandas.csv",
                      usecols=["intervencion_id", "texto"])
    for row in uni.itertuples():
        textos[row.intervencion_id] = " ".join(str(row.texto).split())

    for row in r13.itertuples():
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

    dist = r13[r13.es_relevante == 1].etiqueta.value_counts().to_dict()

    archivos_previos = [f for f in sorted((R / "data" / "etiquetas").glob("etiquetas_*.csv"))
                        if f.name != OUT.name]
    total_antes = sum(len(pd.read_csv(f)) for f in archivos_previos)
    assert total_antes == 1025, f"rondas previas != 1.025: {total_antes}"
    hashes = {f.name: hashlib.md5(f.read_bytes()).hexdigest() for f in archivos_previos}

    r13.to_csv(OUT, index=False)
    r13c = pd.read_csv(OUT)
    assert len(r13c) == len(r13), "salida inconsistente tras escritura"
    hashes2 = {f.name: hashlib.md5(f.read_bytes()).hexdigest() for f in archivos_previos}
    assert hashes == hashes2, "archivos de rondas anteriores modificados (append-only roto)"

    print(f"tanda 9 ({RONDA}): {len(r13)} int / 19.734 palabras | relevantes: {dist} | flag0: {len(r13) - sum(dist.values())}")
    print(f"acumulado: {total_antes} + {len(r13)} = {total_antes + len(r13)}")
    print(f"OK -> {OUT}")


if __name__ == "__main__":
    main()
