"""Entrada de trabajo y traslado. No modifica referencias ni el runner BETO congelado.

Desde la raíz: python scripts/40_gestionar_proyecto.py --help
Instalar/preparar/probar funciona sin GPU; smoke/entrenar requiere GPU CUDA y pesos.
"""

# ---- 1. Rutas y comandos seguros, independientes del directorio de la terminal ----
# El entorno se crea en el nuevo PC; nunca se copia un virtualenv entre equipos.
import argparse
import csv
import io
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tempfile
import venv
import zipfile

RAIZ = Path(__file__).resolve().parents[1]
INVENTARIO = 'entrega/archivos_proyecto.txt'
MANIFIESTO = 'MANIFIESTO_ENTREGA.json'
ENTRADA = 'data/checkpoints/beto_v1/entrada'
RESULTADOS = 'data/checkpoints/beto_v1/ejecucion'
ARCHIVOS_ENTRADA = ['documentos.json', 'folds.json', 'baseline.json', 'checkpoint.json', 'manifest.json']
PRUEBAS_NUEVAS = ['test_preparacion_beto.py', 'test_entrega_portable.py', 'test_muestreo_revision.py', 'test_ampliacion_tfidf.py', 'test_diagnostico_ampliacion.py', 'test_compatibilidad_criterios.py', 'test_referencia_v3.py', 'test_recodificacion_v3.py', 'test_tfidf_supervision_v3.py', 'test_ampliacion_ia89_v3.py', 'test_dataset_sintetico.py']
PRUEBAS_ANTERIORES_SEGURAS = [
    'test_inversiones_hd.py', 'test_referencias_corregidas.py', 'test_modelo_adjudicado.py',
    'test_revision_cierre_66.py', 'test_revision_neutralidad.py',
    'test_revision_intercambios_hd.py', 'test_revision_errores_nuevos.py',
]


def python_entorno(raiz=RAIZ):
    return Path(raiz)/'.venv'/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def ejecutar_python(argumentos, raiz=RAIZ):
    interprete = python_entorno(raiz)
    if not interprete.is_file():
        raise RuntimeError('Falta .venv. Ejecuta primero: python scripts/40_gestionar_proyecto.py instalar')
    entorno = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1')
    subprocess.run([str(interprete), '-X', 'utf8', '-u', *map(str, argumentos)], cwd=raiz, env=entorno, check=True)


# ---- 2. Instalación, preparación y regresiones explícitamente seleccionadas ----
# Nunca descubrir toda la suite: hay pruebas históricas que abren las 306 respuestas.
def instalar(beto=False, raiz=RAIZ):
    if sys.version_info[:2] not in [(3, 11), (3, 12)]:
        raise RuntimeError('Usa Python 3.11 (recomendado) o 3.12. Otras versiones no están habilitadas en esta entrega.')
    if not python_entorno(raiz).exists():
        venv.EnvBuilder(with_pip=True).create(Path(raiz)/'.venv')
    archivos = ['requirements-preparacion.txt']
    if beto:
        archivos.append('requirements-beto.txt')
    argumentos = ['-m', 'pip', 'install']
    for nombre in archivos:
        argumentos += ['-r', str(Path(raiz)/nombre)]
    ejecutar_python(argumentos, raiz)
    ejecutar_python(['-m', 'pip', 'check'], raiz)
    print('Entorno instalado. No se han descargado pesos ni entrenado BETO.')


def preparar(raiz=RAIZ):
    argumentos = ['scripts/38_preparar_beto.py']
    if (Path(raiz)/ENTRADA).exists():
        argumentos += ['--verificar']
    ejecutar_python(argumentos, raiz)


def probar(regresion=False, raiz=RAIZ):
    preparar(raiz)
    patrones = PRUEBAS_NUEVAS + (PRUEBAS_ANTERIORES_SEGURAS if regresion else [])
    for patron in patrones:
        ejecutar_python(['-m', 'unittest', 'discover', '-s', 'tests', '-p', patron, '-v'], raiz)
    print('Controles aprobados. No equivalen a una ejecución del encoder BETO.')


# ---- 3. BETO: delegación al protocolo congelado, sin cambiar parámetros ----
# Se detiene ante fallos. Cada fold completo puede conservarse fuera del equipo.
def ejecutar_beto(modo, raiz=RAIZ):
    preparar(raiz)
    ejecutar_python(['scripts/39_ejecutar_beto.py', modo], raiz)


def entrenar(raiz=RAIZ):
    preparar(raiz)
    for fold in range(1, 6):
        try:
            ejecutar_python(['scripts/39_ejecutar_beto.py', '--fold', fold, '--reanudar'], raiz)
        except subprocess.CalledProcessError:
            if (Path(raiz)/RESULTADOS).exists():
                print('Intento interrumpido; respaldo conservado:', respaldar_resultados(raiz))
            raise
        print('Fold terminado; respaldo:', respaldar_resultados(raiz))
    print('Cinco folds completos. Ejecuta el comando comparar; no se adopta el modelo automáticamente.')


# ---- 4. Inventario explícito y rutas seguras para no exportar secretos o basura ----
# El ZIP no recorre indiscriminadamente la carpeta del usuario: solo una lista aprobada.
def ruta_segura(raiz, nombre):
    ruta = PurePosixPath(nombre)
    if not nombre or '\\' in nombre or ruta.is_absolute() or '..' in ruta.parts or ':' in nombre:
        raise ValueError('Ruta no permitida: '+nombre)
    if any(p.lower() in {'.git', '.venv', '__pycache__', 'modelos', 'entregas'} for p in ruta.parts):
        raise ValueError('Directorio no portable: '+nombre)
    if any(p.lower() in {'.netrc', '.git-credentials', 'id_rsa', 'id_ed25519'} or p.lower() == '.env' or p.lower().startswith('.env.') for p in ruta.parts):
        raise ValueError('No exportar posibles credenciales: '+nombre)
    destino = Path(raiz).joinpath(*ruta.parts)
    if not destino.resolve().is_relative_to(Path(raiz).resolve()):
        raise ValueError('Ruta fuera del proyecto: '+nombre)
    cursor = Path(raiz)
    for parte in ruta.parts:
        cursor = cursor/parte
        if cursor.is_symlink():
            raise ValueError('No exportar enlaces simbólicos: '+nombre)
    return destino


def hash_archivo(ruta):
    digest = hashlib.sha256()
    with Path(ruta).open('rb') as archivo:
        for bloque in iter(lambda: archivo.read(1024*1024), b''):
            digest.update(bloque)
    return digest.hexdigest()


def archivos_resultados(raiz=RAIZ):
    candidatos = [RESULTADOS+'/'+n for n in ['smoke.json', 'comparacion.json']]
    for fold in range(1, 6):
        candidatos += [f'{RESULTADOS}/fold_{fold}/{n}' for n in
            ['predicciones.csv', 'cobertura.json', 'ejecucion.json', 'entrenamiento.jsonl', 'manifest.json']]
    return [n for n in candidatos if ruta_segura(raiz, n).is_file()]


def archivos_portables(raiz=RAIZ):
    lista = (Path(raiz)/INVENTARIO).read_text(encoding='utf-8').splitlines()
    nombres = [n.strip() for n in lista if n.strip() and not n.startswith('#')]
    if len(nombres) != len(set(nombres)):
        raise ValueError('Inventario con duplicados')
    nombres += [ENTRADA+'/'+n for n in ARCHIVOS_ENTRADA] + archivos_resultados(raiz)
    if len(nombres) != len(set(nombres)):
        raise ValueError('El inventario no debe incluir salidas regenerables')
    for nombre in nombres:
        if not ruta_segura(raiz, nombre).is_file():
            raise FileNotFoundError('Falta archivo portable: '+nombre)
    return sorted(nombres)


def revision_informativa(raiz):
    # Informativo: los hashes del ZIP, no esta cadena, describen los bytes entregados.
    if not (Path(raiz)/'.git').exists():
        return None
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=raiz, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


# ---- 5. Exportación sin sobrescrituras e integridad verificable sin instalar nada ----
# Las fuentes/etiquetas históricas permanecen en sus rutas; el paquete activo va incluido.
def escribir_zip(raiz, nombres, salida, tipo):
    raiz, salida = Path(raiz), Path(salida)
    if salida.exists():
        raise FileExistsError('No sobrescribir entrega existente: '+str(salida))
    nombres = sorted(nombres)
    if not nombres or len(nombres) != len(set(nombres)):
        raise ValueError('Lista vacía o duplicada')
    for nombre in nombres:
        ruta_segura(raiz, nombre)
    registro = {
        'version': 'entrega_portable_v1', 'tipo': tipo,
        'generado_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit_informativo': revision_informativa(raiz),
        'sha256_archivos': {n:hash_archivo(raiz/n) for n in nombres},
        'bytes_sin_comprimir': sum((raiz/n).stat().st_size for n in nombres),
        'no_incluye': ['.git', '.venv', 'pesos', 'credenciales', 'caches'],
        'no_certifica_entrenamiento_beto': True,
    }
    salida.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(salida, 'x', compression=zipfile.ZIP_DEFLATED) as archivo:
        for nombre in nombres:
            archivo.write(raiz/nombre, 'FASE_2/'+nombre)
        archivo.writestr('FASE_2/'+MANIFIESTO, json.dumps(registro, ensure_ascii=False, indent=2)+'\n')
    return salida


def exportar(raiz=RAIZ, salida=None):
    salida = salida or Path(raiz)/'entregas'/('FASE_2_portable_'+marca_tiempo()+'.zip')
    return escribir_zip(raiz, archivos_portables(raiz), salida, 'proyecto_con_datos')


def marca_tiempo():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')


def respaldar_resultados(raiz=RAIZ):
    salida = Path(raiz)/'entregas'/('resultados_beto_'+marca_tiempo()+'.zip')
    return escribir_zip(raiz, archivos_resultados(raiz), salida, 'solo_resultados_no_proyecto')


def verificar_entrega(raiz=RAIZ):
    raiz = Path(raiz)
    registro = json.loads((raiz/MANIFIESTO).read_text(encoding='utf-8'))
    if registro['version'] != 'entrega_portable_v1' or not registro['sha256_archivos']:
        raise ValueError('Manifiesto de entrega inválido')
    for nombre, esperado in registro['sha256_archivos'].items():
        archivo = ruta_segura(raiz, nombre)
        if not archivo.is_file() or hash_archivo(archivo) != esperado:
            raise ValueError('Archivo ausente o alterado: '+nombre)
    print('Entrega íntegra:', len(registro['sha256_archivos']), 'archivos. Tipo:', registro['tipo'])
    return registro


# ---- 6. Recepción: leer ZIP no confiable y recalcular sin GPU ni sobrescrituras ----
# Los hashes prueban integridad del respaldo, no que el agente remoto ejecutó ese código.
def exigir_auditoria(condicion, mensaje):
    if not condicion:
        raise ValueError(mensaje)


def json_respaldo(datos):
    def pares_unicos(pares):
        exigir_auditoria(len({k for k, _ in pares}) == len(pares), 'Claves JSON duplicadas')
        return dict(pares)
    def constante_invalida(valor):
        raise ValueError('Número JSON no finito: '+valor)
    return json.loads(datos, object_pairs_hook=pares_unicos, parse_constant=constante_invalida)


def leer_respaldo_resultados(archivo, limite=25*1024*1024):
    """Admite respaldos parciales para integridad; nunca extrae rutas recibidas."""
    archivo = Path(archivo)
    exigir_auditoria(archivo.stat().st_size <= limite, 'ZIP demasiado grande')
    permitidos = {RESULTADOS+'/'+n for n in ['smoke.json', 'comparacion.json']}
    for fold in range(1, 6):
        permitidos.update(f'{RESULTADOS}/fold_{fold}/{n}' for n in
            ['predicciones.csv', 'cobertura.json', 'ejecucion.json', 'entrenamiento.jsonl', 'manifest.json'])
    with zipfile.ZipFile(archivo) as z:
        infos = z.infolist(); nombres = [i.filename for i in infos]
        exigir_auditoria(len(nombres) == len(set(nombres)) <= 28, 'Entradas duplicadas o excesivas')
        exigir_auditoria(sum(i.file_size for i in infos) <= limite, 'Contenido descomprimido demasiado grande')
        for i in infos:
            exigir_auditoria(i.filename in {'FASE_2/'+n for n in permitidos|{MANIFIESTO}}, 'Ruta ajena al respaldo')
            exigir_auditoria(not i.flag_bits & 1 and (i.external_attr >> 16) & 0o170000 != 0o120000,
                'Archivo cifrado o enlace simbólico')
        exigir_auditoria('FASE_2/'+MANIFIESTO in nombres, 'Falta manifiesto de entrega')
        registro = json_respaldo(z.read('FASE_2/'+MANIFIESTO))
        exigir_auditoria(registro['version'] == 'entrega_portable_v1' and
            registro['tipo'] == 'solo_resultados_no_proyecto', 'No es un respaldo de resultados')
        hashes = registro['sha256_archivos']
        exigir_auditoria(isinstance(hashes, dict) and hashes and set(hashes) <= permitidos, 'Inventario inválido')
        exigir_auditoria(set(nombres) == {'FASE_2/'+n for n in set(hashes)|{MANIFIESTO}}, 'Inventario incompleto')
        contenido = {n:z.read('FASE_2/'+n) for n in hashes}
        for n, datos in contenido.items():
            exigir_auditoria(hashlib.sha256(datos).hexdigest() == hashes[n], 'Hash alterado: '+n)
        exigir_auditoria(sum(map(len, contenido.values())) == registro['bytes_sin_comprimir'], 'Tamaño no coincide')
    return registro, contenido


def validar_registros_beto(contenido, manifiesto, documentos, folds, lock):
    """Contrasta metadatos declarados con el paquete local, sin fingir tokenización real."""
    docs = {d['intervencion_id']:d for d in documentos}
    paquete_id = manifiesto['paquete_id']; resumen = []; cobertura_anterior = None
    def objeto(nombre):
        return json_respaldo(contenido[RESULTADOS+'/'+nombre])
    def hardware_valido(h):
        exigir_auditoria(h['gpu_disponible'] is True and h['gpu_memoria_bytes'] > 0 and h['gpu'], 'GPU no declarada')
        for n, v in [('torch','2.6.0'), ('transformers','4.57.6'), ('tokenizers','0.22.2'), ('huggingface-hub','0.36.2')]:
            exigir_auditoria(h['versiones'][n].split('+')[0] == v, 'Versión declarada distinta: '+n)
    for f in folds:
        numero = f['fold']; prefijo = f'fold_{numero}/'
        m = objeto(prefijo+'manifest.json')
        exigir_auditoria(m['paquete_id'] == paquete_id and m['fold'] == numero and m['epocas_completadas'] == 3,
            'Fold/paquete/épocas distintos')
        exigir_auditoria(set(m['sha256_archivos']) == {'cobertura.json','ejecucion.json','entrenamiento.jsonl','predicciones.csv'},
            'Manifiesto de fold incompleto')
        for n, h in m['sha256_archivos'].items():
            exigir_auditoria(hashlib.sha256(contenido[RESULTADOS+'/'+prefijo+n]).hexdigest() == h, 'Hash interno distinto')
        cobertura = objeto(prefijo+'cobertura.json')
        exigir_auditoria(len(cobertura) == len(docs) and {r['intervencion_id'] for r in cobertura} == set(docs), 'Cobertura incompleta/duplicada')
        for r in cobertura:
            n = r['n_tokens_contenido']; esperado = []; inicio = 0
            exigir_auditoria(type(n) is int and 0 < n <= 1000000, 'Número de tokens inválido')
            while True:
                fin = min(inicio+510, n); esperado.append([inicio, fin])
                if fin == n: break
                inicio = fin-64
            exigir_auditoria(r['sha256_texto'] == docs[r['intervencion_id']]['sha256_texto'] and
                r['tramos'] == esperado and r['n_segmentos'] == len(esperado) and
                r['ultimo_token_cubierto'] == n and r['cobertura_completa'] is True, 'Cobertura/texto incoherente')
        exigir_auditoria(cobertura_anterior is None or cobertura_anterior == cobertura, 'Cobertura cambia entre folds')
        cobertura_anterior = cobertura
        train = [k for k in f['train'] if docs[k]['es_relevante'] == 1]
        conteos = Counter(docs[k]['etiqueta'] for k in train)
        pesos = [len(train)/(3*conteos[c]) for c in manifiesto['clases']]
        e = objeto(prefijo+'ejecucion.json'); hardware_valido(e['hardware'])
        exigir_auditoria(e['checkpoint_revision'] == lock['revision'] and e['n_train_relevante'] == len(train), 'Train/checkpoint distintos')
        exigir_auditoria(len(e['pesos_train']) == 3 and all(math.isclose(a,b,rel_tol=1e-12) for a,b in zip(pesos,e['pesos_train'])), 'Pesos de clase distintos')
        pasos_epoca = math.ceil(len(train)/8)
        registros = [json_respaldo(x) for x in contenido[RESULTADOS+'/'+prefijo+'entrenamiento.jsonl'].splitlines() if x.strip()]
        exigir_auditoria(len(registros) == 3 and e['pasos'] == pasos_epoca*3, 'Pasos/épocas incompletos')
        for epoca, r in enumerate(registros, 1):
            exigir_auditoria(r['epoca'] == epoca and r['pasos'] == epoca*pasos_epoca and
                math.isfinite(r['media_loss_grupos']) and r['media_loss_grupos'] >= 0, 'Log de entrenamiento inválido')
        exigir_auditoria(math.isfinite(e['segundos']) and e['segundos'] > 0 and
            0 < e['gpu_pico_bytes'] <= e['hardware']['gpu_memoria_bytes'], 'Tiempo/memoria inválidos')
        exigir_auditoria(not e['carga']['mismatched_keys'] and not e['carga']['error_msgs'], 'Errores declarados al cargar')
        exigir_auditoria(all(k.startswith(('classifier.', 'bert.pooler.')) for k in e['carga']['missing_keys']),
            'Faltan parámetros declarados del encoder')
        resumen.append({'fold':numero,'n_train_relevante':len(train),'pasos':e['pasos'],
            'segundos_declarados':e['segundos'],'gpu_pico_bytes_declarado':e['gpu_pico_bytes'],
            'hardware_declarado':e['hardware'],'entrenamiento':registros})
    smoke = objeto('smoke.json'); hardware_valido(smoke['hardware'])
    exigir_auditoria(smoke['estado'] == 'aprobado_con_pesos_reales' and smoke['paquete_id'] == paquete_id and
        smoke['checkpoint_revision'] == lock['revision'], 'Smoke incompatible')
    for n in ['cabeza_modificada','encoder_modificado','modelo_smoke_descartado','no_es_evaluacion']:
        exigir_auditoria(smoke[n] is True, 'Smoke incompleto: '+n)
    exigir_auditoria(math.isfinite(smoke['loss_tecnica']) and smoke['loss_tecnica'] >= 0, 'Pérdida smoke inválida')
    segmentos = {r['intervencion_id']:r['n_segmentos'] for r in cobertura_anterior}
    train = [k for k in folds[0]['train'] if docs[k]['es_relevante'] == 1]
    train.sort(key=lambda k:(segmentos[k], len(docs[k]['texto']), k))
    exigir_auditoria(smoke['train_ids'] == [train[-1], train[0]] and
        smoke['segmentos'] == [segmentos[k] for k in smoke['train_ids']], 'Smoke no usa los documentos previstos')
    return {'folds':resumen,'smoke_declarado':smoke,
        'documentos_cobertura':len(docs),'tokens_declarados':sum(r['n_tokens_contenido'] for r in cobertura_anterior),
        'segmentos_declarados':sum(segmentos.values()),'documentos_multisegmento':sum(n>1 for n in segmentos.values()),
        'max_segmentos_declarados':max(segmentos.values())}


def resumir_predicciones_beto(contenido, baseline, comparacion):
    """Segunda cuenta aritmética sin sklearn: matrices, F1 y transiciones pareadas."""
    base = {r['intervencion_id']:r for r in baseline}; filas = []
    clases = ['hawkish','dovish','neutral']
    for fold in range(1, 6):
        datos = contenido[f'{RESULTADOS}/fold_{fold}/predicciones.csv'].decode('utf-8-sig')
        for r in csv.DictReader(io.StringIO(datos)):
            filas.append((fold, r['etiqueta'], base[r['intervencion_id']]['pred'], r['pred']))
    for nombre, indice in [('tfidf',2),('beto',3)]:
        def metricas(sub):
            matriz = [[sum(r[1] == y and r[indice] == p for r in sub) for p in clases] for y in clases]
            f1 = []
            for i in range(3):
                den = sum(matriz[i])+sum(f[i] for f in matriz)
                f1.append(2*matriz[i][i]/den if den else 0.)
            return matriz, sum(f1[:2])/2, sum(f1)/3
        observado = comparacion['condiciones'][nombre]
        exigir_auditoria(metricas(filas)[0] == observado['conjunto']['matriz'], 'Matriz aritmética distinta')
        por_fold = [metricas([r for r in filas if r[0] == f]) for f in range(1,6)]
        for indice_metrica, clave in [(1,'media_f1_hd'),(2,'media_macro_f1')]:
            exigir_auditoria(math.isclose(sum(r[indice_metrica] for r in por_fold)/5, observado[clave],
                rel_tol=0, abs_tol=1e-14), 'F1 aritmética distinta')
    def tipo(y, p):
        if y == p: return 'correcto'
        if y != 'neutral' and p != 'neutral': return 'inversion_hd'
        return 'n_a_hd' if y == 'neutral' else 'hd_a_n'
    transiciones = Counter((tipo(y,a),tipo(y,b)) for _,y,a,b in filas)
    return {'comprobacion_aritmetica_independiente_del_runner':True,
        'predicciones_cambiadas':sum(a != b for _,y,a,b in filas),
        'errores_corregidos':sum(y != a and y == b for _,y,a,b in filas),
        'aciertos_perdidos':sum(y == a and y != b for _,y,a,b in filas),
        'transiciones':[{'tfidf':a,'beto':b,'n':n} for (a,b),n in sorted(transiciones.items())]}


def auditar_resultados(archivo, salida=None, raiz=RAIZ):
    """Recalcula los 793 casos mediante 39, conservando el ZIP y las salidas originales."""
    if salida is not None and Path(salida).exists():
        raise FileExistsError('No sobrescribir auditoría existente')
    registro, contenido = leer_respaldo_resultados(archivo)
    exigir_auditoria(len(contenido) == 27, 'Se necesitan cinco folds, smoke y comparación final')
    preparar(raiz)
    m, documentos, folds, lock = [json_respaldo((Path(raiz)/ENTRADA/n).read_bytes()) for n in
        ['manifest.json','documentos.json','folds.json','checkpoint.json']]
    detalles = validar_registros_beto(contenido, m, documentos, folds, lock)
    with tempfile.TemporaryDirectory(prefix='auditoria beto ') as temporal:
        destino = Path(temporal)
        for n, datos in contenido.items():
            relativo = n.removeprefix(RESULTADOS+'/')
            if relativo == 'comparacion.json': continue
            p = destino/relativo; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(datos)
        ejecutar_python(['scripts/39_ejecutar_beto.py', '--consolidar', '--salida', destino], raiz)
        recalculada = json_respaldo((destino/'comparacion.json').read_bytes())
    recibida = json_respaldo(contenido[RESULTADOS+'/comparacion.json'])
    exigir_auditoria(recalculada == recibida, 'La comparación recibida difiere de la recalculada')
    auditoria = {'estado':'integridad_y_metricas_verificadas_no_reentrenamiento',
        'archivo':Path(archivo).name,'sha256_zip':hash_archivo(archivo),'manifiesto_recibido':registro,
        'paquete_id':m['paquete_id'],'comparacion_reproducida_exactamente_como_json':True,
        'entrenamiento_repetido_localmente':False,'codigo_y_pesos_remotos_verificados':False,
        'limites':['No incluye copia/hash del código ejecutado ni binarios remotos.',
            'Cobertura coherente con tokens declarados; no se repitió tokenización con pesos/tokenizer oficiales.',
            'El campo hardware.entrenamiento_realizado=false es estático en el runner; no es un veredicto del fold.'],
        'sha256_verificadores_locales':{n:hash_archivo(Path(raiz)/n) for n in
            ['scripts/38_preparar_beto.py','scripts/39_ejecutar_beto.py','scripts/40_gestionar_proyecto.py']},
        'registros':detalles,'comparacion':recalculada}
    auditoria.update(resumir_predicciones_beto(contenido,
        json_respaldo((Path(raiz)/ENTRADA/'baseline.json').read_bytes()), recalculada))
    if salida is not None:
        p = Path(salida);p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('x', encoding='utf-8') as f:
            json.dump(auditoria, f, ensure_ascii=False, indent=2, allow_nan=False);f.write('\n')
    return auditoria


# ---- 7. Interfaz corta: no hay entrenamiento o instalación automática al consultar ayuda ----
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    acciones = parser.add_subparsers(dest='accion', required=True)
    instalacion = acciones.add_parser('instalar', help='Crear .venv e instalar dependencias CPU; no pesos')
    instalacion.add_argument('--beto', action='store_true', help='Añadir PyTorch del protocolo para equipo GPU CUDA')
    acciones.add_parser('preparar', help='Crear o verificar entrada con los datos incluidos')
    pruebas = acciones.add_parser('probar', help='Pruebas nuevas sin encoder')
    pruebas.add_argument('--regresion', action='store_true', help='Añadir los 64 controles históricos seguros')
    acciones.add_parser('comprobar', help='Comprobar el entorno BETO sin entrenar')
    acciones.add_parser('smoke', help='Prueba técnica real; requiere GPU y pesos accesibles')
    acciones.add_parser('entrenar', help='Cinco folds con respaldo al terminar cada uno; exige smoke previo')
    acciones.add_parser('comparar', help='Consolidar solo si están los cinco folds completos')
    entrega = acciones.add_parser('exportar', help='ZIP del proyecto y datos; no entorno ni pesos')
    entrega.add_argument('--salida', type=Path, help='Ruta nueva del ZIP, relativa a la terminal o absoluta')
    acciones.add_parser('verificar-entrega', help='Verificar ZIP ya extraído; solo biblioteca estándar')
    acciones.add_parser('respaldar', help='Guardar únicamente resultados GPU, incluidos intentos parciales')
    acciones.add_parser('estado', help='Mostrar ubicación y estado básico, sin instalar ni abrir respuestas')
    auditoria = acciones.add_parser('auditar-resultados', help='Verificar ZIP final y recalcular métricas sin GPU ni sobrescribir resultados')
    auditoria.add_argument('archivo', type=Path)
    auditoria.add_argument('--salida', type=Path, help='Archivo JSON nuevo para conservar la auditoría')
    muestra = acciones.add_parser('preparar-muestra-hd', help='Crear 60 candidatos reales para revisión; no etiqueta ni entrena')
    muestra.add_argument('--salida', type=Path, default=RAIZ/'data/auditoria/ampliacion_hd_60_v1')
    ampliacion = acciones.add_parser('evaluar-ampliacion-tfidf', help='Comparar control y B ampliado con 59 nuevos; CPU, sin refit global')
    ampliacion.add_argument('--salida', type=Path, default=RAIZ/'data/evaluacion/ampliacion_tfidf_59_v1')
    diagnostico = acciones.add_parser('diagnosticar-ampliacion-tfidf', help='Reconstruir el ensayo +59 y analizar sus márgenes sin nuevas variantes')
    diagnostico.add_argument('--salida', type=Path, default=RAIZ/'data/auditoria/diagnostico_ampliacion_tfidf_59_v1')
    compatibilidad = acciones.add_parser('auditar-compatibilidad', help='Auditar criterios y estructura IA sin reclasificar ni abrir respuestas humanas')
    compatibilidad.add_argument('--salida', type=Path, default=RAIZ/'data/auditoria/compatibilidad_criterios_v1')
    migracion = acciones.add_parser('preparar-migracion-v3', help='Inventariar IA y humanas autorizadas para revisión v3; no adjudica ni entrena')
    migracion.add_argument('--salida', type=Path, default=RAIZ/'data/auditoria/migracion_v3')
    referencia_v3 = acciones.add_parser('consolidar-referencia-v3', help='Unir las 1.747 revisiones v3; no entrena')
    referencia_v3.add_argument('--salida', type=Path, default=RAIZ/'data/evaluacion/referencia_v3')
    pre2000 = acciones.add_parser('auditar-set-pre2000', help='Revisar estructura/citas del XLSX pre-2000; no corrige ni entrena')
    pre2000.add_argument('--archivo', type=Path, default=RAIZ/'Set_Entrenamiento_Pre_2000.xlsx')
    pre2000.add_argument('--salida', type=Path, default=RAIZ/'data/auditoria/set_pre2000_revision_inicial_v1')
    fase_a = acciones.add_parser('evaluar-recodificacion-v3', help='Fase A: puntuar predicciones congeladas contra v2/v3; no entrena')
    fase_a.add_argument('--salida', type=Path, default=RAIZ/'data/evaluacion/recodificacion_tfidf_v3_fase_a')
    fase_b = acciones.add_parser('entrenar-tfidf-v3', help='Fase B: mismo TF-IDF/folds con supervisión v3; CPU')
    fase_b.add_argument('--salida', type=Path, default=RAIZ/'data/evaluacion/tfidf_supervision_v3_fase_b')
    fase_c = acciones.add_parser('evaluar-ampliacion-ia89-v3', help='Fase C: añadir 89 IA reales solo al train permitido')
    fase_c.add_argument('--salida', type=Path, default=RAIZ/'data/evaluacion/ampliacion_ia89_tfidf_v3_fase_c')
    sintetico = acciones.add_parser('auditar-dataset-sintetico', help='Auditar duplicados/citas/trazabilidad del CSV sintético; no entrena')
    sintetico.add_argument('--archivo', type=Path, default=RAIZ/'Dataset_Sintetico_Post2020.csv')
    sintetico.add_argument('--salida', type=Path, default=RAIZ/'data/auditoria/dataset_sintetico_post2020_v1')
    argumentos = parser.parse_args(argv)
    try:
        if argumentos.accion == 'instalar': instalar(argumentos.beto)
        elif argumentos.accion == 'preparar': preparar()
        elif argumentos.accion == 'probar': probar(argumentos.regresion)
        elif argumentos.accion in ['comprobar', 'smoke', 'comparar']:
            ejecutar_beto({'comprobar':'--comprobar', 'smoke':'--smoke', 'comparar':'--consolidar'}[argumentos.accion])
        elif argumentos.accion == 'entrenar': entrenar()
        elif argumentos.accion == 'auditar-compatibilidad':
            subprocess.run([sys.executable, '-X', 'utf8', 'scripts/auditar_compatibilidad_criterios.py',
                '--salida', str(argumentos.salida.resolve())], cwd=RAIZ, check=True)
        elif argumentos.accion == 'preparar-migracion-v3':
            subprocess.run([sys.executable, '-X', 'utf8', 'scripts/preparar_migracion_v3.py',
                '--salida', str(argumentos.salida.resolve())], cwd=RAIZ, check=True)
        elif argumentos.accion == 'consolidar-referencia-v3':
            subprocess.run([sys.executable, '-X', 'utf8', 'scripts/consolidar_referencia_v3.py',
                '--salida', str(argumentos.salida.resolve())], cwd=RAIZ, check=True)
        elif argumentos.accion == 'auditar-set-pre2000':
            subprocess.run([sys.executable, '-X', 'utf8', 'scripts/auditar_set_pre2000.py',
                '--origen', str(argumentos.archivo.resolve()), '--salida', str(argumentos.salida.resolve())],
                cwd=RAIZ, check=True)
        elif argumentos.accion == 'evaluar-recodificacion-v3':
            subprocess.run([sys.executable, '-X', 'utf8', 'scripts/evaluar_recodificacion_v3.py',
                '--salida', str(argumentos.salida.resolve())], cwd=RAIZ, check=True)
        elif argumentos.accion == 'entrenar-tfidf-v3':
            ejecutar_python(['scripts/entrenar_tfidf_supervision_v3.py',
                '--salida', str(argumentos.salida.resolve())])
        elif argumentos.accion == 'evaluar-ampliacion-ia89-v3':
            ejecutar_python(['scripts/evaluar_ampliacion_ia89_v3.py',
                '--salida', str(argumentos.salida.resolve())])
        elif argumentos.accion == 'auditar-dataset-sintetico':
            subprocess.run([sys.executable, '-X', 'utf8', 'scripts/auditar_dataset_sintetico.py',
                '--origen', str(argumentos.archivo.resolve()), '--salida', str(argumentos.salida.resolve())],
                cwd=RAIZ, check=True)
        elif argumentos.accion == 'diagnosticar-ampliacion-tfidf':
            preparar()
            ejecutar_python(['scripts/diagnosticar_ampliacion_tfidf.py', '--salida', argumentos.salida.resolve()])
        elif argumentos.accion == 'evaluar-ampliacion-tfidf':
            preparar()
            ejecutar_python(['scripts/evaluar_ampliacion_tfidf.py', '--salida', argumentos.salida.resolve()])
        elif argumentos.accion == 'preparar-muestra-hd':
            preparar()
            ejecutar_python(['scripts/muestreo_revision.py', '--salida', argumentos.salida.resolve()])
        elif argumentos.accion == 'exportar':
            preparar(); print('Entrega creada:', exportar(salida=argumentos.salida))
        elif argumentos.accion == 'verificar-entrega': verificar_entrega()
        elif argumentos.accion == 'respaldar': print(respaldar_resultados())
        elif argumentos.accion == 'auditar-resultados':
            r = auditar_resultados(argumentos.archivo, argumentos.salida)
            print(json.dumps({'estado':r['estado'], 'criterios':r['comparacion']['criterios'],
                'cumple_criterios_desarrollo':r['comparacion']['cumple_criterios_desarrollo']}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({'raiz':str(RAIZ), 'python':platform.python_version(),
                'entorno_instalado':python_entorno().is_file(),
                'entrada_presente':(RAIZ/ENTRADA/'manifest.json').is_file(),
                'comparacion_presente':(RAIZ/RESULTADOS/'comparacion.json').is_file(),
                'nota':'Presencia de archivos no valida entrenamiento; usar preparar/comparar.'}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError, subprocess.CalledProcessError) as error:
        print('DETENIDO:', error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
