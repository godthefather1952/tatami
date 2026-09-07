import os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault("MOTIONFORGE_ROOT",str(ROOT))
sys.path.insert(0,str(ROOT/"src"))
