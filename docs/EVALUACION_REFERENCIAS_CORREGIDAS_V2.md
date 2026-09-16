# Referencias corregidas y ejecución local del TF-IDF

**13 correcciones nuevas aplicadas en una referencia versionada; 12 ambiguos conservados. TF-IDF entrenado aquí; BETO sigue bloqueado por acceso a sus pesos.**

La instrucción del investigador autoriza las 13 propuestas del cierre de 66. Las seis decisiones Rxx siguen vigentes: 19 decisiones aceptadas, 16 cambios efectivos respecto de IA. Las citas, razones y confianzas siguen atribuidas al agente; es adjudicación asistida post-predicción, no anotación humana independiente.

## Comparación que separa referencias de entrenamiento

| Supervisión de train | Referencia de validación | F1 H/D medio | Macro-F1 medio | Errores / 793 |
|---|---|---:|---:|---:|
| seis_previas | ia_original | 0.648822 | 0.754311 | 66 |
| seis_previas | corregida_v2 | 0.711084 | 0.798013 | 55 |
| seis_mas_trece | ia_original | 0.684035 | 0.778042 | 62 |
| seis_mas_trece | corregida_v2 | 0.747060 | 0.822250 | 51 |

- **Solo cambiar referencias**, dejando fijo el control: delta F1 H/D +0.062262. No es mejora del modelo.
- **Volver a entrenar**, comparando contra la misma referencia corregida: delta F1 H/D +0.035976; mejora en 4/5 folds.
- 9 predicciones finales distintas; contra referencia v2, 6 errores corregidos y 2 nuevos.
- Mismos folds purgados, textos, parámetros, puerta A, vocabularios e IDF. El control reproduce exactamente A/B/final de la variante adjudicada del experimento 31. No hubo búsqueda de hiperparámetros ni selección de etiquetas por puntuación.

## Qué quedó corregido

`data/evaluacion/referencias_corregidas_v2/referencias_desarrollo_v2.csv` es la vista activa para este experimento: 1.352 IDs con referencia IA, versión con seis decisiones y versión con seis más trece. El entrenamiento seis_mas_trece y la puntuación corregida_v2 leen esas decisiones verificadas. No es solo una lista de sugerencias.

Los originales y resultados históricos no se sobrescriben. Los scripts históricos siguen usando sus versiones para reproducibilidad; cualquier experimento nuevo que quiera la referencia corregida debe consumir explícitamente esta vista verificada. No se alteró relevancia IA, codebook v2 ni referencia de los 12 ambiguos.

Correcciones nuevas aceptadas (H hawkish, D dovish, N neutral):

| Caso | ID | IA → corregida |
|---|---|---|
| H02 | RPM-2006-05-11:674:1 | D → H |
| H08 | RPM-2008-02-07:1684:1 | D → H |
| H13 | RPM-2011-08-18:4280:1 | D → N |
| N07 | RPM-2005-01-11:39:1 | N → H |
| N16 | RPM-2005-03-10:198:1 | N → H |
| N19 | RPM-2015-08-13:6965:1 | N → D |
| N21 | RPM-2007-05-10:1261:1 | N → H |
| N27 | RPM-2005-01-11:5:1 | N → H |
| L02 | RPM-2015-06-11:6854:1 | N → D |
| L04 | RPM-2005-03-10:178:1 | N → H |
| L05 | RPM-2013-06-13:5632:1 | N → D |
| L10 | RPM-2008-12-11:2238:1 | N → D |
| L11 | RPM-2009-08-13:2681:1 | N → D |

## Límites de interpretación

Estas 793 observaciones ya se usaron en desarrollo y las 13 correcciones provienen de revisar desacuerdos después de ver predicciones. Mantener folds por reunión y excluir copias evita introducir la observación validada en su propio train, pero NO elimina el sesgo de la revisión post-predicción. Ni los nuevos scores ni sus diferencias estiman una mejora independiente o sobre todo el corpus.

No hubo acceso a las 306 respuestas antiguas, test nuevo, refit final sobre todo el corpus ni reemplazo de un modelo de producción. Los ajustes por fold son efímeros. Se conservan las correcciones aceptadas aunque no eleven una métrica. Para afirmar generalización hará falta una evaluación realmente nueva y controlada, no reabrir aquel examen.

## BETO: intento y bloqueo

Se intentó acceder al checkpoint oficial dccuchile/bert-base-spanish-wwm-cased: API y config con urllib dieron TLS EOF; curl devolvió SSL_ERROR_SYSCALL, código 35. Dos CPU lógicas y sin nvidia-smi. No se desactivó TLS, no se descargaron pesos y BETO no se entrenó. El registro técnico está junto a la aceptación, en beto_disponibilidad.json. La limitación de acceso no mide la calidad de BETO.

## Artefactos y reproducción

- Aceptación: `data/auditoria/revision_errores_adjudicada_v1/adjudicacion_cierre_66_v1/aceptacion.json`.
- Resultados: `data/evaluacion/referencias_corregidas_v2/`: referencias versionadas, control_folds, protocolo previo, predicciones, métricas por fold, resumen, manifiesto y verificación.
- Las pruebas y el replay certifican integridad/reproducción, no verdad semántica ni independencia.

```bash
python scripts/36_evaluar_referencias_corregidas.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/36_evaluar_referencias_corregidas.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
```

[Protocolo previo](PROTOCOLO_REFERENCIAS_CORREGIDAS_V2.md) · [Evidencia de las 66 lecturas](REVISION_ERRORES_CIERRE_66_V1.md). La indicación histórica «pendientes de aceptación» en el cierre queda superada para estas 13 por la aceptación nueva, sin reescribir aquel informe.
