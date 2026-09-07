from __future__ import annotations
import gc, inspect
from motionforge.config.settings import base_model_dir, motion_model_path, MODEL_DISPLAY_NAME, MODEL_APPROX_GB
from motionforge.errors import ConfigurationError, MemorySafetyError, ModelLoadError, GenerationError
from motionforge.media.images import validate_image, fit_image
from motionforge.system.hardware import detect_hardware, cpu_float16_supported
from .base import VideoModelBackend

class AnimateDiffLightningAdapter(VideoModelBackend):
    def __init__(self, device: str | None = None, quantization: str = "auto"):
        info = detect_hardware()
        self.device = device or info.backend
        self.quantization = quantization
        self.pipe = None
        self.dtype_name = "float16"

    def model_info(self) -> dict:
        return {"name": MODEL_DISPLAY_NAME, "approx_size_gb": MODEL_APPROX_GB, "device": self.device, "dtype": self.dtype_name, "quantization": self.resolved_quantization()}

    def resolved_quantization(self) -> str:
        if self.quantization == "int8":
            raise ConfigurationError("INT8 is not enabled for this AnimateDiff backend; use auto or none. AUTO uses fp16 weights to stay within CPU memory limits.")
        return "none"

    def supports_motion_control(self) -> bool:
        return False

    def load(self) -> None:
        if self.pipe is not None: return
        if not base_model_dir().exists() or not motion_model_path().exists():
            raise ModelLoadError("Model files are missing. Run ./install.sh.")
        hw = detect_hardware()
        if self.device == "cpu" and hw.ram_available_gb < 4.2:
            raise MemorySafetyError(f"Only {hw.ram_available_gb:.1f} GB RAM is available; CPU_SAFE model loading needs about 4.2 GB free. Close other processes and retry.")
        if self.device == "cpu" and not cpu_float16_supported():
            raise ModelLoadError("This PyTorch/CPU build cannot execute float16 convolution. MotionForge will not fall back to a likely out-of-memory float32 load.")
        try:
            import torch
            from diffusers import AnimateDiffVideoToVideoPipeline, MotionAdapter, EulerDiscreteScheduler
            from safetensors.torch import load_file
            dtype = torch.float16
            adapter = MotionAdapter().to("cpu", dtype=dtype)
            state = load_file(str(motion_model_path()), device="cpu")
            adapter.load_state_dict(state)
            del state
            self.pipe = AnimateDiffVideoToVideoPipeline.from_pretrained(
                str(base_model_dir()), motion_adapter=adapter, torch_dtype=dtype,
                variant="fp16", safety_checker=None, feature_extractor=None,
                local_files_only=True,
            )
            self.pipe.scheduler = EulerDiscreteScheduler.from_config(
                self.pipe.scheduler.config, timestep_spacing="trailing", beta_schedule="linear"
            )
            self.pipe.vae.enable_slicing()
            try: self.pipe.unet.enable_forward_chunking(chunk_size=1, dim=1)
            except Exception: pass
            self.pipe.to(self.device)
        except Exception as exc:
            self.pipe = None
            raise ModelLoadError(f"Could not load AnimateDiff locally: {exc}") from exc

    def unload(self) -> None:
        self.pipe = None
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available(): torch.cuda.empty_cache()
        except Exception: pass

    def generate(self, request, progress=None):
        if request.trajectories:
            raise GenerationError("Motion-controlled generation is not supported by the active model. Clear trajectories for STANDARD VIDEO generation.")
        if request.quantization == "int8":
            raise ConfigurationError("INT8 is not supported by the active model backend.")
        if progress: progress("Loading model")
        self.load()
        try:
            import torch
            if progress: progress("Encoding image")
            image = fit_image(validate_image(request.image_path), request.width, request.height)
            source_video = [image.copy() for _ in range(request.num_frames)]
            generator = torch.Generator(device=self.device).manual_seed(request.seed)
            kwargs = dict(
                video=source_video,
                prompt=request.prompt,
                negative_prompt=request.negative_prompt or None,
                height=request.height,
                width=request.width,
                num_inference_steps=request.steps,
                guidance_scale=1.0,
                strength=0.85,
                generator=generator,
                output_type="pil",
            )
            if "enforce_inference_steps" in inspect.signature(self.pipe.__call__).parameters:
                kwargs["enforce_inference_steps"] = True
            if progress: progress("Generating frames")
            with torch.inference_mode():
                output = self.pipe(**kwargs)
            if progress: progress("Decoding")
            return output.frames[0]
        except Exception as exc:
            if isinstance(exc, (GenerationError, ConfigurationError)): raise
            raise GenerationError(f"Local model generation failed: {exc}") from exc
