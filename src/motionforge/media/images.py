from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageOps
from motionforge.errors import GenerationError

ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}
MAX_INPUT_PIXELS = 16_000_000

def validate_image(path: str | Path) -> Image.Image:
    p = Path(path)
    if not p.is_file():
        raise GenerationError("Source image was not found.")
    try:
        img = Image.open(p)
        img.verify()
        img = Image.open(p).convert("RGB")
    except Exception as exc:
        raise GenerationError(f"Invalid image: {exc}") from exc
    if (Image.open(p).format or "").upper() not in ALLOWED_FORMATS:
        raise GenerationError("Image must be PNG, JPEG, or WEBP.")
    if img.width * img.height > MAX_INPUT_PIXELS:
        img.thumbnail((4000, 4000))
    return img

def fit_image(img: Image.Image, width: int, height: int) -> Image.Image:
    contained = ImageOps.contain(img, (width, height), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), "white")
    canvas.paste(contained, ((width-contained.width)//2, (height-contained.height)//2))
    return canvas
