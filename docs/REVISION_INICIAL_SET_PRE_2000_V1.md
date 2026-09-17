# Revisión inicial de `Set_Entrenamiento_Pre_2000.xlsx`

**Fecha:** 17-09-2026  
**Origen revisado:** archivo preparado por el investigador en `main`, copiado sin cambios a esta rama.  
**SHA-256:** `662ec786e234a8bd8824214c81cf8139ad0955a8f139a596ba9bbf18859ad3fb`.

## Conclusión

El set es un avance valioso: contiene texto completo, etiqueta, confianza, relevancia, tipo de acción, instrumento, nota y cita para **257 fragmentos únicos de 1995–1999**. Sin embargo, **todavía no debe mezclarse con el control v3 ni usarse para entrenar**. Requiere una revisión v3 propia porque conserva varias convenciones incompatibles con dirección monetaria doméstica respaldada y tiene incidencias estructurales que afectarían trazabilidad y particiones.

## Inventario

| Campo | Resultado |
|---|---:|
| Filas / IDs únicos | 257 / 257 |
| Textos normalizados únicos | 253 |
| Etiquetas | H27 / D39 / N185 / pendiente6 |
| Relevancia | 157 sí / 100 no |
| Confianza | 193 alta / 64 media |
| Años | 1995:42; 1996:28; 1997:23; 1998:38; 1999:126 |
| Campos obligatorios vacíos | 0 |

La auditoría reproducible está en `data/auditoria/set_pre2000_revision_inicial_v1/` y se ejecuta con `scripts/auditar_set_pre2000.py`.

## Bloqueos estructurales

1. **`pendiente` aparece como cuarta etiqueta en seis filas:** `31972`, `22077`, `32181`, `33268`, `30995` y `31991`. En v3, pendiente es `estado_revision`; la etiqueta debe quedar vacía hasta resolver o ser H/D/N.
2. **Ocho citas no son literales continuas:** `31033`, `31327`, `31333`, `32531`, `32572`, `32795`, `33249` y `31430`. En general fueron truncadas introduciendo `...`, algo que v3 prohíbe aunque la parte inicial provenga del texto.
3. **Cuatro pares tienen texto normalizado idéntico:** `33306/33311`, `25337/25826`, `32311/32315` y `33307/33312`. Deben compartir grupo de partición; los dos últimos IDs D duplican el mismo texto y no aportan observaciones independientes.
4. **Falta identidad suficiente para entrenar con control de contaminación:** el archivo no incluye ID de acta/reunión, actor, offsets o ID de unidad fuente, procedencia de anotación, versión de codebook, estado separado ni hash por texto. La fecha ayuda, pero no reemplaza la trazabilidad al documento y unidad original.
5. Algunos fragmentos declaran `[unidad_trunca]` en la nota. Antes de entrenar debe confirmarse que `texto_original` sea la unidad íntegra o registrar sus offsets y el criterio de segmentación.

## Incompatibilidades semánticas detectadas en el control prioritario

La lectura inicial de las 66 etiquetas H/D, los seis pendientes y candidatos N muestra que no es suficiente reparar el formato. Entre los casos que deben corregirse o adjudicarse están:

- `33261` H: recomienda un alza de la **Fed**, no una dirección monetaria doméstica chilena; corresponde N bajo el objetivo v3.
- `33546` H: diagnóstico de expectativas inflacionarias y recomendación fiscal, sin respuesta monetaria propia; candidato N.
- `31369` D: presenta mantener o relajar sin resolver la opción; el menú por sí solo no determina D.
- `31398` y `31427` D: conectan debilidad con la necesidad de “actuar/reaccionar”, pero no identifican una dirección monetaria; candidatos N.
- `33267` D: cuestiona expectativas de mercado mediante preguntas y condicionales, sin adoptar una dirección propia; candidato N.
- `21910` D y `32795` H: relatos de medidas pasadas; la historia no equivale automáticamente a respaldo actual.
- `33524` D: justificación retrospectiva de una meta de inflación, sin acción o sesgo actual; candidato N.
- `21646`, `29596` y `30714` H: fijan niveles de facilidades, pero la unidad no aporta por sí sola el nivel anterior necesario para inferir alza. No se puede asignar H por nivel absoluto.
- `22418` D: el efecto monetario de cambiar `60%` por `30%` no está demostrado en la unidad y la nota infiere que amplía acceso; requiere norma previa y función documentada.
- `32872` H y `32888` D: suspensión prudencial de una facilidad y rebaja de encaje a influjos de capital no se convierten automáticamente en postura monetaria agregada por los verbos restringir/rebajar.
- `21646` contrasta además con `21715`: este último sí puede compararse con el 5,20% anterior, pero esa evidencia está en otra unidad. Si se usa contexto externo debe incorporarse uniformemente y registrarse, no heredarse de forma ad hoc.

También hay casos correctamente encaminados: decisiones explícitas de alza/baja de la tasa de instancia, acuerdos institucionales, sesgos futuros propios y defensa sustantiva de una instancia expansiva o restrictiva. La observación anterior no invalida el set completo ni estima su precisión; demuestra que necesita adjudicación exhaustiva antes de incorporarlo.

## Tratamiento acordado en el protocolo v3

- Mantener el XLSX original intacto.
- Excluir sus 257 filas del control primario de 1.352 IDs y de la ampliación IA de 89.
- Crear, en una etapa aparte, una capa `pre_2000_v3` con estado, etiqueta anterior/v3, relevancia, cita reparada, fundamento, confianza, hash, procedencia y agrupación por acta/texto.
- Revisar primero las 66 H/D, los seis pendientes, los ocho problemas de cita, los duplicados y los N relevantes con lenguaje direccional.
- Solo después evaluar su aporte como ampliación temporal separada. No usar 1995–1999 como validación independiente si se revisa asistidamente en esta misma etapa.

No se corrigió ni sobrescribió ninguna celda del XLSX y no se ejecutó entrenamiento.
