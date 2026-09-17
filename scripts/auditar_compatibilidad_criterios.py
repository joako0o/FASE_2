"""Auditoría estructural y selección de controles; no reclasifica ni lee gold humano.

Las observaciones semánticas están en lectura.json y fueron escritas por el agente.
Los conteos o marcas lexicales no estiman cuántas etiquetas están mal.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata

RAIZ=Path(__file__).resolve().parents[1]
SALIDA=RAIZ/'data/auditoria/compatibilidad_criterios_v1'
PATRON=r'pausa tras|vota pausa|mantener contra recorte'
PREFIJO_CONTROL='compatibilidad20260917|'


def huella(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def leer_csv(p):
    with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def clave(t):
    return ''.join(c for c in unicodedata.normalize('NFKD',' '.join(t.lower().split())) if not unicodedata.combining(c))


def conteos(rows,columna='etiqueta'):
    return [{'etiqueta':e,'es_relevante':int(r),'n':n} for (e,r),n in sorted(Counter((x[columna],x['es_relevante']) for x in rows).items())]


def seleccionar_controles(rows,corpus,referencias,humanos,focos):
    vetados={clave(corpus[k]['texto']) for k in humanos}
    elegidos=[]
    for etiqueta,relevancia in [('hawkish','1'),('dovish','1'),('neutral','1'),('neutral','0')]:
        pool=[r for r in rows if r['etiqueta']==etiqueta and r['es_relevante']==relevancia and
            r['intervencion_id'] not in humanos|focos and clave(corpus[r['intervencion_id']]['texto']) not in vetados and
            referencias[r['intervencion_id']]['etiqueta_corregida_v2']==r['etiqueta']]
        pool.sort(key=lambda r:hashlib.sha256((PREFIJO_CONTROL+r['intervencion_id']).encode()).hexdigest())
        if len(pool)<2:raise ValueError('No alcanza el estrato de controles')
        elegidos.extend(pool[:2])
    return elegidos


def ejecutar(salida=SALIDA,lectura=SALIDA/'lectura.json'):
    salida=Path(salida)
    salidas=['conteos.json','casos_inspeccionados.json','protocolo.json','manifest.json']
    if any((salida/n).exists() for n in salidas):raise FileExistsError('No sobrescribir auditoría existente')
    lectura=Path(lectura).resolve()
    archivos=sorted((RAIZ/'data/etiquetas').glob('*.csv'))
    rows=[{**r,'archivo':str(p.relative_to(RAIZ))} for p in archivos for r in leer_csv(p)]
    referencias={r['intervencion_id']:r for r in leer_csv(RAIZ/'data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv')}
    corpus={r['intervencion_id']:r for r in leer_csv(RAIZ/'data/L0/corpus.csv')}
    # Solo el ID del marco vacío; nunca se abre gold_ciego_300_listo.xlsx ni respuestas.
    humanos={r['intervencion_id'] for r in leer_csv(RAIZ/'data/muestras/gold_ciego_300.csv')}
    if len(humanos)!=306:raise ValueError('Marco humano de exclusión distinto')
    if len(rows)!=1352 or len({r['intervencion_id'] for r in rows})!=1352:raise ValueError('Marco IA cambió')
    if {r['intervencion_id'] for r in rows}!=set(referencias):raise ValueError('Referencias desalineadas')
    for r in rows:
        ref=referencias[r['intervencion_id']]
        if r['etiqueta']!=ref['etiqueta_ia_original'] or r['es_relevante']!=ref['es_relevante']:raise ValueError('Referencia de origen distinta')
    focos=[r for r in rows if re.search(PATRON,r['nota'],re.I)]
    controles=seleccionar_controles(rows,corpus,referencias,humanos,{r['intervencion_id'] for r in focos})
    observaciones=json.loads(Path(lectura).read_text(encoding='utf-8'))
    obs={r['intervencion_id']:r for r in observaciones}
    if len(obs)!=len(observaciones) or set(obs)!={r['intervencion_id'] for r in focos+controles}:raise ValueError('Lectura y selección no coinciden')
    casos=[]
    for r in focos+controles:
        k=r['intervencion_id'];o=obs[k];t=corpus[k]['texto']
        if o['cita'] not in t or len(o['cita'])>300 or o['etiqueta_nueva'] is not None:raise ValueError('Cita inválida o reclasificación no permitida')
        casos.append({**o,'archivo_ia_original':r['archivo'],'etiqueta_ia_original':r['etiqueta'],
            'etiqueta_v2_vigente':referencias[k]['etiqueta_corregida_v2'],'es_relevante':int(r['es_relevante']),
            'nota_original':r['nota'],'sha256_texto':hashlib.sha256(t.encode()).hexdigest(),
            'n_caracteres_leidos':len(t),'n_palabras_leidas':len(t.split())})
    resumen={'version':'compatibilidad_criterios_v1','filas_ia_originales':len(rows),'archivos_ia':len(archivos),
        'original':conteos(rows),'vista_v2':conteos(list(referencias.values()),'etiqueta_corregida_v2'),
        'etiquetas_con_cambios_aceptados':sum(r['etiqueta_ia_original']!=r['etiqueta_corregida_v2'] for r in referencias.values()),
        'notas_vacias':sum(not r['nota'].strip() for r in rows),'notas_vacias_no_son_infraccion_si_relevante':True,
        'coincidencias_tamiz_notas':len(focos),'tamiz_no_estima_errores':True,
        'filas_en_dos_archivos_prioritarios':{p.name:sum(r['archivo']==str(p.relative_to(RAIZ)) for r in rows) for p in archivos if p.name in ['etiquetas_r13_tanda09.csv','etiquetas_r14_tanda10.csv']},
        'controles_leidos':len(controles),'casos_completos_leidos':len(casos),
        'caracteres_leidos':sum(r['n_caracteres_leidos'] for r in casos),'palabras_leidas':sum(r['n_palabras_leidas'] for r in casos),
        'resultados_controles':dict(Counter(r['resultado_revision'] for r in casos if r['grupo']=='control_por_hash')),
        'porcentaje_de_etiquetas_erroneas_estimado':None,'etiquetas_modificadas':0,'respuestas_humanas_abiertas':False,
        'compatibilidad_de_las_306_humanas':'No evaluada; no extrapolar desde IA ni desde ejemplos del plan B.'}
    salida.mkdir(parents=True,exist_ok=True)
    def guardar(n,d):
        with (salida/n).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
    guardar('conteos.json',resumen);guardar('casos_inspeccionados.json',casos)
    fuentes=archivos+[RAIZ/'data/L0/corpus.csv',RAIZ/'data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv',
        RAIZ/'data/muestras/gold_ciego_300.csv',RAIZ/'docs/codebook_v2.md',RAIZ/'docs/CONVENCIONES_ETIQUETADO.md',
        RAIZ/'docs/INSTRUCCIONES_GOLD.md',RAIZ/'docs/CRITERIO_PLAN_B_TASA_POLITICA_PROPUESTA.md',
        RAIZ/'docs/DEFINICION_POSTURA_MONETARIA_PROPUESTA_V1.md',Path(__file__),Path(lectura)]
    guardar('protocolo.json',{'fuentes_sha256':{str(p.relative_to(RAIZ)):huella(p) for p in fuentes},
        'tamiz_notas':PATRON,'orden_controles':'SHA256('+PREFIJO_CONTROL+'ID)',
        'controles_por_estrato':2,'estratos':['H/1','D/1','N/1','N/0'],
        'exclusiones_controles':'IDs/textos normalizados del marco humano, focos y casos con referencia corregida distinta del original.',
        'lectura_semantica':'Por el mismo agente, con etiquetas visibles; no segunda anotación independiente ni muestra representativa.',
        'no_acredita':'Criterio realmente seguido por cada anotador humano o porcentaje total de etiquetas que cambiaría.'})
    guardar('manifest.json',{'sha256_salidas':{n:huella(salida/n) for n in salidas if n!='manifest.json'}})
    print(json.dumps(resumen,ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,default=SALIDA)
    p.add_argument('--lectura',type=Path,default=SALIDA/'lectura.json')
    a=p.parse_args();ejecutar(a.salida,a.lectura)
