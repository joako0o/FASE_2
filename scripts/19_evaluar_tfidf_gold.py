"""Compara una única predicción TF-IDF congelada con las 306 decisiones humanas.

No entrena, no escoge hiperparámetros ni carga modelos pickle. Requiere la salida
completa del script 18 antes de abrir el Excel. La evaluación usa clases completas;
las incidencias documentales de citas se registran, no se corrigen ni se ocultan.
No equivale a la importación gold validada ni a un acuerdo IA-chat/humano.

Uso: python scripts/19_evaluar_tfidf_gold.py [--experimento carpeta]
"""

# ---- 1. Entradas y métricas prefijadas ----
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix, precision_recall_fscore_support

import config
from fusionar_gold_llenado import analizar, registros
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

SELECCION = cargar_script("18_seleccionar_tfidf.py")
CLASES = SELECCION.BASELINE.CLASES
RUTA_GOLD = config.RUTA_REPO / "gold_ciego_300_listo.xlsx"
RUTA_PROCEDENCIA = config.RUTA_DATOS / "auditoria" / "2026-09-16" / "procedencia_gold.json"
RUTA_INFORME = config.RUTA_REPO / "docs" / "EVALUACION_TFIDF_GOLD.md"
INCIDENCIAS_DOCUMENTALES = {"frase no verbatim", "frase excede 300 caracteres", "falta frase"}


def metricas_clasificacion(reales, predichas):
    """Tres clases fijas, macro sin ponderar por frecuencia y κ nominal no ponderado."""
    reales, predichas = np.asarray(reales), np.asarray(predichas)
    assert len(reales) == len(predichas) > 0
    assert set(reales) <= set(CLASES) and set(predichas) <= set(CLASES)
    precision, recall, f1, soporte = precision_recall_fscore_support(reales, predichas, labels=CLASES, zero_division=0)
    aciertos = int(np.count_nonzero(reales == predichas))
    # κ no está definido cuando ambos vectores son la misma única clase.
    kappa = None if len(set(reales) | set(predichas)) == 1 else float(cohen_kappa_score(reales, predichas, labels=CLASES))
    return {"n": len(reales), "aciertos": aciertos, "errores": len(reales) - aciertos,
            "accuracy": aciertos / len(reales), "tasa_error": 1 - aciertos / len(reales),
            "macro_f1": float(f1.mean()), "kappa": kappa,
            "por_clase": {clase: {"precision": float(p), "recall": float(r), "f1": float(f), "soporte": int(n)}
                          for clase, p, r, f, n in zip(CLASES, precision, recall, f1, soporte)},
            "matriz_confusion": {"filas_humanas": CLASES, "columnas_modelo": CLASES,
                                  "valores": confusion_matrix(reales, predichas, labels=CLASES).tolist()}}


# ---- 2. Verificación de la selección, predicciones y respuestas disponibles ----
def verificar_experimento(ruta):
    """Impide evaluar predicciones sustituidas o un ajuste con entradas cambiadas."""
    protocolo = json.loads((ruta / "protocolo.json").read_text())
    seleccion = json.loads((ruta / "seleccion.json").read_text())
    manifiesto = json.loads((ruta / "predicciones_manifest.json").read_text())
    assert sha256(ruta / "protocolo.json") == seleccion["sha256_protocolo"]
    assert sha256(ruta / "validacion_cv.csv") == seleccion["sha256_validacion"]
    assert sha256(ruta / "seleccion.json") == manifiesto["sha256_seleccion"]
    assert sha256(ruta / "predicciones_gold.csv") == manifiesto["sha256_predicciones"]
    assert manifiesto["respuestas_humanas_leidas"] is False
    for archivo, huella in protocolo["sha256_insumos"].items():
        assert sha256(config.RUTA_REPO / archivo) == huella, f"entrada cambió después de selección: {archivo}"
    resultados = pd.read_csv(ruta / "validacion_cv.csv", float_precision="round_trip")
    ganadora = SELECCION.elegir_configuracion(resultados)
    assert int(ganadora.candidato) == seleccion["candidato"]
    tfidf, lr = SELECCION.parametrizar(ganadora)
    tfidf["ngram_range"] = list(tfidf["ngram_range"])
    assert tfidf == seleccion["parametros_tfidf"] and lr == seleccion["parametros_lr"]
    predicciones = pd.read_csv(ruta / "predicciones_gold.csv")
    assert len(predicciones) == 306 and predicciones.intervencion_id.is_unique
    assert set(predicciones.pred) <= set(CLASES)
    assert set(predicciones.es_relevante_pred) <= {0, 1}
    probabilidades = predicciones[[f"prob_{c}" for c in CLASES]]
    assert np.isfinite(probabilidades).all().all() and probabilidades.ge(0).all().all() and probabilidades.le(1).all().all()
    assert np.allclose(probabilidades.sum(axis=1), 1)
    assert np.allclose(predicciones.score_pred, predicciones.prob_hawkish - predicciones.prob_dovish)
    assert predicciones.loc[predicciones.es_relevante_pred.eq(0), "pred"].eq("neutral").all()
    return predicciones, protocolo, seleccion, manifiesto


def preparar_referencia(cabecera, canonico, cab_lleno, llenado, fecha):
    """Solo permite pendientes de citas; nunca clases vacías, IDs o metadatos inválidos."""
    candidatas, incidencias, pendientes = analizar(cabecera, canonico, cab_lleno, llenado,
                                                  fecha_anotacion=fecha)
    bloqueos = [e for e in incidencias if e["problema"] not in INCIDENCIAS_DOCUMENTALES]
    assert not pendientes, "faltan respuestas humanas"
    assert not bloqueos, f"errores no documentales: {bloqueos[:5]}"
    referencia = pd.DataFrame(candidatas)
    assert referencia.etiqueta.isin(CLASES).all()
    return referencia, incidencias


def unir_referencia(predicciones, referencia):
    assert referencia.intervencion_id.is_unique and predicciones.intervencion_id.is_unique
    assert set(referencia.intervencion_id) == set(predicciones.intervencion_id)
    respuestas = referencia[["intervencion_id", "etiqueta", "es_relevante", "fecha_reunion"]].rename(
        columns={"etiqueta": "etiqueta_humana", "es_relevante": "es_relevante_humano"})
    return predicciones.merge(respuestas, on="intervencion_id", how="left", validate="one_to_one")


def fase_de(fecha):
    fases = [nombre for nombre, inicio, fin in config.FASES_TPM if inicio <= fecha <= fin]
    assert len(fases) == 1, f"fecha fuera de fases o ambigua: {fecha}"
    return fases[0]


# ---- 3. Informe legible generado desde las métricas, no cifras manuales ----
def construir_informe(metricas):
    principal = metricas["principal"]
    piso = metricas["siempre_neutral"]
    sin_repetidos = metricas["sin_textos_repetidos_training"]
    seleccion = metricas["seleccion"]
    matriz = principal["matriz_confusion"]["valores"]
    lineas = ["# Prueba TF-IDF contra las 306 decisiones humanas", "", "## Qué se hizo", "",
              "1. Se compararon 12 configuraciones con validación cruzada de 5 particiones por reunión, usando solo las 1.352 etiquetas IA.",
              "2. Se eligió la mayor media de macro-F1 de validación, sin consultar las respuestas humanas.",
              "3. Se congeló la configuración, se reajustó con las 1.352 y se guardaron las 306 predicciones a partir de texto únicamente.",
              "4. En un proceso posterior se abrió el Excel humano para comparar. No hubo ajustes después del test.", "",
              "## Configuración elegida", "",
              f"- Candidato **{seleccion['candidato']}**: n-gramas {seleccion['parametros_tfidf']['ngram_range']}, min_df={seleccion['parametros_tfidf']['min_df']}, C={seleccion['parametros_lr']['C']}.",
              "- Dos etapas TF-IDF + regresión logística con class_weight=balanced; sin variables de actor, fecha, macro o citas.",
              f"- Macro-F1 promedio en validación IA: **{seleccion['macro_f1_cv_media']:.4f}**. Es una métrica de selección, no una estimación independiente de generalización.", "",
              "## Resultado del examen humano", "",
              f"**Coincidió en {principal['aciertos']} de {principal['n']} intervenciones ({principal['accuracy']:.1%}). No coincidió en {principal['errores']}.**", "",
              "| Métrica | Modelo seleccionado | Siempre neutral |", "|---|---:|---:|",
              f"| Accuracy | {principal['accuracy']:.4f} | {piso['accuracy']:.4f} |",
              f"| Tasa de error | {principal['tasa_error']:.4f} | {piso['tasa_error']:.4f} |",
              f"| Macro-F1 | **{principal['macro_f1']:.4f}** | {piso['macro_f1']:.4f} |",
              f"| Kappa de Cohen | {principal['kappa']:.4f} | {piso['kappa']:.4f} |", "",
              "| Clase humana | Casos | Precisión | Recall | F1 |", "|---|---:|---:|---:|---:|"]
    for clase, m in principal["por_clase"].items():
        lineas.append(f"| {clase} | {m['soporte']} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} |")
    lineas += ["", "### Matriz de confusión", "", "Filas: tu etiqueta. Columnas: predicción del modelo.", "",
               "| Humano / Modelo | hawkish | dovish | neutral |", "|---|---:|---:|---:|"]
    lineas += [f"| {clase} | {fila[0]} | {fila[1]} | {fila[2]} |" for clase, fila in zip(CLASES, matriz)]
    lineas += ["", "## Sensibilidad y límites", "",
               f"- Sin los textos idénticos a training: n={sin_repetidos['n']}, accuracy={sin_repetidos['accuracy']:.4f}, macro-F1={sin_repetidos['macro_f1']:.4f}, κ={sin_repetidos['kappa']:.4f}.",
               f"- Las {metricas['solape']['reuniones_gold']} reuniones del gold también aparecen en training. Es un test por intervención, no por reuniones futuras.",
               "- El muestreo gold enriquece vocabulario de decisión; no representa sin ponderación la prevalencia del corpus. Métricas por fase/señal en el JSON.",
               "- Referencia humana: decisión inicial con revisión posterior de IA, sin cambios de etiquetas según autodeclaración. No es un protocolo completamente ciego.",
               f"- Estado documental: {metricas['documentacion']['n_incidencias_citas']} incidencias de citas pendientes; las clases están completas y son utilizables para esta evaluación. No se forzó una importación gold ni se cambiaron etiquetas.",
               "- El κ calculado es modelo TF-IDF vs decisiones humanas; no IA conversacional vs humano.",
               "- Estos 306 ya se examinaron. No usarlos para ajustar y luego presentar una nueva cifra como test intacto.", "",
               "## Archivos y reproducción", "",
               "- `data/evaluacion/tfidf_gold_v1/validacion_cv.csv`: los 12 candidatos.",
               "- `validacion_folds.csv` y `asignacion_folds.csv` en esa carpeta: resultados y particiones IA.",
               "- `protocolo.json` y `seleccion.json`: búsqueda y elección congeladas antes de la comparación humana.",
               "- `predicciones_gold.csv`: predicciones sin respuestas humanas; manifiesto con hash y fecha.",
               "- `comparacion_gold.csv`: las 306 comparaciones, aciertos/errores, fase y textos repetidos.",
               "- `metricas_gold.json`: resultados completos y trazabilidad.",
               "- Modelo local en `modelos/tfidf_gold_v1.joblib` (ignorado por Git; se reconstruye con script 18).", "",
               "Para repetir, usar rutas de salida NUEVAS; los scripts no sobrescriben el examen registrado.", "",
               "```bash",
               "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/venvs/fase2/bin/python scripts/18_seleccionar_tfidf.py --salida /tmp/tfidf_reproduccion --modelo /tmp/tfidf_reproduccion.joblib",
               "~/venvs/fase2/bin/python scripts/19_evaluar_tfidf_gold.py --experimento /tmp/tfidf_reproduccion --informe /tmp/tfidf_reproduccion.md",
               "```", ""]
    return "\n".join(lineas)


# ---- 4. Comparación final sin entrenamiento ni modificaciones de respuestas ----
def ejecutar(experimento=SELECCION.RUTA_EXPERIMENTO, informe=RUTA_INFORME):
    experimento, informe = Path(experimento), Path(informe)
    exigir_salidas_nuevas(experimento / "comparacion_gold.csv", experimento / "metricas_gold.json", informe)
    predicciones, protocolo, seleccion, manifiesto = verificar_experimento(experimento)
    procedencia = json.loads(RUTA_PROCEDENCIA.read_text())
    assert procedencia["sha256_archivo"] == sha256(RUTA_GOLD)
    cabecera, canonico = registros(config.RUTA_MUESTRAS / "gold_ciego_300.csv")
    cab_lleno, llenado = registros(RUTA_GOLD)
    referencia, incidencias = preparar_referencia(cabecera, canonico, cab_lleno, llenado,
                                                  procedencia["fecha_anotacion_confirmada"])
    assert len(referencia) == procedencia["filas"] == 306
    comparacion = unir_referencia(predicciones, referencia)
    comparacion["es_relevante_humano"] = comparacion.es_relevante_humano.astype(int)
    comparacion["coincide"] = comparacion.pred.eq(comparacion.etiqueta_humana)
    textos = referencia.set_index("intervencion_id").texto
    comparacion["senal_decision"] = comparacion.intervencion_id.map(textos).str.contains(config.PATRON_DECISION, case=False)
    comparacion["fase"] = comparacion.fecha_reunion.map(fase_de)
    datos = SELECCION.BASELINE.cargar_muestra()
    test = SELECCION.cargar_textos_reservados(datos).set_index("intervencion_id").loc[comparacion.intervencion_id]
    assert not set(comparacion.intervencion_id) & set(datos.intervencion_id)
    assert np.array_equal(comparacion.texto_repetido_training, test.texto_repetido_training)
    assert np.array_equal(comparacion.reunion_en_training, test.reunion_en_training)
    sin_repetidos = comparacion[~comparacion.texto_repetido_training]
    def medir(datos):
        return metricas_clasificacion(datos.etiqueta_humana, datos.pred)
    metricas = {
        "fecha_evaluacion_utc": SELECCION.ahora(), "experimento": protocolo["experimento"],
        "referencia": "decisiones humanas declaradas, revisión posterior IA sin cambios declarados",
        "seleccion": seleccion, "principal": medir(comparacion),
        "siempre_neutral": metricas_clasificacion(comparacion.etiqueta_humana, ["neutral"] * len(comparacion)),
        "sin_textos_repetidos_training": medir(sin_repetidos),
        "por_senal_decision": {str(k): medir(d) for k, d in comparacion.groupby("senal_decision")},
        "por_fase": {k: medir(d) for k, d in comparacion.groupby("fase")},
        "relevancia": {"accuracy": float(accuracy_score(comparacion.es_relevante_humano, comparacion.es_relevante_pred)),
                       "clases": [0, 1], "matriz_confusion": confusion_matrix(comparacion.es_relevante_humano, comparacion.es_relevante_pred, labels=[0, 1]).tolist()},
        "solape": {"ids_train_test": 0, "textos_repetidos_training": int(comparacion.texto_repetido_training.sum()),
                   "reuniones_gold": comparacion.meeting_id.nunique(), "reuniones_gold_en_training": manifiesto["reuniones_gold_en_training"]},
        "documentacion": {"estado": "evaluacion_de_clases_con_citas_pendientes; no importacion gold validada",
                          "n_incidencias_citas": len(incidencias), "problemas": dict(Counter(e["problema"] for e in incidencias)),
                          "procedencia": procedencia, "etiquetas_modificadas": False},
        "sha256_entrada": {"gold_humano": sha256(RUTA_GOLD), "procedencia": sha256(RUTA_PROCEDENCIA),
                          "seleccion": sha256(experimento / "seleccion.json"), "predicciones": sha256(experimento / "predicciones_gold.csv"),
                          "evaluador": sha256(Path(__file__)), "importador": sha256(config.RUTA_REPO / "scripts/fusionar_gold_llenado.py")},
        "advertencia_test": "Test ya examinado: no usar para tuning y después afirmar evaluación final intacta. CV de selección optimista; gold no independiente por reunión/texto.",
    }
    comparacion.to_csv(experimento / "comparacion_gold.csv", index=False)
    metricas["sha256_comparacion"] = sha256(experimento / "comparacion_gold.csv")
    SELECCION.escribir_json(experimento / "metricas_gold.json", metricas)
    informe.parent.mkdir(parents=True, exist_ok=True)
    with informe.open("x", encoding="utf-8") as archivo:
        archivo.write(construir_informe(metricas))
    m = metricas["principal"]
    print(f"Test humano: {m['aciertos']}/{m['n']} aciertos; accuracy={m['accuracy']:.4f}; macroF1={m['macro_f1']:.4f}; kappa={m['kappa']:.4f}")
    print("Matriz de confusión (filas humano, columnas modelo):", m["matriz_confusion"])
    print(f"Informe: {informe}")
    return metricas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experimento", type=Path, default=SELECCION.RUTA_EXPERIMENTO)
    parser.add_argument("--informe", type=Path, default=RUTA_INFORME)
    args = parser.parse_args(argv)
    ejecutar(args.experimento, args.informe)


if __name__ == "__main__":
    main()
