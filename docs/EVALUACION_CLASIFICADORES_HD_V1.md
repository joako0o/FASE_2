# Comparación de clasificadores con foco en H/D

**Mejor candidato observado: B0_limpia.** Variantes que cumplen el criterio previo: **ninguna**.

**Estos resultados son contra etiquetas IA, no un nuevo examen humano. BETO no fue ejecutado.** No se reemplazó el modelo guardado.

## Qué se hizo

- [Protocolo congelado antes del ajuste](PROTOCOLO_CLASIFICADORES_HD_V1.md). Se comparan cinco alternativas con la misma validación y una ancla histórica aparte.
- No se pudieron adquirir pesos de BETO: la petición a Hugging Face falló con TLS EOF. Tampoco había checkpoint local o GPU; dos CPU y ~3,8 GiB de RAM. No se instalaron dependencias grandes ni se creó un script ficticio de BETO. Esto no mide su calidad.
- A (relevancia) unigramas compartida entre los cinco modelos limpios. B solo se ajusta con IA relevante. A=0 produce neutral. Palabras 1–4, LR C=2 o SVM C=1, balanced, sin búsqueda posterior.
- Las variantes mixtas agregan caracteres 3–5 (char_wb, máximo 50.000) con igual peso por bloque y L2 global. La jerárquica aprende una puerta neutral/direccional y después H/D, sin conocer la verdad de validación al predecir.
- No se añadieron WCB, FinancES, traducciones ni etiquetas externas. No se reajustó sobre todo el corpus ni se guardaron clasificadores.

## Control de copias textuales

Se mantuvieron las mismas 793 intervenciones de validación. De cada train se retiraron las copias de validación normalizando espacios, minúsculas y acentos. No se tocaron L0 ni las etiquetas; algunos de los 559 ejemplos inicialmente fijos en train pueden salir por esta regla.

| Fold | Train original | Train purgado | Retirados | Validación con copia antes | Con copia después |
|---|---:|---:|---:|---:|---:|
| 1 | 1194 | 1178 | 16 | 5 | 0 |
| 2 | 1193 | 1178 | 15 | 7 | 0 |
| 3 | 1193 | 1178 | 15 | 9 | 0 |
| 4 | 1193 | 1183 | 10 | 5 | 0 |
| 5 | 1194 | 1183 | 11 | 8 | 0 |

La ancla H0 reproduce exactamente las 793 predicciones históricas; **la comparación de candidatos se hace contra B0 limpia**, no contra H0. Quitar copias no elimina equivalencias semánticas, repeticiones dentro de cada conjunto ni el uso previo de esta validación para seleccionar métodos.

## Resultado principal

**F1 H/D = (F1 hawkish + F1 dovish)/2**, calculado sobre todas las filas: las falsas alarmas sobre neutrales también penalizan. La columna principal es su media entre folds. No es una probabilidad por predicción ni el porcentaje de aciertos de una moneda.

| Modelo | F1 H/D medio | DE | Delta vs B0 | Folds mejores | Macro-F1 H/D/N medio |
|---|---:|---:|---:|---:|---:|
| H0_historica | 0.6875 | 0.0893 | -0.0040 | 0/5 | 0.7803 |
| B0_limpia | 0.6915 | 0.0836 | +0.0000 | 0/5 | 0.7835 |
| B1_svm | 0.6285 | 0.0871 | -0.0630 | 1/5 | 0.7404 |
| B2_lr_mixta | 0.6496 | 0.0990 | -0.0418 | 0/5 | 0.7548 |
| B3_svm_mixta | 0.6412 | 0.0265 | -0.0503 | 2/5 | 0.7497 |
| B4_jerarquica | 0.6470 | 0.0858 | -0.0444 | 0/5 | 0.7523 |

H0 es referencia histórica sin purga, no candidata. B0=LR palabras; B1=SVM palabras; B2=LR mixta; B3=SVM mixta; B4=jerárquica palabras.

## ¿Reconoce H/D o predice la clase más frecuente?

La siguiente tabla usa las predicciones conjuntas de las 793 filas. Acierto H/D restringe **solo la evaluación** a H/D verdaderos; una salida neutral cuenta como error. Los modelos no reciben esa selección al predecir. Recall H y D muestran por separado lo que se recupera de cada clase.

| Modelo | Recall H | Recall D | Acierto sobre H/D | Accuracy global | Errores | H↔D | N→dirección | Dirección→N |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H0_historica | 0.7826 | 0.7347 | 0.7627 | 0.9218 | 62 | 17 | 34 | 11 |
| B0_limpia | 0.7826 | 0.7347 | 0.7627 | 0.9243 | 60 | 17 | 32 | 11 |
| B1_svm | 0.7681 | 0.4286 | 0.6271 | 0.9231 | 61 | 12 | 17 | 32 |
| B2_lr_mixta | 0.7826 | 0.6531 | 0.7288 | 0.9155 | 67 | 21 | 35 | 11 |
| B3_svm_mixta | 0.7971 | 0.4490 | 0.6525 | 0.9256 | 59 | 14 | 18 | 27 |
| B4_jerarquica | 0.7681 | 0.7143 | 0.7458 | 0.9117 | 70 | 21 | 40 | 9 |

**Referencias ingenuas:** clase más frecuente elegida en cada train purgado, aplicada a todas las filas sin puerta A. No son candidatas.

| Regla constante | F1 H/D conjunto | Accuracy global | Acierto sobre H/D |
|---|---:|---:|---:|
| mayoritaria | 0.0000 | 0.8512 | 0.0000 |
| mayoritaria_hd | 0.0800 | 0.0870 | 0.5847 |

Una moneda entre H/D tiene 50% de acierto esperado sobre H/D verdaderos; el desbalance permite superar ese número con una regla constante. Superar 50% no demuestra significación ni confiabilidad humana. La tabla no debe compararse directamente con el examen humano anterior: son otras referencias y otro conjunto.

## Errores cambiados y batería conocida

| Modelo | Corregidos vs B0 | Nuevos vs B0 | Aciertos sintéticos / 70 | Invariancia / 20 |
|---|---:|---:|---:|---:|
| H0_historica | 0 | 2 | 25 | 14 |
| B0_limpia | 0 | 0 | 25 | 14 |
| B1_svm | 17 | 18 | 26 | 15 |
| B2_lr_mixta | 3 | 10 | 10 | 19 |
| B3_svm_mixta | 18 | 17 | 20 | 15 |
| B4_jerarquica | 2 | 12 | 25 | 18 |

Son 14 textos inventados conocidos × 5 modelos por variante, no 70 observaciones independientes. Los cuatro pares por fold también son conocidos; invariancia no equivale a corrección. No se ajustó el clasificador para aprobarlos.

## Decisión y límites

**Ninguna alternativa cumple todos los criterios prefijados. Cerrar esta ronda sin adopción ni ampliar la rejilla.**
Requisitos: +0,02 de F1 H/D medio; ≥3/5 folds mejores; pérdida de macro-F1 ≤0,005; pérdidas de recall H y D ≤0,02; pérdida de exactitud sintética ≤0,05. No son pruebas de significación. La mayor media observada por sí sola no basta.
**No se ha demostrado mejora contra personas.** Las 793 IA son desarrollo reutilizado, los folds comparten train y los métodos fueron propuestos con conocimiento de diagnósticos previos. Una confirmación futura necesita una referencia humana nueva y reservada, no reutilizar los 306 conocidos para ajustar.
SVM, caracteres y jerarquía siguen siendo métodos léxicos. Un resultado aquí no descarta un transformer ni demuestra comprensión de emisor, objeto, negación o preferencia. BETO y entrenamiento auxiliar financiero quedan sin ejecutar, no como métodos fallidos.

## Archivos y repetición

`data/evaluacion/clasificadores_hd_v1/`: protocolo, asignaciones, exclusiones de train por ID/hash, auditoría, predicciones, métricas por fold, referencias ingenuas, pruebas sintéticas, comparación, tiempos y manifiesto. `reproducibilidad.json` registra la repetición y tests posteriores cuando estén terminados.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/26_comparar_clasificadores_hd.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/26_comparar_clasificadores_hd.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
python -m unittest discover -s tests -p test_clasificadores_hd.py -v
```
