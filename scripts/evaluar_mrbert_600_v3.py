"""Fine-tuning agrupado de MrBERT-es con 600 humanas v3; diseñado para Colab GPU."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from entrenar_tfidf_supervision_v3 import RAIZ, cargar_datos, clave_texto, metricas_completas, sha256
from evaluar_ampliacion_ia89_v3 import cargar_nuevos
from reestimar_c_wc_con_300_v3 import audited_extra, load_300
from reestimar_c_wc_con_600_v3 import SECOND_PATH, load_second

MODEL_ID = "BSC-LT/MrBERT-es"
MODEL_REVISION = "34a7cc86e0d0a2b77e802d07a189db1c0ef2e7d4"
LABELS = ["hawkish", "dovish", "neutral"]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
SEED = 20260917
MAX_LENGTH = 1024
EPOCHS = 2


def save_json(path, obj): path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def head_tail(tokenizer, text, max_length=MAX_LENGTH):
    ids = tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"]
    room = max_length - tokenizer.num_special_tokens_to_add(pair=False)
    if len(ids) > room:
        head = room // 3; ids = ids[:head] + ids[-(room - head):]
    return tokenizer.prepare_for_model(ids, add_special_tokens=True, max_length=max_length, truncation=True,
                                       padding="max_length", return_attention_mask=True)


def run(out, folds):
    import torch
    from torch import nn
    from torch.utils.data import Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments, set_seed

    if not torch.cuda.is_available(): raise RuntimeError("MrBERT requiere runtime GPU en Colab")
    out = Path(out); out.mkdir(parents=True, exist_ok=True); fold_dir = out / "folds"; fold_dir.mkdir(exist_ok=True)
    base, _, base_sources = cargar_datos(); ia89, ia_sources = cargar_nuevos(); first, second = load_300(), load_second()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)

    class TextDataset(Dataset):
        def __init__(self, frame):
            self.items = [head_tail(tokenizer, text) for text in frame.texto]
            self.labels = [LABEL2ID[x] for x in frame.etiqueta_v3]
        def __len__(self): return len(self.labels)
        def __getitem__(self, index): return {**{k: torch.tensor(v) for k, v in self.items[index].items()}, "labels": torch.tensor(self.labels[index])}

    class WeightedTrainer(Trainer):
        def __init__(self, *args, class_weights=None, **kwargs): super().__init__(*args, **kwargs); self.class_weights = class_weights
        def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
            labels = inputs.pop("labels"); outputs = model(**inputs); loss = nn.CrossEntropyLoss(weight=self.class_weights.to(outputs.logits.device))(outputs.logits, labels)
            return (loss, outputs) if return_outputs else loss

    protocol = {"modelo": MODEL_ID, "revision_huggingface": MODEL_REVISION, "arquitectura": "ModernBERT clasificación directa H/D/N",
        "periodo": "2005-2015", "folds": folds, "max_length": MAX_LENGTH, "truncamiento": "primer tercio + últimos dos tercios",
        "epochs": EPOCHS, "learning_rate": 2e-5, "batch_train": 2, "gradient_accumulation": 8, "weight_decay": .01,
        "class_weights": "inversa de raíz de frecuencia, recalculada solo en outer train", "seed_base": SEED,
        "purga": "reunión y texto para IA89 y ambas tandas humanas; texto para train histórico", "predictores_excluidos": "citas, fundamentos, confianza, estratos y metadatos de adjudicación",
        "evaluacion_independiente": False, "fuentes_sha256": {**{k: sha256(v) for k, v in base_sources.items()}, **{k: sha256(v) for k, v in ia_sources.items()},
            "primera300": sha256(RAIZ / "data/evaluacion/anotacion_adicional_300_v3_cerrada_v1/referencia_300_v3.csv"), "segunda300": sha256(SECOND_PATH), "script": sha256(Path(__file__))}}
    save_json(out / "protocolo.json", protocol)
    audits = []
    for fold in folds:
        target = fold_dir / f"predicciones_fold_{fold}.csv"
        if target.exists():
            print(f"Fold {fold}: ya existe; se conserva para reanudación", flush=True); continue
        set_seed(SEED + fold)
        val = base[base.fold_validacion.eq(fold)].copy(); keys = set(val.texto.map(clave_texto))
        train = base[~base.fold_validacion.eq(fold) & ~base.texto.map(clave_texto).isin(keys)].copy()
        extras = [audited_extra(data, val, fold, origin) for data, origin in ((ia89, "ia89"), (first, "humana300_primera"), (second, "humana300_dirigida"))]
        audits.extend(extras)
        audit_fold = pd.concat(extras, ignore_index=True)
        audit_fold[["fold", "origen", "intervencion_id", "meeting_id", "etiqueta_v3", "excluir_reunion", "excluir_texto", "incluido"]].to_csv(
            fold_dir / f"inclusion_fold_{fold}.csv", index=False, lineterminator="\n")
        for extra in extras: train = pd.concat([train, extra[extra.incluido].reindex(columns=train.columns)], ignore_index=True)
        if set(train.meeting_id) & set(val.meeting_id) or set(train.texto.map(clave_texto)) & keys: raise ValueError(f"Contaminación fold {fold}")
        counts = train.etiqueta_v3.value_counts(); weights = torch.tensor([1 / np.sqrt(counts[label]) for label in LABELS], dtype=torch.float32); weights /= weights.mean()
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, revision=MODEL_REVISION, num_labels=3,
            id2label={i: label for i, label in enumerate(LABELS)}, label2id=LABEL2ID)
        args = TrainingArguments(output_dir=str(out / f"tmp_fold_{fold}"), num_train_epochs=EPOCHS, learning_rate=2e-5,
            per_device_train_batch_size=2, per_device_eval_batch_size=4, gradient_accumulation_steps=8, warmup_ratio=.1,
            weight_decay=.01, lr_scheduler_type="linear", logging_steps=25, save_strategy="no", report_to="none", fp16=True,
            seed=SEED + fold, data_seed=SEED + fold, remove_unused_columns=False)
        trainer = WeightedTrainer(model=model, args=args, train_dataset=TextDataset(train), processing_class=tokenizer, class_weights=weights)
        trainer.train(); prediction = trainer.predict(TextDataset(val)); pred = np.argmax(prediction.predictions, axis=1)
        pd.DataFrame({"intervencion_id": val.intervencion_id, "meeting_id": val.meeting_id, "fold": fold,
            "etiqueta_v3": val.etiqueta_v3, "pred_mrbert": [LABELS[i] for i in pred],
            **{f"logit_{label}": prediction.predictions[:, i] for i, label in enumerate(LABELS)}}).to_csv(target, index=False, lineterminator="\n")
        save_json(fold_dir / f"ejecucion_fold_{fold}.json", {"n_train": len(train), "n_validacion": len(val), "train_por_clase": counts.to_dict(), "class_weights": dict(zip(LABELS, weights.tolist())), "seed": SEED + fold})
        del trainer, model; torch.cuda.empty_cache(); print(f"Fold {fold}: terminado", flush=True)
    completed = sorted(fold_dir.glob("predicciones_fold_*.csv"))
    if len(completed) == 5:
        table = pd.concat([pd.read_csv(path, dtype={"intervencion_id": str, "meeting_id": str}) for path in completed], ignore_index=True).sort_values(["fold", "intervencion_id"])
        if len(table) != 793 or table.intervencion_id.nunique() != 793: raise ValueError("Predicciones incompletas")
        table.to_csv(out / "predicciones.csv", index=False, lineterminator="\n"); metrics = metricas_completas(table.rename(columns={"pred_mrbert": "pred"}), "pred")
        save_json(out / "metricas.json", {"mrbert_600": metrics, "evaluacion_independiente": False, "modelo_adoptado": False})
        save_json(out / "entorno.json", {"python": platform.python_version(), "torch": torch.__version__, "transformers": __import__("transformers").__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)})
        outputs = ["protocolo.json", "predicciones.csv", "metricas.json", "entorno.json"] + [str(p.relative_to(out)) for p in sorted(fold_dir.glob("*"))]
        save_json(out / "manifest.json", {"sha256_salidas": {name: sha256(out / name) for name in outputs}})
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    else: print(f"Completados {len(completed)}/5 folds; vuelve a ejecutar para reanudar.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--salida", type=Path, required=True); parser.add_argument("--folds", default="1,2,3,4,5")
    args = parser.parse_args(); run(args.salida, [int(x) for x in args.folds.split(",")])
