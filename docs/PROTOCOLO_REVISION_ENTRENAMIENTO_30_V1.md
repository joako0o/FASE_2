# Revisión humana acotada del entrenamiento — 30 casos v1

Autorizada el 2026-09-16 («ok hazlo») después de proponer una revisión de 10 H, 10 D y 10 neutrales, antes de entrenar un modelo contextual. **Esta fase prepara la revisión; no la da por completada sin respuestas del investigador.**

## Objetivo y alcance

Comprobar si una pequeña muestra de etiquetas IA de entrenamiento sigue el codebook v2, especialmente diagnóstico frente a postura. No evaluar un clasificador, no estimar precisión poblacional, no generar etiquetas humanas por IA. El muestreo balanceado por etiqueta IA no reproduce la distribución del corpus. Diez casos por estrato no prueban calidad global.

## Selección fijada antes de leer decisiones humanas

- Pool inicial: los 559 registros del grupo `descubrimiento_lexico`, utilizado solo como entrenamiento en las comparaciones posteriores. No significa que jamás haya sido usado en una validación anterior a ese diseño.
- Excluir los 306 IDs del marco `data/muestras/gold_ciego_300.csv`, leyendo únicamente su columna de ID, nunca las respuestas del Excel ni predicciones humanas.
- Excluir también copias de esos textos utilizando exclusivamente el texto original de L0 vinculado a esos IDs, sin leer sus etiquetas humanas, mostrar esos textos o predecirlos.
- Excluir copias normalizadas de los 793 registros de validación reutilizada. Clave textual: espacios normalizados, minúsculas y sin acentos (función versionada del script 26). No equivale a deduplicación semántica.
- Deduplicar el pool por esa clave: conservar el primer ID según rango SHA256 independiente de etiqueta. No borrar fuentes ni corregir posibles conflictos automáticamente.
- Ranking determinista `SHA256("20260916|seleccion|" + intervencion_id)`. De cada clase IA, tomar los primeros diez; sin elegir por error de un modelo, confianza, longitud, actor, claridad ni aparente postura. Detener si algún estrato no alcanza diez.
- Mezclar las 30 seleccionadas con otro ranking: `SHA256("20260916|orden|" + intervencion_id)`. Asignar códigos públicos R01–R30, sin codificar la clase. No reemplazar casos difíciles o largos después de verlos.

## Revisión sin etiqueta IA visible

Formulario estático con texto íntegro, fecha, actor y cargo. No truncar ni añadir contexto de otras intervenciones. La guía mostrada es una copia de las secciones 1–3 del codebook v2, sin ejemplos que sugieran respuestas particulares. No modificar reglas.

El investigador marca H/D/N, relevancia y cita literal de hasta 300 caracteres para contenido relevante. Puede elegir **«No puedo decidir»**, que requiere explicar por qué y **no es una cuarta etiqueta para entrenar**. Con relevancia 0, pedir neutral y motivo, conforme a las validaciones vigentes. Un caso sin respuesta no se imputa como neutral. Se permite exportar avance parcial y recuperarlo desde el mismo JSON en el navegador; se verifica versión, hash de muestra y códigos antes de restaurar y se recalcula la validez, sin confiar en el contador exportado.

Pedir que decida antes de consultar IA/etiquetas anteriores y que declare si recibió ayuda o vio las etiquetas. No afirmar ciego estricto ni independencia: puede reconocer textos ya vistos y conoce el diseño 10/10/10. Indicar que no intente completar cuotas. La clave de correspondencia se conserva fuera de la carpeta servida, pero está accesible al dueño del repositorio: no es un secreto criptográfico.

**Nada de revelar resultados mientras responde:** el formulario no contiene etiquetas IA, citas IA, confianza IA ni predicciones. No ofrece botón de comparación ni feedback de acuerdo. No calcula un porcentaje de aciertos.

## Respuestas y seguridad del flujo

Autoguardado solo en el navegador, si localStorage está disponible; exportación a JSON con ID/hash de muestra y códigos de casos. No se suben respuestas automáticamente ni se almacenan por el servidor HTTP. Pedir descargar el JSON y adjuntarlo al chat. El almacenamiento local puede borrarse o depender del navegador/origen: el archivo descargado es el respaldo.

La carpeta pública contiene únicamente `index.html`. La clave reservada, protocolo y manifiesto quedan en su directorio padre, nunca servidos por la vista previa. Renderizar textos y guía con `textContent`, escapar `<` en el JSON embebido y no cargar scripts, imágenes ni servicios externos.

No modificar anotaciones canónicas ni archivos congelados. La primera devolución se conservará como artefacto nuevo antes de compararla; posteriores cambios deberán tener otra versión. La preparación no ejecuta una importación o comparación prematura. Los desacuerdos futuros se revisarán, no se convertirán automáticamente en errores de IA ni correcciones aprobadas.

## Artefactos mínimos y reproducción

- `scripts/27_preparar_revision_entrenamiento.py`: selección, formulario y manifiesto con fuentes verificadas; rechaza sobrescribir.
- `scripts/plantillas/revision_entrenamiento.html`: interfaz usada por el generador, sin clave IA.
- `tests/test_revision_entrenamiento.py`: selección, integridad y no filtración de etiquetas.
- `data/auditoria/revision_entrenamiento_30_v1/`: clave reservada, protocolo/manifest y formulario público. Sin Excel vacío ni duplicado del corpus.

Reproducir en un temporal que se elimina; comparar clave y HTML. Verificar que las 30 correspondencias sean únicas, 10 por clase IA, solo del pool elegible y con textos originales completos. Comprobar que los 195 archivos preexistentes permanezcan intactos. No abrir el test humano en la suite; omitir expresamente su prueba antigua. No reescribir experimentos cerrados.

BETO sigue pendiente de adquisición de pesos; no hay entrenamiento contextual, modelos nuevos ni resultados humanos en esta fase. Esta revisión es desarrollo de entrenamiento, nunca un test humano independiente.

### Comprobación opcional de la interfaz

Además de tests Python y sintaxis JS, se prueba navegación, citas, duda, relevancia, autoguardado, recuperación y descarga en DOM simulado con **jsdom 26.1.0**, instalado fuera del repositorio. No es una inspección visual en navegador real ni una respuesta humana. No se modifica `requirements.txt` o dependencias del clasificador.

```bash
npm install --prefix /ruta/temporal-ui jsdom@26.1.0 --no-audit --no-fund
REVISION_JSDOM_NODE_PATH=/ruta/temporal-ui/node_modules/jsdom python -m unittest discover -s tests -p test_revision_entrenamiento.py -v
```

Sin esa variable se omite el test DOM opcional, no se afirma que haya pasado. La suite global del cierre excluye únicamente la prueba antigua de lectura humana cuando Node/jsdom están disponibles.
