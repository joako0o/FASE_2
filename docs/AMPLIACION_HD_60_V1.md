# Primera ampliación H/D: 60 candidatos reales para revisión

## Para el investigador

Abrir **`revision_60_candidatos.xlsx`**, hoja **Inicio**. Empezar por **Bloque 1**, que tiene diez casos. «Leer texto» lleva a la intervención completa, dividida únicamente para que se vea bien en Excel; el enlace del caso permite volver a su respuesta.

Completar las celdas amarillas: postura, relevancia, cita literal y motivo/duda cuando corresponda. Se puede elegir **Neutral** o **No puedo decidir**: no hay cuotas de respuestas que completar. Guardar con Ctrl+S/Cmd+S y devolver el mismo XLSX, incluso parcial. No generar ejemplos, rellenar con otra IA sin declararlo ni convertir el archivo a JSON. No modificar IDs o textos.

Las respuestas parten vacías. «Lista» en Estado significa que están los campos requeridos, no que el criterio sea correcto. La guía está dentro del libro. No hay etiquetas propuestas por caso, probabilidades, hojas ocultas ni macros. Sí se conoce que la muestra fue dirigida a lenguaje potencialmente H/D: no se afirma ceguera absoluta.

## Alcance autorizado

El investigador aprobó preparar una primera selección de 60 candidatos reales con «siii» y pidió continuar con «sigue». La idea de sintéticos de PLAN §9.24 **no se ejecuta**. Tampoco se entrena, se importan nuevas etiquetas ni se altera la referencia v2, el filtro A o los cinco folds originales. Alcanzar 200 H/200 D es un objetivo orientativo posterior, no una cuota que estas 60 observaciones deban satisfacer.

## Diseño reproducible de la búsqueda

- Corpus propio L0, texto completo y original. No datos externos, clasificación masiva de producción, llamadas a modelos o descargas de pesos.
- Excluir los **1.352 IDs anotados** (unión de archivos de etiquetas y paquete vigente) y los **306 IDs del marco humano**. Del marco humano se usa únicamente `intervencion_id`; no se abren respuestas del Excel devuelto ni etiquetas humanas. Los textos de esos IDs se consultan en L0 solo para impedir duplicados.
- Excluir también copias con whitespace, mayúsculas y acentos normalizados; deduplicar candidatos con la misma clave. Evitar casi copias mediante Jaccard de trigramas de palabras ≥0,85 frente a excluidos y seleccionados. Esto no garantiza ausencia de toda paráfrasis semántica.
- Descartar textos marcados dañados, caracteres incompatibles con XML y unidades de menos de 200 caracteres. No corregir OCR. Estos filtros afectan la representatividad y quedan registrados.
- Buscar patrones de acción sobre TPM/tasas, retiro de estímulo, mayor estímulo y sesgos. Dos **canales de búsqueda**, H y D, no etiquetas asignadas ni probabilidades calibradas. Una mención negada o una tasa extranjera puede activar una pista: la revisión del texto completo debe resolverla.
- Por cada canal: diez candidatos con patrón de decisión, diez de trayectoria y diez de contraste. Las categorías son mecánicas, no diagnósticos humanos: contraste tiene prioridad cuando hay conectores, pausa o pistas de ambos sentidos. El código registra cualquier reasignación si una familia no alcanza; no relaja los límites de diversidad silenciosamente.
- Orden determinista por hash con semilla 20260916. Diversificar años, longitudes, actores y reuniones; máximo dos casos por reunión y doce por actor. La longitud corta se define como ≤1.800 caracteres, media hasta 4.000 y larga por encima de 4.000. Se priorizan categorías menos representadas durante la selección; no se imponen etiquetas.
- Mezclar el orden de presentación y asignar C01–C60, en seis bloques de diez. No separar las hojas por canal ni revelar sus pistas.

Las fuentes, el procedimiento y los hashes están registrados. La selección debe reproducirse exactamente en IDs, texto y orden; no se usa el hash binario de un XLSX regenerado como única prueba de equivalencia, porque sus metadatos ZIP pueden variar.

## Separación futura de entrenamiento y validación

**No existe un train ampliado todavía.** Cada candidato lleva, únicamente en el archivo técnico, los folds prohibidos por compartir reunión o texto normalizado con la validación original de ese fold. Los restantes son *potencialmente* permitidos, nunca una incorporación automática.

Antes de entrenar con respuestas nuevas: comprobar identidad y citas, conservar originales, resolver dudas según el protocolo, volver a validar copias/parentescos y purgar por reunión/texto en cada fold. Los casos de una reunión de validación nunca pueden añadirse al train de ese mismo fold. El código actual 38/39 no consume esta muestra ni sus respuestas: una ampliación requerirá una etapa y un paquete nuevos.

La muestra enriquecida es para desarrollo/entrenamiento: **no estima prevalencias, no es un nuevo test representativo ni recupera la independencia de los 306 casos antiguos**. No cambiar las referencias de los 793 casos a raíz de los nuevos ejemplos.

## Artefactos y reproducción

Carpeta: `data/auditoria/ampliacion_hd_60_v1/`.

- **`revision_60_candidatos.xlsx`**: único archivo que necesita el investigador.
- `NO_CONSULTAR_antes_de_responder_seleccion.json`: trazabilidad técnica, pistas de búsqueda y plan de exclusiones. No consultarlo antes de responder. No contiene etiquetas humanas nuevas.
- `resumen.json`: conteos, diversidad y límites.
- `manifest.json`: hashes de fuentes y salidas.
- `verificacion.json`: controles efectuados tras generar el libro.

Con el entorno de preparación instalado:

```bash
python scripts/40_gestionar_proyecto.py preparar-muestra-hd --salida entregas/otra_muestra_60
```

Exige una ruta inexistente; no sobrescribe una muestra o respuestas. Se conserva una sola entrada de usuario. La lógica de muestreo está en el módulo `scripts/muestreo_revision.py`; reutiliza las utilidades Excel de 29 sin modificar archivos congelados. No se añadió una variante de modelo ni un script numerado 41. La reducción definitiva de dependencias históricas sigue pendiente de la limpieza extrema final.

## Recepción futura

Aceptar el XLSX completado o parcial. **No pasarlo al importador de las 30 anotaciones anteriores:** son otra muestra y otras posiciones. La recepción debe comprobar C01–C60, textos y celdas, cotejar citas, distinguir pendientes de respuestas y registrar ayuda/fecha declaradas. No ejecutar fórmulas externas o macros en libros recibidos. Ninguna fecha, respuesta o independencia se presume a partir de la fecha de creación del archivo.
