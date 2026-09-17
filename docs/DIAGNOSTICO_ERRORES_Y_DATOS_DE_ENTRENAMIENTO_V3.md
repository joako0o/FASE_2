# Diagnóstico de errores v3 y decisión sobre nuevas bases de entrenamiento

## 1. Dónde están los 64 errores

La matriz usa filas como referencia real v3 y columnas como predicción congelada, en orden H, D, N:

| Real \ Predicción | H | D | N | Soporte | Errores | Tasa de error |
|---|---:|---:|---:|---:|---:|---:|
| Hawkish | 65 | 11 | 12 | 88 | 23 | 26,14% |
| Dovish | 4 | 25 | 3 | 32 | 7 | 21,88% |
| Neutral | 12 | 22 | 639 | 673 | 34 | 5,05% |

Métricas por clase:

| Clase | Precisión | Recall | F1 |
|---|---:|---:|---:|
| Hawkish | 0,8025 | 0,7386 | 0,7692 |
| Dovish | 0,4310 | 0,7813 | 0,5556 |
| Neutral | 0,9771 | 0,9495 | 0,9631 |

El 91,93% de accuracy global está dominado por los 673 neutrales (84,87% de la validación), por lo que no debe interpretarse solo.

## 2. Tipo y gravedad operativa

| Tipo de error | Conteo | % de los 64 | Lectura operativa |
|---|---:|---:|---|
| H ↔ D | 15 | 23,44% | Dirección opuesta; prioridad 1 |
| Neutral → H/D | 34 | 53,13% | Señal direccional falsa; prioridad 2 |
| H/D → neutral | 15 | 23,44% | Omisión de señal; prioridad 3 |

Desagregación exacta: H→D 11, H→N 12, D→H 4, D→N 3, N→H 12 y N→D 22.

**Conclusión:** sí es materialmente preocupante si el objetivo es inferir dirección monetaria. En especial, la precisión dovish de 0,431 significa que solo 25 de 58 predicciones D son D bajo v3. También hay 15 inversiones directas H/D. No obstante, esto no prueba un defecto definitivo de la arquitectura: son predicciones congeladas de un modelo supervisado con el criterio anterior. El diagnóstico justifica la fase B, pero impide afirmar que el modelo histórico ya sea adecuado para producción bajo v3.

De los 64 errores, 22 están en IDs cuya referencia fue recodificada y 42 ya ocurren en IDs cuya etiqueta no cambió. Los errores aparecen en 37 reuniones; no son un único episodio aislado. La mayor concentración es RPM-2005-03-10, con seis errores.

## 3. ¿Usar el set pre-2000 entregado?

**Sí conviene probar su valor, pero no entrenarlo en su estado actual.** Sus 257 filas pueden aportar vocabulario de otro régimen histórico y más ejemplos direccionales, pero hoy contiene seis etiquetas `pendiente`, ocho citas no literales y cuatro pares de texto duplicado, además de casos incompatibles con el criterio doméstico de dirección respaldada.

Tratamiento recomendado:

1. terminar una adjudicación v3 completa, reparar citas y registrar procedencia/grupos;
2. excluir pendientes no resueltos y resolver duplicados antes de entrenar;
3. conservar la fase B con solo los 1.352 IA-base como control;
4. evaluar pre-2000 únicamente como una ampliación separada, nunca mezclada silenciosamente con el control;
5. mantener validación real post-2000 y los folds históricos; el set pre-2000 entra solo en entrenamiento;
6. aceptar la ampliación solo si mejora F1-HD y reduce errores H↔D de forma consistente, sin deterioro relevante en neutral ni concentración en uno o dos folds.

Esto preserva la atribución causal: cualquier cambio podrá asociarse al set histórico, no a una combinación de varias ampliaciones.

## 4. ¿Puede servir una base sintética de unas 5.000 intervenciones?

**Puede ser útil como aumento de entrenamiento, especialmente para H y D escasos, pero no sirve como validación ni reemplaza datos reales.** Al ser casi cuatro veces mayor que la base IA de control, usarla completa de inmediato puede hacer que el modelo aprenda estilo del generador, plantillas o palabras que revelan artificialmente la etiqueta.

Condiciones mínimas para que el experimento sea informativo:

- cada intervención debe tener una dirección latente definida antes de redactar el texto y cumplir codebook v3;
- incluir neutrales difíciles, tasas fijas sin comparación, alternativas condicionales y casos donde se menciona una dirección sin respaldarla;
- registrar `synthetic_id`, etiqueta, relevancia, escenario, plantilla/familia, semilla, modelo/generador, versión del prompt y fecha;
- agrupar por escenario y familia de plantilla para evitar paráfrasis hermanas atravesando particiones;
- deduplicar entre sintéticos y contra todos los textos reales;
- usar sintéticos solo en entrenamiento y evaluar siempre sobre los mismos 793 ejemplos reales;
- no combinar en el mismo primer ensayo sintéticos, 89 IA nuevas y pre-2000;
- hacer una curva de dosis: 0, 250, 500, 1.000, 2.500 y 5.000 sintéticos, con muestreo balanceado y, si corresponde, menor peso para ejemplos sintéticos;
- informar por separado precisión/recall/F1 de H, D y N, las seis confusiones y resultados por fold;
- revisar manualmente una muestra estratificada antes de habilitar cualquier entrenamiento.

## 5. Secuencia recomendada

1. **Fase B:** mismo TF-IDF, 1.352 reales, folds y parámetros históricos, supervisión v3.
2. Diagnosticar si baja la precisión D o persisten inversiones H/D.
3. **Tratamiento sintético separado:** curva de dosis, entrenamiento con real+sintético, evaluación exclusivamente real.
4. **Fase C:** probar las 89 IA nuevas por separado, como ya estaba fijado.
5. **Tratamiento pre-2000:** solo después de su auditoría v3 completa.
6. Comparar todos los tratamientos contra el mismo control B, no entre mezclas acumulativas difíciles de atribuir.

La base sintética es prometedora para corregir escasez de clase, pero su utilidad se demostrará únicamente si mejora errores reales fuera de sus familias de generación.
