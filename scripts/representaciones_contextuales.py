"""Vistas deterministas del híbrido v1: sin etiquetas, aprendizaje ni datos externos."""
# ---- 1. Patrones congelados: candidatos no equivalen a posturas ----
from decimal import Decimal
import re

from sklearn.feature_extraction.text import TfidfVectorizer, strip_accents_unicode

PATRON_CANDIDATO = re.compile(
    r"\b(?:tpm|tasas? de politica|politica monetaria|sesgo\w*|estimul\w*|"
    r"opcion(?:es)?|vot\w*|propon\w*|propong\w*|recomend\w*|normaliz\w*)\b")
PATRON_CORTE = re.compile(r"(?<=[.!?])\s+|\n+")
PATRON_TOKEN = re.compile(r"(?<!\w)[+-](?=\d)|\d+(?:[.,]\d+)?|%|(?u:\b[^\W\d]\w+\b)")
PATRON_AMBIGUO = re.compile(r"\b\d+[.,]\d{3}\b")


# ---- 2. Tokenización: decimal atómico y unidades, no interpretación económica ----
def tokens_numericos(texto):
    tokens = []
    texto = texto.replace('−', '-')
    for coincidencia in PATRON_TOKEN.finditer(texto):
        token = coincidencia.group()
        if token in ('+', '-'):
            anterior = texto[coincidencia.start()-1] if coincidencia.start() else ''
            if not anterior or anterior.isspace() or anterior == '(':
                tokens.append('signo_mas' if token == '+' else 'signo_menos')
        elif token == '%':
            tokens.append('unidad_porcentaje')
        elif token[0].isdigit():
            # Decimal evita redondeo binario; formateo fijo, sin exponentes.
            numero = format(Decimal(token.replace(',', '.')), 'f')
            if '.' in numero:
                numero = numero.rstrip('0').rstrip('.')
            tokens.append('numero_' + numero.replace('.', 'd'))
        else:
            tokens.append(token)
    return tokens


def parametros_numericos(parametros):
    return {**parametros, 'tokenizer': tokens_numericos, 'token_pattern': None}


# ---- 3. Extracción con posiciones del original; no cruza intervenciones ----
def intervalos_oraciones(texto):
    limites = [0] + [m.end() for m in PATRON_CORTE.finditer(texto)] + [len(texto)]
    intervalos = []
    for inicio, fin in zip(limites, limites[1:]):
        while inicio < fin and texto[inicio].isspace():
            inicio += 1
        while fin > inicio and texto[fin-1].isspace():
            fin -= 1
        if inicio < fin:
            intervalos.append((inicio, fin))
    return intervalos


def extraer_ventanas(texto):
    oraciones = intervalos_oraciones(texto)
    indices = set()
    for i, (inicio, fin) in enumerate(oraciones):
        if PATRON_CANDIDATO.search(strip_accents_unicode(texto[inicio:fin].lower())):
            indices.update(range(max(0, i-1), min(len(oraciones), i+2)))
    grupos = []
    for i in sorted(indices):
        if grupos and i == grupos[-1][-1] + 1:
            grupos[-1].append(i)
        else:
            grupos.append([i])
    return [(oraciones[g[0]][0], oraciones[g[-1]][1]) for g in grupos]


class AnalizadorContexto:
    """Genera n-gramas por ventana, sin puentes artificiales entre fragmentos."""
    def __init__(self, numerico=False):
        parametros = dict(strip_accents='unicode', lowercase=True, ngram_range=(1, 4))
        if numerico:
            parametros = parametros_numericos(parametros)
        self.analizar = TfidfVectorizer(**parametros).build_analyzer()

    def __call__(self, texto):
        return [termino for inicio, fin in extraer_ventanas(texto)
                for termino in self.analizar(texto[inicio:fin])]


# ---- 4. Ejemplos inventados, congelados antes de ajustar: no son corpus anotado ----
CASOS_CONDUCTUALES = (
    ('alza', 'accion', 'Propongo subir la TPM en 25 puntos base.', 'hawkish'),
    ('baja', 'accion', 'Propongo bajar la TPM en 25 puntos base.', 'dovish'),
    ('rechazo_baja', 'negacion', 'Rechazo bajar la TPM porque aumentan los riesgos inflacionarios.', 'hawkish'),
    ('objeto', 'objeto', 'Propongo reducir el estímulo monetario mediante un aumento de la TPM.', 'hawkish'),
    ('menu', 'menu', 'Las opciones son subir o mantener la TPM. Se presentan sin expresar preferencia por ninguna.', 'neutral'),
    ('condicional', 'condicion', 'Si persiste la inflación, sería necesario subir la TPM.', 'hawkish'),
    ('contrafactual', 'tiempo', 'Habría apoyado subir la TPM si hubiera aumentado la inflación. Eso no ocurrió y mi opción es bajar la tasa de política monetaria.', 'dovish'),
    ('extranjero', 'atribucion', 'La Fed elevó su tasa. En Chile propongo bajar la TPM en 25 puntos base.', 'dovish'),
    ('decimal_coma', 'numeros', 'Mi opción es reducir la TPM desde 5,25% a 5% anual.', 'dovish'),
    ('decimal_punto', 'numeros', 'Mi opción es reducir la TPM desde 5.25% a 5% anual.', 'dovish'),
    ('nombre_uno', 'nombre', 'Pérez propone subir la TPM en 25 puntos base.', 'hawkish'),
    ('nombre_dos', 'nombre', 'Gómez propone subir la TPM en 25 puntos base.', 'hawkish'),
    ('conclusion', 'longitud', 'Se presentó información descriptiva sobre actividad y empleo. Se revisaron las estadísticas del mes. Mi opción es bajar la TPM en 25 puntos base.', 'dovish'),
    ('mantener_sesgo', 'sesgo', 'Mi opción es mantener la TPM hoy, conservando un sesgo explícito al alza.', 'hawkish'),
)
PARES_INVARIANTES = (('decimal_coma', 'decimal_punto'), ('nombre_uno', 'nombre_dos'),
                     ('baja', 'extranjero'), ('baja', 'conclusion'))
