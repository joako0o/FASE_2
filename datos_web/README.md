# Datos para el scrollytelling

Paquete generado por `scripts/preparar_datos_web.py`. No editar los JSON manualmente.

- `resumen.json`: cifras canónicas del corpus.
- `metodologia.json`: definiciones y advertencias obligatorias.
- `series_generales.json`: orientación, tópicos y decisiones por año.
- `topicos.json`: 14 componentes auditados y cruce blando con H/D/N.
- `estructura_actas.json`: distribución por quintil documental.
- `actores.json`: perfiles, radar, tópicos, léxico y serie anual.
- `reuniones.json`: 132 fichas agregadas, acuerdos, dispersión y votos trazables.
- `actas/index.json`: selector de reuniones.
- `actas/2005.json` … `actas/2015.json`: intervenciones para carga diferida.
- `manifest.json`: tamaños y SHA-256.

El frontend debe cargar primero `resumen`, `metodologia`, `series_generales`, `topicos` y `actas/index`; los años se cargan solo al abrir una reunión. No llamar “transcripción” a `intervenciones`: son secuencias reconstruidas desde el acta publicada.
