# Revisión v3 — piloto r1

**Fecha:** 17-09-2026  
**Archivo:** `data/etiquetas/etiquetas_piloto_r1.csv`  
**Alcance:** 110/110 intervenciones, incluidas H, D, N y relevancia.

## Resultado frente a v2 vigente

| Resultado | Casos |
|---|---:|
| Compatibles | 107 |
| Cambios de etiqueta | **3** |
| Cambios de relevancia | 0 |
| Pendientes | 0 |

Transiciones:

| ID | V2 | V3 | Fundamento resumido |
|---|---|---|---|
| RPM-2006-09-07:873:1 | D | **H** | Mantiene hoy, pero declara necesarios ajustes futuros al alza, aunque más distantes. Una pausa más larga no es D relativa. |
| RPM-2008-02-07:1672:1 | D | **N** | Mantiene y suprime todo sesgo. Ser menos restrictivo que el mensaje anterior no equivale a respaldar una baja o sesgo expansivo. |
| RPM-2008-11-13:2167:3 | D | **N** | Concuerda con mantener y solo pide incluir el recorte entre las opciones. Presentar una opción no es hacerla propia. |

Distribución:

| Versión | H | D | N |
|---|---:|---:|---:|
| V2 vigente | 6 | 6 | 98 |
| V3 | 7 | 3 | 100 |

## Revisión de N y relevancia

Se revisaron los 98 N. Las unidades con trayectorias de tasa del escenario base, expectativas de mercado, exposición del staff, preguntas o metodología no se convirtieron en H/D cuando el actor no adoptó esa dirección. Las mantenciones que descartan ambas direcciones permanecen N.

Los 24 N con relevancia0 son formalidades, ofrecimientos de palabra, encabezados o trámites sin contenido direccional evaluable. No se detectó en este lote un caso comparable a 1739:1 de las rondas prioritarias que obligara a elevar relevancia.

## Evidencia y límites

La tabla completa está en `data/auditoria/revision_etiquetas_piloto_r1_v3/revision.csv`, con v2/v3, cita, fundamento, confianza y hash. Se cotejaron 110 IDs, citas/vacíos permitidos y hashes contra L0. Las etiquetas eran visibles y la revisión fue del agente; no constituye segunda anotación humana ciega.

El lote queda cerrado con cero pendientes. El avance acumulado es 187/1.747 y quedan 1.560 IDs. No se entrenó ni se sobrescribió v2.
