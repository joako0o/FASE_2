"""Selección reproducible, textos íntegros y ausencia de etiquetas IA en el formulario."""
# ---- 1. Fixtures inventados: ninguna decisión humana se lee o genera ----
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script,sha256
E = cargar_script('27_preparar_revision_entrenamiento.py')


def fixture():
    datos=pd.DataFrame({'intervencion_id':[f'id-{i:03d}' for i in range(90)],
        'texto':[f'Intervención íntegra número {i}. Una frase final.' for i in range(90)],
        'etiqueta':[E.CLASES[i%3] for i in range(90)],'es_relevante':['1']*90,
        'meeting_id':[f'reunion-{i//3}' for i in range(90)],'fecha':['2010-01-01']*90,
        'actor':['Persona']*90,'cargo':['Consejero']*90})
    mascara=np.array([True]*84+[False]*6)
    return datos,mascara


# ---- 2. Selección prefijada sin ID/copia humana o de validación ----
class Seleccion(unittest.TestCase):
    def test_balance_y_orden_no_codifica_clase(self):
        datos,mascara=fixture()
        seleccion,auditoria=E.seleccionar(datos,mascara,{'id-000'},[datos.loc[0,'texto']])
        self.assertEqual(seleccion.etiqueta.value_counts().to_dict(),{c:10 for c in E.CLASES})
        self.assertEqual(seleccion.caso_id.tolist(),[f'R{i:02d}' for i in range(1,31)])
        self.assertEqual(auditoria['n_solapes_seleccion_humana_o_validacion'],0)
        self.assertNotEqual(seleccion.etiqueta.tolist(),sorted(seleccion.etiqueta.tolist()))
        self.assertTrue(seleccion.texto.map(E.ANTERIOR.clave_texto).is_unique)

    def test_reproducible_aunque_cambie_orden_de_entrada(self):
        datos,mascara=fixture()
        primera=E.seleccionar(datos,mascara,set(),[])[0]
        orden=np.arange(90)[::-1]
        segunda=E.seleccionar(datos.iloc[orden].reset_index(drop=True),mascara[orden],set(),[])[0]
        pd.testing.assert_frame_equal(primera,segunda)

    def test_excluye_copias_humanas_y_validacion(self):
        datos,mascara=fixture()
        datos.loc[3,'texto']='  INTERVENCIÓN HUMANA  '
        datos.loc[4,'texto']=datos.loc[84,'texto'].upper()
        seleccion,_=E.seleccionar(datos,mascara,{'id-001'},['intervencion humana'])
        self.assertFalse(set(seleccion.intervencion_id)&{'id-001','id-003','id-004',*[f'id-{i:03d}' for i in range(84,90)]})

    def test_no_rellena_cupos_si_falta_una_clase(self):
        datos,mascara=fixture()
        datos.loc[datos.etiqueta.eq('dovish'),'etiqueta']='neutral'
        with self.assertRaises(AssertionError):
            E.seleccionar(datos,mascara,set(),[])

    def test_no_modifica_fuente_ni_recorta_texto(self):
        datos,mascara=fixture()
        original=datos.copy(deep=True)
        seleccion,_=E.seleccionar(datos,mascara,set(),[])
        pd.testing.assert_frame_equal(datos,original)
        for fila in seleccion.itertuples():
            self.assertEqual(fila.texto,datos.set_index('intervencion_id').loc[fila.intervencion_id,'texto'])


# ---- 3. Payload sin respuestas IA, escape de contenido y JavaScript válido ----
class Formulario(unittest.TestCase):
    def test_solo_columnas_publicas_y_hash_reproducible(self):
        datos,mascara=fixture()
        seleccion,_=E.seleccionar(datos,mascara,set(),[])
        publico=E.construir_publico(seleccion,'Guía')
        self.assertEqual(set(publico['casos'][0]),{'caso_id','texto','fecha','actor','cargo'})
        self.assertEqual(publico['muestra_sha256'],E.huella_texto(E.serializar(publico['casos'])))
        self.assertNotIn('etiqueta_ia',E.serializar(publico))
        self.assertNotIn('intervencion_id',E.serializar(publico))

    def test_corpus_no_inyecta_html_y_se_recupera_integro(self):
        datos,mascara=fixture()
        seleccion,_=E.seleccionar(datos,mascara,set(),[])
        ataque='</script><img src=x onerror="alert(1)">\nTexto completo.'
        seleccion.loc[0,'texto']=ataque
        publico=E.construir_publico(seleccion,'Guía <literal>')
        html=E.construir_html(publico)
        self.assertNotIn(ataque,html)
        self.assertEqual(E.leer_publico(html),publico)
        self.assertNotIn('.innerHTML',html)
        self.assertNotIn('NO_ABRIR_hasta_finalizar_clave.csv',html)

    @unittest.skipUnless(shutil.which('node'),'Node no disponible para comprobar JS')
    def test_sintaxis_javascript(self):
        plantilla=E.RUTA_PLANTILLA.read_text()
        javascript=re.search(r'<script>\n(.*?)</script>',plantilla,re.S).group(1)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta=Path(carpeta)/'revision.js'
            ruta.write_text(javascript)
            subprocess.run(['node','--check',str(ruta)],check=True,capture_output=True,text=True)

    @unittest.skipUnless(os.environ.get('REVISION_JSDOM_NODE_PATH'),'DOM opcional: indicar ruta de jsdom 26.1.0')
    def test_flujo_interactivo_en_dom_simulado(self):
        datos,mascara=fixture()
        seleccion,_=E.seleccionar(datos,mascara,set(),[])
        html=E.construir_html(E.construir_publico(seleccion,'Guía de prueba'))
        javascript=r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const {JSDOM}=require(process.env.REVISION_JSDOM_NODE_PATH);
const html=fs.readFileSync(process.argv[2],'utf8');
let exportado,nombre;
function abrir(previo=null,sinAlmacen=false){
 const dom=new JSDOM(html,{url:'https://revision.example/',runScripts:'dangerously',beforeParse(w){
  w.confirm=()=>true;w.Blob=class{constructor(partes){this.partes=partes;}};
  w.URL.createObjectURL=b=>{exportado=JSON.parse(b.partes.join(''));return 'blob:prueba';};
  w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=function(){nombre=this.download;};
  if(sinAlmacen)Object.defineProperty(w,'localStorage',{get(){throw Error('bloqueado');}});
  else if(previo)w.localStorage.setItem(previo.clave,previo.valor);
 }});return dom;
}
(async()=>{
 const dom=abrir(),w=dom.window,d=w.document,$=id=>d.getElementById(id);
 const datos=JSON.parse($('datos').textContent),clave='dh-revision-30:'+datos.muestra_sha256;
 const marcar=valor=>{const r=d.querySelector('input[value="'+valor+'"]');r.checked=true;r.dispatchEvent(new w.Event('change'));};
 const escribir=(id,valor)=>{$(id).value=valor;$(id).dispatchEvent(new w.Event('input'));};
 assert.equal($('navegacion').children.length,30);assert.match($('progreso').textContent,/^0 de 30/);
 assert.equal($('texto').textContent,datos.casos[0].texto);
 marcar('hawkish');assert.match($('progreso').textContent,/^0 de 30/);
 escribir('cita',datos.casos[0].texto);assert.match($('progreso').textContent,/^1 de 30/);
 escribir('cita','Esta cita no aparece en el original');assert.match($('progreso').textContent,/^0 de 30/);
 escribir('cita',datos.casos[0].texto);
 $('siguiente').click();marcar('no_puedo_decidir');escribir('nota','No identifico una postura.');
 assert.match($('progreso').textContent,/^2 de 30/);
 $('anterior').click();assert.equal(d.querySelector('input[name="etiqueta"]:checked').value,'hawkish');
 const rango=d.createRange();rango.selectNodeContents($('texto'));w.getSelection().removeAllRanges();w.getSelection().addRange(rango);
 $('usar-seleccion').click();assert.equal($('cita').value,datos.casos[0].texto);
 $('nav-R03').click();marcar('neutral');$('no-relevante').checked=true;$('no-relevante').dispatchEvent(new w.Event('change'));
 escribir('nota','Solo formalidad');assert.match($('progreso').textContent,/^3 de 30/);
 marcar('dovish');assert.match($('progreso').textContent,/^2 de 30/);
 marcar('neutral');$('limpiar-caso').click();assert.match($('progreso').textContent,/^2 de 30/);
 $('descargar').click();assert.equal(exportado.n_listas,2);assert.equal(exportado.completa,false);
 assert.equal(exportado.respuestas.length,30);assert.equal(exportado.muestra_sha256,datos.muestra_sha256);assert.match(nombre,/_parcial_/);
 assert.equal(exportado.respuestas[1].etiqueta,'no_puedo_decidir');assert.equal(exportado.respuestas[2].etiqueta,null);
 const parcial=JSON.parse(JSON.stringify(exportado));
 async function importar(doc){Object.defineProperty($('importar'),'files',{configurable:true,value:[{size:1000,text:async()=>JSON.stringify(doc)}]});$('importar').dispatchEvent(new w.Event('change'));await new Promise(r=>setImmediate(r));}
 await importar({...parcial,muestra_sha256:'incorrecta'});assert.match($('aviso').textContent,/No se importó/);assert.match($('progreso').textContent,/^2 de 30/);
 parcial.respuestas[2]={caso_id:'R03',etiqueta:'neutral',es_relevante:'1',cita:datos.casos[2].texto,nota:'',lista:false};
 await importar(parcial);assert.match($('progreso').textContent,/^3 de 30/);
 const copia={clave,valor:w.localStorage.getItem(clave)},restaurado=abrir(copia);
 assert.match(restaurado.window.document.getElementById('progreso').textContent,/^3 de 30/);restaurado.window.close();
 for(const c of datos.casos){$('nav-'+c.caso_id).click();$('no-relevante').checked=false;$('no-relevante').dispatchEvent(new w.Event('change'));marcar('neutral');escribir('cita',c.texto);}
 $('descargar').click();assert.equal(exportado.completa,true);assert.equal(exportado.n_listas,30);assert.match(nombre,/_completa_/);
 const aislado=abrir(null,true);assert.match(aislado.window.document.getElementById('guardado').textContent,/Sin autoguardado/);aislado.window.close();
 dom.window.close();console.log('DOM: navegación, cita, duda, relevancia, guardado, exportación e importación correctos.');
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        with tempfile.TemporaryDirectory() as carpeta:
            pagina=Path(carpeta)/'fixture.html'
            script=Path(carpeta)/'prueba.cjs'
            pagina.write_text(html)
            script.write_text(javascript)
            resultado=subprocess.run(['node',str(script),str(pagina)],capture_output=True,text=True,timeout=30)
            self.assertEqual(resultado.returncode,0,resultado.stdout+resultado.stderr)

    def test_no_sobrescribe(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with self.assertRaises(FileExistsError):
                E.ejecutar(Path(carpeta))

    @unittest.skipUnless((E.RUTA_SALIDA/'manifest.json').exists(),'Preparación pendiente')
    def test_artefacto_real_sin_filtraciones_ni_textos_recortados(self):
        protocolo=json.loads((E.RUTA_SALIDA/'protocolo.json').read_text())
        for nombre,huella in protocolo['sha256_insumos'].items():
            self.assertEqual(sha256(E.config.RUTA_REPO/nombre),huella)
        clave=pd.read_csv(E.RUTA_SALIDA/'NO_ABRIR_hasta_finalizar_clave.csv',dtype=str)
        publico=E.leer_publico((E.RUTA_SALIDA/'formulario/index.html').read_text())
        self.assertEqual(len(clave),30)
        self.assertEqual(clave.etiqueta_ia.value_counts().to_dict(),{c:10 for c in E.CLASES})
        self.assertEqual({p.name for p in (E.RUTA_SALIDA/'formulario').iterdir()},{'index.html'})
        datos,mascara,_,_=E.ANTERIOR.L.cargar_insumos()
        self.assertTrue(set(clave.intervencion_id)<=set(datos[mascara].intervencion_id))
        ids_humanos=set(pd.read_csv(E.RUTA_MARCO_HUMANO,usecols=['intervencion_id']).intervencion_id)
        self.assertFalse(set(clave.intervencion_id)&ids_humanos)
        originales=datos.set_index('intervencion_id')
        correspondencias=clave.set_index('caso_id')
        for caso in publico['casos']:
            self.assertEqual(set(caso),{'caso_id','texto','fecha','actor','cargo'})
            fila=correspondencias.loc[caso['caso_id']]
            self.assertEqual(caso['texto'],originales.loc[fila.intervencion_id,'texto'])
            self.assertEqual(E.huella_texto(caso['texto']),fila.sha256_texto_original)
        self.assertEqual(publico['muestra_sha256'],protocolo['muestra_sha256'])
        manifest=json.loads((E.RUTA_SALIDA/'manifest.json').read_text())
        for nombre,huella in manifest['sha256_salidas'].items():
            self.assertEqual(sha256(E.RUTA_SALIDA/nombre),huella)


if __name__=='__main__':
    unittest.main()
