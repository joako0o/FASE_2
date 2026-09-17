"""Pruebas de traslado con archivos sintéticos; no abre etiquetas ni ejecuta BETO."""
import importlib.util
import hashlib
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


class RecepcionResultados(unittest.TestCase):
    def respaldo(self, raiz):
        p=raiz/E.RESULTADOS/'fold_1';p.mkdir(parents=True)
        (p/'entrenamiento.jsonl').write_text('{}\n')
        return E.respaldar_resultados(raiz)

    def test_13_integridad_parcial_no_equivale_a_cinco_folds(self):
        with tempfile.TemporaryDirectory() as t:
            z=self.respaldo(Path(t));registro,datos=E.leer_respaldo_resultados(z)
            self.assertEqual(len(datos),1)
            with patch.object(E,'preparar') as preparar:
                with self.assertRaisesRegex(ValueError,'cinco folds'):E.auditar_resultados(z)
                preparar.assert_not_called()

    def test_14_zip_rechaza_traversal_y_archivos_no_autorizados(self):
        for nombre in ['../fuera','FASE_2/.env','FASE_2/scripts/ejecutar.py','/tmp/a','FASE_2/data/gold.csv']:
            with tempfile.TemporaryDirectory() as t:
                z=self.respaldo(Path(t))
                with zipfile.ZipFile(z,'a') as f:f.writestr(nombre,'no abrir')
                with self.assertRaisesRegex(ValueError,'Ruta ajena'):E.leer_respaldo_resultados(z)

    def test_15_zip_rechaza_duplicados_enlaces_y_tamano(self):
        with tempfile.TemporaryDirectory() as t:
            z=self.respaldo(Path(t))
            with self.assertRaisesRegex(ValueError,'grande'):E.leer_respaldo_resultados(z,limite=10)
            with zipfile.ZipFile(z,'a') as f:
                enlace=zipfile.ZipInfo('FASE_2/'+E.RESULTADOS+'/smoke.json')
                enlace.create_system=3;enlace.external_attr=(0o120777 << 16);f.writestr(enlace,'/tmp/secreto')
            with self.assertRaisesRegex(ValueError,'enlace'):E.leer_respaldo_resultados(z)
        with tempfile.TemporaryDirectory() as t:
            z=self.respaldo(Path(t))
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',UserWarning)
                with zipfile.ZipFile(z,'a') as f:f.writestr('FASE_2/'+E.MANIFIESTO,'{}')
            with self.assertRaisesRegex(ValueError,'duplicadas'):E.leer_respaldo_resultados(z)

    def test_16_json_y_hash_alterado(self):
        for datos in ['{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}']:
            with self.assertRaises(ValueError):E.json_respaldo(datos)
        with tempfile.TemporaryDirectory() as t:
            z=self.respaldo(Path(t));otro=Path(t)/'alterado.zip'
            with zipfile.ZipFile(z) as f,zipfile.ZipFile(otro,'w') as g:
                for n in f.namelist():g.writestr(n,b'cambiado' if n.endswith('.jsonl') else f.read(n))
            with self.assertRaisesRegex(ValueError,'Hash alterado'):E.leer_respaldo_resultados(otro)

    def ejemplo_registros(self):
        def h(b):return hashlib.sha256(b).hexdigest()
        def serial(v):return json.dumps(v).encode()
        docs=[{'intervencion_id':k,'texto':k,'sha256_texto':h(k.encode()),'etiqueta':c,'es_relevante':1}
              for k,c in zip(['a','b','c'],['hawkish','dovish','neutral'])]
        folds=[{'fold':f,'train':['a','b','c'],'validacion':[]} for f in range(1,6)]
        m={'paquete_id':'sintetico','clases':['hawkish','dovish','neutral']};lock={'revision':'fixture'}
        cobertura=[{'intervencion_id':d['intervencion_id'],'sha256_texto':d['sha256_texto'],
            'n_tokens_contenido':5,'n_segmentos':1,'tramos':[[0,5]],'ultimo_token_cubierto':5,'cobertura_completa':True} for d in docs]
        hardware={'gpu_disponible':True,'gpu':'fixture_no_real','gpu_memoria_bytes':1000,
            'versiones':{'torch':'2.6.0','transformers':'4.57.6','tokenizers':'0.22.2','huggingface-hub':'0.36.2'}}
        ejecucion={'hardware':hardware,'checkpoint_revision':'fixture','n_train_relevante':3,'pesos_train':[1,1,1],
            'pasos':3,'segundos':1,'gpu_pico_bytes':500,'carga':{'mismatched_keys':[],'error_msgs':[],'missing_keys':[]}}
        datos={}
        for f in range(1,6):
            pref=E.RESULTADOS+f'/fold_{f}/'
            datos[pref+'ejecucion.json']=serial(ejecucion);datos[pref+'cobertura.json']=serial(cobertura)
            datos[pref+'predicciones.csv']=b'fixture_sin_predicciones_reales\n'
            datos[pref+'entrenamiento.jsonl']=b'\n'.join(serial({'epoca':i,'pasos':i,'media_loss_grupos':.4}) for i in range(1,4))
            datos[pref+'manifest.json']=serial({'paquete_id':'sintetico','fold':f,'epocas_completadas':3,
                'sha256_archivos':{n:h(datos[pref+n]) for n in ['ejecucion.json','cobertura.json','predicciones.csv','entrenamiento.jsonl']}})
        datos[E.RESULTADOS+'/smoke.json']=serial({'hardware':hardware,'estado':'aprobado_con_pesos_reales','paquete_id':'sintetico',
            'checkpoint_revision':'fixture','cabeza_modificada':True,'encoder_modificado':True,'modelo_smoke_descartado':True,
            'no_es_evaluacion':True,'loss_tecnica':.4,'train_ids':['c','a'],'segmentos':[1,1]})
        return datos,m,docs,folds,lock

    def cambiar_objeto(self,datos,nombre,transformar):
        clave=E.RESULTADOS+'/'+nombre;obj=json.loads(datos[clave]);transformar(obj)
        datos[clave]=json.dumps(obj).encode()
        if nombre.startswith('fold_') and not nombre.endswith('manifest.json'):
            carpeta,n=nombre.split('/');k=E.RESULTADOS+'/'+carpeta+'/manifest.json';m=json.loads(datos[k])
            m['sha256_archivos'][n]=hashlib.sha256(datos[clave]).hexdigest();datos[k]=json.dumps(m).encode()

    def test_17_registros_sinteticos_coherentes(self):
        r=E.validar_registros_beto(*self.ejemplo_registros())
        self.assertEqual(r['documentos_cobertura'],3);self.assertEqual(len(r['folds']),5)

    def test_18_rechaza_metadatos_aunque_se_recalculen_hashes(self):
        casos=[('fold_1/ejecucion.json',lambda r:r.update(pasos=99)),
               ('fold_1/ejecucion.json',lambda r:r.update(pesos_train=[2,2,2])),
               ('fold_1/ejecucion.json',lambda r:r['hardware']['versiones'].update(torch='2.7.0')),
               ('fold_1/ejecucion.json',lambda r:r['carga'].update(missing_keys=['bert.encoder.layer.0.weight'])),
               ('fold_1/cobertura.json',lambda r:r[0].update(tramos=[[1,5]])),
               ('fold_1/manifest.json',lambda r:r.update(paquete_id='otro')),
               ('smoke.json',lambda r:r.update(encoder_modificado=False)),
               ('smoke.json',lambda r:r.update(train_ids=['a','b']))]
        for nombre,cambio in casos:
            with self.subTest(nombre=nombre):
                args=self.ejemplo_registros();self.cambiar_objeto(args[0],nombre,cambio)
                with self.assertRaises(ValueError):E.validar_registros_beto(*args)

    def test_19_no_sobrescribe_auditoria(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'auditoria.json';p.write_text('conservar')
            with self.assertRaises(FileExistsError):E.auditar_resultados(Path(t)/'no_existe.zip',p)
            self.assertEqual(p.read_text(),'conservar')

    def test_20_recuento_aritmetico_y_transiciones(self):
        datos={};base=[]
        for f in range(1,6):
            datos[f'{E.RESULTADOS}/fold_{f}/predicciones.csv']=f'intervencion_id,etiqueta,pred\n{f},dovish,dovish\n'.encode()
            base.append({'intervencion_id':str(f),'pred':'hawkish'})
        comp={'condiciones':{
            'tfidf':{'media_f1_hd':0.,'media_macro_f1':0.,'conjunto':{'matriz':[[0,0,0],[5,0,0],[0,0,0]]}},
            'beto':{'media_f1_hd':.5,'media_macro_f1':1/3,'conjunto':{'matriz':[[0,0,0],[0,5,0],[0,0,0]]}}}}
        r=E.resumir_predicciones_beto(datos,base,comp)
        self.assertEqual(r['errores_corregidos'],5);self.assertEqual(r['aciertos_perdidos'],0)
        self.assertEqual(r['predicciones_cambiadas'],5)
        comp['condiciones']['beto']['media_f1_hd']=.9
        with self.assertRaisesRegex(ValueError,'F1 aritmética'):E.resumir_predicciones_beto(datos,base,comp)


if __name__=='__main__':unittest.main()
