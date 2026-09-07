from __future__ import annotations
from motionforge.config.settings import MODEL_DISPLAY_NAME

_BACKENDS = {"animatediff_lightning": "motionforge.models.animatediff_adapter:AnimateDiffLightningAdapter"}

def available_backends() -> list[str]:
    return list(_BACKENDS)

def create_backend(name: str = "animatediff_lightning", **kwargs):
    if name not in _BACKENDS:
        raise KeyError(f"Unknown backend: {name}")
    module_name, cls_name = _BACKENDS[name].split(":")
    module = __import__(module_name, fromlist=[cls_name])
    return getattr(module, cls_name)(**kwargs)

def default_model_name() -> str:
    return MODEL_DISPLAY_NAME
