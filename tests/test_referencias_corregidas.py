"""Aplicación exacta, aislamiento y comparación 2×2; no abre respuestas humanas."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script, sha256
E = cargar_script('36_evaluar_referencias_corregidas.py')


def ejemplo():
    datos = pd.DataFrame([
        {'intervencion_id': 'a', 'texto': 'Subir.', 'etiqueta': 'neutral', 'es_relevante': '1'},
        {'intervencion_id': 'b', 'texto': 'Duda.', 'etiqueta': 'dovish', 'es_relevante': '1'}])
    asignacion = pd.DataFrame({'intervencion_id': ['a', 'b'], 'fold_validacion': [1, 2]})
    correcciones = pd.DataFrame([{'intervencion_id': 'a', 'etiqueta_ia_original': 'neutral',
        'etiqueta_corregida': 'hawkish', 'sha256_texto': hashlib.sha256(b'Subir.').hexdigest()}])
    return datos, asignacion, correcciones


class Correcciones(unittest.TestCase):
    def test_01_aplica_solo_por_id_sin_mutar(self):
        d, a, c = ejemplo(); antes = d.copy(deep=True)
        r = E.aplicar_correcciones(d, a, c)
        pd.testing.assert_frame_equal(d, antes)
        self.assertEqual(r.etiqueta.tolist(), ['hawkish', 'dovish'])
        pd.testing.assert_frame_equal(r.drop(columns='etiqueta'), d.drop(columns='etiqueta'))

    def test_02_rechaza_texto_o_etiqueta_discordante(self):
        for campo, valor in [('sha256_texto', 'incorrecto'), ('etiqueta_ia_original', 'dovish')]:
            d, a, c = ejemplo(); c.loc[0, campo] = valor
            with self.assertRaises(AssertionError): E.aplicar_correcciones(d, a, c)

    def test_03_rechaza_clase_nula_invalida_o_no_cambio(self):
        for valor in [None, 'ambigua', 'neutral']:
            d, a, c = ejemplo(); c.loc[0, 'etiqueta_corregida'] = valor
            with self.assertRaises(AssertionError): E.aplicar_correcciones(d, a, c)

    def test_04_rechaza_relevancia_cero_o_fold_cero(self):
        d, a, c = ejemplo(); d.loc[0, 'es_relevante'] = '0'
        with self.assertRaises(AssertionError): E.aplicar_correcciones(d, a, c)
        d, a, c = ejemplo(); a.loc[0, 'fold_validacion'] = 0
        with self.assertRaises(AssertionError): E.aplicar_correcciones(d, a, c)

    def test_05_rechaza_id_ajeno_o_duplicado(self):
        d, a, c = ejemplo()
        with self.assertRaises(AssertionError): E.aplicar_correcciones(d, a, pd.concat([c, c]))
        c.loc[0, 'intervencion_id'] = 'fuera'
        with self.assertRaises(AssertionError): E.aplicar_correcciones(d, a, c)

    def test_06_aceptacion_y_12_ambiguos_inmutables(self):
        original, seis, nueva, particiones, vista, controles = E.cargar()
        self.assertEqual(len(vista), 1352)
        self.assertEqual(int(vista.correccion_nueva_aceptada.sum()), 13)
        self.assertEqual(int(original.etiqueta.ne(nueva.etiqueta).sum()), 16)
        self.assertEqual(int(seis.etiqueta.ne(nueva.etiqueta).sum()), 13)
        self.assertEqual(int(controles.referencias_corregidas_en_val.sum()), 13)
        for _, _, train, val in particiones:
            self.assertFalse(set(original.iloc[train].meeting_id) & set(original.iloc[val].meeting_id))

    def test_07_referencia_cambiada_no_es_modelo_cambiado(self):
        filas = []
        for supervision in E.SUPERVISIONES:
            for i in range(793):
                real = ['hawkish', 'dovish', 'neutral'][i % 3]
                filas.append({'intervencion_id': str(i), 'fold': i % 5 + 1,
                    'supervision': supervision, 'etiqueta_ia_original': real,
                    'etiqueta_corregida_v2': 'hawkish' if i == 2 else real,
                    'pred': 'hawkish' if i == 2 else real})
        r, _ = E.puntuar(pd.DataFrame(filas))
        self.assertEqual(r['predicciones_distintas'], 0)
        self.assertEqual(r['delta_entrenamiento_referencia_corregida_fija'], 0)
        self.assertGreater(r['delta_solo_referencia_control_fijo'], 0)

    def test_08_referencia_identica_entre_modelos(self):
        p = pd.read_csv(E.SALIDA/'predicciones_validacion.csv')
        r, _ = E.puntuar(p)
        self.assertFalse(r['evaluacion_independiente'])
        p.loc[p.supervision.eq('seis_mas_trece'), 'etiqueta_corregida_v2'] = 'neutral'
        with self.assertRaises(AssertionError): E.puntuar(p)

    def test_09_control_reproduce_ancla_31_y_puerta(self):
        p = pd.read_csv(E.SALIDA/'predicciones_validacion.csv')
        anterior = pd.read_csv(E.PREV.SALIDA/'predicciones_validacion.csv')
        a = p[p.supervision.eq('seis_previas')].sort_values('intervencion_id').reset_index(drop=True)
        b = anterior[anterior.variante.eq('adjudicada')].sort_values('intervencion_id').reset_index(drop=True)
        columnas = ['intervencion_id', 'meeting_id', 'fold', 'pred_a', 'pred_b', 'pred']
        pd.testing.assert_frame_equal(a[columnas], b[columnas])
        n = p[p.supervision.eq('seis_mas_trece')].sort_values('intervencion_id').reset_index(drop=True)
        self.assertEqual(a.pred_a.tolist(), n.pred_a.tolist())
        for fila in p.itertuples():
            self.assertEqual(fila.pred, 'neutral' if fila.pred_a == 0 else fila.pred_b)

    def test_10_matriz_doble_y_vista_real(self):
        p = pd.read_csv(E.SALIDA/'predicciones_validacion.csv')
        r, folds = E.puntuar(p)
        self.assertEqual(len(p), 1586)
        self.assertEqual(len(folds), 20)
        self.assertEqual(r, json.loads((E.SALIDA/'metricas.json').read_text()))
        vista = pd.read_csv(E.SALIDA/'referencias_desarrollo_v2.csv').set_index('intervencion_id')
        for fila in p.itertuples():
            self.assertEqual(fila.etiqueta_corregida_v2, vista.loc[fila.intervencion_id].etiqueta_corregida_v2)
            self.assertEqual(fila.etiqueta_ia_original, vista.loc[fila.intervencion_id].etiqueta_ia_original)
        self.assertFalse(r['modelo_persistido']); self.assertFalse(r['beto_ejecutado'])
        self.assertFalse(r['examen_306_abierto'])

    def test_11_hashes_preparacion_y_salidas(self):
        p = json.loads((E.SALIDA/'protocolo.json').read_text())
        E.PREV.verificar_hashes(p['sha256_insumos'])
        for n, h in p['sha256_preparacion'].items(): self.assertEqual(sha256(E.SALIDA/n), h)
        m = json.loads((E.SALIDA/'manifest.json').read_text())
        for n, h in m['sha256_salidas'].items(): self.assertEqual(sha256(E.SALIDA/n), h)
        self.assertEqual(sha256(E.INFORME), m['sha256_informe'])
        self.assertTrue(m['ancla_31_reproducida'])

    def test_12_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); informe = d/'informe.md'; informe.write_text('intacto')
            with self.assertRaises(FileExistsError): E.preparar(d/'salida', informe)
            with self.assertRaises(FileExistsError): E.preparar(d, d/'otro.md')
            with self.assertRaises(FileExistsError): E.ejecutar(d/'salida', informe)
            self.assertEqual(informe.read_text(), 'intacto')


if __name__ == '__main__': unittest.main()
