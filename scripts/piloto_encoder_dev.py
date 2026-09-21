"""Piloto encoder vs. lineal en desarrollo agrupado (NO abre la evaluación ciega).

Propósito: ejecutar en máquina con GPU el paso 3 de la hoja de ruta — la
comparación pareada encoder vs. arquitectura lineal formal bajo el mismo
protocolo de validación. Este sandbox no tiene acceso a HuggingFace/PyTorch;
el script se entrega preparado para correr donde exista GPU.

Requisitos (NO están en requirements.txt del repo):
    pip install torch transformers accelerate

Protocolo:
1. Mismo split agrupado por reunión que `estabilidad_lineal.py`
   (GroupShuffleSplit, 20 % de reuniones en prueba, semilla 20260915).
2. Encoder BETO (`dccuchile/bert-base-spanish-wwm-uncased`) en dos etapas que
   espejan el sistema formal: A relevancia (binaria) y B H/D/N entre
   relevantes; etiqueta final A=0 -> neutral, si no B.
3. SEEDS = 5 semillas; se reporta media ± desviación por modelo y la
   distribución bootstrap PAREADA (mismo test, remuestreo de reuniones) del
   Δmacro-F1 encoder − lineal por semilla. El titular se escribe contra estos
   intervalos, no contra medias sueltas.
4. Tuning simétrico: por defecto hiperparámetros fijos y razonables; para la
   corrida del paper usar --grid, que selecciona lr/épocas con GroupKFold(3)
   interno SOLO sobre la parte de entrenamiento, al mismo nivel de esfuerzo
   que el tuning del lineal.
5. La evaluación ciega permanece cerrada: el script se niega a tocarla salvo
   que se invoque con --abrir-ciega, flag pensado como extensión prospectiva
   documentada que decide la persona investigadora, no un ajuste más.

Uso:
    python scripts/piloto_encoder_dev.py --epocas 4            # piloto
    python scripts/piloto_encoder_dev.py --grid --semillas 5   # corrida paper
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import FeatureUnion

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data/entrenamiento_wc600.csv"
CIEGA_PRED = ROOT / "data/predicciones_evaluacion_ciega.csv"
SALIDA = ROOT / "resultados/robustez_supervisada/piloto_encoder_dev.json"
SEMILLA_SPLIT = 20260915
SEMILLAS_ENCODER = [20260915 + k for k in range(5)]
ORDEN = ("hawkish", "dovish", "neutral")
MODELO_ENCODER = "dccuchile/bert-base-spanish-wwm-uncased"

WORD_A = {"strip_accents": "unicode", "lowercase": True, "ngram_range": (1, 1), "min_df": 3, "max_df": 0.9, "sublinear_tf": True}
WORD_B = {**WORD_A, "ngram_range": (1, 4)}
CHAR = {"analyzer": "char_wb", "ngram_range": (3, 5), "min_df": 3, "max_df": 0.98, "sublinear_tf": True, "strip_accents": "unicode", "lowercase": True, "max_features": 120000}
LR = {"class_weight": "balanced", "C": 2.0, "max_iter": 2000, "random_state": SEMILLA_SPLIT}

# --- infraestructura sklearn del brazo lineal (idéntica a estabilidad_lineal) ---


def _vectorizer(words, weight=1.0):
    return FeatureUnion([("word", TfidfVectorizer(**words)), ("char", TfidfVectorizer(**CHAR))], transformer_weights={"word": 1.0, "char": weight}, n_jobs=1)


def ajustar_lineal(train):
    va = _vectorizer(WORD_A)
    ma = LogisticRegression(**LR).fit(va.fit_transform(train.texto), train.relevancia_v3.astype(int))
    relevantes = train.relevancia_v3.eq("1")
    vb = _vectorizer(WORD_B)
    mb = LogisticRegression(**LR).fit(vb.fit_transform(train.loc[relevantes, "texto"]), train.loc[relevantes, "etiqueta_v3"])
    return va, ma, vb, mb


def etiqueta_lineal(va, ma, vb, mb, textos):
    relevancia = ma.predict(va.transform(textos)).astype(int)
    return np.where(relevancia == 0, "neutral", mb.predict(vb.transform(textos)))


# --- brazo encoder ---


def entrenar_etapa(textos, etiquetas, ids_reunion, semilla, lr, epocas, batch, max_len, num_labels):
    import torch
    from torch.utils.data import DataLoader, Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    rng = random.Random(semilla)
    torch.manual_seed(semilla)
    np.random.seed(semilla % (2**32))

    tokenizer = AutoTokenizer.from_pretrained(MODELO_ENCODER)

    class Conjunto(Dataset):
        def __len__(self):
            return len(textos)

        def __getitem__(self, i):
            return textos[i], etiquetas[i]

    def colate(lote):
        t = [x[0] for x in lote]
        y = [x[1] for x in lote]
        enc = tokenizer(t, truncation=True, max_length=max_len, padding=True, return_tensors="pt")
        enc["labels"] = torch.tensor(y)
        return enc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    modelo = AutoModelForSequenceClassification.from_pretrained(MODELO_ENCODER, num_labels=num_labels).to(device)
    # pesos de clase balanceados, espejo de class_weight="balanced"
    conteo = np.bincount(etiquetas, minlength=num_labels)
    pesos = len(etiquetas) / (num_labels * np.maximum(conteo, 1))
    pesos = torch.tensor(pesos, dtype=torch.float, device=device)
    perdida = torch.nn.CrossEntropyLoss(weight=pesos)
    optim = torch.optim.AdamW(modelo.parameters(), lr=lr, weight_decay=0.01)
    generador = torch.Generator().manual_seed(semilla)
    loader = DataLoader(Conjunto(), batch_size=batch, shuffle=True, collate_fn=colate, generator=generador)
    scheduler = get_linear_schedule_with_warmup(optim, 0, len(loader) * epocas)

    modelo.train()
    for _ in range(epocas):
        for lote in loader:
            lote = {k: v.to(device) for k, v in lote.items()}
            optim.zero_grad()
            salida = modelo(**lote)
            perdida(salida.logits, lote["labels"]).backward()
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
            optim.step()
            scheduler.step()

    def predecir(textos_nuevos, batch_inf=32):
        modelo.eval()
        out = []
        with torch.no_grad():
            for i in range(0, len(textos_nuevos), batch_inf):
                enc = tokenizer(textos_nuevos[i : i + batch_inf], truncation=True, max_length=max_len, padding=True, return_tensors="pt").to(device)
                out.append(modelo(**enc).logits.argmax(-1).cpu().numpy())
        return np.concatenate(out)

    return predecir


def etiqueta_encoder(train, eval_textos, semilla, lr, epocas, batch, max_len):
    mapa_b = {"hawkish": 0, "dovish": 1, "neutral": 2}
    rel_train = train.relevancia_v3.astype(int).to_numpy()
    predecir_a = entrenar_etapa(train.texto.tolist(), rel_train.tolist(), None, semilla, lr, epocas, batch, max_len, 2)
    relevancia = predecir_a(eval_textos)
    relevantes = train.relevancia_v3.eq("1")
    predecir_b = entrenar_etapa(
        train.loc[relevantes, "texto"].tolist(),
        [mapa_b[e] for e in train.loc[relevantes, "etiqueta_v3"]],
        None,
        semilla,
        lr,
        epocas,
        batch,
        max_len,
        3,
    )
    dura_b = [list(mapa_b)[p] for p in predecir_b(eval_textos)]
    return np.where(relevancia == 0, "neutral", dura_b)


# --- métricas y bootstrap pareado (idénticas a las del repo) ---


def metricas(y_true, y_pred):
    f1, recalls = {}, {}
    for c in ORDEN:
        vp = int(np.sum((y_true == c) & (y_pred == c)))
        fp = int(np.sum((y_true != c) & (y_pred == c)))
        fn = int(np.sum((y_true == c) & (y_pred != c)))
        prec = vp / (vp + fp) if vp + fp else np.nan
        rec = vp / (vp + fn) if vp + fn else np.nan
        f1[c] = 0.0 if (np.isnan(prec) or np.isnan(rec) or prec + rec == 0) else 2 * prec * rec / (prec + rec)
        recalls[c] = rec
    return {
        "accuracy": float(np.mean(y_true == y_pred)),
        "macro_f1": float(np.mean([f1[c] for c in ORDEN])),
        "f1_hd": float((f1["hawkish"] + f1["dovish"]) / 2),
        "f1_d": f1["dovish"],
        "f1_h": f1["hawkish"],
        "f1_n": f1["neutral"],
        "recall_d": recalls["dovish"],
    }


def bootstrap_pareado(filas, clave_modelo_a, clave_modelo_b, remuestras=10_000, semilla=20260917):
    """Δ = modelo_b − modelo_a, remuestreando reuniones completas."""
    rng = random.Random(semilla)
    reuniones = sorted({f["meeting"] for f in filas})
    por_reunion = defaultdict(list)
    for f in filas:
        por_reunion[f["meeting"]].append(f)
    deltas = defaultdict(list)
    for _ in range(remuestras):
        muestra = [f for m in rng.choices(reuniones, k=len(reuniones)) for f in por_reunion[m]]
        y = np.array([f["y"] for f in muestra])
        a = metricas(y, np.array([f[clave_modelo_a] for f in muestra]))
        b = metricas(y, np.array([f[clave_modelo_b] for f in muestra]))
        for k in ("macro_f1", "f1_hd", "f1_d"):
            deltas[k].append(b[k] - a[k])

    def pct(xs, q):
        xs = sorted(xs)
        i = (len(xs) - 1) * q / 100
        lo, hi = math.floor(i), math.ceil(i)
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)

    return {
        k: {"ic95": [pct(v, 2.5), pct(v, 97.5)], "mediana": pct(v, 50), "p_mayor_que_cero": sum(1 for x in v if x > 0) / len(v)}
        for k, v in deltas.items()
    }


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epocas", type=int, default=4)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--semillas", type=int, default=5)
    ap.add_argument("--grid", action="store_true", help="selección interna lr/épocas con GroupKFold(3) sobre el train")
    ap.add_argument("--remuestras", type=int, default=10_000)
    ap.add_argument("--abrir-ciega", action="store_true", help="EXTENSIÓN PROSPECTIVA: ejecuta también sobre las 300 ciegas. Decisión documentada de la persona investigadora.")
    args = ap.parse_args()

    import torch  # validación temprana

    data = pd.read_csv(TRAIN, dtype=str, keep_default_na=False)
    tr_idx, te_idx = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEMILLA_SPLIT).split(data, groups=data.meeting_id))
    train, test = data.iloc[tr_idx], data.iloc[te_idx]
    y_test = test.etiqueta_v3.to_numpy()
    print(f"Split agrupado semilla {SEMILLA_SPLIT}: train {len(train)} filas / {train.meeting_id.nunique()} reuniones; "
          f"test {len(test)} filas / {test.meeting_id.nunique()} reuniones "
          f"(D test = {int((y_test == 'dovish').sum())})")

    # brazo lineal en el MISMO split (pareado)
    va, ma, vb, mb = ajustar_lineal(train)
    pred_lineal = etiqueta_lineal(va, ma, vb, mb, test.texto)
    filas = [{"meeting": m, "y": y, "lineal": p} for m, y, p in zip(test.meeting_id, y_test, pred_lineal)]
    met_lineal = metricas(y_test, pred_lineal)
    print(f"lineal   : macro={met_lineal['macro_f1']:.4f} f1_hd={met_lineal['f1_hd']:.4f} f1_d={met_lineal['f1_d']:.4f}")

    # grid interno opcional (una semilla, GroupKFold(3) sobre el train)
    hiper = [(args.lr, args.epocas)]
    if args.grid:
        mejor, mejor_puntaje = None, -1
        for lr_g in (2e-5, 3e-5, 5e-5):
            for ep_g in (3, 4):
                puntajes = []
                for tr_g, va_g in GroupKFold(3).split(train, groups=train.meeting_id):
                    sub, val = train.iloc[tr_g], train.iloc[va_g]
                    pred = etiqueta_encoder(sub, val.texto.tolist(), SEMILLAS_ENCODER[0], lr_g, ep_g, args.batch, args.max_len)
                    puntajes.append(metricas(val.etiqueta_v3.to_numpy(), pred)["macro_f1"])
                media = float(np.mean(puntajes))
                print(f"  grid lr={lr_g:.0e} épocas={ep_g}: macro interno {media:.4f}")
                if media > mejor_puntaje:
                    mejor, mejor_puntaje = (lr_g, ep_g), media
        hiper = [mejor]
        print(f"grid seleccionó lr={mejor[0]:.0e}, épocas={mejor[1]}")

    lr_e, ep_e = hiper[0]
    por_semilla = []
    for semilla in SEMILLAS_ENCODER[: args.semillas]:
        pred_enc = etiqueta_encoder(train, test.texto.tolist(), semilla, lr_e, ep_e, args.batch, args.max_len)
        met = metricas(y_test, pred_enc)
        for f, p in zip(filas, pred_enc):
            f[f"encoder_s{semilla}"] = p
        por_semilla.append({"semilla": semilla, **met})
        print(f"encoder s{semilla}: macro={met['macro_f1']:.4f} f1_hd={met['f1_hd']:.4f} f1_d={met['f1_d']:.4f}")

    boots = [bootstrap_pareado(filas, "lineal", f"encoder_s{s}", args.remuestras, 20260917) for s in SEMILLAS_ENCODER[: args.semillas]]
    sintesis_boots = {
        k: {
            "mediana_ic_medianas": float(np.median([b[k]["mediana"] for b in boots])),
            "semillas_ic_excluye_cero": sum(1 for b in boots if not (b[k]["ic95"][0] <= 0 <= b[k]["ic95"][1])),
            "detalle_por_semilla": [{"semilla": s, **boots[i][k]} for i, s in enumerate(SEMILLAS_ENCODER[: args.semillas])],
        }
        for k in boots[0]
    }

    if args.abrir_ciega:
        raise SystemExit("PENDIENTE: la extensión a la ciega se implementa SOLO tras documentar la decisión; este flag existe para dejar registro explícito, no para ejecutarla por accidente.")

    salida = {
        "version": "piloto_encoder_dev_v1",
        "split": {"semilla": SEMILLA_SPLIT, "test_filas": len(test), "test_d": int((y_test == "dovish").sum())},
        "encoder": {"modelo": MODELO_ENCODER, "lr": lr_e, "epocas": ep_e, "batch": args.batch, "max_len": args.max_len, "semillas": SEMILLAS_ENCODER[: args.semillas], "grid_interno": bool(args.grid)},
        "lineal": met_lineal,
        "encoder_por_semilla": por_semilla,
        "encoder_media_desv": {
            k: {"media": float(np.mean([s[k] for s in por_semilla])), "desv": float(np.std([s[k] for s in por_semilla], ddof=1))}
            for k in ("macro_f1", "f1_hd", "f1_d")
        },
        "bootstrap_pareado_delta_encoder_menos_lineal": sintesis_boots,
        "ciega": "no tocada" if not args.abrir_ciega else "flag registrado; ejecución bloqueada hasta documentar decisión",
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nEscrito: {SALIDA}")


if __name__ == "__main__":
    principal()
