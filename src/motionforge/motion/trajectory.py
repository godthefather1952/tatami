from __future__ import annotations
from pydantic import BaseModel, Field, model_validator

class Keyframe(BaseModel):
    frame: int = Field(ge=0)
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)

class Trajectory(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    keyframes: list[Keyframe] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_frames(self):
        frames = [k.frame for k in self.keyframes]
        if len(frames) != len(set(frames)):
            raise ValueError("trajectory keyframe frames must be unique")
        self.keyframes.sort(key=lambda k: k.frame)
        return self

class TrajectorySet(BaseModel):
    trajectories: list[Trajectory] = Field(default_factory=list)
