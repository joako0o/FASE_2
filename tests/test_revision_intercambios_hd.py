"""Cobertura y evidencia de la tanda 2, no certificación semántica de opiniones."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script,sha256
E=cargar_script('33_revisar_intercambios_hd.py')


def inventario():
    return [
        {'intervencion_id':'a','etiqueta_ia':'hawkish','pred_adjudicada':'dovish','revision_cualitativa':'tanda_1_nuevos'},
        {'intervencion_id':'b','etiqueta_ia':'dovish','pred_adjudicada':'hawkish','revision_cualitativa':'pendiente'},
        {'intervencion_id':'c','etiqueta_ia':'neutral','pred_adjudicada':'hawkish','revision_cualitativa':'pendiente'},
        {'intervencion_id':'d','etiqueta_ia':'hawkish','pred_adjudicada':'neutral','revision_cualitativa':'pendiente'}]


class Cobertura(unittest.TestCase):
    def test_selecciona_hd_pendientes_sin_repetir_tanda_1(self):
        filas=inventario();antes=copy.deepcopy(filas)
        seleccion=E.pendientes_hd(filas,{'a'})
        self.assertEqual([r['intervencion_id'] for r in seleccion],['b'])
        acumulado=E.actualizar_cobertura(filas,seleccion)
        self.assertEqual(filas,antes)
        self.assertEqual([r['revision_cualitativa'] for r in acumulado],['tanda_1_nuevos','tanda_2_hd','pendiente','pendiente'])
        self.assertEqual(E.pendientes_hd(acumulado,{'a','b'}),[])

    def test_rechaza_cobertura_inconsistente_y_duplicados(self):
        with self.assertRaises(AssertionError):E.pendientes_hd(inventario(),set())
        with self.assertRaises(AssertionError):E.pendientes_hd(inventario()+[inventario()[0]],{'a'})
        with self.assertRaises(AssertionError):E.actualizar_cobertura(inventario(),[inventario()[0]])

    def test_propuesta_puede_discrepar_de_ia_y_del_modelo(self):
        # La sugerencia N es válida aunque el intercambio observado fuera D/H.
        lectura={'estado_revision':'referencia_cuestionable','postura_sugerida_agente':'neutral','citas_agente':['Mantener.']}
        E.validar_lectura(lectura,'Mantener.','dovish')
        lectura['postura_sugerida_agente']='dovish'
        with self.assertRaises(AssertionError):E.validar_lectura(lectura,'Mantener.','dovish')

    def test_respaldada_debe_coincidir_con_referencia(self):
        lectura={'estado_revision':'referencia_respaldada','postura_sugerida_agente':'hawkish','citas_agente':['Subir.']}
        E.validar_lectura(lectura,'Subir.','hawkish')
        with self.assertRaises(AssertionError):E.validar_lectura(lectura,'Subir.','dovish')

    def test_duda_no_es_etiqueta_y_cita_no_se_inventa(self):
        lectura={'estado_revision':'ambigua','postura_sugerida_agente':None,'citas_agente':['Subir.']}
        E.validar_lectura(lectura,'Subir.','dovish')
        with self.assertRaises(AssertionError):E.validar_lectura(lectura,'Bajar.','dovish')
        lectura['postura_sugerida_agente']='neutral'
        with self.assertRaises(AssertionError):E.validar_lectura(lectura,'Subir.','dovish')

    def test_fuentes_reales_16_textos_y_citas_completas(self):
        previo=json.loads((E.ANTERIOR.SALIDA/'casos_revisados.json').read_text())
        filas=E.ANTERIOR.leer_csv(E.ANTERIOR.SALIDA/'inventario_errores.csv')
        seleccion=E.pendientes_hd(filas,{r['intervencion_id'] for r in previo})
        self.assertEqual(len(seleccion),16)
        lecturas=json.loads(E.LECTURAS.read_text())['lecturas']
        self.assertEqual({r['intervencion_id'] for r in seleccion},{r['intervencion_id'] for r in lecturas})
        corpus={r['intervencion_id']:r['texto'] for r in E.ANTERIOR.leer_csv(E.RAIZ/'data/L0/corpus.csv')}
        etiquetas={r['intervencion_id']:r['etiqueta_ia'] for r in seleccion}
        for r in lecturas:E.validar_lectura(r,corpus[r['intervencion_id']],etiquetas[r['intervencion_id']])
        self.assertEqual(sum(len(corpus[r['intervencion_id']]) for r in seleccion),65147)

    def test_no_sobrescribe_resultados(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileExistsError):E.ejecutar(Path(t),Path(t)/'informe.md')

    @unittest.skipUnless((E.SALIDA/'manifest.json').exists(),'Tanda 2 todavía no generada')
    def test_integridad_cobertura_y_propuestas_no_aplicadas(self):
        m=json.loads((E.SALIDA/'manifest.json').read_text())
        for nombre,digest in m['sha256_insumos'].items():self.assertEqual(sha256(E.RAIZ/nombre),digest)
        for nombre,digest in m['sha256_salidas'].items():self.assertEqual(sha256(E.SALIDA/nombre),digest)
        self.assertEqual(sha256(E.INFORME),m['sha256_informe'])
        r=json.loads((E.SALIDA/'resumen.json').read_text())
        self.assertEqual(r['acumulado']['revisados'],23)
        self.assertEqual(r['acumulado']['pendientes'],43)
        self.assertEqual(r['etiquetas_modificadas'],0)
        self.assertFalse(r['propuestas_nuevas_aceptadas_por_usuario'])
        acumulado=E.ANTERIOR.leer_csv(E.SALIDA/'inventario_acumulado.csv')
        anterior=E.ANTERIOR.leer_csv(E.ANTERIOR.SALIDA/'inventario_errores.csv')
        self.assertEqual([{k:v for k,v in r.items() if k!='revision_cualitativa'} for r in acumulado],
                         [{k:v for k,v in r.items() if k!='revision_cualitativa'} for r in anterior])


if __name__=='__main__':unittest.main()
