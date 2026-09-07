#!/usr/bin/env python3
from __future__ import annotations
import argparse, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from motionforge.app import app
from motionforge.config.settings import PRESETS, repo_root
from motionforge.system.hardware import detect_hardware
from motionforge.system.backend import resource_tier
from motionforge.motion.trajectory import Trajectory, Keyframe
from motionforge.motion.interpolation import interpolate_trajectory
from motionforge.media.images import validate_image, fit_image
from motionforge.media.video import encode_mp4, probe_video
from motionforge.inference.request import GenerationRequest
from motionforge.inference.pipeline import InferencePipeline

parser=argparse.ArgumentParser(); parser.add_argument("--generation",action="store_true"); args=parser.parse_args()
print("MOTIONFORGE SMOKE TEST")
hw=detect_hardware(); print("Hardware ............ PASS",hw.backend,hw.ram_gb,"GB")
print("Backend ............. PASS",resource_tier(hw))
traj=Trajectory(id="point_1",keyframes=[Keyframe(frame=0,x=.2,y=.5),Keyframe(frame=3,x=.8,y=.5)])
assert len(interpolate_trajectory(traj,4))==4; print("Trajectory .......... PASS")
asset=repo_root()/"tests/assets/red_ball.png"; img=validate_image(asset); assert fit_image(img,128,128).size==(128,128); print("Image processing .... PASS")
with tempfile.TemporaryDirectory() as td:
    vp=Path(td)/"test.mp4"; encode_mp4([img.resize((64,64)) for _ in range(2)],vp,2); assert probe_video(vp)["frames"]>=2
print("Video encoder ....... PASS")
client=TestClient(app); r=client.get("/health"); assert r.status_code==200 and r.json()["status"]=="ok"; print("Server/health ....... PASS")
if args.generation:
    p=PRESETS["CPU_SAFE"]
    req=GenerationRequest(prompt="a small red ball gently moving across a white table",image_path=str(asset),seed=1234,width=p.width,height=p.height,num_frames=p.num_frames,fps=p.fps,steps=p.steps,trajectories=[],preset=p.name)
    result=InferencePipeline().generate(req,progress=lambda s: print("Generation ..........",s))
    probe=probe_video(result.video_path)
    assert result.video_path.stat().st_size>0 and probe["frames"]>=2
    print("REAL GENERATION ..... PASS",result.video_path,probe)
print("SMOKE TEST COMPLETE")
