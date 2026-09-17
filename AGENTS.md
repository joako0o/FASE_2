# Continuidad de FASE_2

1. Leer primero `docs/CONTINUIDAD.md`, `EMPEZAR_AQUI.md` y `docs/AVANCE.md`. No reconstruir decisiones buscando respuestas antiguas.
2. Trabajar en la rama asignada por el entorno de la sesión actual. La entrega previa procede de `arena/01a0a81b-fase-2`, PR #4. No cambiar automáticamente a esa rama en otra sesión; comprobar si el PR fue integrado.
3. Ya se recibieron cinco folds BETO externos y se verificaron integridad/métricas: F1 H/D 0,625043 frente a 0,747060 de TF-IDF; inversiones 25 frente a 15. No adoptado. Leer `docs/RESULTADOS_BETO_V1.md`. Falta cerrar procedencia del código/entorno remoto; no repetir entrenamiento ni afirmar reproducción GPU local.
4. Referencias corregidas v2, cinco folds purgados y filtro A fijos. No alterar etiquetas/textos/OCR, no volver a pedir las seis aceptaciones ni las trece correcciones, no repetir las 30 anotaciones.
5. Los 793 casos son desarrollo reutilizado con ayuda IA, no un test independiente. Diez inversiones conocidas y cinco ambiguas no forman un nuevo test.
6. No abrir las respuestas antiguas de 306 ni ejecutar la suite general. Usar `python scripts/40_gestionar_proyecto.py probar --regresion`, que selecciona módulos permitidos.
7. No ejecutar scripts 01–39 secuencialmente: son historia de etapas, no un instalador. Entrada actual en 40; lógica congelada en 38/39. No refit global ni scoring del corpus sin una decisión posterior.
8. Respetar hashes/bytes/rutas de los artefactos congelados y las reglas de `docs/REGLAS.md`. Si hace falta corregir el runner tras la primera prueba GPU, versionar explícitamente y reconstruir el paquete; no mezclar folds de paquetes diferentes.
9. No pagos, credenciales en chat, TLS desactivado ni datasets externos nuevos. Si no hay GPU/acceso a pesos, registrar el bloqueo honestamente.
10. Mantener limpio: no commitear `.venv`, pesos, caches o ZIP; conservar evidencia necesaria. Actualizar `docs/AVANCE.md`, `docs/CONTINUIDAD.md` e inventario `entrega/archivos_proyecto.txt` al cerrar trabajo nuevo.
11. Antes de entregar, comprobar el ZIP extraído sin `.git`, su manifiesto y las pruebas seleccionadas. Un respaldo de resultados no es un proyecto completo. No cerrar/fusionar PR sin autorización explícita.

12. **Limpieza final extrema pendiente y obligatoria**: leer `docs/REGLAS.md` §12. La entrega actual con ~40 scripts es provisional; el gestor 40 no cumple por sí solo la limpieza. Refactorizar a una entrada y pocos módulos esenciales, retirar dependencias/material obsoleto y separar el histórico recuperable del paquete operativo. Verificar equivalencia sin alterar datos/etiquetas; no declarar cierre antes de cumplirlo.

13. Meta 300 H/300 D totales sin forzar etiquetas ni esperar Excel. Cuatro tandas/89 nuevos IDs revisados; altos nuevos H29/D30, catálogo preparado H154/D119, faltan H146/D181. Continuar G001–G020 de `data/auditoria/meta_hd_300_v1/seleccion_05/cola.json` por lectura íntegra; canal no es etiqueta. E009 es D alto pero excluido como copia cercana: el contador usa `uso_propuesto=hd_alta_confianza`, no solo etiqueta/confianza. Excluir todos los IDs revisados y mantener v2/folds/A, sin entrenamiento ni sintéticos automáticos.

14. Ensayo TF-IDF con 59 altos ya ejecutado y no adoptado: F1 H/D 0,747060→0,713526, errores51→57, H↔D15→17. Ver `docs/RESULTADOS_AMPLIACION_TFIDF_59_V1.md`. No repetirlo o adoptar/refit automáticamente; fuentes/v2/folds/A intactos. La meta300/300 permanece, con recomendación de revisar calidad/representatividad antes de acumular por cuota.

15. Diagnóstico del deterioro +59 terminado: `docs/DIAGNOSTICO_AMPLIACION_TFIDF_59_V1.md`, 16 textos/12.005 contribuciones/replay exacto/116tests. Fronteras de referencia no son correcciones aprobadas. No reetiquetar o entrenar variantes automáticamente; contrastes de acto discursivo antes de acumular por cuota, sin añadir estos casos a su train.
