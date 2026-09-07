from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from motionforge.motion.trajectory import Trajectory

class GenerationRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=1000)
    negative_prompt: str | None = Field(default=None, max_length=1000)
    image_path: str
    seed: int = Field(default=0, ge=0, le=2**32-1)
    width: int = Field(ge=64, le=1024)
    height: int = Field(ge=64, le=1024)
    num_frames: int = Field(ge=2, le=32)
    fps: int = Field(ge=1, le=30)
    steps: int = Field(ge=1, le=20)
    trajectories: list[Trajectory] = Field(default_factory=list)
    preset: str = "CPU_SAFE"
    quantization: str = "auto"

    @model_validator(mode="after")
    def dimensions(self):
        if self.width % 8 or self.height % 8:
            raise ValueError("width and height must be divisible by 8")
        if self.quantization not in {"auto", "none", "int8"}:
            raise ValueError("quantization must be auto, none, or int8")
        return self
