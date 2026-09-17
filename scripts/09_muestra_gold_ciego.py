# 09_muestra_gold_ciego.py
# =============================================================================
# Muestra gold ciega para validación humana (decisión 9 del PLAN)
#
# CONTEXTO
# El training set de 1.025 etiquetas ia_ronda quedó cerrado (sesión 8f AVANCE).
# El siguiente control de calidad del etiquetado IA es un gold ciego de ~300
# intervenciones que el usuario etiqueta SIN ver las etiquetas de la IA:
# - Es test puro: ninguna intervención del gold pertenece al training set.
# - Sobre las mismas ~300 se comparará IA vs humano (kappa Cohen) y, luego,
#   humano vs modelo fine-tuneado (test set final de la Fase 7/8).
#
# DISEÑO
# - Universo: escalado_tandas.csv menos TODA intervención ya etiquetada en
#   data/etiquetas/ (así el gold no contamina el entrenamiento). Se excluye el
#   residuo pre-fases de jul-2005 (50 intervenciones: el training set ya cubre
#   2005 con el piloto y las tandas cronológicas 1 a 4).
# - Estratos: las 9 fases del ciclo TPM de 08_muestra_estrato_fases.py
#   (cuota CUOTA_FASE por fase).
# - Sub-estratos por señal de decisión: dentro de cada fase, FRACCION_DECISION
#   de la cuota se toma de intervenciones con vocabulario de decisión (regex
#   PATRON_DECISION) y el resto del universo general. Objetivo: enriquecer el
#   gold con casos donde vive la clase minoritaria (hawkish/dovish), dado que
#   una muestra puramente aleatoria entregaría ~90% de neutrales y haría el
#   kappa y el test poco informativos. La selección NO mira etiquetas (no
#   existen para este universo): el sesgo del marco se documenta aquí.
# - Instrumento: una fila por intervención, orden aleatorio, columnas vacías
#   para el etiquetador humano siguiendo el esquema L1 (PLAN §4.2) + ayudas de
#   lectura (fecha_reunion, actor, cargo, texto). Las columnas de metadatos van
#   prellenadas (metodo=humano_gold, ronda=gold_ciego, version_codebook=v2,
#   etiquetador=usuario) para poder concatenar el resultado a capa L1.
#
# PARÁMETROS: solo constantes de este archivo.
# SALIDA: data/muestras/gold_ciego_300.csv + gold_ciego_300_resumen.csv
# =============================================================================

import glob

import pandas as pd
from utilidades import exigir_salidas_nuevas

import config as C

SEMILLA = C.SEED_MAESTRA + 1
CUOTA_FASE = 34                 # 9 fases * 34 = 306 intervenciones
FRACCION_DECISION = 2 / 3       # 23 con señal + 11 generales por fase

# fases del gold: las mismas del training set (config.FASES_TPM); se excluye
# 2005_alzas porque el training set ya cubre 2005 con el piloto y las tandas
# cronologicas 1 a 4, y su residuo no etiquetado es minimo (50 intervenciones)
FASES = [f for f in C.FASES_TPM if f[0] != "2005_alzas"]

COLUMNAS = ["orden", "intervencion_id", "fecha_reunion", "actor", "cargo",
            "texto", "etiqueta", "confianza", "es_relevante", "nota",
            "frase_justificante", "metodo", "ronda", "version_codebook",
            "fecha", "etiquetador"]


def main() -> None:
    # Fuentes/muestras congeladas: no regenerar sobre selecciones existentes.
    exigir_salidas_nuevas(C.RUTA_MUESTRAS / "gold_ciego_300.csv", C.RUTA_MUESTRAS / "gold_ciego_300_resumen.csv")
    uni = pd.read_csv(C.RUTA_MUESTRAS / "escalado_tandas.csv", parse_dates=["fecha"])

    # exclusión dura: cualquier intervención ya etiquetada (training set)
    ya = pd.concat([pd.read_csv(f, usecols=["intervencion_id"])
                    for f in glob.glob(str(C.RUTA_ETIQUETAS / "etiquetas_*.csv"))])
    libre = uni[~uni.intervencion_id.isin(ya.intervencion_id)].copy()
    libre["senal_decision"] = libre.texto.str.contains(C.PATRON_DECISION, case=False)

    partes = []
    n_dec = round(CUOTA_FASE * FRACCION_DECISION)   # 23
    for nombre, ini, fin in FASES:
        cand = libre[(libre.fecha >= ini) & (libre.fecha <= fin)].copy()
        con_senal = cand[cand.senal_decision]
        sin_senal = cand[~cand.senal_decision]
        a = con_senal.sample(n=min(n_dec, len(con_senal)), random_state=SEMILLA)
        b = sin_senal.sample(n=min(CUOTA_FASE - n_dec, len(sin_senal)),
                             random_state=SEMILLA)
        faltan = CUOTA_FASE - len(a) - len(b)
        assert faltan == 0, f"fase {nombre}: candidatos insuficientes " \
                            f"({len(con_senal)} con señal, {len(sin_senal)} sin señal)"
        sel = pd.concat([a, b]).assign(fase=nombre)
        partes.append(sel)
        print(f"  {nombre}: {len(a)} con señal + {len(b)} sin señal = {len(sel)}")
    gold = pd.concat(partes)
    assert gold.intervencion_id.is_unique, "duplicados en el gold"
    assert not gold.intervencion_id.isin(ya.intervencion_id).any(), \
        "el gold no puede intersectar el training set"

    # instrumento en orden aleatorio (el usuario no debe ver bloques por fase)
    gold = gold.sample(frac=1, random_state=SEMILLA + 1).reset_index(drop=True)
    out = pd.DataFrame({
        "orden": gold.index + 1,
        "intervencion_id": gold.intervencion_id,
        "fecha_reunion": gold.fecha.dt.date,
        "actor": gold.actor, "cargo": gold.cargo, "texto": gold.texto,
        "etiqueta": "", "confianza": "", "es_relevante": "", "nota": "",
        "frase_justificante": "", "metodo": "humano_gold",
        "ronda": "gold_ciego", "version_codebook": "v2",
        "fecha": "", "etiquetador": "usuario",
    })[COLUMNAS]
    out.to_csv(C.RUTA_MUESTRAS / "gold_ciego_300.csv", index=False)

    resumen = (gold.groupby(["fase", "senal_decision"], as_index=False)
                   .agg(intervenciones=("intervencion_id", "count"),
                        palabras=("largo_palabras", "sum")))
    resumen.to_csv(C.RUTA_MUESTRAS / "gold_ciego_300_resumen.csv", index=False)
    print(f"\ngold_ciego_300: {len(out)} intervenciones / "
          f"{gold.largo_palabras.sum():,} palabras")
    print(resumen.to_string(index=False))


if __name__ == "__main__":
    main()
