from __future__ import annotations
from pathlib import Path
import importlib.util, os, sys, tempfile
from motionforge.config.settings import base_model_dir, motion_model_path, repo_root
from motionforge.system.hardware import detect_hardware

def model_files_available() -> bool:
    required = [
        base_model_dir()/"model_index.json",
        base_model_dir()/"unet"/"diffusion_pytorch_model.fp16.safetensors",
        base_model_dir()/"text_encoder"/"model.fp16.safetensors",
        base_model_dir()/"vae"/"diffusion_pytorch_model.fp16.safetensors",
        motion_model_path(),
    ]
    return all(p.is_file() and p.stat().st_size > 0 for p in required)

def run_diagnostics() -> list[tuple[str,str,str]]:
    hw = detect_hardware()
    checks=[]
    checks.append(("Environment","PASS",sys.platform))
    checks.append(("Python","PASS" if sys.version_info >= (3,11) else "FAIL",sys.version.split()[0]))
    checks.append(("PyTorch","PASS" if importlib.util.find_spec("torch") else "FAIL","installed" if importlib.util.find_spec("torch") else "missing"))
    checks.append(("CPU Backend","PASS",f"{hw.cpu_threads} threads"))
    checks.append(("CUDA","PASS" if hw.cuda_available else "WARN",hw.gpu or "optional / unavailable"))
    checks.append(("RAM","PASS" if hw.ram_gb >= 4.5 else "WARN",f"{hw.ram_gb:.1f} GB"))
    checks.append(("Disk","PASS" if hw.disk_free_gb >= 6 else "FAIL",f"{hw.disk_free_gb:.1f} GB free"))
    try:
        import imageio_ffmpeg
        ff=imageio_ffmpeg.get_ffmpeg_exe(); ff_ok=Path(ff).exists()
    except Exception: ff_ok=False
    checks.append(("FFmpeg","PASS" if ff_ok else "FAIL","available" if ff_ok else "missing"))
    checks.append(("Model Files","PASS" if model_files_available() else "FAIL","available" if model_files_available() else "missing"))
    out=repo_root()/"outputs"
    try:
        out.mkdir(exist_ok=True); fd,p=tempfile.mkstemp(dir=out); os.close(fd); os.unlink(p); writable=True
    except Exception: writable=False
    checks.append(("Writable Outputs","PASS" if writable else "FAIL",str(out)))
    checks.append(("Core Imports","PASS","motionforge"))
    return checks
