#!/usr/bin/env python3
from __future__ import annotations
import json, os
from pathlib import Path
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY","1"); os.environ.setdefault("DO_NOT_TRACK","1")
from huggingface_hub import snapshot_download, hf_hub_download
from motionforge.config.settings import BASE_MODEL_REPO, MOTION_REPO, MOTION_FILE, base_model_dir, motion_model_path, models_dir, MODEL_APPROX_GB
from motionforge.system.diagnostics import model_files_available

BASE_PATTERNS=[
 "model_index.json","scheduler/*","tokenizer/*",
 "text_encoder/config.json","text_encoder/model.fp16.safetensors",
 "unet/config.json","unet/diffusion_pytorch_model.fp16.safetensors",
 "vae/config.json","vae/diffusion_pytorch_model.fp16.safetensors",
]
def main():
    print(f"Model: AnimateDiff-Lightning 2-step + Stable Diffusion 1.5\nApproximate download: {MODEL_APPROX_GB:.1f} GB\nDestination: {models_dir()}")
    base_model_dir().mkdir(parents=True,exist_ok=True)
    motion_model_path().parent.mkdir(parents=True,exist_ok=True)
    snapshot_download(BASE_MODEL_REPO, local_dir=str(base_model_dir()), allow_patterns=BASE_PATTERNS)
    hf_hub_download(MOTION_REPO, filename=MOTION_FILE, local_dir=str(motion_model_path().parent))
    for repo,filename,dest in [
      (BASE_MODEL_REPO,"README.md",models_dir()/"sd15_MODEL_CARD.md"),
      (MOTION_REPO,"LICENSE.md",models_dir()/"animatediff_LICENSE.md"),
    ]:
        try:
            p=hf_hub_download(repo,filename=filename,local_dir=str(models_dir()/"_docs"))
            dest.write_text(Path(p).read_text(encoding="utf-8"),encoding="utf-8")
        except Exception: pass
    manifest={"base_repo":BASE_MODEL_REPO,"motion_repo":MOTION_REPO,"motion_file":MOTION_FILE,"approx_size_gb":MODEL_APPROX_GB}
    (models_dir()/"model_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    if not model_files_available(): raise SystemExit("Downloaded files failed validation")
    print("Model files validated. No Hugging Face token was used.")
if __name__=="__main__": main()
