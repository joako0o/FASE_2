# REGLAS DE TRABAJO — Proyecto D&H

> Reglamento permanente del proyecto. Se aplica a todo código, dato y documento del repo.
> Acordadas con el investigador el 2026-09-15. Cualquier cambio a estas reglas se propone, se acuerda y se registra aquí.

## 1. Limpieza total
- Nada de **código muerto**: ni bloques comentados "por si acaso", ni funciones que nadie llama, ni archivos huérfanos. Si no se usa, se borra.
- Nada de duplicados: si dos scripts necesitan lo mismo → va como función compartida.
- Al cerrar cada unidad de trabajo se revisa que no quede nada sin usar.

## 2. Código por secciones, explicado
- Todo script se organiza en **secciones con título** (ej. `# ---- 1. Carga de datos ----`).
- Cada sección lleva un comentario con **explicación simple pero completa** de qué hace y por qué. Se entiende sin ejecutar el código.
- **Cualquier programador debe poder entender el código**: nombres de variables y funciones claros y en español, cero trucos crípticos, cero abreviaturas inventadas.

## 3. Metodológicamente correcto, siempre
- Toda decisión metodológica queda **justificada por escrito** (en el script, el codebook o el PLAN).
- Sesgo conservador: cuando dos criterios compiten, se elige el que genera conclusiones más débiles pero más defendibles (ver R9 del codebook).
- Los supuestos se declaran; no se esconden dentro del código.
- Los números que lleguen al paper/scrollytelling salen de **scripts reproducibles**, nunca de corridas manuales no registradas.

## 4. Buenas prácticas de código
- **Funciones** para toda lógica no trivial; una función = una responsabilidad.
- **Parámetros en un solo lugar** (seeds, rutas, tamaños de muestra): nada de valores mágicos dispersos.
- **Seed fija y registrada** en todo muestreo/aleatoriedad. Reproducibilidad total: el mismo script + los mismos datos = el mismo resultado.
- **Validaciones con `assert`** al final de cada etapa: forma esperada, nulos, duplicados de `intervencion_id`. Un fallo detiene la pipeline, no pasa en silencio.
- Dependencias fijadas (`requirements.txt`).

## 5. Disciplina de datos
- **Capa L0 inmutable**: el corpus original nunca se edita a mano ni se sobrescribe; todo cambio se hace por script hacia capas nuevas.
- **Etiquetas append-only**: nunca se sobrescriben ni editan corridas pasadas; una corrección es una nueva corrida registrada.
- Todo output registra: fecha, versión de codebook/config con que se generó.
- No se commitean artefactos grandes (checkpoints, modelos): van fuera de git vía `.gitignore`.

## 6. Orden del repo
- La numeración por fase documenta el desarrollo histórico, no obliga a conservar un script por experimento en la entrega final. La estructura final debe cumplir la limpieza obligatoria de §12.
- Nombres `snake_case`, descriptivos.
- Documentación en `docs/`; datos en `data/`; este orden no se negocia dentro del proyecto.

## 7. Git y GitHub
- **Un PR por unidad de progreso** (docs, codebook, ronda de etiquetado, entregable).
- Commits pequeños con mensajes descriptivos (qué y por qué, no "update").
- Nunca credenciales ni datos sensibles en el repo (en este proyecto toda la data es pública, pero la regla queda).
- Trabajo siempre sobre la rama de sesión configurada en el entorno.

## 8. Documentos vivos — regla de cierre
- **`docs/AVANCE.md` se actualiza SIEMPRE al cierre de cada sesión de trabajo**: qué se hizo, qué sigue, bloqueos. Es la memoria del proyecto entre sesiones.
- `PLAN.md` se actualiza cuando cambia una decisión de diseño.
- El codebook se versiona (v1, v2, …); nunca se edita retroactivamente una versión ya usada para etiquetar.

## 9. Reglas de la IA en este proyecto
- La IA etiqueta según el codebook vigente, no según intuición del momento; si un caso no está cubierto, se etiqueta con la mejor aproximación + nota, y se propone agregar el caso al §6 del codebook.
- La IA declara sus incertidumbres (confianza `baja` cuando corresponde) en vez de forzar certeza.
- Cada ronda de etiquetado se cierra con PR + actualización de AVANCE.md.

## 10. Estilo: lenguaje profesional, sin emojis
- Todo el material del proyecto (documentos, código, comentarios, mensajes de commit, descripciones de PR y salidas) usa **lenguaje profesional**.
- **Prohibido el uso de emojis** en cualquier archivo del repositorio.
- (Regla agregada el 2026-09-15 a solicitud del investigador.)

## 11. Cambios a estas reglas
Se pueden agregar o modificar reglas, siempre: propuesta → acuerdo con el investigador → registro en este archivo con fecha.

## 12. Limpieza extrema obligatoria antes de la entrega final

**Requisito explícito del investigador, 2026-09-16:** «al final tenemos que hace limpieza extrema y de jar lo necesesario y esencial porque 40 scripts no lo veo correcto».

- **La organización actual es provisional.** La limpieza final sigue pendiente y es una condición de cierre del proyecto, no una mejora opcional.
- No basta con añadir un lanzador que llame a decenas de scripts antiguos, borrar caches, crear índices o cambiar nombres. El investigador no debe recibir una colección de unos 40 scripts experimentales como producto final.
- Refactorizar el flujo elegido en **una entrada de ejecución y un conjunto pequeño de módulos con responsabilidades claras**. Reducir realmente dependencias históricas, código duplicado y generadores/variantes descartados. No fijar un número arbitrario ni juntar todo en un archivo gigante para aparentar limpieza.
- Conservar en la entrega operativa únicamente el código usado, datos imprescindibles, configuración/dependencias, pruebas pertinentes y documentación breve necesaria para ejecutar, verificar y continuar.
- Retirar del árbol activo archivos muertos, plantillas/formularios ya cerrados, copias redundantes, pruebas de rutas retiradas y documentación obsoleta. La evidencia histórica necesaria debe quedar identificada y recuperable mediante una revisión Git o archivo separado; **no incluirla automáticamente toda en el paquete operativo**.
- Antes de retirar una dependencia, comprobar sus usos y completar su sustitución. Preservar originales irreemplazables, adjudicaciones y procedencia necesarias. La refactorización no autoriza cambiar etiquetas, folds, filtro A, texto ni resultados para hacer pasar pruebas.
- No falsear manifiestos históricos para ocultar cambios: conservar su versión reproducible aparte y generar manifiestos nuevos para la entrega reducida. Las comprobaciones de equivalencia deben justificar qué se mantiene y qué se retira.
- **Criterios de aceptación del cierre:** inventario final con función de cada archivo; lista de retirados/fusionados y ubicación del histórico necesario; ejecución desde una instalación limpia usando solo el paquete reducido; pruebas de integridad/equivalencia aprobadas; instrucciones cortas y ausencia de dependencias ocultas de la carpeta histórica.
- Registrar este cierre en AVANCE/CONTINUIDAD. **No marcar «limpieza final terminada» mientras la solución operativa siga dependiendo de los aproximadamente 40 scripts actuales.** Este requisito prevalece sobre la costumbre de conservar cada etapa en el árbol de entrega.
