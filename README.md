# MotionForge

Local CPU-compatible AI video generation.

No API keys.  
No remote inference.  
Designed for GitHub Codespaces.

## Quick start

1. Create/open this repository in GitHub Codespaces.
2. Open the terminal.
3. Run `./install.sh`.
4. After installation finishes, run `./start.sh`.
5. Click the forwarded port named **MotionForge** / **Open in Browser**.
6. Upload PNG/JPEG/WEBP, enter a prompt, and click **GENERATE STANDARD VIDEO**.

The server binds to `0.0.0.0:7860`; the Codespaces port remains private by default. MotionForge never opens a browser process inside the container.

## What the model does

The default backend combines the public Stable Diffusion 1.5 fp16 components with ByteDance AnimateDiff-Lightning 2-step. MotionForge creates a short source video by repeating the uploaded image, then runs **text-guided local video-to-video diffusion**. The uploaded image is therefore the starting video and the prompt guides denoising. This is genuine model inference, not pan/zoom, interpolation, prerecorded video, or a remote API.

Selective downloads keep the default payload around 3.1 GB rather than downloading every precision/format variant in the upstream repositories. See `MODEL_LICENSES.md` for model licensing.

## CPU behavior

CPU generation prioritizes compatibility over speed. Short, low-resolution clips are recommended. The `CPU_SAFE` preset is intentionally tiny: 128×128, 4 frames, 4 fps, 2 distilled denoising steps. MotionForge does not publish a fabricated timing estimate because runtime varies sharply by Codespace CPU.

`CPU_STANDARD` increases resolution/frame count and requires more memory. CUDA is used when available, but is never required.

## Motion paths

MotionForge v0.1.0 includes normalized trajectory data structures, serialization, interpolation, and an editor that can add/move/remove keyframes across multiple trajectory IDs. The active AnimateDiff-Lightning backend does **not** accept sparse point trajectories, so **MOTION CONTROLLED** generation is disabled. Standard generation refuses to proceed when trajectories are present, preventing silent ignored controls.

## Outputs

Generated files are stored under `outputs/YYYY-MM-DD/` as an H.264 MP4 (with MPEG-4 fallback) plus a JSON metadata file containing prompts, seed, model/backend, resolution, frame count, FPS, steps, duration, trajectories, and hardware information.

## Offline operation

Network access is needed only during installation for apt/pip and public model downloads. Once dependencies and weights are present, normal generation runs locally and can operate offline. No telemetry, analytics, inference provider, API key, or secret is required.

## Diagnostics and tests

- `python scripts/diagnose.py`
- `python scripts/verify_install.py`
- `python scripts/smoke_test.py`
- `python scripts/smoke_test.py --generation` — smallest real model generation
- `pytest`

`./install.sh` runs diagnostics, unit tests, smoke tests, and install verification automatically. It is safe to rerun and skips already-cached Hugging Face files.

## Troubleshooting

If installation fails, rerun `./install.sh`; downloads are resumable. If RAM is low, stop other processes and use `CPU_SAFE`. MotionForge blocks model loading when available RAM is below its conservative floor instead of risking a Codespace crash. If port 7860 is occupied, the app selects the next free port from 7861–7869 and prints it.

If model files are missing, rerun `./install.sh`. The default models are public and should not request a Hugging Face token.

## Architecture

UI → validated `GenerationRequest` → `InferencePipeline` → replaceable `VideoModelBackend` → local AnimateDiff adapter → frames → FFmpeg MP4 → browser preview/download.

Trajectory code lives separately under `src/motionforge/motion/` so future backends can implement true point/flow/pose/camera conditioning without changing the UI-to-inference boundary.

## Updating

Pull/download the newer repository version, then rerun `./install.sh`. Existing outputs are never deleted.

## Roadmap

Future versions may add a trajectory-conditioned backend, reference-video motion extraction, pose/camera control, motion brushes, identity-preservation adapters, and MotionForge-owned motion LoRAs/control networks. v0.1.0 intentionally prioritizes a tiny real local generation path first.
