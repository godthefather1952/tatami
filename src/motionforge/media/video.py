from __future__ import annotations
from pathlib import Path
import imageio.v2 as imageio
import numpy as np
from motionforge.errors import EncodingError

def encode_mp4(frames, output: str | Path, fps: int) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    arrays = [np.asarray(f.convert("RGB") if hasattr(f, "convert") else f, dtype=np.uint8) for f in frames]
    if not arrays:
        raise EncodingError("No frames were produced by the model.")
    try:
        writer = imageio.get_writer(str(output), fps=fps, codec="libx264", format="FFMPEG", macro_block_size=1)
        for frame in arrays: writer.append_data(frame)
        writer.close()
    except Exception:
        try:
            writer = imageio.get_writer(str(output), fps=fps, codec="mpeg4", format="FFMPEG", macro_block_size=1)
            for frame in arrays: writer.append_data(frame)
            writer.close()
        except Exception as exc:
            raise EncodingError(f"FFmpeg could not encode MP4: {exc}") from exc
    if not output.exists() or output.stat().st_size <= 0:
        raise EncodingError("Encoder produced an empty MP4.")
    return output

def probe_video(path: str | Path) -> dict:
    p = Path(path)
    reader = imageio.get_reader(str(p), format="FFMPEG")
    try:
        count = reader.count_frames()
        meta = reader.get_meta_data()
        first = reader.get_data(0)
        return {"frames": int(count), "fps": float(meta.get("fps", 0)), "shape": list(first.shape), "bytes": p.stat().st_size}
    finally:
        reader.close()
