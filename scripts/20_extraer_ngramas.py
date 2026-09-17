"""Extrae catálogo de descubrimiento y candidatos de revisión, sin abrir el gold.

Solo 40 % de las reuniones IA interviene en la construcción/revisión del léxico.
Las otras reuniones quedan para validación interna. El catálogo de las 1.352 se
materializa DESPUÉS de congelar/evaluar el diccionario, como salida descriptiva.

Uso: python scripts/20_extraer_ngramas.py [--salida carpeta_nueva]
"""

# ---- 1. Dependencias y protocolo prefijado ----
import argparse
from datetime import datetime, timezone
from pathlib import Path

import config
import lexico_ngramas as L
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

BASELINE = cargar_script("15_baseline_tfidf.py")
ESCRITURA = cargar_script("18_seleccionar_tfidf.py")


# ---- 2. Extracción reproducible antes de revisar o validar ----
def ejecutar(salida=L.RUTA_LEXICO):
    salida = Path(salida)
    exigir_salidas_nuevas(salida)
    datos = BASELINE.cargar_muestra()
    particion = L.particionar(datos)
    descubrimiento = datos[particion.rol.eq("descubrimiento_lexico")].copy()
    archivos = [config.RUTA_L0 / "corpus.csv", config.RUTA_REPO / "requirements.txt",
                config.RUTA_REPO / "docs/codebook_v2.md", config.RUTA_REPO / "scripts/lexico_ngramas.py",
                Path(__file__), *sorted(config.RUTA_ETIQUETAS.glob("etiquetas_*.csv"))]
    protocolo = {
        "version": "v1", "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "objetivo": "N-gramas de 1 a 4 palabras, revisión contextual IA y comparación interna de características. No etiquetas de intervenciones ni gold humano.",
        "fraccion_reuniones_descubrimiento": L.FRACCION_DESCUBRIMIENTO, "semilla": L.SEMILLA_PARTICION,
        "min_intervenciones": L.MIN_INTERVENCIONES, "min_reuniones": L.MIN_REUNIONES,
        "n_ia_total": len(datos), "n_descubrimiento": len(descubrimiento),
        "reuniones_descubrimiento": descubrimiento.meeting_id.nunique(),
        "n_reserva_validacion": int(particion.rol.eq("validacion_interna").sum()),
        "distribucion_descubrimiento": descubrimiento.etiqueta.value_counts().to_dict(),
        "priorizacion": f"{L.POR_CRITERIO_Y_LONGITUD} por longitud/criterio (frecuencia, asociación H y D) más {L.EXTRA_POLITICA_POR_DIRECCION} candidatos monetarios por dirección; se deduplican",
        "asociacion": "log2 de tasa documental en clase / tasa en resto, suavizado 0,5; NO etiqueta semántica automática",
        "normalizacion": "minúsculas, sin acentos, tokens de una o más letras/dígitos; no se eliminan stopwords dentro del n-grama; no cruza . ! ? ; :",
        "revision": "Agente IA lee hasta tres contextos por candidato (clases y reuniones distintas cuando existen). No adjudicación humana. No ver contextos de la reserva ni del gold.",
        "evaluacion_prefijada": {
            "particiones": "GroupKFold 5 solo en reserva; descubrimiento se añade al train de cada fold, nunca al conjunto validado",
            "variantes": ["unigramas", "unigramas_lexico", "ngramas_1_4", "ngramas_1_4_lexico"],
            "etapa_a": "fija: TF-IDF unigramas min_df=3 C=2 balanced, entrenada dentro de cada fold",
            "etapa_b": "TF-IDF ngramas (1,1) o (1,4), min_df=3, C=2, balanced, sin búsqueda adicional",
            "lexico": "4 indicadores binarios: restrictiva/expansiva afirmada/negada; unión con TF-IDF B sin cambiar A",
            "negacion": "ventana izquierda de 3 tokens en la oración; no invertir la dirección; excepción no solo/solamente",
            "solapamientos": "coincidencia más larga; categoría contextual/sin dirección puede bloquear un término corto",
            "metricas": "macro-F1 medio y conjunto, precisión/recall/F1 por clase, matrices y diferencias pareadas por fold",
            "adopcion": "No reemplazo automático del modelo vigente; comparación exploratoria interna. No probar de nuevo sobre los 306 humanos.",
        },
        "limites": "La IA de esta sesión ya conoce el resultado agregado del gold previo. El baseline se eligió antes con CV sobre las 1.352: esta reserva no es un test final nuevo. Solo protege la construcción del léxico de sus filas de validación.",
        "sha256_insumos": {str(p.relative_to(config.RUTA_REPO)): sha256(p) for p in archivos},
    }
    salida.mkdir(parents=True)
    ESCRITURA.escribir_json(salida / "protocolo.json", protocolo)
    particion.to_csv(salida / "particion.csv", index=False)
    catalogo = L.construir_catalogo(descubrimiento)
    candidatos = L.candidatos_priorizados(catalogo)
    contextos = L.extraer_contextos(descubrimiento, candidatos)
    catalogo.to_csv(salida / "catalogo_descubrimiento.csv", index=False)
    candidatos.to_csv(salida / "candidatos_revision.csv", index=False)
    contextos.to_csv(salida / "contextos_revision.csv", index=False)
    ESCRITURA.escribir_json(salida / "extraccion_manifest.json", {
        "filas_catalogo": len(catalogo), "candidatos": len(candidatos), "contextos": len(contextos),
        "ngrama_por_longitud": catalogo.n_palabras.value_counts().sort_index().to_dict(),
        "sha256_archivos": {p.name: sha256(p) for p in sorted(salida.iterdir()) if p.is_file()},
    })
    print(f"Descubrimiento: {len(descubrimiento)} intervenciones / {descubrimiento.meeting_id.nunique()} reuniones.")
    print(f"Reserva para validación: {len(datos) - len(descubrimiento)} intervenciones.")
    print(f"Catálogo: {len(catalogo)} n-gramas; candidatos: {len(candidatos)}; contextos: {len(contextos)}.")
    print(candidatos[["ngrama", "intervenciones", "reuniones", "df_hawkish", "df_dovish", "df_neutral"]].to_string(index=False))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=L.RUTA_LEXICO)
    args = parser.parse_args(argv)
    ejecutar(args.salida)


if __name__ == "__main__":
    main()
