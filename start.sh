#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$ROOT"

export MOTIONFORGE_ROOT="$ROOT"
export HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_DISABLE_IMPLICIT_TOKEN=1
export DO_NOT_TRACK=1
export MALLOC_ARENA_MAX="${MALLOC_ARENA_MAX:-2}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-2}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-2}"

# First run: install the app and anonymously download the public models.
if [[ ! -d .venv ]]; then
  echo "First launch detected. Installing MotionForge..."
  ./install.sh
fi

source .venv/bin/activate

# If dependencies exist but weights were skipped/missing, fetch them now.
if ! python - <<'PY'
from motionforge.system.diagnostics import model_files_available
raise SystemExit(0 if model_files_available() else 1)
PY
then
  echo "Public model files are missing. Downloading anonymously..."
  python scripts/download_models.py
fi

python - <<'PY'
import torch, gradio, diffusers, transformers
from motionforge.system.diagnostics import model_files_available
if not model_files_available():
    raise SystemExit("MotionForge model files are missing and could not be downloaded.")
from motionforge.system.hardware import detect_hardware
from motionforge.system.environment import environment_name
from motionforge.system.backend import resource_tier
from motionforge.config.settings import MODEL_DISPLAY_NAME
h=detect_hardware()
print("=====================================")
print("          MOTIONFORGE v0.1.0")
print("=====================================")
print(f"""
Environment:
{environment_name()}

Backend:
{h.backend.upper()}

RAM:
{h.ram_gb:.1f} GB

Model:
{MODEL_DISPLAY_NAME}

Authentication:
NONE — no API key or model token required

Preset:
{resource_tier(h)}

Starting web app...

http://localhost:7860

In GitHub Codespaces, open the forwarded port named:
MotionForge
=====================================""")
PY

exec python -m motionforge.app 2>&1 | tee -a logs/motionforge.log
