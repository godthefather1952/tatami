#!/usr/bin/env python3
from __future__ import annotations
import os, sys, tempfile
from pathlib import Path
from motionforge.config.settings import repo_root
from motionforge.system.diagnostics import model_files_available
from motionforge.system.hardware import detect_hardware
from motionforge.system.environment import is_codespaces
from motionforge.models.registry import available_backends, default_model_name
from motionforge.motion.serialization import dumps, loads
from motionforge.motion.trajectory import TrajectorySet, Trajectory, Keyframe
from motionforge.media.video import encode_mp4, probe_video
from PIL import Image

checks=[]
def check(name, cond, detail=""):
    checks.append((name, bool(cond), detail)); print(f"{name:.<28} {'PASS' if cond else 'FAIL'} {detail}")
check("Python", sys.version_info >= (3,11), sys.version.split()[0])
check("Virtualenv", sys.prefix != sys.base_prefix, sys.prefix)
try: import torch, diffusers, transformers, gradio; imports=True
except Exception as e: imports=False
check("Core imports", imports, "")
check("PyTorch", imports and hasattr(torch,"inference_mode"), getattr(torch,"__version__","missing") if imports else "missing")
hw=detect_hardware(); check("Backend selection", hw.backend in {"cpu","cuda"}, hw.backend)
check("Model location", model_files_available(), str(repo_root()/"models"))
check("Model registry", "animatediff_lightning" in available_backends(), default_model_name())
traj=TrajectorySet(trajectories=[Trajectory(id="p",keyframes=[Keyframe(frame=0,x=.2,y=.3)])])
check("Trajectory serialization", loads(dumps(traj))==traj)
try:
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/"x.mp4"; encode_mp4([Image.new("RGB",(64,64),"red") for _ in range(2)],out,2); pr=probe_video(out); vid=pr["frames"]>=2
except Exception: vid=False
check("FFmpeg/video encoder",vid, "")
check("UI imports", imports, "")
check("Outputs writable", os.access(repo_root()/"outputs",os.W_OK), str(repo_root()/"outputs"))
check("Codespaces detection", isinstance(is_codespaces(),bool), str(is_codespaces()))
if all(ok for _,ok,_ in checks): print("\nMOTIONFORGE INSTALLATION VERIFIED")
else: raise SystemExit(1)
