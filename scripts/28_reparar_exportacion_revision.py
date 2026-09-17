"""Hotfix de exportación, sin cambiar muestra, etiquetas ni clave de autoguardado.

Conserva HTML/manifiesto v1 en un archivo fuera de la carpeta pública. Actualiza
la misma ruta del formulario para no cambiar su URL en el visor. El generador 27
y su plantilla congelada permanecen intactos; generan la versión original.
"""
# ---- 1. Elementos de respaldo: no dependen de descarga, portapapeles o red ----
from datetime import datetime, timezone
import json
from pathlib import Path

from utilidades import exigir_salidas_nuevas, sha256

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / 'data/auditoria/revision_entrenamiento_30_v1'
MARCA = '<!-- exportacion-revision-v1.1 -->'
PANEL = '''
<section id="respaldo-json" hidden aria-labelledby="titulo-respaldo" style="margin-top:20px">
<h3 id="titulo-respaldo">Respaldo en texto · sin descargar archivo</h3>
<p class="muted">Si el visor bloquea la descarga, copia este JSON y pégalo en el chat. Incluye también tus respuestas parciales. No cierres la página hasta tener un respaldo.</p>
<textarea id="json-respaldo" readonly rows="10" aria-label="JSON de tus respuestas para copiar" spellcheck="false"></textarea>
<button id="copiar-json" type="button" class="primary">Copiar JSON</button>
<button id="seleccionar-json" type="button">Seleccionar todo el JSON</button>
<p id="copia-status" class="status" role="status"></p>
</section>'''
EXPORTACION = r'''
// Preparar el texto antes de intentar descargar: el sandbox puede bloquear sin error.
function prepararRespaldo(){
 recoger();
 const respuestas=datos.casos.map(c=>({caso_id:c.caso_id,...estado.respuestas[c.caso_id],lista:!problema(estado.respuestas[c.caso_id],c)}));
 const n=respuestas.filter(r=>r.lista).length;
 const exportacion={version:datos.version,muestra_sha256:datos.muestra_sha256,fecha_exportacion_utc:new Date().toISOString(),n_listas:n,completa:n===datos.casos.length,procedencia:{ayuda:estado.ayuda,vio_etiquetas_ia:estado.vio_etiquetas},respuestas};
 $('json-respaldo').value=JSON.stringify(exportacion,null,2)+'\n';
 $('respaldo-json').hidden=false;
 $('copia-status').textContent='Respaldo preparado con '+n+' respuestas listas. Puedes copiarlo aunque esté incompleto.';
 return exportacion;
}
function seleccionarRespaldo(){const t=$('json-respaldo');t.focus();t.select();t.setSelectionRange(0,t.value.length);}
$('mostrar-json').addEventListener('click',()=>{prepararRespaldo();seleccionarRespaldo();});
$('seleccionar-json').addEventListener('click',()=>{prepararRespaldo();seleccionarRespaldo();$('copia-status').textContent='Texto seleccionado: pulsa Ctrl+C o Cmd+C. En móvil, usa la opción Copiar del menú de selección.';});
$('copiar-json').addEventListener('click',async()=>{
 prepararRespaldo();
 const texto=$('json-respaldo').value;
 try {
  if(!navigator.clipboard||typeof navigator.clipboard.writeText!=='function')throw Error('Portapapeles no disponible');
  await navigator.clipboard.writeText(texto);
  $('copia-status').textContent='JSON copiado. Pégalo en el chat.';
 } catch(error){
  seleccionarRespaldo();
  let copiado=false;
  try {copiado=typeof document.execCommand==='function'&&document.execCommand('copy');}catch(ignorado){}
  $('copia-status').textContent=copiado?'JSON copiado. Pégalo en el chat.':'La copia automática está bloqueada. El texto está seleccionado: pulsa Ctrl+C o Cmd+C y pégalo en el chat. En móvil, mantén pulsado el texto y elige Copiar.';
 }
});
$('descargar').addEventListener('click',()=>{
 const exportacion=prepararRespaldo();
 try {
  const blob=new Blob([$('json-respaldo').value],{type:'application/json;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const enlace=document.createElement('a');enlace.href=url;
  enlace.download=datos.version+'_'+(exportacion.completa?'completa':'parcial')+'_'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';
  document.body.appendChild(enlace);enlace.click();enlace.remove();
  setTimeout(()=>URL.revokeObjectURL(url),60000);
  $('export-status').textContent='Descarga solicitada, no confirmada. Si no aparece el archivo, usa Copiar JSON en el respaldo de abajo y pégalo en el chat.';
 } catch(error){
  $('export-status').textContent='No se pudo iniciar la descarga. Tus respuestas siguen en el respaldo de texto: usa Copiar JSON o selecciona y copia manualmente.';
 }
});
'''
INICIO = r'''
$('guia').textContent=datos.guia;mostrar();
// No escribir un estado vacío al abrir: podría pisar un respaldo no recuperado.
const recuperadas=Object.values(estado.respuestas).filter(r=>r.etiqueta||r.cita||r.nota||r.es_relevante==='0').length;
$('recuperacion').textContent=recuperadas
 ?'Se recuperó contenido guardado en '+recuperadas+' de las 30 respuestas. Comprueba tu avance y usa Mostrar / copiar JSON para respaldarlo.'
 :'No se encontró avance recuperable en esta vista. Si ya habías respondido, no lo rellenes otra vez todavía: avisa en el chat. Puede estar guardado en otro navegador o vista.';
try {localStorage.getItem(claveLocal);$('guardado').textContent=recuperadas?'Avance local recuperado; pendiente respaldar':'Sin avance recuperado en esta vista';}
catch(error){$('guardado').textContent='Sin autoguardado disponible: copia el JSON antes de salir.';}
'''


# ---- 2. Aplicar solo cambios de interfaz sobre HTML conocido, sin tocar su payload ----
def payload(html):
    return json.loads(html.split('<script id="datos" type="application/json">',1)[1].split('</script>',1)[0])


def reparar_html(original):
    assert MARCA not in original, 'Interfaz ya reparada'
    boton='<button id="descargar" type="button" class="primary">Descargar respuestas JSON</button>'
    assert original.count(boton)==1
    nuevo=original.replace(boton,boton+' <button id="mostrar-json" type="button">Mostrar / copiar JSON</button>')
    estado='<p id="export-status" class="status" role="status"></p>'
    assert nuevo.count(estado)==1
    nuevo=nuevo.replace(estado,estado+PANEL)
    inicio=nuevo.index("$('descargar').addEventListener('click',()=>{")
    fin=nuevo.index("$('importar').addEventListener",inicio)
    nuevo=nuevo[:inicio]+EXPORTACION+'\n'+nuevo[fin:]
    final="$('guia').textContent=datos.guia;mostrar();guardar();"
    assert nuevo.count(final)==1
    nuevo=nuevo.replace(final,INICIO)
    nuevo=nuevo.replace('<main>','<main>'+MARCA+'<p id="recuperacion" class="intro" role="status"></p>',1)
    assert payload(original)==payload(nuevo), 'Se alteró la muestra o la guía'
    assert "const claveLocal='dh-revision-30:'+datos.muestra_sha256;" in nuevo
    return nuevo


def escribir_atomico(ruta,texto):
    temporal=ruta.with_name(ruta.name+'.tmp')
    exigir_salidas_nuevas(temporal)
    try:
        temporal.write_text(texto,encoding='utf-8')
        temporal.replace(ruta)
    finally:
        temporal.unlink(missing_ok=True)


# ---- 3. Historial explícito y publicación en la misma ruta para conservar el origen ----
def ejecutar(salida=SALIDA):
    pagina=salida/'formulario/index.html'
    manifiesto=salida/'manifest.json'
    registro=salida/'reparacion_exportacion_v1_1.json'
    archivo=salida/'archivo_interfaz_v1'
    exigir_salidas_nuevas(registro,archivo)
    anterior=json.loads(manifiesto.read_text())
    assert sha256(pagina)==anterior['sha256_salidas']['formulario/index.html']
    original=pagina.read_text()
    nuevo=reparar_html(original)
    archivo.mkdir()
    (archivo/'index.html').write_bytes(pagina.read_bytes())
    (archivo/'manifest.json').write_bytes(manifiesto.read_bytes())
    escribir_atomico(pagina,nuevo)
    actualizado=json.loads((archivo/'manifest.json').read_text())
    actualizado['sha256_salidas']['formulario/index.html']=sha256(pagina)
    actualizado['interfaz']='v1.1; misma muestra y ruta. V1 conservada en archivo_interfaz_v1.'
    escribir_atomico(manifiesto,json.dumps(actualizado,ensure_ascii=False,indent=2)+'\n')
    registro.write_text(json.dumps({
        'fecha_utc':datetime.now(timezone.utc).isoformat(),'motivo':'Usuario no puede descargar JSON; causa del navegador/visor no confirmada.',
        'sha256_html_v1':sha256(archivo/'index.html'),'sha256_html_v1_1':sha256(pagina),
        'sha256_manifest_v1':sha256(archivo/'manifest.json'),'muestra_sha256':payload(nuevo)['muestra_sha256'],
        'sha256_reparador':sha256(Path(__file__)),
        'misma_ruta_y_clave_localstorage':True,'payload_original_intacto':True,
        'respuestas_usuario_recuperadas':'No comprobable desde el servidor; requiere confirmación del usuario.',
        'limite_reproducibilidad':'El script 27 y reproducibilidad.json describen v1 archivada; este reparador genera v1.1 desde ella.',
        'datos_o_etiquetas_modificados':False},ensure_ascii=False,indent=2)+'\n')
    print('Interfaz v1.1 publicada en la misma ruta; muestra y clave de guardado sin cambios.')


if __name__=='__main__':
    ejecutar()
