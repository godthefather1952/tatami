#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$ROOT"; export MOTIONFORGE_ROOT="$ROOT" HF_HUB_DISABLE_TELEMETRY=1 DO_NOT_TRACK=1
if [[ ! -d .venv ]]; then echo "MotionForge has not been installed."; echo; echo "Run:"; echo "./install.sh"; exit 1; fi
source .venv/bin/activate
python - <<'PY'
import torch,gradio,diffusers,transformers
from motionforge.system.diagnostics import model_files_available
if not model_files_available(): raise SystemExit("MotionForge model files are missing. Run ./install.sh")
from motionforge.system.hardware import detect_hardware
from motionforge.system.environment import environment_name
from motionforge.system.backend import resource_tier
from motionforge.config.settings import MODEL_DISPLAY_NAME
h=detect_hardware()
print("=====================================")
print("          MOTIONFORGE v0.1.0")
print("=====================================")
print(f"\nEnvironment:\n{environment_name()}\n\nBackend:\n{h.backend.upper()}\n\nRAM:\n{h.ram_gb:.1f} GB\n\nModel:\n{MODEL_DISPLAY_NAME}\n\nQuantization:\nAUTO -> FP16\n\nPreset:\n{resource_tier(h)}\n\nStarting MotionForge...\n\nhttp://localhost:7860\n\nOpen the forwarded port named:\nMotionForge\n=====================================")
PY
exec python -m motionforge.app 2>&1 | tee -a logs/motionforge.log
