from __future__ import annotations
from datetime import datetime
from pathlib import Path
from motionforge.config.settings import repo_root

def ensure_runtime_dirs() -> None:
    for name in ("models", "outputs", "logs"):
        (repo_root() / name).mkdir(parents=True, exist_ok=True)

def output_paths(seed: int, now: datetime | None = None) -> tuple[Path, Path]:
    now = now or datetime.now()
    folder = repo_root() / "outputs" / now.strftime("%Y-%m-%d")
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"motionforge_{now.strftime('%Y%m%d_%H%M%S')}_seed{seed}"
    return folder / f"{stem}.mp4", folder / f"{stem}.json"
