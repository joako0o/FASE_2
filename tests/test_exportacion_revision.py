"""Regresión de descarga bloqueada y rescate local; solo respuestas inventadas."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from utilidades import cargar_script, sha256
E=cargar_script('28_reparar_exportacion_revision.py')


def original_sintetico():
    datos={'version':'fixture','muestra_sha256':'muestra-inventada','guia':'Guía de prueba',
        'casos':[{'caso_id':f'R{i:02d}','texto':f'Texto inventado {i}. Sin respuestas humanas.',
                  'actor':'Actor de prueba','cargo':'Consejero','fecha':'2010-01-01'} for i in range(1,31)]}
    plantilla=(E.RAIZ/'scripts/plantillas/revision_entrenamiento.html').read_text()
    return plantilla.replace('__DATOS_REVISION__',json.dumps(datos,ensure_ascii=False))


class Exportacion(unittest.TestCase):
    def test_payload_y_clave_local_sin_cambios(self):
        original=original_sintetico()
        nuevo=E.reparar_html(original)
        self.assertEqual(E.payload(original),E.payload(nuevo))
        self.assertIn("const claveLocal='dh-revision-30:'+datos.muestra_sha256;",nuevo)
        self.assertIn('id="json-respaldo" readonly',nuevo)
        self.assertNotIn('NO_ABRIR_hasta_finalizar_clave.csv',nuevo)
        self.assertNotIn('.innerHTML',nuevo)
        with self.assertRaises(AssertionError): E.reparar_html(nuevo)

    def test_archiva_original_y_rechaza_reaplicacion(self):
        with tempfile.TemporaryDirectory() as temporal:
            salida=Path(temporal)
            (salida/'formulario').mkdir()
            pagina=salida/'formulario/index.html'
            pagina.write_text(original_sintetico())
            previo=pagina.read_bytes()
            manifest={'sha256_salidas':{'formulario/index.html':sha256(pagina)}}
            (salida/'manifest.json').write_text(json.dumps(manifest))
            E.ejecutar(salida)
            self.assertEqual((salida/'archivo_interfaz_v1/index.html').read_bytes(),previo)
            self.assertEqual(E.reparar_html(previo.decode()),pagina.read_text())
            self.assertEqual(json.loads((salida/'manifest.json').read_text())['sha256_salidas']['formulario/index.html'],sha256(pagina))
            self.assertFalse(list(salida.rglob('*.tmp')))
            with self.assertRaises(FileExistsError): E.ejecutar(salida)

    @unittest.skipUnless(os.environ.get('REVISION_JSDOM_NODE_PATH'),'Requiere jsdom 26.1.0 para DOM simulado')
    def test_descarga_y_portapapeles_bloqueados_sin_perder_avance(self):
        js=r"""
const {JSDOM}=require(process.env.REVISION_JSDOM_NODE_PATH);
const fs=require('node:fs'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8');
const clave='dh-revision-30:muestra-inventada';
const respuestas=Object.fromEntries(Array.from({length:30},(_,i)=>['R'+String(i+1).padStart(2,'0'),{etiqueta:null,es_relevante:'1',cita:'',nota:''}]));
respuestas.R01={etiqueta:'dovish',es_relevante:'1',cita:'Texto inventado 1.',nota:'Decisión de prueba'};
respuestas.R02={etiqueta:'no_puedo_decidir',es_relevante:'1',cita:'',nota:'Falta contexto de prueba'};
const previo={muestra_sha256:'muestra-inventada',respuestas,ayuda:'ninguna',vio_etiquetas:'no'};
function abrir({almacen=true,crudo=JSON.stringify(previo),descarga='bloqueada',clipboard='denegado'}={}){
 let escrituras=0,copiado=null,blob=null;const errores=[];
 const dom=new JSDOM(html,{url:'https://misma-vista.example/',runScripts:'dangerously',beforeParse(w){
  w.addEventListener('error',e=>errores.push(e.message));
  if(almacen){if(crudo!==null)w.localStorage.setItem(clave,crudo);const set=w.Storage.prototype.setItem;w.Storage.prototype.setItem=function(...args){escrituras++;return set.apply(this,args);};}
  else Object.defineProperty(w,'localStorage',{get(){throw Error('Almacenamiento bloqueado');}});
  w.Blob=class{constructor(partes){blob=JSON.parse(partes.join(''));}};
  w.URL.createObjectURL=()=>{if(descarga==='bloqueada')throw Error('Bloqueo de descargas');return 'blob:sin-descarga-real';};
  w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=()=>{};
  w.document.execCommand=()=>false;
  if(clipboard!=='ausente')Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async t=>{if(clipboard==='denegado')throw Error('Permiso denegado');copiado=t;}}});
 }});
 return {dom,w:dom.window,$:id=>dom.window.document.getElementById(id),errores,get escrituras(){return escrituras;},get copiado(){return copiado;},get blob(){return blob;}};
}
(async()=>{
 for(const descarga of ['bloqueada','silenciosa']){
  const a=abrir({descarga});assert.equal(a.escrituras,0);assert.match(a.$('recuperacion').textContent,/2 de las 30/);
  assert.match(a.$('progreso').textContent,/2 de 30/);a.$('descargar').click();
  assert.equal(a.$('respaldo-json').hidden,false);
  const json=JSON.parse(a.$('json-respaldo').value);assert.equal(json.respuestas.length,30);assert.equal(json.n_listas,2);
  assert.equal(json.respuestas[0].etiqueta,'dovish');assert.equal(json.respuestas[0].nota,'Decisión de prueba');
  assert.equal(json.respuestas[1].etiqueta,'no_puedo_decidir');assert.equal(json.procedencia.ayuda,'ninguna');
  if(descarga==='bloqueada')assert.match(a.$('export-status').textContent,/No se pudo iniciar/);else assert.match(a.$('export-status').textContent,/no confirmada/);
  a.$('copiar-json').click();await new Promise(r=>setImmediate(r));assert.match(a.$('copia-status').textContent,/Ctrl\+C/);
  assert.equal(a.$('json-respaldo').selectionStart,0);assert.equal(a.$('json-respaldo').selectionEnd,a.$('json-respaldo').value.length);
  assert.deepEqual(a.errores,[]);a.w.close();
 }
 const ok=abrir({clipboard:'permitido'});ok.$('mostrar-json').click();ok.$('copiar-json').click();await new Promise(r=>setImmediate(r));
 assert.equal(JSON.parse(ok.copiado).n_listas,2);assert.match(ok.$('copia-status').textContent,/JSON copiado/);ok.w.close();
 const ausente=abrir({clipboard:'ausente'});ausente.$('mostrar-json').click();ausente.$('copiar-json').click();await new Promise(r=>setImmediate(r));assert.match(ausente.$('copia-status').textContent,/Ctrl\+C/);ausente.w.close();
 const corrupto=abrir({crudo:'{json-incompleto'});assert.equal(corrupto.escrituras,0);assert.equal(corrupto.w.localStorage.getItem(clave),'{json-incompleto');assert.match(corrupto.$('recuperacion').textContent,/No se encontró/);corrupto.w.close();
 const vacio=abrir({crudo:null});assert.equal(vacio.escrituras,0);assert.equal(vacio.w.localStorage.getItem(clave),null);vacio.w.close();
 const sin=abrir({almacen:false});assert.match(sin.$('guardado').textContent,/Sin autoguardado/);
 sin.$('nota').value='Respuesta no guardada de prueba';sin.$('nota').dispatchEvent(new sin.w.Event('input'));
 sin.$('descargar').click();assert.equal(JSON.parse(sin.$('json-respaldo').value).respuestas[0].nota,'Respuesta no guardada de prueba');assert.deepEqual(sin.errores,[]);sin.w.close();
 console.log('Respaldo funciona sin descargas, clipboard o localStorage; estado v1 restaurado sin escritura al abrir.');
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        with tempfile.TemporaryDirectory() as temporal:
            pagina=Path(temporal)/'fixture.html'
            programa=Path(temporal)/'test.cjs'
            pagina.write_text(E.reparar_html(original_sintetico()))
            programa.write_text(js)
            r=subprocess.run(['node',str(programa),str(pagina)],capture_output=True,text=True,timeout=30)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)


if __name__=='__main__': unittest.main()
