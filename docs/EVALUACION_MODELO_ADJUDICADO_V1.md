# Referencia TF-IDF tras adjudicación: resultado

**Se entrenaron las dos condiciones TF-IDF. BETO no se ejecutó.**

Mismos parámetros, textos, cinco folds purgados y 793 etiquetas IA de validación. Solo tres etiquetas de train cambian: R01 N→H, R03 D→N y R12 D→H. Seis adjudicaciones se aplican en una vista experimental; tres ya coincidían con IA. Originales y relevancia IA intactos.

| Condición | F1 H/D medio | Macro-F1 medio | Errores | Recall H | Recall D |
|---|---:|---:|---:|---:|---:|
| original | 0.691477 | 0.783501 | 60 | 0.782609 | 0.734694 |
| adjudicada | 0.648822 | 0.754311 | 66 | 0.797101 | 0.612245 |

- Delta F1 H/D medio: **-0.042656**; mejora en 1/5 folds.
- 9 predicciones finales distintas; 1 errores corregidos y 7 nuevos, respecto de la misma referencia IA.
- La condición original reproduce exactamente A, B y salida final de B0 limpia del experimento 26. La puerta A y vocabularios no cambian entre condiciones.

## Interpretación y cierre

Esto aísla el efecto de tres etiquetas, no una mejora de comprensión del lenguaje. Las adjudicaciones no se revierten por bajar un score contra IA; tampoco se extrapolan al corpus. La validación ya se utilizó en desarrollo y puede contener etiquetas discutibles. No es test nuevo ni confirmación humana.

No se ajustaron n-gramas/C/umbrales ni se seleccionó otra variante tras medir. Se conserva la referencia adjudicada para comparar BETO con exactamente la misma supervisión cuando sus pesos sean accesibles. El modelo histórico no se reemplazó; estos ajustes por fold son efímeros, sin refit final o scoring general.

## BETO y textos largos

El acceso a config/API de Hugging Face volvió a fallar con TLS EOF y no hay GPU detectada. No hay resultados de BETO ni bibliotecas/pesos grandes descargados. El protocolo fija cobertura completa por segmentos, agregación por intervención y un ensayo sin búsqueda de hiperparámetros; ese runner todavía no está implementado ni validado con pesos reales. No confundir el diseño con una ejecución.

## Reproducir

```bash
python scripts/31_evaluar_adjudicacion.py --preparar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/31_evaluar_adjudicacion.py --ejecutar --salida /ruta/nueva --informe /ruta/informe_nuevo.md
```

[Protocolo previo](PROTOCOLO_MODELO_ADJUDICADO_V1.md) · [Aceptación humana asistida](ADJUDICACION_SEIS_DISCREPANCIAS_30_V1.md).

Las nueve pruebas de recepción anteriores no son las pruebas de este entrenamiento. La verificación/reproducción de esta unidad se registra en su propio `reproducibilidad.json`. No se abre el libro de 306 respuestas.
