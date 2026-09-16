"""Auditoría completa, offline y de solo lectura de los insumos del proyecto.

Reproduce fuentes, muestras históricas y serie en temporales, valida las 19
corridas IA, el gold recibido y la alineación/métricas del baseline vigente.
No reetiqueta gold ni altera L0. --reproducir-baseline repite también el fit.

Uso: python scripts/17_auditar_estado_gold.py --reproducir-baseline
Salidas: data/auditoria/2026-09-16/estado_proyecto.json e incidencias_gold_actual.csv.
El informe estado_gold.json anterior se conserva como evidencia del bug original.
"""

# ---- 1. Dependencias y parámetros de auditoría ----
import argparse
from datetime import date
import json
import platform

import numpy as np
import openpyxl
import pandas as pd
import scipy
import sklearn
from sklearn.model_selection import GroupKFold

import config
from auditoria_datos import auditar_fuentes, auditar_muestras, auditar_serie, reproducir_muestreos
from fusionar_gold_llenado import CANONICO, COLS_LLENAR, analizar, registros
from utilidades import cargar_script, cargar_entrenamiento, norm, sha256

FECHA_CORTE = "2026-09-16"
RUTA_GOLD = config.RUTA_REPO / "gold_ciego_300_listo.xlsx"
RUTA_SALIDA = config.RUTA_DATOS / "auditoria" / FECHA_CORTE


# ---- 2. Gold: controles separados de citas y de fechas ----
def auditar_gold(entrenamiento):
    cabecera, canonico = registros(CANONICO)
    cab_lleno, llenado = registros(RUTA_GOLD)
    _, incidencias, pendientes = analizar(cabecera, canonico, cab_lleno, llenado,
                                          corte=date.fromisoformat(FECHA_CORTE))
    gold = pd.DataFrame(llenado)
    assert len(gold) == 306 and gold.intervencion_id.is_unique
    assert not set(gold.intervencion_id) & set(entrenamiento.intervencion_id)
    original = pd.DataFrame(canonico).set_index("intervencion_id").loc[gold.intervencion_id]
    devuelto = gold.set_index("intervencion_id")
    cambios = {c: int(devuelto[c].map(norm).ne(original[c].map(norm)).sum())
               for c in cabecera if c not in COLS_LLENAR + ["intervencion_id"]}
    fechas = pd.to_datetime(gold.fecha, errors="coerce")
    informe = pd.DataFrame(incidencias, columns=["orden", "intervencion_id", "problema"])
    reuniones_gold = set(gold.intervencion_id.str.extract(r"(RPM-\d{4}-\d{2}-\d{2})")[0])
    reuniones_train = set(entrenamiento.intervencion_id.str.extract(r"(RPM-\d{4}-\d{2}-\d{2})")[0])
    resumen = {
        "archivo": str(RUTA_GOLD.relative_to(config.RUTA_REPO)), "sha256": sha256(RUTA_GOLD),
        "filas": len(gold), "pendientes": len(pendientes),
        "distribucion": gold.etiqueta.value_counts().to_dict(),
        "confianza": gold.confianza.value_counts().to_dict(),
        "relevancia": gold.es_relevante.value_counts().to_dict(),
        "campos_completos": {c: int(gold[c].str.strip().ne("").sum()) for c in COLS_LLENAR},
        "cambios_columnas_protegidas_y_fecha": cambios,
        "problemas": informe.problema.value_counts().to_dict(),
        "importable": not incidencias and not pendientes,
        "fecha_min": str(fechas.min()), "fecha_max": str(fechas.max()),
        "fechas_futuras": int(fechas.gt(pd.Timestamp(FECHA_CORTE)).sum()),
        "incremento_diario": bool(fechas.diff().dropna().eq(pd.Timedelta(days=1)).all()),
        "solape_ids_training": 0, "reuniones_gold": len(reuniones_gold),
        "reuniones_compartidas_training": len(reuniones_gold & reuniones_train),
    }
    # La declaración humana no altera el libro ni borra sus incidencias originales.
    # Se informa por separado qué bloqueos quedan usando la fecha confirmada.
    ruta_procedencia = RUTA_SALIDA / "procedencia_gold.json"
    if ruta_procedencia.exists():
        procedencia = json.loads(ruta_procedencia.read_text(encoding="utf-8"))
        assert procedencia["sha256_archivo"] == sha256(RUTA_GOLD), "procedencia de otro archivo"
        assert procedencia["filas"] == len(gold), "procedencia con distinta cobertura"
        _, errores_confirmados, pendientes_confirmados = analizar(
            cabecera, canonico, cab_lleno, llenado,
            fecha_anotacion=procedencia["fecha_anotacion_confirmada"],
            corte=date.fromisoformat(FECHA_CORTE))
        resumen["procedencia_declarada"] = procedencia
        resumen["con_fecha_confirmada"] = {
            "fecha": procedencia["fecha_anotacion_confirmada"],
            "problemas": pd.Series([e["problema"] for e in errores_confirmados], dtype=str).value_counts().to_dict(),
            "importable": not errores_confirmados and not pendientes_confirmados,
        }
    return resumen, informe


# ---- 3. Baseline: índices de test, clases, métricas y trazabilidad ----
def auditar_baseline(reproducir):
    baseline = cargar_script("15_baseline_tfidf.py")
    muestra = baseline.cargar_muestra()
    ruta_oof = config.RUTA_L2 / "baseline_tfidf_oof.csv"
    guardado = pd.read_csv(ruta_oof)
    metricas = json.loads((config.RUTA_L2 / "baseline_tfidf_metrics.json").read_text())
    assert muestra.intervencion_id.tolist() == guardado.intervencion_id.tolist()
    assert guardado.intervencion_id.is_unique
    assert muestra.etiqueta.equals(guardado.etiqueta)
    assert muestra.fecha.equals(guardado.fecha)
    assert set(guardado.pred) <= set(baseline.CLASES)
    assert np.isfinite(guardado.score_pred).all() and guardado.score_pred.between(-1, 1).all()
    esperados = np.zeros(len(muestra), dtype=int)
    for numero, (train, test) in enumerate(GroupKFold(n_splits=baseline.N_FOLDS).split(
            muestra.texto, muestra.etiqueta, muestra.meeting_id), 1):
        assert not set(muestra.meeting_id.iloc[train]) & set(muestra.meeting_id.iloc[test])
        esperados[test] = numero
    assert np.array_equal(guardado.fold, esperados), "folds desalineados respecto de los IDs"
    assert guardado.groupby("fecha").fold.nunique().eq(1).all()
    recalculadas = baseline.calcular_metricas(guardado)
    for clave, valor in recalculadas.items():
        assert metricas[clave] == valor, f"métrica inconsistente: {clave}"
    assert sha256(ruta_oof) == metricas["sha256_oof"]
    for ruta, huella in metricas["sha256_insumos"].items():
        assert sha256(config.RUTA_REPO / ruta) == huella, f"baseline obsoleto respecto de {ruta}"
    resumen = {**recalculadas, "alineacion_oof": True, "hashes_verificados": True,
               "reproduccion_fit": reproducir}
    if reproducir:
        nuevo = baseline.evaluar_oof(muestra)
        assert nuevo.pred.equals(guardado.pred), "fit no reproduce clases OOF"
        assert np.allclose(nuevo.score_pred.astype(float), guardado.score_pred, atol=1e-4)
        assert np.array_equal(nuevo.fold, guardado.fold)
        resumen["predicciones_y_scores_reproducidos"] = True
    return resumen


# ---- 4. Inventario auditable de datos y código mantenidos ----
def auditar_inventario():
    csvs = {}
    for ruta in sorted(config.RUTA_DATOS.rglob("*.csv")):
        # Los informes de auditoría usan ';'; el resto del proyecto usa ','.
        separador = ";" if "auditoria" in ruta.parts and ruta.name.startswith("incidencias_") else ","
        datos = pd.read_csv(ruta, sep=separador)
        assert datos.columns.is_unique
        csvs[str(ruta.relative_to(config.RUTA_REPO))] = len(datos)
    scripts = sorted((config.RUTA_REPO / "scripts").glob("*.py"))
    for ruta in scripts:
        compile(ruta.read_text(), str(ruta), "exec")
    return {"csv_parseables": csvs, "scripts_compilables": len(scripts),
            "sha256_scripts": {r.name: sha256(r) for r in scripts}}


# ---- 5. Informe con alcance y pendientes explícitos ----
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproducir-baseline", action="store_true")
    args = parser.parse_args(argv)
    entrenamiento = cargar_entrenamiento()
    resumen_gold, incidencias = auditar_gold(entrenamiento)
    resumen = {
        "fecha_corte": FECHA_CORTE, "fecha_ejecucion": date.today().isoformat(),
        "version_codebook": "v2", "fuentes": auditar_fuentes(),
        "training": {"archivos_validados": len(list(config.RUTA_ETIQUETAS.glob("etiquetas_*.csv"))),
                     "etiquetas_ia": len(entrenamiento), "duplicados": 0,
                     "distribucion": entrenamiento.etiqueta.value_counts().to_dict(),
                     "irrelevantes": int(entrenamiento.es_relevante.eq(0).sum())},
        "muestras": auditar_muestras(entrenamiento),
        "reproduccion_muestreos": reproducir_muestreos(),
        "gold": resumen_gold, "baseline": auditar_baseline(args.reproducir_baseline),
        "serie": auditar_serie(),
        "entorno": {"python": platform.python_version(), "pandas": pd.__version__,
                    "numpy": np.__version__, "openpyxl": openpyxl.__version__,
                    "scikit_learn": sklearn.__version__, "scipy": scipy.__version__},
    }
    RUTA_SALIDA.mkdir(parents=True, exist_ok=True)
    incidencias.to_csv(RUTA_SALIDA / "incidencias_gold_actual.csv", index=False, sep=";", encoding="utf-8-sig")
    resumen["inventario"] = auditar_inventario()
    (RUTA_SALIDA / "estado_proyecto.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Auditoría técnica OK. Gold importable: {resumen_gold['importable']}")
    print(f"Training: {len(entrenamiento)}; macroF1 IA: {resumen['baseline']['macro_f1']}")
    print("Incidencias del gold original:", resumen_gold["problemas"])
    if "con_fecha_confirmada" in resumen_gold:
        print("Con fecha confirmada:", resumen_gold["con_fecha_confirmada"])
    print(f"Informe: {RUTA_SALIDA / 'estado_proyecto.json'}")


if __name__ == "__main__":
    main()
