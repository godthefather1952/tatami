# Model licenses

MotionForge code is Apache-2.0, but the downloaded model weights have their own licenses.

## Stable Diffusion 1.5

Repository: `stable-diffusion-v1-5/stable-diffusion-v1-5`  
License: CreativeML Open RAIL-M. The upstream model card describes research-oriented use and use-based restrictions. MotionForge does not claim ownership of these weights.

## AnimateDiff-Lightning

Repository: `ByteDance/AnimateDiff-Lightning`  
Checkpoint: `animatediff_lightning_2step_diffusers.safetensors`  
License: CreativeML Open RAIL-M.

`./install.sh` downloads these public weights without an authentication token and stores small copies of upstream license/model-card files under `models/` when available. Users are responsible for complying with the upstream model licenses.
