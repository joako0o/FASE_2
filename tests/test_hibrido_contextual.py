"""Pruebas sintéticas y de linaje IA; nunca abren las respuestas humanas."""
# ---- 1. Módulos versionados y datos didácticos ----
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import representaciones_contextuales as R
from utilidades import cargar_script, sha256
E = cargar_script('24_evaluar_hibrido_contextual.py')


class Representaciones(unittest.TestCase):
    def test_decimal_atomico_unidad_digito_y_negacion(self):
        tokens = R.tokens_numericos('no bajar desde 5,25% a 5% anual')
        self.assertEqual(tokens, ['no', 'bajar', 'desde', 'numero_5d25', 'unidad_porcentaje',
                                  'numero_5', 'unidad_porcentaje', 'anual'])
        self.assertNotIn('25', tokens)
        self.assertEqual(R.tokens_numericos('5,250 %'), R.tokens_numericos('5.25%'))

    def test_signos_fechas_y_formato_ambiguo(self):
        self.assertEqual(R.tokens_numericos('-25 +5 −2'),
                         ['signo_menos', 'numero_25', 'signo_mas', 'numero_5', 'signo_menos', 'numero_2'])
        self.assertNotIn('signo_menos', R.tokens_numericos('2007-01-11'))
        self.assertTrue(R.PATRON_AMBIGUO.search('5.250'))
        self.assertFalse(R.PATRON_AMBIGUO.search('5.25%'))

    def test_ventana_preserva_negacion_condicion_y_decimales(self):
        texto = 'No lo considero. Si la inflación persiste, propongo subir la TPM de 5 a 5,25%; no bajar. Luego se debate.'
        self.assertEqual(R.extraer_ventanas(texto), [(0, len(texto))])
        self.assertIn('no bajar', R.AnalizadorContexto()(texto))
        self.assertIn('numero_5d25 unidad_porcentaje', R.AnalizadorContexto(True)(texto))

    def test_sin_candidato_no_inventa_contexto(self):
        self.assertEqual(R.extraer_ventanas('Las estadísticas se publicaron ayer.'), [])
        self.assertEqual(R.AnalizadorContexto()('Las estadísticas se publicaron ayer.'), [])

    def test_no_puentes_entre_ventanas_ni_solapes(self):
        texto = 'TPM sube. alfa. beta. gamma. delta. omega. Sesgo baja.'
        ventanas = R.extraer_ventanas(texto)
        self.assertEqual(len(ventanas), 2)
        self.assertLess(ventanas[0][1], ventanas[1][0])
        self.assertNotIn('alfa omega', R.AnalizadorContexto()(texto))
        for inicio, fin in ventanas:
            self.assertTrue(texto[inicio:fin])
        self.assertEqual(R.extraer_ventanas('  Propongo bajar la TPM.\n  '), [(2, 24)])

    def test_apoyo_y_rechazo_no_reciben_etiqueta_de_regla(self):
        for texto in ['Apoyo bajar la TPM.', 'Rechazo bajar la TPM.',
                      'La Fed elevó su tasa; propongo mantener la TPM.',
                      'Habría subido la TPM si hubiese sido necesario.']:
            self.assertEqual(R.extraer_ventanas(texto), [(0, len(texto))])
        self.assertEqual(len(E.VARIANTES), 4)
        self.assertEqual(len(R.CASOS_CONDUCTUALES), 14)
        self.assertEqual(len({c[0] for c in R.CASOS_CONDUCTUALES}), 14)

    def test_vocabulario_exclusivo_train_y_ngramas_explicitos(self):
        parametros = {**E.ANTERIOR.PARAMETROS_TFIDF, 'min_df': 1, 'max_df': 1.0}
        with patch.object(E.ANTERIOR, 'PARAMETROS_TFIDF', parametros):
            for numerico in (False, True):
                vector, matriz = E.ajustar_bloque(['Propongo subir la TPM.', 'Prefiero bajar la TPM.'], numerico, True)
                self.assertIn('propongo subir la tpm', vector.vocabulary_)
                self.assertNotIn('xenotermino', vector.vocabulary_)
                antes = dict(vector.vocabulary_)
                E.transformar(vector, ['TPM xenotermino 7,25%.'])
                self.assertEqual(vector.vocabulary_, antes)
                self.assertEqual(matriz.shape[0], 2)

    def test_bloque_contextual_vacio_es_cero(self):
        vector, matriz = E.ajustar_bloque(['Resumen mensual.', 'Datos anuales.', 'Cifras locales.'], contexto=True)
        self.assertIsNone(vector)
        self.assertEqual(matriz.shape, (3, 0))
        self.assertEqual(E.transformar(vector, ['otro']).shape, (1, 0))

    def test_no_sobrescribe_ni_prepara_si_informe_existe(self):
        with tempfile.TemporaryDirectory() as temporal:
            informe = Path(temporal) / 'informe.md'
            informe.write_text('congelado')
            with self.assertRaises(FileExistsError):
                E.preparar(Path(temporal) / 'datos', informe)
            self.assertEqual(informe.read_text(), 'congelado')

    def test_frena_codigo_o_asignacion_modificados(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal)
            (salida / 'asignacion_folds.csv').write_text('original')
            (salida / 'protocolo.json').write_text(json.dumps({
                'variantes': E.VARIANTES, 'sha256_asignacion': 'alterado', 'sha256_insumos': {}}))
            with self.assertRaises(AssertionError):
                E.verificar_protocolo(salida)

    def test_metricas_y_criterio_no_promueven_empate(self):
        pred, folds, pruebas = [], [], []
        for variante in E.VARIANTES:
            for fold in range(1, 6):
                pred.append(dict(variante=variante, fold=fold, etiqueta='neutral', pred='neutral'))
                folds.append(dict(variante=variante, fold=fold, macro_f1=1/3))
                pruebas.append(dict(variante=variante, fold=fold, acierto=True))
        tabla = E.resumir(pd.DataFrame(pred), pd.DataFrame(folds), pd.DataFrame(pruebas),
                         dict(delta_minimo=.01, folds_mejora_minimos=3, perdida_recall_maxima=.02, perdida_conductual_maxima=.05))
        self.assertFalse(tabla.cumple_para_confirmar.any())
        self.assertTrue(tabla.delta_media.eq(0).all())


class ArtefactosHibrido(unittest.TestCase):
    @unittest.skipUnless((E.RUTA_SALIDA / 'manifest.json').exists(), 'aún sin corrida')
    def test_resultados_recalculables_y_linaje(self):
        salida = E.RUTA_SALIDA
        protocolo = E.verificar_protocolo(salida)
        manifest = json.loads((salida / 'manifest.json').read_text())
        for nombre, huella in manifest['sha256_salidas'].items():
            self.assertEqual(sha256(salida / nombre), huella)
        self.assertEqual(sha256(E.RUTA_INFORME), manifest['sha256_informe'])
        pred = pd.read_csv(salida / 'predicciones_validacion.csv')
        folds = pd.read_csv(salida / 'resultados_folds.csv')
        pruebas = pd.read_csv(salida / 'pruebas_conductuales.csv')
        self.assertEqual(len(pred), 3172)
        self.assertEqual(len(folds), 20)
        self.assertEqual(len(pruebas), 280)
        self.assertFalse(pred.duplicated(['intervencion_id', 'variante']).any())
        self.assertTrue(pred.groupby('intervencion_id').pred_a.nunique().eq(1).all())
        self.assertTrue(pred.groupby('meeting_id').fold.nunique().eq(1).all())
        self.assertTrue(pred.loc[pred.pred_a.eq(0), 'pred'].eq('neutral').all())
        for fila in folds.itertuples():
            sub = pred[pred.fold.eq(fila.fold) & pred.variante.eq(fila.variante)]
            for nombre, valor in E.ANTERIOR.metricas(sub.etiqueta, sub.pred).items():
                self.assertAlmostEqual(getattr(fila, nombre), valor)
        pd.testing.assert_frame_equal(E.resumir(pred, folds, pruebas, protocolo['tolerancias']),
                                      pd.read_csv(salida / 'comparacion_variantes.csv'))
        pd.testing.assert_frame_equal(E.comparar_errores(pred), pd.read_csv(salida / 'errores.csv'))
        anterior = pd.read_csv(E.LONGITUD.RUTA_SALIDA / 'predicciones_validacion.csv')
        columnas = ['intervencion_id', 'meeting_id', 'etiqueta', 'fold', 'pred']
        pd.testing.assert_frame_equal(pred[pred.variante.eq('B0_base')][columnas].reset_index(drop=True),
                                      anterior[anterior.ngram_max.eq(4)][columnas].reset_index(drop=True))
        datos = E.ANTERIOR.BASELINE.cargar_muestra().set_index('intervencion_id')
        ventanas = pd.read_csv(salida / 'ventanas_validacion.csv', keep_default_na=False)
        for fila in ventanas.itertuples():
            self.assertEqual(datos.loc[fila.intervencion_id, 'texto'][fila.inicio:fila.fin], fila.fragmento)


if __name__ == '__main__':
    unittest.main()
