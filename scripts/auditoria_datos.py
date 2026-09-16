"""Auditoría integral de fuentes, selecciones, linaje y capas derivadas.

Funciones usadas por script 17. Todas las regeneraciones escriben en temporales;
los muestreos históricos se reconstruyen con las exclusiones de su propia etapa,
no con el training final (que cambiaría sus resultados).
"""

# ---- 1. Lectura y comparación de contenido ----
from contextlib import redirect_stdout
import io
from pathlib import Path
import re
import shutil
import tempfile
from unittest.mock import patch

import pandas as pd

import config
from utilidades import cargar_script, norm, sha256


def tabla(ruta):
    return pd.read_csv(ruta, dtype=str, keep_default_na=False)


def comparar_tablas(actual, esperado):
    """Comparación de valores, orden y columnas; tolerancia solo numérica de CSV."""
    pd.testing.assert_frame_equal(actual.reset_index(drop=True), esperado.reset_index(drop=True),
                                  check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12)


# ---- 2. Fuentes Excel, capa inmutable y metadata ----
def auditar_fuentes():
    corpus = pd.read_csv(config.RUTA_L0 / "corpus.csv")
    transformacion = cargar_script("01_excel_a_capa_l0.py")
    original = pd.read_excel(config.RUTA_EXCEL, sheet_name=config.HOJA_TRANSCRIPCION)
    original.Fecha = pd.to_datetime(original.Fecha)
    original = original.rename(columns=transformacion.RENOMBRE_COLUMNAS)
    reconstruido = transformacion.agregar_derivados(transformacion.construir_identificadores(original))
    transformacion.validar(reconstruido)
    # Roundtrip CSV para comparar las mismas representaciones de fechas y NA.
    reconstruido = pd.read_csv(io.StringIO(reconstruido.to_csv(index=False)))
    comparar_tablas(corpus, reconstruido)
    assert corpus.fecha.eq(corpus.meeting_id.str.removeprefix("RPM-")).all()
    for nombre, eda in transformacion.generar_eda(corpus).items():
        comparar_tablas(pd.read_csv(config.RUTA_L0 / f"{nombre}.csv"), eda)

    macro_script = cargar_script("07_macro_desde_excel.py")
    macro = pd.read_csv(config.RUTA_L2 / "macro_por_reunion.csv")
    mensual = pd.read_csv(config.RUTA_L2 / "macro_mensual.csv")
    comparar_tablas(macro, macro_script.construir_macro_por_reunion(set(corpus.meeting_id)))
    comparar_tablas(mensual, macro_script.construir_macro_mensual())
    metadata = pd.read_csv(config.RUTA_L2 / "actores_metadata.csv")
    nueva = cargar_script("02_metadata_actores.py").construir_metadata_actores()
    nueva = pd.read_csv(io.StringIO(nueva.to_csv(index=False)))
    comparar_tablas(metadata.sort_values("actor"), nueva.sort_values("actor"))
    assert set(metadata.actor) == set(corpus.actor)
    assert metadata.n_intervenciones.sum() == len(corpus)
    pendientes = pd.read_csv(config.RUTA_L2 / "pendientes_manifest.csv")
    return {"l0_reconstruido_desde_excel": True, "eda_reproducidas": 3,
            "macro_reconstruida_desde_excel": True, "reuniones_macro": len(macro),
            "meses_panel": len(mensual), "nulos_macro_reunion": macro.isna().sum().to_dict(),
            "metadata_reproducida": True, "actores_con_verificado_historico": int(metadata.verificado.sum()),
            "campos_metadata_totalmente_vacios": metadata.columns[metadata.isna().all()].tolist(),
            "pendientes_macro": pendientes.serie.tolist(),
            "textos_danados": int(corpus.flag_texto_danado.sum()),
            "fuentes_sha256": {p.name: sha256(p) for p in [config.RUTA_EXCEL, config.RUTA_EXCEL_MACRO]},
            "limites": ["Reproducir metadata no verifica sus fuentes biográficas externas.",
                        "El Excel macro no aporta vintages/fechas de publicación para acreditar datos conocidos en tiempo real."]}


# ---- 3. Cobertura, textos y exclusiones de las muestras ----
def auditar_muestras(entrenamiento):
    corpus = tabla(config.RUTA_L0 / "corpus.csv").set_index("intervencion_id")
    muestras = {}
    resumen = {}
    for ruta in sorted(config.RUTA_MUESTRAS.glob("*.csv")):
        datos = tabla(ruta)
        if "intervencion_id" not in datos:
            continue
        assert datos.intervencion_id.is_unique, f"duplicados en {ruta.name}"
        assert set(datos.intervencion_id) <= set(corpus.index), f"IDs fuera L0: {ruta.name}"
        if "texto" in datos:
            for fila in datos.itertuples():
                assert norm(fila.texto) == norm(corpus.loc[fila.intervencion_id, "texto"]), f"texto alterado {ruta.name}"
        muestras[ruta.name] = datos
        resumen[ruta.name] = len(datos)
    piloto = muestras["piloto_300.csv"]
    escalado = muestras["escalado_tandas.csv"]
    gold = muestras["gold_ciego_300.csv"]
    assert set(piloto.intervencion_id).isdisjoint(escalado.intervencion_id)
    sano = set(corpus.index[corpus.flag_texto_danado.eq("False")])
    assert set(piloto.intervencion_id) | set(escalado.intervencion_id) == sano
    assert set(muestras["test_retest_30.csv"].intervencion_id) <= set(piloto.intervencion_id)
    assert len(muestras["test_retest_30.csv"]) == config.N_TEST_RETEST
    assert set(gold.intervencion_id).isdisjoint(entrenamiento.intervencion_id)
    # Cada corrida sigue el marco y corte de tanda que efectivamente la originó.
    linaje = []
    for ruta in sorted(config.RUTA_ETIQUETAS.glob("etiquetas_*.csv")):
        etiquetas = tabla(ruta)
        if "piloto" in ruta.name:
            marco, tanda = "piloto_300_tandas.csv", int(re.search(r"r(\d+)", ruta.stem)[1])
        elif ruta.name.startswith("etiquetas_r"):
            marco, tanda = "estrato_enriquecido.csv", int(re.search(r"tanda(\d+)", ruta.stem)[1])
        else:
            ronda = int(re.search(r"r(\d+)", ruta.stem)[1])
            marco = "escalado_tandas.csv" if ronda <= 8 else "estrato_fases.csv" if ronda <= 12 else "estrato_tanda9.csv"
            tanda = ronda - 4
        candidatos = muestras[marco]
        esperados = set(candidatos.loc[candidatos.tanda.astype(int).eq(tanda), "intervencion_id"])
        assert set(etiquetas.intervencion_id) == esperados, f"cobertura incorrecta {ruta.name}"
        linaje.append({"corrida": ruta.name, "marco": marco, "tanda": tanda, "filas": len(etiquetas)})
    # Texto repetido puede cruzar el holdout aun con IDs disjuntos: se informa.
    textos_train = set(corpus.loc[entrenamiento.intervencion_id, "texto"].map(norm))
    repetidos = gold.loc[gold.texto.map(norm).isin(textos_train), "intervencion_id"].tolist()
    return {"filas_por_muestra": resumen, "linaje_corridas": linaje,
            "gold_texto_identico_a_training": repetidos,
            "intervenciones_sin_etiqueta_ia": len(corpus) - len(entrenamiento),
            "sanas_fuera_training_y_gold": len(sano - set(entrenamiento.intervencion_id) - set(gold.intervencion_id))}


# ---- 4. Reconstrucción histórica de muestreos en temporal ----
def reproducir_muestreos():
    resultados = {}
    originales_muestras, originales_etiquetas = config.RUTA_MUESTRAS, config.RUTA_ETIQUETAS
    pasos = [
        ("03_muestra_piloto.py", [], ["piloto_300.csv", "piloto_300_estratos.csv", "test_retest_30.csv"]),
        ("04_tandas_por_presupuesto.py", [], ["piloto_300_tandas.csv", "tandas_resumen.csv"]),
        ("06_tandas_escalado.py", [], ["escalado_tandas.csv", "escalado_tandas_resumen.csv"]),
        ("08_muestra_estrato_fases.py", list(range(5, 9)), ["estrato_fases.csv", "estrato_fases_resumen.csv"]),
        ("09_muestra_gold_ciego.py", list(range(5, 13)), ["gold_ciego_300.csv", "gold_ciego_300_resumen.csv"]),
        ("10_muestra_enriquecida.py", list(range(5, 13)), ["estrato_enriquecido.csv", "estrato_enriquecido_resumen.csv"]),
        ("10_muestra_tanda9_stance.py", list(range(5, 13)), ["estrato_tanda9.csv", "estrato_tanda9_resumen.csv"]),
    ]
    with tempfile.TemporaryDirectory() as carpeta:
        muestras, etiquetas = Path(carpeta) / "muestras", Path(carpeta) / "etiquetas"
        muestras.mkdir(); etiquetas.mkdir()
        for nombre, rondas, salidas in pasos:
            for ruta in etiquetas.glob("*.csv"):
                ruta.unlink()
            archivos = list(originales_etiquetas.glob("etiquetas_piloto_*.csv"))
            archivos += [originales_etiquetas / f"etiquetas_escalado_r{r}.csv" for r in rondas]
            if nombre == "10_muestra_tanda9_stance.py":
                archivos += [originales_etiquetas / "etiquetas_r13_tanda09.csv",
                             originales_etiquetas / "etiquetas_r14_tanda10.csv"]
            for archivo in archivos:
                shutil.copyfile(archivo, etiquetas / archivo.name)
            with patch.object(config, "RUTA_MUESTRAS", muestras), patch.object(config, "RUTA_ETIQUETAS", etiquetas):
                modulo = cargar_script(nombre)
                with redirect_stdout(io.StringIO()):
                    modulo.main()
            for salida in salidas:
                comparar_tablas(pd.read_csv(muestras / salida), pd.read_csv(originales_muestras / salida))
            resultados[nombre] = {"salidas_identicas": salidas, "exclusiones": [a.name for a in archivos]}
    return resultados


# ---- 5. Serie agregada: cobertura antes del merge y reproducción ----
def auditar_serie():
    original = config.RUTA_L2
    with tempfile.TemporaryDirectory() as carpeta:
        temporal = Path(carpeta)
        shutil.copyfile(original / "macro_por_reunion.csv", temporal / "macro_por_reunion.csv")
        with patch.object(config, "RUTA_L2", temporal), redirect_stdout(io.StringIO()):
            cargar_script("16_validacion_serie_stance.py").main()
        comparar_tablas(pd.read_csv(original / "serie_stance_reunion.csv"),
                         pd.read_csv(temporal / "serie_stance_reunion.csv"))
    return {"serie_reproducida": True, "n_reuniones": len(pd.read_csv(original / "serie_stance_reunion.csv"))}
