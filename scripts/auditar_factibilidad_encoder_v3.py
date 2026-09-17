"""Registra de forma reproducible la factibilidad local de la ronda de encoder contextual."""
import hashlib
import importlib.util
import json
import os
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/evaluacion/encoder_contextual_factibilidad_v3_v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(out=OUT):
    out = Path(out)
    if out.exists():
        raise FileExistsError("No sobrescribir auditoría")
    cache = Path.home() / ".cache/huggingface/hub"
    weights = list(cache.glob("models--*/*/snapshots/**/*model*")) if cache.exists() else []
    result = {
        "cpu_logicas": os.cpu_count(), "ram_total_gib": round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30, 3),
        "backend_torch": importlib.util.find_spec("torch") is not None,
        "backend_tensorflow": importlib.util.find_spec("tensorflow") is not None,
        "backend_flax": importlib.util.find_spec("flax") is not None,
        "transformers_instalado": importlib.util.find_spec("transformers") is not None,
        "pesos_encoder_locales": len(weights), "gpu_visible": bool(os.environ.get("CUDA_VISIBLE_DEVICES")),
        "decision": "no_ejecutar_finetuning_contextual_en_este_entorno",
        "motivos": ["sin backend tensorial", "sin pesos locales", "2 CPU y menos de 4 GiB RAM para CV externa agrupada de cinco folds"],
        "modelo_descargado": False, "etiquetas_validacion_consultadas": False,
    }
    out.mkdir(parents=True)
    result_path = out / "resumen.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    protocol = {"ronda": "encoder contextual español", "modelo_previsto": "BETO u otro encoder español reproducible",
                "condicion_reanudacion": "backend, pesos versionados y cómputo suficiente para cinco outer folds con selección solo interna",
                "python": platform.python_version(), "script_sha256": sha(Path(__file__))}
    protocol_path = out / "protocolo.json"
    protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps({"sha256_salidas": {
        result_path.name: sha(result_path), protocol_path.name: sha(protocol_path)}}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
