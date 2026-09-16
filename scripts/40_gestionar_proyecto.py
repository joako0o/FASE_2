"""Entrada de trabajo y traslado. No modifica referencias ni el runner BETO congelado.

Desde la raíz: python scripts/40_gestionar_proyecto.py --help
Instalar/preparar/probar funciona sin GPU; smoke/entrenar requiere GPU CUDA y pesos.
"""

# ---- 1. Rutas y comandos seguros, independientes del directorio de la terminal ----
# El entorno se crea en el nuevo PC; nunca se copia un virtualenv entre equipos.
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import venv
import zipfile

RAIZ = Path(__file__).resolve().parents[1]
INVENTARIO = 'entrega/archivos_proyecto.txt'
MANIFIESTO = 'MANIFIESTO_ENTREGA.json'
ENTRADA = 'data/checkpoints/beto_v1/entrada'
RESULTADOS = 'data/checkpoints/beto_v1/ejecucion'
ARCHIVOS_ENTRADA = ['documentos.json', 'folds.json', 'baseline.json', 'checkpoint.json', 'manifest.json']
PRUEBAS_NUEVAS = ['test_preparacion_beto.py', 'test_entrega_portable.py']
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


# ---- 6. Interfaz corta: no hay entrenamiento o instalación automática al consultar ayuda ----
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
    argumentos = parser.parse_args(argv)
    try:
        if argumentos.accion == 'instalar': instalar(argumentos.beto)
        elif argumentos.accion == 'preparar': preparar()
        elif argumentos.accion == 'probar': probar(argumentos.regresion)
        elif argumentos.accion in ['comprobar', 'smoke', 'comparar']:
            ejecutar_beto({'comprobar':'--comprobar', 'smoke':'--smoke', 'comparar':'--consolidar'}[argumentos.accion])
        elif argumentos.accion == 'entrenar': entrenar()
        elif argumentos.accion == 'exportar':
            preparar(); print('Entrega creada:', exportar(salida=argumentos.salida))
        elif argumentos.accion == 'verificar-entrega': verificar_entrega()
        elif argumentos.accion == 'respaldar': print(respaldar_resultados())
        else:
            print(json.dumps({'raiz':str(RAIZ), 'python':platform.python_version(),
                'entorno_instalado':python_entorno().is_file(),
                'entrada_presente':(RAIZ/ENTRADA/'manifest.json').is_file(),
                'comparacion_presente':(RAIZ/RESULTADOS/'comparacion.json').is_file(),
                'nota':'Presencia de archivos no valida entrenamiento; usar preparar/comparar.'}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print('DETENIDO:', error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
