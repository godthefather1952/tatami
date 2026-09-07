from .hardware import HardwareInfo

def resource_tier(info: HardwareInfo) -> str:
    if info.cuda_available:
        return "GPU_ACCELERATED"
    if info.ram_gb >= 10:
        return "CPU_STANDARD"
    return "CPU_SAFE"

def select_device(info: HardwareInfo) -> str:
    return "cuda" if info.cuda_available else "cpu"
