"""Controles de selección, cobertura y evidencia; no validación semántica IA."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script,sha256
E=cargar_script('34_revisar_neutralidad.py')


def inventados():
    filas=[{'intervencion_id':i,'etiqueta_ia':'neutral','pred_adjudicada':'hawkish','revision_cualitativa':'pendiente'} for i in ['c','d','b','a']]
    filas[-1]['revision_cualitativa']='tanda_1_nuevos'
    corpus={i:{'texto':t} for i,t in [('a','x'),('b','bb'),('c','cc'),('d','texto largo')]}
    return filas,corpus


class Seleccion(unittest.TestCase):
    def test_longitud_id_sin_repetir_y_sin_mutar(self):
        filas,corpus=inventados();antes=copy.deepcopy(filas)
        elegidas,pendientes=E.seleccionar_cortos(filas,corpus,2)
        self.assertEqual([r['intervencion_id'] for r in elegidas],['b','c'])
        self.assertEqual([r['intervencion_id'] for r in pendientes],['d'])
        self.assertEqual(filas,antes)
        acumulado=E.actualizar_cobertura(filas,elegidas)
        self.assertEqual(filas,antes)
        self.assertEqual({r['intervencion_id'] for r in acumulado if r['revision_cualitativa']=='pendiente'},{'d'})

    def test_no_hay_hd_pendientes_y_no_hay_duplicados(self):
        filas,corpus=inventados();filas[0]['etiqueta_ia']='dovish'
        with self.assertRaises(AssertionError):E.seleccionar_cortos(filas,corpus)
        filas,corpus=inventados()
        with self.assertRaises(AssertionError):E.seleccionar_cortos(filas+[filas[0]],corpus)
        with self.assertRaises(AssertionError):E.actualizar_cobertura(filas,[filas[-1]])

    def test_no_reinterpreta_duda_como_neutral(self):
        lectura={'estado_revision':'ambigua','postura_sugerida_agente':None,'citas_agente':['Llevar a 3,5%.']}
        E.ANTERIOR.validar_lectura(lectura,'Llevar a 3,5%.','hawkish')
        lectura['postura_sugerida_agente']='neutral'
        with self.assertRaises(AssertionError):E.ANTERIOR.validar_lectura(lectura,'Llevar a 3,5%.','hawkish')

    def test_no_inventa_cita_para_justificar_cambio(self):
        lectura={'estado_revision':'referencia_cuestionable','postura_sugerida_agente':'dovish','citas_agente':['Bajar.']}
        with self.assertRaises(AssertionError):E.ANTERIOR.validar_lectura(lectura,'Subir.','neutral')

    def test_30_textos_reales_integros_y_todas_las_citas(self):
        filas=E.UTIL.leer_csv(E.ANTERIOR.SALIDA/'inventario_acumulado.csv')
        corpus={r['intervencion_id']:r for r in E.UTIL.leer_csv(E.RAIZ/'data/L0/corpus.csv')}
        elegidas,resto=E.seleccionar_cortos(filas,corpus)
        self.assertEqual(len(elegidas),30);self.assertEqual(len(resto),13)
        self.assertEqual(sum(len(corpus[r['intervencion_id']]['texto']) for r in elegidas),72911)
        self.assertLessEqual(max(len(corpus[r['intervencion_id']]['texto']) for r in elegidas),min(len(corpus[r['intervencion_id']]['texto']) for r in resto))
        lecturas=json.loads(E.LECTURAS.read_text())['lecturas']
        self.assertEqual({r['intervencion_id'] for r in elegidas},{r['intervencion_id'] for r in lecturas})
        etiquetas={r['intervencion_id']:r['etiqueta_ia'] for r in elegidas}
        for r in lecturas:E.ANTERIOR.validar_lectura(r,corpus[r['intervencion_id']]['texto'],etiquetas[r['intervencion_id']])

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileExistsError):E.ejecutar(Path(t),Path(t)/'informe.md')

    @unittest.skipUnless((E.SALIDA/'manifest.json').exists(),'Tanda aún no generada')
    def test_integridad_acumulada_y_no_cambios(self):
        m=json.loads((E.SALIDA/'manifest.json').read_text())
        for nombre,digest in m['sha256_insumos'].items():self.assertEqual(sha256(E.RAIZ/nombre),digest)
        for nombre,digest in m['sha256_salidas'].items():self.assertEqual(sha256(E.SALIDA/nombre),digest)
        self.assertEqual(sha256(E.INFORME),m['sha256_informe'])
        actual=E.UTIL.leer_csv(E.SALIDA/'inventario_acumulado.csv')
        previo=E.UTIL.leer_csv(E.ANTERIOR.SALIDA/'inventario_acumulado.csv')
        self.assertEqual([{k:v for k,v in r.items() if k!='revision_cualitativa'} for r in actual],[{k:v for k,v in r.items() if k!='revision_cualitativa'} for r in previo])
        resumen=json.loads((E.SALIDA/'resumen.json').read_text())
        self.assertEqual(resumen['acumulado']['revisados'],53)
        self.assertEqual(resumen['acumulado']['pendientes'],13)
        self.assertEqual(resumen['etiquetas_modificadas'],0)
        self.assertFalse(resumen['nuevas_propuestas_aceptadas'])

    @unittest.skipUnless((E.SALIDA/'manifest.json').exists(),'Tanda aún no generada')
    def test_etapa_a_b_y_final_corresponden_a_predicciones_guardadas(self):
        casos=json.loads((E.SALIDA/'casos_revisados.json').read_text())
        pred={r['intervencion_id']:r for r in E.UTIL.leer_csv(E.UTIL.MODELO/'predicciones_validacion.csv') if r['variante']=='adjudicada'}
        for caso in casos:
            r=pred[caso['intervencion_id']]
            self.assertEqual(caso['pred_a'],int(r['pred_a']))
            self.assertEqual(caso['pred_b'],r['pred_b'])
            self.assertEqual(caso['pred_adjudicada'],r['pred'])
            self.assertEqual(caso['pred_a'],1)
            self.assertEqual(caso['pred_b'],caso['pred_adjudicada'])


if __name__=='__main__':unittest.main()
