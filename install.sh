#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$ROOT"
STEP="initialization"
fail(){ code=$?; echo; echo "MOTIONFORGE INSTALLATION FAILED"; echo; echo "Step:"; echo "$STEP"; echo; echo "Reason:"; echo "command exited with code $code"; echo; echo "Suggested action:"; echo "Review the message above, ensure the Codespace has network/disk space, then rerun ./install.sh. The installer is idempotent."; exit "$code"; }
trap fail ERR
export HF_HUB_DISABLE_TELEMETRY=1 DO_NOT_TRACK=1 PYTHONUNBUFFERED=1 MOTIONFORGE_ROOT="$ROOT"
[[ "$(uname -s)" == "Linux" ]] || { echo "MotionForge requires Linux."; exit 1; }
STEP="checking Python"
PYTHON=""
for p in python3.11 python3.12 python3; do if command -v "$p" >/dev/null 2>&1; then PYTHON="$p"; break; fi; done
[[ -n "$PYTHON" ]] || { echo "Python 3.11+ is required."; exit 1; }
"$PYTHON" - <<'PY'
import sys
assert sys.version_info >= (3,11), "Python 3.11+ required"
PY
STEP="checking FFmpeg"
if ! command -v ffmpeg >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y ffmpeg; fi
fi
STEP="creating virtual environment"
[[ -d .venv ]] || "$PYTHON" -m venv .venv
source .venv/bin/activate
STEP="upgrading packaging tools"
python -m pip install --upgrade pip setuptools wheel
STEP="installing CPU PyTorch"
if ! python -c 'import torch' >/dev/null 2>&1; then python -m pip install --index-url https://download.pytorch.org/whl/cpu 'torch>=2.6,<2.11' 'torchvision>=0.21,<0.26'; fi
STEP="installing MotionForge dependencies"
python -m pip install -e '.[test]'
STEP="creating directories"
mkdir -p models outputs logs tests/assets
STEP="creating test asset"
python - <<'PY'
from pathlib import Path
from PIL import Image,ImageDraw
p=Path('tests/assets/red_ball.png')
if not p.exists():
 im=Image.new('RGB',(128,128),'white'); d=ImageDraw.Draw(im); d.ellipse((42,42,86,86),fill='red'); im.save(p)
PY
if [[ "${MOTIONFORGE_SKIP_MODEL_DOWNLOAD:-0}" != "1" ]]; then
  STEP="downloading public model weights"; python scripts/download_models.py
else
  echo "Skipping model download because MOTIONFORGE_SKIP_MODEL_DOWNLOAD=1"
fi
STEP="running diagnostics"
if [[ "${MOTIONFORGE_SKIP_MODEL_DOWNLOAD:-0}" == "1" ]]; then python scripts/diagnose.py || true; else python scripts/diagnose.py; fi
STEP="running unit tests"; pytest
STEP="running smoke tests"; python scripts/smoke_test.py
if [[ "${MOTIONFORGE_SKIP_MODEL_DOWNLOAD:-0}" != "1" ]]; then STEP="verifying installation"; python scripts/verify_install.py; fi
echo; echo "MOTIONFORGE INSTALLATION COMPLETE"; echo; echo "Run:"; echo "./start.sh"
