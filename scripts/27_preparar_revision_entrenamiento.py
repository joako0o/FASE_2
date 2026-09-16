"""Prepara 30 casos de entrenamiento para revisión humana sin etiqueta IA visible.

No revisa por el investigador, compara etiquetas, entrena ni importa respuestas.
La única carpeta que debe servirse por HTTP es salida/formulario/.
"""
# ---- 1. Fuentes inmutables y parámetros de selección fijados antes de responder ----
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pandas as pd

import config
from utilidades import cargar_script, exigir_salidas_nuevas, sha256

ANTERIOR = cargar_script('26_comparar_clasificadores_hd.py')
ESCRIBIR = ANTERIOR.ESCRIBIR
VERSION = 'revision_entrenamiento_30_v1'
SEMILLA = 20260916
POR_CLASE = 10
CLASES = ('hawkish','dovish','neutral')
RUTA_SALIDA = config.RUTA_DATOS / 'auditoria' / VERSION
RUTA_DISENO = config.RUTA_REPO / 'docs/PROTOCOLO_REVISION_ENTRENAMIENTO_30_V1.md'
RUTA_PLANTILLA = config.RUTA_REPO / 'scripts/plantillas/revision_entrenamiento.html'
RUTA_MARCO_HUMANO = config.RUTA_MUESTRAS / 'gold_ciego_300.csv'


def huella_texto(texto):
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def serializar(objeto):
    return json.dumps(objeto,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def rango(identificador,etapa):
    return huella_texto(f'{SEMILLA}|{etapa}|{identificador}')


# ---- 2. Muestreo: excluir test humano y validación, no cambiar textos/etiquetas ----
def seleccionar(datos,mascara,ids_humanos,textos_humanos):
    assert datos.intervencion_id.is_unique
    claves = datos.texto.map(ANTERIOR.clave_texto)
    vetadas = set(claves[~mascara]) | {ANTERIOR.clave_texto(t) for t in textos_humanos}
    elegible = mascara & ~datos.intervencion_id.isin(ids_humanos).to_numpy() & ~claves.isin(vetadas).to_numpy()
    pool = datos[elegible].copy()
    pool['_clave'] = pool.texto.map(ANTERIOR.clave_texto)
    pool['_rango'] = pool.intervencion_id.map(lambda i:rango(i,'seleccion'))
    antes_deduplicar = len(pool)
    pool = pool.sort_values(['_rango','intervencion_id']).drop_duplicates('_clave',keep='first')
    assert set(pool.etiqueta)<=set(CLASES)
    partes = []
    for clase in CLASES:
        sub = pool[pool.etiqueta.eq(clase)]
        assert len(sub)>=POR_CLASE,f'No alcanzan diez casos en {clase}'
        partes.append(sub.head(POR_CLASE))
    seleccion = pd.concat(partes).copy()
    seleccion['_orden'] = seleccion.intervencion_id.map(lambda i:rango(i,'orden'))
    seleccion = seleccion.sort_values(['_orden','intervencion_id']).reset_index(drop=True)
    seleccion['caso_id'] = [f'R{i:02d}' for i in range(1,len(seleccion)+1)]
    assert len(seleccion)==3*POR_CLASE
    assert seleccion._clave.is_unique
    assert not set(seleccion.intervencion_id)&set(ids_humanos)
    assert not set(seleccion._clave)&vetadas
    auditoria = {'n_descubrimiento_inicial':int(mascara.sum()),'n_pool_antes_deduplicar':antes_deduplicar,
        'n_pool_deduplicado':len(pool),'pool_por_clase_ia':pool.etiqueta.value_counts().to_dict(),
        'seleccion_por_clase_ia':seleccion.etiqueta.value_counts().to_dict(),
        'n_reuniones_seleccion':seleccion.meeting_id.nunique(),
        'n_ids_humanos_excluidos_del_marco':len(ids_humanos),
        'n_solapes_seleccion_humana_o_validacion':0,
        'n_caracteres_seleccion':int(seleccion.texto.str.len().sum()),
        'max_caracteres_intervencion':int(seleccion.texto.str.len().max()),
        'min_caracteres_intervencion':int(seleccion.texto.str.len().min())}
    return seleccion,auditoria


# ---- 3. Payload público sin clave y HTML autosuficiente, sin servicios externos ----
def construir_publico(seleccion,guia):
    columnas = ['caso_id','texto','fecha','actor','cargo']
    casos = seleccion[columnas].astype(str).to_dict(orient='records')
    return {'version':VERSION,'muestra_sha256':huella_texto(serializar(casos)),'casos':casos,'guia':guia}


def construir_html(publico):
    plantilla = RUTA_PLANTILLA.read_text(encoding='utf-8')
    assert plantilla.count('__DATOS_REVISION__')==1
    # Impide que texto del corpus cierre la etiqueta script o inserte HTML.
    datos = serializar(publico).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    return plantilla.replace('__DATOS_REVISION__',datos)


def leer_publico(html):
    inicio = '<script id="datos" type="application/json">'
    return json.loads(html.split(inicio,1)[1].split('</script>',1)[0])


# ---- 4. Creación exclusiva y manifiesto; no se abren las respuestas humanas ----
def ejecutar(salida=RUTA_SALIDA):
    salida = Path(salida)
    exigir_salidas_nuevas(salida)
    datos,mascara,_,fuentes = ANTERIOR.L.cargar_insumos()
    ids_humanos = set(pd.read_csv(RUTA_MARCO_HUMANO,usecols=['intervencion_id'],dtype=str).intervencion_id)
    assert len(ids_humanos)==306
    # Texto original de L0 solo para impedir copias del test; ninguna etiqueta humana.
    l0 = pd.read_csv(config.RUTA_L0/'corpus.csv',usecols=['intervencion_id','texto'],dtype=str,keep_default_na=False)
    textos_humanos = l0[l0.intervencion_id.isin(ids_humanos)].texto.tolist()
    assert len(textos_humanos)==306
    seleccion,auditoria = seleccionar(datos,mascara,ids_humanos,textos_humanos)
    codebook = (config.RUTA_REPO/'docs/codebook_v2.md').read_text()
    guia = codebook.split('## 1. Unidad y variables',1)[1].split('## 4. Ejemplos semilla',1)[0]
    guia = '## 1. Unidad y variables'+guia
    publico = construir_publico(seleccion,guia)
    clave = seleccion[['caso_id','intervencion_id','etiqueta','es_relevante']].rename(
        columns={'etiqueta':'etiqueta_ia','es_relevante':'es_relevante_ia'}).copy()
    clave['sha256_texto_original'] = seleccion.texto.map(huella_texto)
    archivos = list((config.RUTA_REPO/'scripts').glob('*.py')) + [RUTA_PLANTILLA,RUTA_DISENO,RUTA_MARCO_HUMANO,
        config.RUTA_REPO/'tests/test_revision_entrenamiento.py',config.RUTA_REPO/'docs/codebook_v2.md',
        config.RUTA_REPO/'modelos/tfidf_gold_v1.joblib']
    fuentes.update({str(p.relative_to(config.RUTA_REPO)):sha256(p) for p in archivos})
    protegidos = json.loads((ANTERIOR.ANTERIOR.L.RUTA_VALIDACION/'integridad_cierre.json').read_text())['sha256_fuentes']
    fuentes.update(protegidos)
    for nombre,huella in fuentes.items():
        assert sha256(config.RUTA_REPO/nombre)==huella,nombre
    salida.mkdir(parents=True)
    (salida/'formulario').mkdir()
    # Esta clave NO va en la carpeta servida, ni se enlaza desde el formulario.
    clave.to_csv(salida/'NO_ABRIR_hasta_finalizar_clave.csv',index=False)
    (salida/'formulario/index.html').write_text(construir_html(publico),encoding='utf-8')
    ESCRIBIR(salida/'protocolo.json',{
        'version':VERSION,'fecha_preparacion_utc':datetime.now(timezone.utc).isoformat(),
        'semilla':SEMILLA,'n_por_clase_ia':POR_CLASE,'auditoria':auditoria,
        'muestra_sha256':publico['muestra_sha256'],'sha256_insumos':fuentes,
        'algoritmo':'Rango SHA256 por ID; deduplicación antes de estratos; otro rango para orden ciego.',
        'intervenciones_completas':True,'etiquetas_ia_en_formulario':False,
        'ocultacion':'Solo interfaz/servidor, no secreto frente al dueño del repositorio.',
        'estado':'Preparada; esperando decisiones del investigador. Sin comparación.',
        'gold_respuestas_abiertas':False,'gold_textos_l0_solo_exclusion':True,
        'entrenamiento_o_correccion_realizados':False,'beto_ejecutado':False})
    for nombre,huella in fuentes.items():
        assert sha256(config.RUTA_REPO/nombre)==huella,nombre
    ESCRIBIR(salida/'manifest.json',{
        'sha256_salidas':{str(p.relative_to(salida)):sha256(p) for p in sorted(salida.rglob('*')) if p.is_file()},
        'muestra_sha256':publico['muestra_sha256'],'n_casos':len(seleccion)})
    print('Preparados 30 casos sin mostrar correspondencias ni etiquetas individuales.',flush=True)
    print(json.dumps(auditoria,ensure_ascii=False,indent=2),flush=True)
    print('Servir únicamente:',salida/'formulario',flush=True)
    return publico['muestra_sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path,default=RUTA_SALIDA)
    args = parser.parse_args()
    ejecutar(args.salida)


if __name__=='__main__':
    main()
