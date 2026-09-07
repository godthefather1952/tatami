from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os

APP_NAME = "MotionForge"
VERSION = "0.1.0"
DEFAULT_PORT = 7860
BASE_MODEL_REPO = "stable-diffusion-v1-5/stable-diffusion-v1-5"
MOTION_REPO = "ByteDance/AnimateDiff-Lightning"
MOTION_FILE = "animatediff_lightning_2step_diffusers.safetensors"
MODEL_DISPLAY_NAME = "AnimateDiff-Lightning 2-step + Stable Diffusion 1.5"
MODEL_APPROX_GB = 3.1

@dataclass(frozen=True)
class GenerationPreset:
    name: str
    width: int
    height: int
    num_frames: int
    fps: int
    steps: int
    strength: float
    guidance_scale: float
    min_ram_gb: float

PRESETS = {
    "CPU_SAFE": GenerationPreset("CPU_SAFE", 128, 128, 4, 4, 2, 0.85, 1.0, 4.5),
    "CPU_STANDARD": GenerationPreset("CPU_STANDARD", 256, 256, 8, 6, 2, 0.85, 1.0, 7.0),
    "GPU_ACCELERATED": GenerationPreset("GPU_ACCELERATED", 384, 384, 12, 8, 2, 0.85, 1.0, 8.0),
}

def repo_root() -> Path:
    override = os.getenv("MOTIONFORGE_ROOT")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[3]

def models_dir() -> Path:
    return repo_root() / "models"

def base_model_dir() -> Path:
    return models_dir() / "sd15"

def motion_model_path() -> Path:
    return models_dir() / "animatediff_lightning" / MOTION_FILE
