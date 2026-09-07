from __future__ import annotations
from dataclasses import asdict, dataclass
import os, shutil
import psutil

@dataclass
class HardwareInfo:
    cpu_threads: int
    ram_gb: float
    ram_available_gb: float
    disk_free_gb: float
    cuda_available: bool
    gpu: str | None
    vram_gb: float | None
    backend: str

    def to_dict(self):
        return asdict(self)

def detect_hardware() -> HardwareInfo:
    import torch
    vm = psutil.virtual_memory()
    disk = shutil.disk_usage(os.getenv("MOTIONFORGE_ROOT", "."))
    cuda = bool(torch.cuda.is_available())
    gpu = None
    vram = None
    if cuda:
        try:
            gpu = torch.cuda.get_device_name(0)
            vram = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        except Exception:
            gpu = "CUDA device"
    return HardwareInfo(
        cpu_threads=os.cpu_count() or 1,
        ram_gb=round(vm.total / (1024**3), 2),
        ram_available_gb=round(vm.available / (1024**3), 2),
        disk_free_gb=round(disk.free / (1024**3), 2),
        cuda_available=cuda,
        gpu=gpu,
        vram_gb=vram,
        backend="cuda" if cuda else "cpu",
    )

def cpu_float16_supported() -> bool:
    import torch
    try:
        x = torch.ones((1, 1, 4, 4), dtype=torch.float16)
        layer = torch.nn.Conv2d(1, 1, 1).to(dtype=torch.float16)
        _ = layer(x)
        return True
    except Exception:
        return False
