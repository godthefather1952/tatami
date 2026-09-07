# MotionForge v0.1.0 model selection

MotionForge v0.1.0 prioritizes a generation path that can actually run on a CPU-only GitHub Codespace. The default backend is **AnimateDiff-Lightning 2-step + Stable Diffusion 1.5**, used through Diffusers' `AnimateDiffVideoToVideoPipeline`.

## Why this stack

The application needs both the uploaded image and the prompt to affect a genuine local generative video result. MotionForge therefore repeats the uploaded image into a short source clip and runs real text-guided video-to-video diffusion over those frames. This is not a pan/zoom, interpolation-only, prerecorded, or remote-inference path.

The selected weights are comparatively small for a supported open-weight diffusion video stack:

- AnimateDiff-Lightning 2-step motion adapter: approximately 0.9 GB.
- Selective Stable Diffusion 1.5 fp16 components used by MotionForge: approximately 2.1 GB.
- Approximate default payload: 3.1 GB, excluding package caches and small configuration/tokenizer files.

The pipeline is loaded lazily on first generation. CPU inference uses fp16 weights because that materially reduces resident memory on current x86 PyTorch builds while remaining a real CPU backend. The application verifies fp16 convolution support before loading the model and refuses unsafe model loads when available RAM is below its conservative threshold.

## Candidates rejected for v0.1.0

| Candidate | Reason not selected for CPU-safe default |
| --- | --- |
| Stable Video Diffusion | Larger practical payload and weak/no text-prompt conditioning in its established image-to-video pipeline. |
| Wan 2.1 / VACE 1.3B | The full usable stack is much larger because of its large text encoder and transformer. |
| SkyReels 1.3B I2V | Text encoder footprint is too large for a typical CPU Codespace. |
| LTX-Video 2B | Model plus large text encoder exceeds the preferred first-run RAM/download envelope. |
| Zeroscope video-to-video | Technically smaller, but its non-commercial licensing is less suitable for a general open-source project default. |

## Motion control

The active model does not natively accept MotionForge point trajectories. The trajectory editor and serialization/interpolation layer are implemented, but motion-controlled generation is deliberately disabled rather than silently ignoring trajectory input. Standard video generation remains real local diffusion.

## Licensing

MotionForge source code is Apache-2.0. Third-party model weights retain their own licenses. See `MODEL_LICENSES.md` before redistributing or using model weights.
