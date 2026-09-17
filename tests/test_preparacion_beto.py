"""Preparación y controles sin encoder. NO son pruebas de BETO con pesos reales."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script, sha256
P=cargar_script('38_preparar_beto.py')
R=cargar_script('39_ejecutar_beto.py')


class Preparacion(unittest.TestCase):
    def test_01_ventanas_limites_y_sin_huecos(self):
        for n in [1,509,510,511,956,957,20000]:
            ids=list(range(n));tramos=P.ventanas(ids)
            self.assertEqual(tramos[0][0],0);self.assertEqual(tramos[-1][1],n)
            self.assertTrue(all(0<b-a<=510 for a,b in tramos))
            for anterior,actual in zip(tramos,tramos[1:]):self.assertEqual(anterior[1]-actual[0],64)
            cubierta=set(i for a,b in tramos for i in range(a,b))
            self.assertEqual(cubierta,set(ids))
        self.assertEqual(P.ventanas(list(range(510))),[(0,510)])

    def test_02_rechaza_segmentacion_invalida(self):
        for ids,maximo,overlap in [([],510,64),([1],510,510),([1],510,-1),([1],0,0)]:
            with self.assertRaises(ValueError):P.ventanas(ids,maximo,overlap)

    def test_03_ultima_acumulacion_incompleta(self):
        grupos=P.grupos(list(range(19)))
        self.assertEqual([len(g) for g in grupos],[8,8,3])
        self.assertEqual(sum(grupos,[]),list(range(19)))
        # Cada documento pesa 1/tamaño real dentro del grupo, no 1/8 al final.
        self.assertAlmostEqual(sum(1/len(grupos[-1]) for _ in grupos[-1]),1)
        with self.assertRaises(ValueError):P.grupos([1],0)

    def test_04_pesos_balanceados_y_clases_presentes(self):
        pesos=P.pesos_clase([0,0,1,2,2,2])
        np.testing.assert_allclose(pesos,[1,2,2/3])
        self.assertAlmostEqual(float(np.dot(pesos,[2,1,3])),6)
        with self.assertRaises(ValueError):P.pesos_clase([0,1])

    def test_05_loss_documental_no_cancela_peso_y_no_duplica_etiqueta(self):
        logits=np.array([[2.,0.,-1.],[-1.,1.,2.]])
        uno=P.perdida_referencia(logits,0,1)
        self.assertAlmostEqual(P.perdida_referencia(logits,0,3),3*uno)
        self.assertAlmostEqual(P.perdida_referencia(np.repeat(logits,2,axis=0),0,1),uno)
        # CE(media de logits) no es media de CE por segmento.
        partes=np.mean([P.perdida_referencia(x[None,:],0,1) for x in logits])
        self.assertNotAlmostEqual(uno,float(partes))
        with self.assertRaises(ValueError):P.perdida_referencia([[float('nan'),1,2]],0,1)

    def test_06_rechaza_checkpoint_y_vocabulario_distinto(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'vocab.txt';contenido=b'[PAD]\n[UNK]\n';p.write_bytes(contenido)
            oid=hashlib.sha1(b'blob '+str(len(contenido)).encode()+b'\0'+contenido).hexdigest()
            lock={'archivos':{'vocab.txt':{'bytes':len(contenido),'git_blob':oid}}}
            self.assertTrue(P.verificar_checkpoint(t,lock))
            p.write_bytes(b'[PAD]\n[CLS]\n')
            with self.assertRaises(ValueError):P.verificar_checkpoint(t,lock)
            lock['archivos']['vocab.txt']['sha256']='0'*64
            with self.assertRaises(ValueError):P.verificar_checkpoint(t,lock)

    def test_07_paquete_real_sin_citas_y_mismos_folds(self):
        m,docs,folds,baseline,lock=P.cargar_paquete()
        self.assertEqual(len(docs),1352);self.assertEqual(len(baseline),793)
        self.assertEqual([len(f['train']) for f in folds],[1178,1178,1178,1183,1183])
        self.assertFalse(any('citas' in d or 'nota' in d or 'frase_justificante' in d for d in docs))
        self.assertEqual(lock['revision'],'c4d86612f51b4f46759c8390d1798c2febe71b93')
        self.assertEqual(lock['archivos']['pytorch_model.bin']['bytes'],439621341)
        self.assertFalse(m['examen_306_abierto'])

    def test_08_rechaza_fuga_y_texto_alterado(self):
        _,docs,folds,baseline,_=P.cargar_paquete()
        f=copy.deepcopy(folds);f[0]['train'].append(f[0]['validacion'][0])
        with self.assertRaises(AssertionError):P.validar_datos(docs,f,baseline)
        d=copy.deepcopy(docs);d[0]['texto']+=' alterado'
        with self.assertRaises(AssertionError):P.validar_datos(d,folds,baseline)
        b=copy.deepcopy(baseline);b[0]['etiqueta_corregida_v2']='invalida'
        with self.assertRaises(AssertionError):P.validar_datos(docs,folds,b)

    def test_09_no_evaluacion_final_sin_cinco_folds(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(RuntimeError,'Faltan folds'):R.consolidar(P.PAQUETE,t)
            self.assertFalse((Path(t)/'comparacion.json').exists())

    def test_10_no_sobrescribe_paquete(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileExistsError):P.preparar(t)

    def test_11_tokenizador_de_juguete_y_ventanas_no_encoder(self):
        from transformers import BertTokenizerFast
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'vocab.txt';p.write_text('[PAD]\n[UNK]\n[CLS]\n[SEP]\n[MASK]\nSubir\nla\ntasa\n.\n')
            tok=BertTokenizerFast(vocab_file=str(p),do_lower_case=False,strip_accents=False)
            ids=tok('Subir la tasa. '*160,add_special_tokens=False,truncation=False)['input_ids']
            self.assertEqual(len(ids),640)
            tramos=P.ventanas(ids);self.assertEqual(tramos[-1][1],640)
            for a,b in tramos:
                encoded=tok.prepare_for_model(ids[a:b],add_special_tokens=True,truncation=False)
                self.assertLessEqual(len(encoded['input_ids']),512)
                self.assertEqual(encoded['input_ids'][1:-1],ids[a:b])

    def test_12_codigo_gpu_sintaxis_y_locks_sin_inventar_ejecucion(self):
        ast.parse((P.RAIZ/'scripts/39_ejecutar_beto.py').read_text())
        lock=json.loads(P.LOCK.read_text())
        acceso=json.loads((P.AUDITORIA/'acceso.json').read_text())
        self.assertFalse(acceso['entrenamiento_beto_realizado']);self.assertFalse(acceso['pesos_descargados'])
        self.assertNotEqual(acceso['vocabulario_historico_rechazado']['blob'],lock['archivos']['vocab.txt']['git_blob'])
        self.assertFalse(lock['safetensors_disponible_en_revision'])


    def _salidas_sinteticas_identicas_al_control(self, destino, alterar=None):
        """Fixture SOLO temporal; no simula haber ejecutado el encoder."""
        import pandas as pd
        m,_,folds,base,_=P.cargar_paquete()
        t=pd.DataFrame(base).rename(columns={'etiqueta_corregida_v2':'etiqueta'})
        for c in P.CLASES:t[f'prob_b_{c}']=t.pred_b.eq(c).astype(float)
        if alterar=='a':t.loc[0,'pred_a']=1-int(t.loc[0,'pred_a'])
        if alterar=='prob':t.loc[0,[f'prob_b_{c}' for c in P.CLASES]]=0.
        for f in folds:
            carpeta=Path(destino)/f"fold_{f['fold']}";carpeta.mkdir()
            archivo=carpeta/'predicciones.csv';t[t.fold.eq(f['fold'])].to_csv(archivo,index=False)
            P.escribir(carpeta/'manifest.json',{'paquete_id':m['paquete_id'],'fold':f['fold'],
                'epocas_completadas':3,'sha256_archivos':{'predicciones.csv':sha256(archivo)},
                'fixture_sintetica_no_ejecucion':True})

    def test_13_comparador_con_fixture_no_neural_y_ambiguos_aparte(self):
        with tempfile.TemporaryDirectory() as t:
            self._salidas_sinteticas_identicas_al_control(t)
            R.consolidar(P.PAQUETE,t)
            r=json.loads((Path(t)/'comparacion.json').read_text())
            self.assertEqual(r['condiciones']['tfidf'],r['condiciones']['beto'])
            b=r['condiciones']['tfidf']
            self.assertAlmostEqual(b['media_f1_hd'],.747060,places=6)
            self.assertEqual(b['conjunto']['matriz'],[[62,6,8],[9,38,4],[10,14,642]])
            self.assertEqual(b['conjunto']['hd_a_n'],12)
            self.assertEqual(b['conjunto']['n_a_hd'],24)
            casos=r['diagnostico_15_inversiones_conocidas_no_test']
            self.assertEqual(len(casos),15);self.assertEqual(sum(c['ambiguo_hd_conocido'] for c in casos),5)
            self.assertTrue(r['criterios_calculados_sobre_todos_los_793'])
            self.assertFalse(r['cumple_criterios_desarrollo'])
            self.assertFalse(r['evaluacion_independiente'])
            self.assertFalse(r['modelo_adoptado_automaticamente'])
            with self.assertRaises(FileExistsError):R.consolidar(P.PAQUETE,t)

    def test_14_comparador_rechaza_puerta_y_probabilidades_alteradas(self):
        for alterar in ['a','prob']:
            with self.subTest(alterar=alterar),tempfile.TemporaryDirectory() as t:
                self._salidas_sinteticas_identicas_al_control(t,alterar)
                with self.assertRaises(AssertionError):R.consolidar(P.PAQUETE,t)
                self.assertFalse((Path(t)/'comparacion.json').exists())


if __name__=='__main__':unittest.main()
