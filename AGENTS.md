# Continuidad de FASE_2

1. Leer primero `docs/CONTINUIDAD.md`, `EMPEZAR_AQUI.md` y `docs/AVANCE.md`. No reconstruir decisiones buscando respuestas antiguas.
2. Trabajar en la rama asignada por el entorno de la sesión actual. La entrega previa procede de `arena/01a0a81b-fase-2`, PR #4. No cambiar automáticamente a esa rama en otra sesión; comprobar si el PR fue integrado.
3. La tarea pendiente es una comparación BETO controlada. Preparado no significa entrenado: no hay ejecución real ni métricas BETO en esta entrega.
4. Referencias corregidas v2, cinco folds purgados y filtro A fijos. No alterar etiquetas/textos/OCR, no volver a pedir las seis aceptaciones ni las trece correcciones, no repetir las 30 anotaciones.
5. Los 793 casos son desarrollo reutilizado con ayuda IA, no un test independiente. Diez inversiones conocidas y cinco ambiguas no forman un nuevo test.
6. No abrir las respuestas antiguas de 306 ni ejecutar la suite general. Usar `python scripts/40_gestionar_proyecto.py probar --regresion`, que selecciona módulos permitidos.
7. No ejecutar scripts 01–39 secuencialmente: son historia de etapas, no un instalador. Entrada actual en 40; lógica congelada en 38/39. No refit global ni scoring del corpus sin una decisión posterior.
8. Respetar hashes/bytes/rutas de los artefactos congelados y las reglas de `docs/REGLAS.md`. Si hace falta corregir el runner tras la primera prueba GPU, versionar explícitamente y reconstruir el paquete; no mezclar folds de paquetes diferentes.
9. No pagos, credenciales en chat, TLS desactivado ni datasets externos nuevos. Si no hay GPU/acceso a pesos, registrar el bloqueo honestamente.
10. Mantener limpio: no commitear `.venv`, pesos, caches o ZIP; conservar evidencia necesaria. Actualizar `docs/AVANCE.md`, `docs/CONTINUIDAD.md` e inventario `entrega/archivos_proyecto.txt` al cerrar trabajo nuevo.
11. Antes de entregar, comprobar el ZIP extraído sin `.git`, su manifiesto y las pruebas seleccionadas. Un respaldo de resultados no es un proyecto completo. No cerrar/fusionar PR sin autorización explícita.
