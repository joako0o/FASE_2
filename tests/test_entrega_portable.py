"""Pruebas de traslado con archivos sintéticos; no abre etiquetas ni ejecuta BETO."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

RUTA = Path(__file__).resolve().parents[1]/'scripts/40_gestionar_proyecto.py'
spec = importlib.util.spec_from_file_location('entrega40', RUTA)
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)


class EntregaPortable(unittest.TestCase):
    def crear_ejemplo(self, raiz):
        (raiz/'entrega').mkdir()
        (raiz/E.INVENTARIO).write_text('entrega/archivos_proyecto.txt\nREADME.md\ndata/prueba.csv\n', encoding='utf-8')
        (raiz/'README.md').write_text('Ejemplo sintético, no resultados del proyecto.\n', encoding='utf-8')
        (raiz/'data').mkdir()
        (raiz/'data/prueba.csv').write_bytes('texto\r\nEspañol: acción\r\n'.encode())
        (raiz/E.ENTRADA).mkdir(parents=True)
        for nombre in E.ARCHIVOS_ENTRADA:
            (raiz/E.ENTRADA/nombre).write_text('{}\n')

    def test_01_inventario_excluye_basura_no_declarada(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp); self.crear_ejemplo(raiz)
            for nombre in ['.env', 'archivo_personal.txt', 'modelos/peso.bin', '.venv/secreto.txt']:
                p=raiz/nombre;p.parent.mkdir(exist_ok=True);p.write_text('NO EXPORTAR')
            nombres=E.archivos_portables(raiz)
            self.assertEqual(len(nombres),8)
            self.assertNotIn('.env',nombres)
            self.assertFalse(any('personal' in n or '.venv/' in n or 'modelos/' in n for n in nombres))

    def test_02_zip_sin_git_y_bytes_crlf_intactos(self):
        with tempfile.TemporaryDirectory(prefix='entrega con espacios ') as tmp:
            raiz=Path(tmp)/'original';raiz.mkdir();self.crear_ejemplo(raiz)
            archivo=E.exportar(raiz,Path(tmp)/'entrega.zip')
            destino=Path(tmp)/'otro pc con espacios'
            with zipfile.ZipFile(archivo) as z:z.extractall(destino)
            copia=destino/'FASE_2';r=E.verificar_entrega(copia)
            self.assertEqual(r['tipo'],'proyecto_con_datos')
            self.assertIsNone(r['git_commit_informativo'])
            self.assertEqual((copia/'data/prueba.csv').read_bytes(),(raiz/'data/prueba.csv').read_bytes())

    def test_03_rechaza_archivo_alterado(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp)/'original';raiz.mkdir();self.crear_ejemplo(raiz)
            archivo=E.exportar(raiz,Path(tmp)/'entrega.zip')
            with zipfile.ZipFile(archivo) as z:z.extractall(Path(tmp)/'copia')
            copia=Path(tmp)/'copia/FASE_2';(copia/'README.md').write_text('alterado')
            with self.assertRaisesRegex(ValueError,'alterado'):E.verificar_entrega(copia)

    def test_04_rechaza_rutas_ajenas_y_caches(self):
        with tempfile.TemporaryDirectory() as tmp:
            for nombre in ['../fuera','/absoluta','C:/secreto','.env','.env.local','.netrc','id_rsa',r'..\fuera','.git/config','.venv/bin/python','modelos/peso.bin','entregas/copia.zip','scripts/__pycache__/a.pyc']:
                with self.subTest(nombre=nombre), self.assertRaises(ValueError):E.ruta_segura(tmp,nombre)

    def test_05_rechaza_inventario_incompleto_o_duplicado(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp);self.crear_ejemplo(raiz);p=raiz/E.INVENTARIO
            original=p.read_text();p.write_text(original+'README.md\n')
            with self.assertRaises(ValueError):E.archivos_portables(raiz)
            p.write_text(original+'falta.txt\n')
            with self.assertRaises(FileNotFoundError):E.archivos_portables(raiz)

    def test_06_no_sobrescribe_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp);self.crear_ejemplo(raiz);archivo=E.exportar(raiz,raiz/'copia.zip')
            anterior=archivo.read_bytes()
            with self.assertRaises(FileExistsError):E.exportar(raiz,archivo)
            self.assertEqual(archivo.read_bytes(),anterior)

    def test_07_preparacion_repetida_verifica_no_reescribe(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(E,'ejecutar_python') as ejecutar:
            raiz=Path(tmp);E.preparar(raiz)
            self.assertEqual(ejecutar.call_args.args[0],['scripts/38_preparar_beto.py'])
            (raiz/E.ENTRADA).mkdir(parents=True);E.preparar(raiz)
            self.assertEqual(ejecutar.call_args.args[0],['scripts/38_preparar_beto.py','--verificar'])

    def test_08_suite_acotada_sin_examen_antiguo(self):
        with patch.object(E,'preparar'),patch.object(E,'ejecutar_python') as ejecutar:
            E.probar(True)
            patrones=[c.args[0][-2] for c in ejecutar.call_args_list]
            self.assertEqual(patrones,E.PRUEBAS_NUEVAS+E.PRUEBAS_ANTERIORES_SEGURAS)
            self.assertNotIn('test_integridad.py',patrones)
            self.assertNotIn('test_seleccion_y_test.py',patrones)

    def test_09_fallo_fold_detiene_y_respalda_sin_continuar(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(E,'preparar'),patch.object(E,'respaldar_resultados') as copia,patch.object(E,'ejecutar_python') as ejecutar:
            raiz=Path(tmp);(raiz/E.RESULTADOS).mkdir(parents=True)
            ejecutar.side_effect=subprocess.CalledProcessError(1,['fallo sintetico'])
            with self.assertRaises(subprocess.CalledProcessError):E.entrenar(raiz)
            self.assertEqual(ejecutar.call_count,1);copia.assert_called_once_with(raiz)

    def test_10_respaldo_no_incluye_pesos_ni_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp);carpeta=raiz/E.RESULTADOS/'fold_1';carpeta.mkdir(parents=True)
            (carpeta/'entrenamiento.jsonl').write_text('{}\n')
            (carpeta/'peso.bin').write_bytes(b'no incluir')
            archivo=E.respaldar_resultados(raiz)
            with zipfile.ZipFile(archivo) as z:
                self.assertNotIn('FASE_2/'+E.RESULTADOS+'/fold_1/peso.bin',z.namelist())
                r=json.loads(z.read('FASE_2/'+E.MANIFIESTO))
                self.assertEqual(r['tipo'],'solo_resultados_no_proyecto')
                self.assertEqual(len(r['sha256_archivos']),1)

    def test_11_cinco_folds_sin_cambiar_parametros(self):
        with patch.object(E,'preparar'),patch.object(E,'ejecutar_python') as ejecutar,patch.object(E,'respaldar_resultados') as copia:
            E.entrenar()
            self.assertEqual(ejecutar.call_count,5);self.assertEqual(copia.call_count,5)
            for numero,llamada in enumerate(ejecutar.call_args_list,1):
                self.assertEqual(llamada.args[0],['scripts/39_ejecutar_beto.py','--fold',numero,'--reanudar'])

    def test_12_rechaza_enlace_a_archivo_externo(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp)/'raiz';raiz.mkdir();externo=Path(tmp)/'externo.txt';externo.write_text('no incluir')
            try:(raiz/'enlace.txt').symlink_to(externo)
            except OSError as error:self.skipTest('El sistema no permite crear symlinks: '+str(error))
            with self.assertRaises(ValueError):E.ruta_segura(raiz,'enlace.txt')


if __name__=='__main__':unittest.main()
