"""Extracción y señales léxicas compartidas por descubrimiento y validación.

Las etiquetas de frases no son etiquetas de intervenciones. La coincidencia
respeta tokens y oraciones; la negación se registra aparte, nunca invierte
automáticamente hawkish/dovish. Revisión semántica en diccionario_v1.csv.
"""

# ---- 1. Parámetros prefijados y normalización reproducible ----
import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import GroupShuffleSplit

import config

RUTA_LEXICO = config.RUTA_DATOS / "lexico" / "ngramas_v1"
RUTA_VALIDACION = config.RUTA_DATOS / "evaluacion" / "lexico_ngramas_v1"
FRACCION_DESCUBRIMIENTO = 0.4  # reuniones; no requiere proporción exacta de filas
SEMILLA_PARTICION = config.SEED_MAESTRA + 20
MIN_INTERVENCIONES = 5
MIN_REUNIONES = 3
POR_CRITERIO_Y_LONGITUD = 6
EXTRA_POLITICA_POR_DIRECCION = 6
CLASES = ["hawkish", "dovish", "neutral"]
CATEGORIAS = {"restrictiva", "expansiva", "contextual", "sin_direccion"}
COLUMNAS_SENALES = ["restrictiva", "restrictiva_negada", "expansiva", "expansiva_negada"]
NEGADORES = {"no", "nunca", "ni", "sin", "tampoco"}
VENTANA_NEGACION = 3
BORDES_VACIOS = set("a al ante con de del desde durante el ella ellos en entre hacia hasta la las lo los para por que se sin sobre su sus un una y o es ha ser son como mas esta este estos estas cual quien cuyo siendo haber".split())
PATRON_POLITICA = r"tasa|tpm|monetari|inflaci|estimul|expans|restrict|normaliz|recort|baj|alza|aument|disminu|subir|mantener|reduc|sesgo|vot"


def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))


def oraciones_tokens(texto):
    # Primero colapsar whitespace para no cortar por quiebres OCR de línea.
    texto = normalizar(" ".join(texto.split()))
    return [re.findall(r"(?u)\b\w+\b", parte) for parte in re.split(r"[.!?;:]+", texto) if parte.strip()]


def ngramas(texto):
    return [" ".join(tokens[i:i + n]) for tokens in oraciones_tokens(texto)
            for n in range(1, 5) for i in range(len(tokens) - n + 1)]


def particionar(datos):
    division = GroupShuffleSplit(n_splits=1, train_size=FRACCION_DESCUBRIMIENTO, random_state=SEMILLA_PARTICION)
    descubrimiento, reserva = next(division.split(datos, groups=datos.meeting_id))
    assert not set(datos.iloc[descubrimiento].meeting_id) & set(datos.iloc[reserva].meeting_id)
    roles = np.full(len(datos), "validacion_interna", dtype=object)
    roles[descubrimiento] = "descubrimiento_lexico"
    return pd.DataFrame({"intervencion_id": datos.intervencion_id, "meeting_id": datos.meeting_id, "rol": roles})


# ---- 2. Conteos documentales, reuniones y asociación (no etiquetas automáticas) ----
def construir_catalogo(datos):
    vector = CountVectorizer(analyzer=ngramas, min_df=MIN_INTERVENCIONES, dtype=np.int32)
    matriz = vector.fit_transform(datos.texto)
    vocabulario = vector.get_feature_names_out()
    presentes = matriz.copy()
    presentes.data[:] = 1
    frecuencia = np.asarray(presentes.sum(axis=0)).ravel()
    reuniones = np.zeros(len(vocabulario), dtype=int)
    for reunion in datos.meeting_id.unique():
        sub = presentes[datos.meeting_id.eq(reunion).to_numpy()]
        reuniones += np.asarray(sub.sum(axis=0)).ravel() > 0
    tfidf = TfidfTransformer(sublinear_tf=True).fit_transform(matriz)
    tabla = pd.DataFrame({"ngrama": vocabulario, "n_palabras": [len(n.split()) for n in vocabulario],
                          "intervenciones": frecuencia, "reuniones": reuniones,
                          "apariciones": np.asarray(matriz.sum(axis=0)).ravel(),
                          "tfidf_medio": np.asarray(tfidf.mean(axis=0)).ravel()})
    for clase in CLASES:
        mascara = datos.etiqueta.eq(clase).to_numpy()
        tabla[f"df_{clase}"] = np.asarray(presentes[mascara].sum(axis=0)).ravel()
        tabla[f"tasa_{clase}"] = (tabla[f"df_{clase}"] + 0.5) / (int(mascara.sum()) + 1)
    for clase in ["hawkish", "dovish"]:
        total = int(datos.etiqueta.eq(clase).sum())
        tasa_resto = (tabla.intervenciones - tabla[f"df_{clase}"] + 0.5) / (len(datos) - total + 1)
        tabla[f"asociacion_{clase}"] = np.log2(tabla[f"tasa_{clase}"] / tasa_resto)
    tabla = tabla[tabla.reuniones.ge(MIN_REUNIONES)].copy()
    return tabla.sort_values(["intervenciones", "ngrama"], ascending=[False, True]).reset_index(drop=True)


def candidatos_priorizados(catalogo):
    # No se quitan palabras dentro de una frase: se evitan bordes incompletos
    # y n-gramas numéricos para dedicar la revisión a expresiones interpretables.
    elegibles = catalogo[catalogo.ngrama.map(lambda n: all(t.isalpha() for t in n.split())
                 and n.split()[0] not in BORDES_VACIOS and n.split()[-1] not in BORDES_VACIOS)].copy()
    razones = {}
    for longitud in range(1, 5):
        sub = elegibles[elegibles.n_palabras.eq(longitud)]
        for criterio in ["intervenciones", "asociacion_hawkish", "asociacion_dovish"]:
            ordenados = sub.sort_values([criterio, "intervenciones", "ngrama"], ascending=[False, False, True]) if criterio != "intervenciones" else sub.sort_values(["intervenciones", "ngrama"], ascending=[False, True])
            for n in ordenados.head(POR_CRITERIO_Y_LONGITUD).ngrama:
                razones.setdefault(n, []).append(f"top_{criterio}_{longitud}pal")
    monetarios = elegibles[elegibles.ngrama.str.contains(PATRON_POLITICA, regex=True)]
    for clase in ["hawkish", "dovish"]:
        ordenados = monetarios.sort_values([f"asociacion_{clase}", "intervenciones", "ngrama"], ascending=[False, False, True])
        for n in ordenados.head(EXTRA_POLITICA_POR_DIRECCION).ngrama:
            razones.setdefault(n, []).append(f"senal_politica_{clase}")
    salida = catalogo[catalogo.ngrama.isin(razones)].copy()
    salida["criterios_seleccion"] = salida.ngrama.map(lambda n: "; ".join(razones[n]))
    return salida.sort_values(["n_palabras", "ngrama"]).reset_index(drop=True)


def extraer_contextos(datos, candidatos):
    # Hasta tres ejemplos por frase, diversificando clases y reuniones. Son
    # fragmentos normalizados para lectura, no citas gold ni decisiones nuevas.
    registros = []
    conjuntos = [set(ngramas(t)) for t in datos.texto]
    for candidato in candidatos.itertuples():
        coincidencias = datos[[candidato.ngrama in conjunto for conjunto in conjuntos]]
        seleccionadas, reuniones = [], set()
        for clase in CLASES:
            sub = coincidencias[coincidencias.etiqueta.eq(clase) & ~coincidencias.meeting_id.isin(reuniones)]
            if len(sub):
                fila = sub.iloc[0]
                seleccionadas.append(fila); reuniones.add(fila.meeting_id)
        for fila in coincidencias.itertuples():
            if len(seleccionadas) >= 3:
                break
            if fila.meeting_id not in reuniones:
                seleccionadas.append(coincidencias.loc[coincidencias.intervencion_id.eq(fila.intervencion_id)].iloc[0])
                reuniones.add(fila.meeting_id)
        for fila in seleccionadas:
            texto = normalizar(" ".join(fila.texto.split()))
            patron = r"\b" + r"\W+".join(map(re.escape, candidato.ngrama.split())) + r"\b"
            encontrado = re.search(patron, texto)
            assert encontrado is not None
            contexto = texto[max(0, encontrado.start() - 180):encontrado.end() + 240]
            registros.append({"ngrama": candidato.ngrama, "intervencion_id": fila.intervencion_id,
                              "meeting_id": fila.meeting_id, "etiqueta_ia": fila.etiqueta, "contexto": contexto})
    return pd.DataFrame(registros)


# ---- 3. Coincidencias para variables adicionales del clasificador ----
def validar_diccionario(diccionario, candidatos):
    assert diccionario.ngrama.is_unique and set(diccionario.ngrama) == set(candidatos.ngrama)
    assert set(diccionario.senal) <= CATEGORIAS
    assert diccionario.justificacion.notna().all() and diccionario.justificacion.str.strip().ne("").all()
    assert diccionario.metodo.eq("revision_ia_contextos_descubrimiento").all()
    assert diccionario.version.eq("v1").all()


def matriz_senales(textos, diccionario):
    mapa = {tuple(f.ngrama.split()): f.senal for f in diccionario.itertuples()}
    matriz = np.zeros((len(textos), len(COLUMNAS_SENALES)), dtype=float)
    posiciones = {nombre: i for i, nombre in enumerate(COLUMNAS_SENALES)}
    for fila, texto in enumerate(textos):
        for tokens in oraciones_tokens(texto):
            inicio = 0
            while inicio < len(tokens):
                for largo in range(min(4, len(tokens) - inicio), 0, -1):
                    frase = tuple(tokens[inicio:inicio + largo])
                    if frase not in mapa:
                        continue
                    senal = mapa[frase]
                    if senal in {"restrictiva", "expansiva"}:
                        # Las coincidencias contextuales más largas bloquean el
                        # conteo de una señal más corta contenida en ellas.
                        izquierda = tokens[max(0, inicio - VENTANA_NEGACION):inicio]
                        negada = any(t in NEGADORES and not (t == "no" and i + 1 < len(izquierda)
                                      and izquierda[i + 1] in {"solo", "solamente"}) for i, t in enumerate(izquierda))
                        clave = senal + ("_negada" if negada else "")
                        matriz[fila, posiciones[clave]] = 1.0
                    inicio += largo
                    break
                else:
                    inicio += 1
    return matriz
