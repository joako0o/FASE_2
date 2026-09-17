"""Selección, evidencia y álgebra del diagnóstico; no certifica postura semántica."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script, sha256
D = cargar_script('37_diagnosticar_inversiones_hd.py')


def ejemplo():
    pred = pd.DataFrame([
        {'intervencion_id': 'a', 'supervision': 'seis_mas_trece', 'etiqueta_corregida_v2': 'dovish', 'pred': 'hawkish'},
        {'intervencion_id': 'b', 'supervision': 'seis_mas_trece', 'etiqueta_corregida_v2': 'hawkish', 'pred': 'dovish'},
        {'intervencion_id': 'c', 'supervision': 'seis_mas_trece', 'etiqueta_corregida_v2': 'neutral', 'pred': 'hawkish'},
        {'intervencion_id': 'd', 'supervision': 'seis_mas_trece', 'etiqueta_corregida_v2': 'dovish', 'pred': 'hawkish'}])
    revision = pd.DataFrame([
        {'intervencion_id': 'a', 'estado_revision': 'referencia_respaldada', 'postura_sugerida_agente': 'dovish'},
        {'intervencion_id': 'b', 'estado_revision': 'ambigua', 'postura_sugerida_agente': ''},
        {'intervencion_id': 'd', 'estado_revision': 'referencia_cuestionable', 'postura_sugerida_agente': 'dovish'}])
    return pred, revision, {'d': 'dovish'}


class Inversiones(unittest.TestCase):
    def test_01_selecciona_todas_y_separa_ambiguas_sin_mutar(self):
        p, r, a = ejemplo(); original = p.copy(deep=True)
        seleccion, ambiguos = D.seleccionar(p, r, a)
        self.assertEqual(seleccion.intervencion_id.tolist(), ['a', 'd'])
        self.assertEqual(ambiguos.intervencion_id.tolist(), ['b'])
        pd.testing.assert_frame_equal(p, original)

    def test_02_no_inventa_aceptacion_y_rechaza_duplicados(self):
        p, r, a = ejemplo()
        with self.assertRaises(AssertionError): D.seleccionar(p, r, {})
        with self.assertRaises(AssertionError): D.seleccionar(pd.concat([p, p.iloc[:1]]), r, a)
        with self.assertRaises(AssertionError): D.seleccionar(p, pd.concat([r, r.iloc[:1]]), a)
        with self.assertRaises(AssertionError): D.seleccionar(p, r.iloc[:1], a)

    def test_03_citas_literales_sin_inventar_ni_truncar(self):
        D.validar_citas({'citas': ['subir']}, 'Vota por subir.')
        for citas in [[], ['bajar'], ['subir', 'subir'], ['x'*301]]:
            with self.assertRaises(AssertionError): D.validar_citas({'citas': citas}, 'Vota por subir.'+'x'*301)

    def test_04_descomposicion_completa_y_residuo(self):
        valores = np.arange(1, 21, dtype=float)/20
        pesos = np.arange(-10, 10, dtype=float)
        nombres = np.array([f't{i:02d}' for i in range(20)])
        frec = {c: np.ones(20) for c in ['hawkish', 'dovish', 'neutral']}
        d, filas = D.descomponer(csr_matrix([valores]), pesos, .3, nombres, frec)
        self.assertAlmostEqual(d['margen'], .3+float(valores@pesos))
        self.assertEqual(len(filas), 20)
        self.assertEqual(len(d['top_a_favor_prediccion']), 6)
        self.assertEqual(len(d['top_a_favor_referencia']), 6)
        mostrados = d['top_a_favor_prediccion']+d['top_a_favor_referencia']
        self.assertAlmostEqual(d['margen'], d['intercepto']+sum(r['aporte'] for r in mostrados)+d['residuo_no_mostrado'])
        for f in filas: self.assertAlmostEqual(f['aporte'], f['tfidf']*f['coef_contraste'])

    def test_05_textos_completos_y_primera_cita_prefijada(self):
        original, _, _, _, _, seleccion, ambiguos, lecturas = D.cargar()
        casos = json.loads((D.SALIDA/'casos.json').read_text())
        textos = original.set_index('intervencion_id').texto
        self.assertEqual(len(seleccion), 10); self.assertEqual(len(ambiguos), 5)
        self.assertEqual({c['intervencion_id'] for c in casos}, set(seleccion.intervencion_id))
        self.assertEqual(sum(len(c['texto_completo']) for c in casos), 40937)
        for c in casos:
            k = c['intervencion_id']
            self.assertEqual(c['texto_completo'], textos.loc[k])
            self.assertEqual(c['sha256_texto'], hashlib.sha256(textos.loc[k].encode()).hexdigest())
            self.assertEqual(c['sonda']['texto'], lecturas[k]['citas'][0])
            self.assertEqual(c['sonda']['pred_b'], max(c['sonda']['scores_b'], key=c['sonda']['scores_b'].get))
            self.assertEqual(c['sonda']['coincide_referencia'], c['sonda']['pred_b'] == c['etiqueta_corregida_v2'])

    def test_06_reproduce_793_y_margenes_guardados(self):
        pred = pd.read_csv(D.E.SALIDA/'predicciones_validacion.csv')
        pred = pred[pred.supervision.eq('seis_mas_trece')]
        actual = pd.read_csv(D.SALIDA/'predicciones_reconstruidas.csv')
        cols = ['intervencion_id', 'meeting_id', 'fold', 'pred_a', 'pred_b', 'pred']
        ordenar = lambda t: t[cols].sort_values('intervencion_id').reset_index(drop=True)
        pd.testing.assert_frame_equal(ordenar(actual), ordenar(pred))
        aportes = pd.read_csv(D.SALIDA/'aportes.csv')
        casos = json.loads((D.SALIDA/'casos.json').read_text())
        for c in casos:
            self.assertEqual(c['pred_a'], 1)
            sub = aportes[aportes.intervencion_id.eq(c['intervencion_id'])]
            self.assertTrue(sub.termino.is_unique)
            np.testing.assert_allclose(sub.aporte, sub.tfidf*sub.coef_contraste, atol=1e-12)
            d = c['descomposicion']
            self.assertAlmostEqual(sub.aporte.sum()+d['intercepto'], d['margen'])
            self.assertAlmostEqual(d['margen'], c['scores_b'][c['pred']]-c['scores_b'][c['etiqueta_corregida_v2']])
            self.assertGreater(d['margen'], 0)

    def test_07_hashes_y_limites(self):
        p = json.loads((D.SALIDA/'protocolo.json').read_text())
        D.E.PREV.verificar_hashes(p['sha256_insumos'])
        m = json.loads((D.SALIDA/'manifest.json').read_text())
        for n, h in m['sha256_salidas'].items(): self.assertEqual(sha256(D.SALIDA/n), h)
        self.assertEqual(sha256(D.INFORME), m['sha256_informe'])
        resumen = json.loads((D.SALIDA/'resumen.json').read_text())
        for campo in ['etiquetas_modificadas', 'metricas_36_modificadas', 'nuevo_candidato_evaluado', 'beto_ejecutado', 'examen_306_abierto']:
            self.assertIs(resumen[campo], False)
        self.assertEqual(resumen['predicciones_reproducidas'], 793)

    def test_08_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as t:
            d = Path(t); informe = d/'informe.md'; informe.write_text('intacto')
            with self.assertRaises(FileExistsError): D.preparar(d/'salida', informe)
            with self.assertRaises(FileExistsError): D.preparar(d, d/'otro.md')
            with self.assertRaises(FileExistsError): D.ejecutar(d/'salida', informe)
            self.assertEqual(informe.read_text(), 'intacto')


if __name__ == '__main__': unittest.main()
