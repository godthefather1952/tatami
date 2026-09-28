# MotionForge

A browser-based, self-hosted image-to-video AI app.

**No API keys. No Hugging Face token. No remote inference service.**

MotionForge downloads public open-weight models anonymously, runs inference on the machine hosting the app, and serves a mobile-friendly web interface.

## Fastest way to run it

### GitHub Codespaces

1. Open this repository on GitHub.
2. Choose **Code → Codespaces → Create codespace on main**.
3. In the Codespaces terminal, run:

```bash
./start.sh
```

That is the only command required.

On a first launch, `start.sh` automatically:

- creates the Python environment if needed,
- installs MotionForge,
- anonymously downloads the public model files,
- validates the installation,
- launches the web app.

When port **7860** appears, open the forwarded port named **MotionForge**.

The devcontainer marks port 7860 public, so the resulting web-app URL does not require a MotionForge login or API token. The Codespace itself still has to be running.

> A public port means anyone with the URL can submit generations while your Codespace is running. Change the port visibility to private if you do not want that.

## How it works

Upload a PNG, JPEG, or WEBP image and enter a motion prompt.

MotionForge then:

1. validates and resizes the image,
2. repeats it into a short source clip,
3. runs local text-guided video-to-video diffusion,
4. generates new frames,
5. encodes the result as an MP4,
6. writes a JSON metadata file beside the video.

The active backend is:

- **Stable Diffusion 1.5**
- **ByteDance AnimateDiff-Lightning 2-step**
- Diffusers `AnimateDiffVideoToVideoPipeline`

The default model payload is about **3.1 GB**.

## No-token model downloads

MotionForge explicitly downloads the public model repositories anonymously.

The downloader passes `token=False` and sets:

```text
HF_HUB_DISABLE_IMPLICIT_TOKEN=1
```

A Hugging Face account is not required for the configured models.

Internet access is needed for the initial package/model download. Once dependencies and weights are present, inference is local and can run without an inference API.

## Hardware presets

| Preset | Resolution | Frames | FPS | Steps | Intended use |
| --- | ---: | ---: | ---: | ---: | --- |
| `CPU_SAFE` | 64×64 | 4 | 4 | 2 | Low-memory CPU acceptance mode |
| `CPU_STANDARD` | 256×256 | 8 | 6 | 2 | Larger CPU machines |
| `GPU_ACCELERATED` | 384×384 | 12 | 8 | 2 | CUDA GPU |

The app detects the available hardware and recommends a preset automatically.

`CPU_SAFE` intentionally prioritizes completing real local model inference over visual quality. It is a small proof-of-function mode for constrained environments.

## Web interface

The browser UI includes:

- source-image upload,
- motion prompt,
- optional negative prompt,
- hardware preset,
- deterministic seed,
- generation status,
- video preview,
- MP4 download,
- generation-metadata download,
- hardware/model status.

The interface is built with Gradio and served through FastAPI/Uvicorn on `0.0.0.0:7860`. If that port is busy, MotionForge searches 7861–7869.

## Important motion-control status

MotionForge contains trajectory data structures, serialization, interpolation, and an experimental trajectory editor.

The current AnimateDiff-Lightning backend **does not support true point-trajectory conditioning**.

For that reason, the web app does not pretend that the feature works. If trajectory data is present during standard generation, MotionForge refuses the request instead of silently ignoring it.

A future backend can implement `VideoModelBackend.supports_motion_control()` and consume those trajectories without requiring the UI/inference boundary to be redesigned.

## Output files

Each generation creates:

```text
outputs/YYYY-MM-DD/
  motionforge_YYYYMMDD_HHMMSS_seed1234.mp4
  motionforge_YYYYMMDD_HHMMSS_seed1234.json
```

Metadata includes:

- prompt and negative prompt,
- seed,
- model/backend,
- resolution,
- frame count,
- FPS,
- denoising steps,
- strength,
- guidance scale,
- generation duration,
- trajectories,
- hardware information.

## Architecture

```text
Browser
  ↓
Gradio web UI
  ↓
GenerationRequest
  ↓
InferencePipeline
  ↓
VideoModelBackend
  ↓
AnimateDiff-Lightning + Stable Diffusion 1.5
  ↓
Generated frames
  ↓
FFmpeg
  ↓
MP4 + JSON metadata
```

The model implementation is behind a replaceable backend interface, so newer video models can be added without rebuilding the web app.

## Manual installation

If you prefer separate installation and startup:

```bash
./install.sh
./start.sh
```

The installer is idempotent and cached model downloads are reused.

## Diagnostics

```bash
python scripts/diagnose.py
python scripts/verify_install.py
python scripts/smoke_test.py
python scripts/smoke_test.py --generation
pytest
```

## Resource protection

MotionForge includes several safeguards for constrained hosts:

- FP16 model weights,
- lazy model loading,
- low-memory UNet construction,
- duplicate motion-adapter release,
- VAE slicing,
- CPU thread limits,
- allocator cleanup,
- free-RAM checks before model loading.

On CPU, model loading is blocked when available memory is below the conservative safety floor instead of intentionally risking a host crash.

## Licensing

MotionForge source code is Apache-2.0.

Third-party model weights retain their own licenses. See [MODEL_LICENSES.md](MODEL_LICENSES.md) before redistributing model weights or using them in another product.
