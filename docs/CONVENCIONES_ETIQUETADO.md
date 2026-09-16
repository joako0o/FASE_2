# Convenciones históricas del entrenamiento IA

## Alcance y procedencia

El codebook v2 permanece congelado en `docs/codebook_v2.md`. Este documento
conserva las convenciones que estaban en generadores redundantes ahora retirados
y resume decisiones registradas en AVANCE durante el entrenamiento. **No es una
nueva versión de codebook ni autoriza reetiquetar respuestas humanas.** Las
anotaciones originales, citas y notas permanecen en los 19 CSV append-only.

El registro de sesiones previo puede consultarse con
`git show 957200f74b61c0527d57c333dd360b3587d0a7e8:docs/AVANCE.md`.
Ese registro contiene cifras y estados obsoletos: no usarlo como estado actual.

## Reglas preservadas literalmente de los scripts retirados

### 13_ronda_tanda09.py (retirado)

Convenciones vigentes (codebook v2 + heredadas de sesiones anteriores):
- Opciones del staff con recomendacion explicita reciben la clase de la opcion
  recomendada (igual que en tandas previas, p.ej. id 214:4); frases tipo
  "dificil justificar otra opcion" = recomendacion (score 0.70-0.80).
- Acuerdo+comunicado con alza = hawkish 0.85-0.95.
- Voto/pausa explicita dentro de un ciclo de alzas con opcion de alza viva
  = dovish (contra la corriente de fase), 0.65-0.75.
- Mantencion de TPM reafirmando "ajustes pausados" pendientes = hawkish media
  (convencion sesion 8c).
- Voto "mantener" cuando el staff ofrecia {disminuir, mantener} sin
  recomendacion = neutral con nota.
- Tramite (solicitar opciones, aprobar comunicado, levantar sesion) = flag 0.

### 14_ronda_tanda10.py (retirado)

Convenciones heredadas vigentes ademas de las de r13:
- "Vota mantener" cuando el staff ofrecia {disminuir 25, mantener} y el sesgo
  previo era a la baja = hawkish relativo (contra la corriente de la fase),
  p.ej. enero-2007 y abril-2007 (mirrores de la regla de pausas en alzas).
- Mantener descartando explicitamente ambas direcciones = neutral pura.
- Acuerdo+comunicado con alza y reafirmacion de alzas futuras = hawkish 0.95.

## Síntesis de decisiones ya registradas en las sesiones 8–12

- Diagnóstico, expectativas de terceros y menú de opciones sin recomendación:
  neutral. "El mercado espera unánimemente una mantención" no es postura propia.
- Recomendación explícita del staff: clasificar su dirección; no volverla neutral
  por el cargo de quien habla. "Difícil justificar otra opción" puede constituir
  recomendación (rondas enriquecidas).
- Mantención con sesgo explícito: evaluar el sesgo declarado; reafirmar un retiro
  pausado pendiente se usó como hawkish, retirar el sesgo al alza como dovish.
- Pausa dentro de un ciclo de alzas: se usó dovish relativo. Mantener descartando
  ambas direcciones, o como única opción relevante sin sesgo: neutral.
- Votos explícitos de alza o recorte tienen señal direccional aun cuando su
  magnitud difiere del acuerdo mayoritario. La intensidad queda en probabilidades
  y nota, no en una clase adicional.
- Fórmulas de ofrecimiento de palabra, suspensión y cierre: neutral, relevancia 0,
  nota obligatoria. El resto del diagnóstico económico puede seguir siendo
  relevante 1 aunque su etiqueta de postura sea neutral.
- Las citas son fragmentos contiguos, hasta 300 caracteres, con OCR y palabras
  intactas; solo se normalizan espacios. Se corrigieron citas IA con elipsis
  antes de congelar el training actual.

## Ambigüedades pendientes de adjudicación independiente

Las convenciones relativas al menú de opciones requieren contexto, pero el
instrumento evalúa cada intervención autónomamente. También puede entrar en
tensión "mantener contra recorte = hawkish relativo" con un sesgo explícito a la
baja. No resolver esta tensión mirando etiquetas del gold y luego presentar ese
mismo gold como un test final intacto. Registrar el criterio prospectivamente y,
si cambia, crear nueva versión y evaluación independiente.

Otros casos pendientes del registro histórico: eufemismo "ajustes" en comunicados,
retórica acomodaticia sin pedir cambios, acuerdos por referencia a otras voces y
votos sin justificación suficiente. El test-retest de 30 IDs sigue sin una segunda
anotación documentada. No se afirma estabilidad de 90 % ya lograda.

## Linaje de las dos muestras enriquecidas

`estrato_enriquecido.csv` no es basura: originó 77 etiquetas (41 + 36) que siguen
siendo parte del training. Su selección de 252 filas se conserva para documentar
el diseño y reproducirlo con exclusiones históricas; no se debe tratar todo su
remanente como un nuevo holdout. `estrato_tanda9.csv` originó otras 250 etiquetas.
El auditor reconstruye ambas selecciones en temporales y comprueba cada ronda.
