"""Selección/linaje, no pruebas de la corrección semántica de una opinión IA."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

RAIZ=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RAIZ/'scripts'))
spec=importlib.util.spec_from_file_location('revision32',RAIZ/'scripts/32_revisar_errores_nuevos.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)


def predicciones():
    filas=[]
    # a nuevo error; b error persistente; c corregido; d sigue correcto.
    for variante,salidas in [('original',['hawkish','hawkish','hawkish','neutral']),
                              ('adjudicada',['neutral','neutral','dovish','neutral'])]:
        for identificador,etiqueta,pred in zip('abcd',['hawkish','dovish','dovish','neutral'],salidas):
            filas.append({'intervencion_id':identificador,'meeting_id':'m'+identificador,
                          'fold':'1','variante':variante,'etiqueta':etiqueta,'pred':pred})
    return filas


class Seleccion(unittest.TestCase):
    def test_solo_nuevos_no_confunde_persistentes_o_corregidos(self):
        filas=predicciones();copia=copy.deepcopy(filas)
        errores,nuevos=E.seleccionar(filas)
        self.assertEqual([r['intervencion_id'] for r in errores],['a','b'])
        self.assertEqual([r['intervencion_id'] for r in nuevos],['a'])
        self.assertEqual(filas,copia)
        self.assertEqual(errores[1]['revision_cualitativa'],'pendiente')

    def test_rechaza_etiquetas_de_validacion_o_folds_distintos(self):
        for campo,valor in [('etiqueta','neutral'),('fold','2'),('meeting_id','otro')]:
            filas=predicciones();filas[4][campo]=valor
            with self.assertRaises(AssertionError):E.seleccionar(filas)

    def test_rechaza_duplicados_o_poblaciones_distintas(self):
        for filas in [predicciones()+[predicciones()[0]],predicciones()[:-1]]:
            with self.assertRaises(AssertionError):E.seleccionar(filas)

    def test_cita_literal_solo_espacios_y_limite(self):
        lectura={'estado_revision':'referencia_respaldada','postura_sugerida_agente':'dovish',
                 'citas_agente':['No subir.']}
        E.validar_lectura(lectura,'No\n subir. Bajar.')
        for cita in ['Subir.','x'*301,'']:
            lectura['citas_agente']=[cita]
            with self.assertRaises(AssertionError):E.validar_lectura(lectura,'No subir.')

    def test_duda_no_es_etiqueta_final(self):
        lectura={'estado_revision':'ambigua','postura_sugerida_agente':None,'citas_agente':['Mantener.']}
        E.validar_lectura(lectura,'Mantener.')
        lectura['postura_sugerida_agente']='neutral'
        with self.assertRaises(AssertionError):E.validar_lectura(lectura,'Mantener.')

    def test_fuentes_reales_seleccionadas_y_todos_los_extractos(self):
        errores,nuevos=E.seleccionar(E.leer_csv(E.MODELO/'predicciones_validacion.csv'))
        self.assertEqual(len(errores),66);self.assertEqual(len(nuevos),7)
        lecturas=json.loads(E.LECTURAS.read_text())['lecturas']
        self.assertEqual({r['intervencion_id'] for r in lecturas},{r['intervencion_id'] for r in nuevos})
        corpus={r['intervencion_id']:r['texto'] for r in E.leer_csv(RAIZ/'data/L0/corpus.csv')}
        for r in lecturas:E.validar_lectura(r,corpus[r['intervencion_id']])

    def test_salida_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileExistsError):E.ejecutar(Path(t),Path(t)/'informe.md')

    @unittest.skipUnless((E.SALIDA/'manifest.json').exists(),'Revisión aún no generada')
    def test_integridad_y_cobertura_sin_nuevas_etiquetas(self):
        m=json.loads((E.SALIDA/'manifest.json').read_text())
        for nombre,digest in m['sha256_insumos'].items():self.assertEqual(E.sha256(RAIZ/nombre),digest)
        for nombre,digest in m['sha256_salidas'].items():self.assertEqual(E.sha256(E.SALIDA/nombre),digest)
        self.assertEqual(E.sha256(E.INFORME),m['sha256_informe'])
        r=json.loads((E.SALIDA/'resumen.json').read_text())
        self.assertEqual(r['revisados'],7);self.assertEqual(r['pendientes'],59)
        self.assertEqual(r['referencias_respaldadas']+r['casos_ambiguos'],7)
        self.assertEqual(r['etiquetas_modificadas'],0)
        casos=json.loads((E.SALIDA/'casos_revisados.json').read_text())
        self.assertEqual(sum(len(c['texto_completo']) for c in casos),r['caracteres_textos_revisados'])


if __name__=='__main__':unittest.main()
