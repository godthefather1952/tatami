from __future__ import annotations
import os, socket
from fastapi import FastAPI
import gradio as gr
from motionforge import __version__
from motionforge.config.settings import DEFAULT_PORT
from motionforge.system.hardware import detect_hardware
from motionforge.system.diagnostics import model_files_available
from motionforge.system.paths import ensure_runtime_dirs
from motionforge.system.logging import configure_logging
from motionforge.ui.interface import build_interface

ensure_runtime_dirs(); log=configure_logging(); hw=detect_hardware()
app=FastAPI(title="MotionForge", version=__version__)

@app.get("/health")
def health():
    return {"status":"ok","version":__version__,"backend":hw.backend,"model_available":model_files_available()}

app = gr.mount_gradio_app(app, build_interface(), path="/")

def find_port(start=DEFAULT_PORT):
    for port in range(start, start+10):
        with socket.socket() as s:
            try: s.bind(("0.0.0.0",port)); return port
            except OSError: continue
    raise RuntimeError("No free port found in 7860-7869")

def main():
    import uvicorn
    port=int(os.getenv("MOTIONFORGE_PORT", find_port()))
    log.info("startup backend=%s ram=%.2f port=%s",hw.backend,hw.ram_gb,port)
    print(f"MotionForge is running.\n\nOpen the forwarded port labeled:\nMotionForge\n\nPort:\n{port}\n\nhttp://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__": main()
