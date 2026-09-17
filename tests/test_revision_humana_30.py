"""Auditoría de la nueva devolución de 30, sin abrir el examen anterior de 306."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd
from openpyxl import Workbook

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script,sha256
E=cargar_script('30_comparar_revision_humana.py')


def fixture(ruta,mutar=None):
    publico={'casos':[{'caso_id':f'R{i:02d}','texto':f'Texto inventado {i}. Otra frase.'} for i in range(1,31)]}
    libro=Workbook();hoja=libro.active;hoja.title='Hoja1'
    hoja.append(E.ENCABEZADOS)
    for i,c in enumerate(publico['casos'],1):
        hoja.append([i,c['texto'],'Neutral',c['texto'],'Comentario de prueba'])
    if mutar: mutar(hoja)
    libro.save(ruta)
    return publico


def clave_de(humanas):
    return pd.DataFrame([{'caso_id':r.caso_id,'intervencion_id':f'original-{i}',
        'etiqueta_ia':E.CLASES[i%3],'es_relevante_ia':'1',
        'sha256_texto_original':hashlib.sha256(r.texto_original.encode()).hexdigest()}
        for i,r in enumerate(humanas.itertuples())])


class Recepcion(unittest.TestCase):
    def test_identificadores_no_inventa_ids(self):
        for v in [1,1.0,'1','R01']:
            self.assertEqual(E.identificar(v),'R01')
        for v in [True,0,31,1.5,'otro','R99']:
            with self.assertRaises((AssertionError,ValueError)):
                E.identificar(v)

    def test_texto_integro_y_relevancia_no_imputada(self):
        with tempfile.TemporaryDirectory() as t:
            ruta=Path(t)/'fixture.xlsx'
            publico=fixture(ruta,lambda s:setattr(s['B2'],'value','Texto  inventado 1.\nOtra frase.'))
            h=E.leer_devolucion(ruta,publico)
            self.assertEqual(len(h),30)
            self.assertEqual(h.texto_identico.sum(),29)
            self.assertTrue(h.relevancia_humana.eq('no_declarada').all())
            self.assertEqual(h.etiqueta_humana.value_counts().to_dict(),{'neutral':30})

    def test_rechaza_duplicados_textos_ajenos_o_formulas(self):
        mutaciones=[lambda s:setattr(s['A3'],'value',1),lambda s:setattr(s['B2'],'value','Texto recortado'),
                    lambda s:setattr(s['C2'],'value','=1+1'),lambda s:setattr(s['C2'],'value','positivo'),
                    lambda s:s.delete_rows(31)]
        with tempfile.TemporaryDirectory() as t:
            for i,mutacion in enumerate(mutaciones):
                ruta=Path(t)/f'f{i}.xlsx';publico=fixture(ruta,mutacion)
                with self.assertRaises(AssertionError): E.leer_devolucion(ruta,publico)

    def test_marcadores_no_cuentan_como_cita(self):
        for marcador in ['','-','.','...','…',' — ']:
            self.assertEqual(E.calidad_cita(marcador,'Texto. — ...'),'ausente_o_marcador')
        self.assertEqual(E.calidad_cita('Texto diferente','Texto original'),'no_literal')
        self.assertEqual(E.calidad_cita('Texto\n original','Texto original'),'literal_hasta_300')
        self.assertEqual(E.calidad_cita('x'*301,'x'*301),'literal_larga')


class Comparacion(unittest.TestCase):
    def test_matriz_orientacion_y_no_es_importacion(self):
        with tempfile.TemporaryDirectory() as t:
            ruta=Path(t)/'f.xlsx';p=fixture(ruta);h=E.leer_devolucion(ruta,p)
            tabla,r=E.comparar(h,clave_de(h))
            self.assertEqual(r['matriz_filas_ia_columnas_humano'],[[0,0,10],[0,0,10],[0,0,10]])
            self.assertEqual(r['acuerdos'],10)
            self.assertEqual(r['desacuerdos'],20)
            self.assertFalse(r['importacion_canonica_realizada'])
            self.assertEqual(r['procedencia_revision']['ayuda_recibida'],'no_declarada')
            self.assertTrue(tabla.etiqueta_humana.eq('neutral').all())

    def test_duda_y_ausencia_no_se_imputan_neutral(self):
        def mutar(s):
            s['C2']='No puedo decidir';s['C3']=None
        with tempfile.TemporaryDirectory() as t:
            ruta=Path(t)/'f.xlsx';p=fixture(ruta,mutar);h=E.leer_devolucion(ruta,p)
            tabla,r=E.comparar(h,clave_de(h))
            self.assertEqual(r['n_decisiones_comparables'],28)
            self.assertEqual(r['n_sin_decision_comparable'],2)
            self.assertEqual(r['acuerdos'],10)
            self.assertFalse(tabla.iloc[0].comparacion_disponible)
            self.assertEqual(tabla.iloc[0].etiqueta_humana,'no_puedo_decidir')
            self.assertEqual(tabla.iloc[1].etiqueta_humana,'sin_respuesta')

    def test_une_por_id_y_detecta_clave_con_hash_incorrecto(self):
        with tempfile.TemporaryDirectory() as t:
            ruta=Path(t)/'f.xlsx';p=fixture(ruta);h=E.leer_devolucion(ruta,p)
            clave=clave_de(h)
            a,_=E.comparar(h,clave);b,_=E.comparar(h.iloc[::-1],clave.iloc[::-1])
            pd.testing.assert_frame_equal(a,b)
            clave.loc[0,'sha256_texto_original']='incorrecto'
            with self.assertRaises(AssertionError): E.comparar(h,clave)

    def test_salida_existente_no_se_sobrescribe(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileExistsError): E.ejecutar(Path(t),Path(t)/'informe.md')

    @unittest.skipUnless((E.SALIDA/'manifest.json').exists(),'Comparación todavía no ejecutada')
    def test_resultados_recalculados_e_integridad_original(self):
        recibo=json.loads((E.DEVOLUCION/'recepcion.json').read_text())
        self.assertEqual(sha256(E.ORIGINAL),recibo['sha256_original'])
        tabla=pd.read_csv(E.SALIDA/'comparacion.csv',keep_default_na=False)
        r=json.loads((E.SALIDA/'resumen.json').read_text())
        validas=tabla.etiqueta_humana.isin(E.CLASES)
        self.assertEqual(int((tabla[validas].etiqueta_humana==tabla[validas].etiqueta_ia).sum()),r['acuerdos'])
        matriz=pd.crosstab(tabla[validas].etiqueta_ia,tabla[validas].etiqueta_humana).reindex(index=E.CLASES,columns=E.CLASES,fill_value=0)
        self.assertEqual(matriz.values.tolist(),r['matriz_filas_ia_columnas_humano'])
        m=json.loads((E.SALIDA/'manifest.json').read_text())
        for nombre,h in m['sha256_insumos'].items(): self.assertEqual(sha256(E.RAIZ/nombre),h)
        for nombre,h in m['sha256_salidas'].items(): self.assertEqual(sha256(E.SALIDA/nombre),h)
        self.assertEqual(sha256(E.INFORME),m['sha256_informe'])


if __name__=='__main__': unittest.main()
