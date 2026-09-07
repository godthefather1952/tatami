from __future__ import annotations
import json, time
from motionforge.models.registry import create_backend
from motionforge.media.video import encode_mp4, probe_video
from motionforge.system.hardware import detect_hardware
from motionforge.system.paths import output_paths
from motionforge.system.logging import configure_logging
from .result import GenerationResult

class InferencePipeline:
    def __init__(self, backend=None):
        self.backend = backend or create_backend()
        self.log = configure_logging()

    def generate(self, request, progress=None) -> GenerationResult:
        start = time.monotonic()
        self.log.info("generation_start preset=%s seed=%s size=%sx%s frames=%s steps=%s", request.preset, request.seed, request.width, request.height, request.num_frames, request.steps)
        frames = self.backend.generate(request, progress=progress)
        if progress: progress("Encoding MP4")
        video_path, metadata_path = output_paths(request.seed)
        encode_mp4(frames, video_path, request.fps)
        probe = probe_video(video_path)
        duration = time.monotonic() - start
        metadata = {
            "prompt": request.prompt, "negative_prompt": request.negative_prompt, "seed": request.seed,
            "model": self.backend.model_info(), "backend": self.backend.device,
            "quantization": self.backend.resolved_quantization(), "resolution": [request.width, request.height],
            "frame_count": probe["frames"], "fps": request.fps, "steps": request.steps,
            "generation_duration_seconds": duration,
            "trajectories": [t.model_dump() for t in request.trajectories],
            "system_information": detect_hardware().to_dict(),
        }
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        self.log.info("generation_complete seconds=%.2f output=%s", duration, video_path)
        if progress: progress("Complete")
        return GenerationResult(video_path, metadata_path, duration, probe["frames"])
