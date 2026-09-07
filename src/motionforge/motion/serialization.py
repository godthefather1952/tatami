from __future__ import annotations
import json
from .trajectory import TrajectorySet

def dumps(data: TrajectorySet) -> str:
    return data.model_dump_json(indent=2)

def loads(raw: str | dict | list | None) -> TrajectorySet:
    if raw in (None, "", []):
        return TrajectorySet()
    if isinstance(raw, str):
        raw = json.loads(raw)
    if isinstance(raw, list):
        raw = {"trajectories": raw}
    return TrajectorySet.model_validate(raw)
