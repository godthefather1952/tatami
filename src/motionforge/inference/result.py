from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass
class GenerationResult:
    video_path: Path
    metadata_path: Path
    duration_seconds: float
    frame_count: int
