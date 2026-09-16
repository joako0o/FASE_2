"""Integridad y cobertura de las 66 opiniones; no certifica su verdad semántica."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script,sha256
E=cargar_script('35_cerrar_revision_66.py')


class Cierre(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventario=E.UTIL.leer_csv(E.ANTERIOR.SALIDA/'inventario_acumulado.csv')
        cls.cola=json.loads((E.ANTERIOR.SALIDA/'pendientes.json').read_text())
        cls.corpus={r['intervencion_id']:r for r in E.UTIL.leer_csv(E.RAIZ/'data/L0/corpus.csv')}
        cls.lecturas=json.loads(E.LECTURAS.read_text())['lecturas']

    def test_01_toda_la_cola_sin_mutar(self):
        antes=copy.deepcopy(self.inventario)
        seleccion=E.seleccionar_restantes(self.inventario,self.corpus,self.cola)
        self.assertEqual([r['intervencion_id'] for r in seleccion],[r['intervencion_id'] for r in self.cola])
        self.assertEqual(len(seleccion),13)
        actualizado=E.actualizar_cobertura(self.inventario,seleccion)
        self.assertEqual(self.inventario,antes)
        self.assertNotIn('pendiente',{r['revision_cualitativa'] for r in actualizado})

    def test_02_rechaza_omision_desorden_y_longitud_falsa(self):
        mala=copy.deepcopy(self.cola);mala[0]['n_caracteres']+=1
        for cola in [self.cola[1:],list(reversed(self.cola)),mala]:
            with self.assertRaises(AssertionError):E.seleccionar_restantes(self.inventario,self.corpus,cola)

    def test_03_rechaza_duplicados_y_cierre_parcial(self):
        with self.assertRaises(AssertionError):
            E.seleccionar_restantes(self.inventario+[self.inventario[0]],self.corpus,self.cola)
        with self.assertRaises(AssertionError):E.actualizar_cobertura(self.inventario,self.cola[:-1])
        with self.assertRaises(AssertionError):E.actualizar_cobertura(self.inventario,self.cola+[self.cola[0]])

    def test_04_lecturas_y_citas_reales(self):
        self.assertEqual(len(self.lecturas),13)
        self.assertEqual({r['intervencion_id'] for r in self.lecturas},{r['intervencion_id'] for r in self.cola})
        self.assertEqual(sum(len(self.corpus[r['intervencion_id']]['texto']) for r in self.lecturas),105621)
        for r in self.lecturas:
            E.VALIDADOR.validar_lectura(r,self.corpus[r['intervencion_id']]['texto'],'neutral')
        falsa={**self.lecturas[0],'citas_agente':['No existe esta cita inventada.']}
        with self.assertRaises(AssertionError):E.VALIDADOR.validar_lectura(falsa,'Mantener.','neutral')

    def test_05_textos_integros_y_anotaciones_originales(self):
        casos=json.loads((E.SALIDA/'casos_revisados.json').read_text())
        ia={r['intervencion_id']:r for p in sorted((E.RAIZ/'data/etiquetas').glob('etiquetas_*.csv')) for r in E.UTIL.leer_csv(p)}
        for caso in casos:
            texto=self.corpus[caso['intervencion_id']]['texto']
            self.assertEqual(caso['texto_completo'],texto)
            self.assertEqual(caso['sha256_texto'],hashlib.sha256(texto.encode()).hexdigest())
            self.assertEqual(caso['anotacion_ia_original'],ia[caso['intervencion_id']])
        self.assertEqual(len(casos[-1]['texto_completo']),14172)
        self.assertEqual(casos[-1]['intervencion_id'],'RPM-2007-12-13:1602:1')

    def test_06_a_b_final_contra_predicciones_congeladas(self):
        pred={r['intervencion_id']:r for r in E.UTIL.leer_csv(E.UTIL.MODELO/'predicciones_validacion.csv') if r['variante']=='adjudicada'}
        casos=json.loads((E.SALIDA/'casos_revisados.json').read_text())
        for caso in casos:
            r=pred[caso['intervencion_id']]
            self.assertEqual(caso['pred_a'],int(r['pred_a']))
            self.assertEqual(caso['pred_b'],r['pred_b'])
            self.assertEqual(caso['pred_adjudicada'],r['pred'])
            self.assertEqual(caso['pred_a'],1)
            self.assertEqual(caso['pred_adjudicada'],caso['pred_b'])

    def test_07_conteos_y_sin_adjudicacion(self):
        r=json.loads((E.SALIDA/'resumen.json').read_text())
        self.assertEqual(r['tanda_4']['revisados'],13)
        for estado,cantidad in [('referencia_respaldada',8),('referencia_cuestionable',5),('ambigua',0)]:
            self.assertEqual(r['tanda_4'][estado],cantidad)
        self.assertEqual(r['acumulado'],{'revisados':66,'pendientes':0,'referencia_respaldada':41,
            'referencia_cuestionable':13,'ambigua':12,'caracteres_pendientes':0,'caracteres_textos':265245})
        self.assertEqual(json.loads((E.SALIDA/'pendientes.json').read_text()),[])
        self.assertEqual(r['etiquetas_modificadas'],0)
        for campo in ['nuevas_propuestas_aceptadas','entrenamiento_realizado','metricas_recalculadas','examen_306_abierto']:
            self.assertIs(r[campo],False)

    def test_08_inventario_y_opiniones_previas_sin_reescritura(self):
        actual=E.UTIL.leer_csv(E.SALIDA/'inventario_acumulado.csv')
        quitar=lambda filas:[{k:v for k,v in r.items() if k!='revision_cualitativa'} for r in filas]
        self.assertEqual(quitar(actual),quitar(self.inventario))
        previos=sum([json.loads((p/'casos_revisados.json').read_text()) for p in [E.UTIL.SALIDA,E.VALIDADOR.SALIDA,E.ANTERIOR.SALIDA]],[])
        nuevos=json.loads((E.SALIDA/'casos_revisados.json').read_text())
        filas=E.UTIL.leer_csv(E.SALIDA/'revision_consolidada.csv')
        esperadas=[{k:'' if v is None else str(v) for k,v in r.items()} for r in E.consolidar(previos+nuevos)]
        self.assertEqual(filas,esperadas)
        self.assertEqual(len(filas),66)
        self.assertEqual(len({r['intervencion_id'] for r in filas}),66)
        for r in filas:
            self.assertEqual(r['cambios_aplicados'],'False')
            self.assertEqual(r['nuevas_correcciones_aceptadas'],'False')
            self.assertTrue((E.RAIZ/r['archivo_evidencia']).is_file())
            if r['estado_revision']=='ambigua':self.assertEqual(r['postura_sugerida_agente'],'')

    def test_09_hashes_insumos_salidas_e_informe(self):
        m=json.loads((E.SALIDA/'manifest.json').read_text())
        for nombre,digest in m['sha256_insumos'].items():self.assertEqual(sha256(E.RAIZ/nombre),digest)
        for nombre,digest in m['sha256_salidas'].items():self.assertEqual(sha256(E.SALIDA/nombre),digest)
        self.assertEqual(sha256(E.INFORME),m['sha256_informe'])

    def test_10_no_sobrescribe_ni_informe_ni_directorio(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);informe=p/'informe.md';informe.write_text('intacto')
            with self.assertRaises(FileExistsError):E.ejecutar(p/'nueva',informe)
            self.assertFalse((p/'nueva').exists());self.assertEqual(informe.read_text(),'intacto')
            with self.assertRaises(FileExistsError):E.ejecutar(p,p/'otro.md')


if __name__=='__main__':unittest.main()
