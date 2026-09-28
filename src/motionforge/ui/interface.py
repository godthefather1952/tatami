from __future__ import annotations
import gradio as gr

from motionforge.config.settings import PRESETS, MODEL_DISPLAY_NAME
from motionforge.inference.request import GenerationRequest
from motionforge.inference.pipeline import InferencePipeline
from motionforge.motion.serialization import loads
from motionforge.system.hardware import detect_hardware
from motionforge.system.environment import environment_name
from motionforge.system.backend import resource_tier
from .components import upsert_keyframe, remove_keyframe, clear_trajectories

_PIPELINE = None

CSS = """
.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
}
.hero {
    padding: 18px 20px;
    border: 1px solid var(--border-color-primary);
    border-radius: 18px;
    margin-bottom: 14px;
}
.hero h1 { margin: 0 0 8px 0 !important; }
.badges { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    border: 1px solid var(--border-color-primary);
    font-size: 12px;
    font-weight: 700;
}
.primary-action button { min-height: 52px; font-weight: 800; }
@media (max-width: 760px) {
    .gradio-container { padding: 8px !important; }
    .hero { padding: 14px; border-radius: 14px; }
}
"""

def _pipeline():
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = InferencePipeline()
    return _PIPELINE

def build_interface():
    hw = detect_hardware()
    tier = resource_tier(hw)
    status = (
        f"Environment: {environment_name()}\n"
        f"Backend: {hw.backend.upper()}\n"
        f"RAM: {hw.ram_gb:.1f} GB\n"
        f"Model: {MODEL_DISPLAY_NAME}\n"
        "Authentication: NONE\n"
        "Model Status: Ready after first load\n"
        f"Recommended Preset: {tier}"
    )

    with gr.Blocks(title="MotionForge", css=CSS) as demo:
        gr.HTML(
            """
            <div class="hero">
              <h1>MOTIONFORGE</h1>
              <div>Upload one image, describe the motion, and generate a short AI video directly on this server.</div>
              <div class="badges">
                <span class="badge">NO API KEY</span>
                <span class="badge">NO HUGGING FACE TOKEN</span>
                <span class="badge">LOCAL MODEL INFERENCE</span>
                <span class="badge">MOBILE FRIENDLY</span>
              </div>
            </div>
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                image = gr.Image(
                    type="filepath",
                    label="1. SOURCE IMAGE",
                    sources=["upload"],
                    height=320,
                )
                prompt = gr.Textbox(
                    label="2. DESCRIBE THE MOTION",
                    lines=4,
                    placeholder="The subject gently turns toward the camera while the background stays stable.",
                )
                negative = gr.Textbox(
                    label="NEGATIVE PROMPT — optional",
                    lines=2,
                    placeholder="distorted, blurry, duplicate limbs",
                )

                with gr.Row():
                    preset = gr.Dropdown(
                        choices=list(PRESETS),
                        value=tier,
                        label="QUALITY / HARDWARE PRESET",
                    )
                    seed = gr.Number(value=1234, precision=0, label="SEED")

                generate = gr.Button(
                    "GENERATE VIDEO",
                    variant="primary",
                    elem_classes=["primary-action"],
                )

                with gr.Accordion("Experimental motion-path editor", open=False):
                    gr.Markdown(
                        "The current AnimateDiff backend does not support true point-trajectory "
                        "conditioning yet. These controls are retained for future compatible backends. "
                        "Standard generation will refuse to silently ignore a saved path."
                    )
                    traj_json = gr.JSON(
                        value={"trajectories": []},
                        label="Trajectory JSON",
                    )
                    with gr.Row():
                        tid = gr.Textbox(value="point_1", label="Trajectory ID")
                        frame = gr.Number(value=0, precision=0, label="Frame")
                    with gr.Row():
                        x = gr.Slider(0, 1, value=0.5, step=0.01, label="X")
                        y = gr.Slider(0, 1, value=0.5, step=0.01, label="Y")
                    with gr.Row():
                        add = gr.Button("Add / Move Keyframe")
                        remove = gr.Button("Remove Keyframe")
                        clear = gr.Button("Clear All")

            with gr.Column(scale=1):
                gen_status = gr.Textbox(
                    value="Ready",
                    label="GENERATION STATUS",
                    interactive=False,
                )
                video = gr.Video(label="GENERATED VIDEO", format="mp4", height=360)
                with gr.Row():
                    download = gr.File(label="DOWNLOAD MP4")
                    metadata = gr.File(label="GENERATION METADATA")
                gr.Textbox(
                    value=status,
                    label="SYSTEM",
                    lines=8,
                    interactive=False,
                )

        add.click(upsert_keyframe, [traj_json, tid, frame, x, y], traj_json)
        remove.click(remove_keyframe, [traj_json, tid, frame], traj_json)
        clear.click(clear_trajectories, outputs=traj_json)

        def run(
            img,
            prompt_text,
            neg,
            preset_name,
            seed_value,
            traj_raw,
            progress=gr.Progress(track_tqdm=False),
        ):
            if not img:
                raise gr.Error("Upload a PNG, JPEG, or WEBP image.")
            if not (prompt_text or "").strip():
                raise gr.Error("Describe the motion you want in the prompt box.")

            p = PRESETS[preset_name]
            trajectories = loads(traj_raw).trajectories
            if trajectories:
                raise gr.Error(
                    "The current model cannot apply point trajectories. "
                    "Clear the experimental trajectory data before standard generation."
                )

            req = GenerationRequest(
                prompt=prompt_text.strip(),
                negative_prompt=(neg or "").strip() or None,
                image_path=img,
                seed=int(seed_value),
                width=p.width,
                height=p.height,
                num_frames=p.num_frames,
                fps=p.fps,
                steps=p.steps,
                strength=p.strength,
                guidance_scale=p.guidance_scale,
                trajectories=[],
                preset=p.name,
                quantization="auto",
            )

            def stage(message):
                progress(0, desc=message)

            try:
                result = _pipeline().generate(req, progress=stage)
                return (
                    str(result.video_path),
                    str(result.video_path),
                    str(result.metadata_path),
                    f"Complete — {result.frame_count} frames in {result.duration_seconds:.1f}s",
                )
            except Exception as exc:
                raise gr.Error(str(exc))

        generate.click(
            run,
            [image, prompt, negative, preset, seed, traj_json],
            [video, download, metadata, gen_status],
            concurrency_limit=1,
        )

    return demo.queue(default_concurrency_limit=1)
