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

def _pipeline():
    global _PIPELINE
    if _PIPELINE is None: _PIPELINE = InferencePipeline()
    return _PIPELINE

def build_interface():
    hw=detect_hardware(); tier=resource_tier(hw)
    status=f"Environment: {environment_name()}\nBackend: {hw.backend.upper()}\nRAM: {hw.ram_gb:.1f} GB\nModel: {MODEL_DISPLAY_NAME}\nModel Status: Not Loaded\nPreset: {tier}"
    with gr.Blocks(title="MotionForge") as demo:
        gr.Markdown("# MOTIONFORGE\n**Local Motion-Control Video AI**\n\nNo API keys. No remote inference. CPU compatible.\n\n> CPU generation prioritizes compatibility over speed. Short, low-resolution clips are recommended.")
        with gr.Row():
            with gr.Column():
                image=gr.Image(type="filepath", label="SOURCE IMAGE", sources=["upload"])
                prompt=gr.Textbox(label="PROMPT", lines=3, placeholder="the subject gently moves while the camera remains stable")
                negative=gr.Textbox(label="NEGATIVE PROMPT", lines=2)
                gr.Markdown("### MOTION PATHS — experimental data editor\nMotion-controlled generation is not yet supported by the active model. Trajectories are never silently applied to STANDARD VIDEO.")
                traj_json=gr.JSON(value={"trajectories":[]}, label="Trajectory JSON")
                with gr.Row():
                    tid=gr.Textbox(value="point_1", label="Trajectory ID")
                    frame=gr.Number(value=0, precision=0, label="Frame")
                    x=gr.Slider(0,1,value=0.5,step=0.01,label="X")
                    y=gr.Slider(0,1,value=0.5,step=0.01,label="Y")
                with gr.Row():
                    add=gr.Button("Add / Move Keyframe")
                    remove=gr.Button("Remove Keyframe")
                    clear=gr.Button("Clear All")
                preset=gr.Dropdown(choices=list(PRESETS), value=tier, label="GENERATION PRESET")
                seed=gr.Number(value=1234, precision=0, label="SEED")
                generate=gr.Button("GENERATE STANDARD VIDEO", variant="primary")
                gr.Button("GENERATE MOTION CONTROLLED", interactive=False)
            with gr.Column():
                gr.Textbox(value=status, label="SYSTEM STATUS", lines=8, interactive=False)
                gen_status=gr.Textbox(value="Idle", label="Generation Status", interactive=False)
                video=gr.Video(label="VIDEO", format="mp4")
                download=gr.File(label="Download MP4")
                metadata=gr.File(label="Generation metadata")
        add.click(upsert_keyframe, [traj_json,tid,frame,x,y], traj_json)
        remove.click(remove_keyframe, [traj_json,tid,frame], traj_json)
        clear.click(clear_trajectories, outputs=traj_json)

        def run(img,prompt_text,neg,preset_name,seed_value,traj_raw,progress=gr.Progress(track_tqdm=False)):
            if not img: raise gr.Error("Upload a PNG, JPEG, or WEBP image.")
            p=PRESETS[preset_name]
            trajectories=loads(traj_raw).trajectories
            if trajectories:
                raise gr.Error("STANDARD VIDEO does not apply motion paths. Clear trajectories, or wait for a backend with true trajectory conditioning.")
            req=GenerationRequest(prompt=prompt_text,negative_prompt=neg or None,image_path=img,seed=int(seed_value),width=p.width,height=p.height,num_frames=p.num_frames,fps=p.fps,steps=p.steps,trajectories=[],preset=p.name,quantization="auto")
            def stage(s): progress(0, desc=s)
            try:
                result=_pipeline().generate(req, progress=stage)
                return str(result.video_path), str(result.video_path), str(result.metadata_path), f"Complete — {result.frame_count} frames"
            except Exception as exc:
                raise gr.Error(str(exc))
        generate.click(run,[image,prompt,negative,preset,seed,traj_json],[video,download,metadata,gen_status],concurrency_limit=1)
    return demo.queue(default_concurrency_limit=1)
