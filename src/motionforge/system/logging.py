from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from motionforge.config.settings import repo_root

def configure_logging() -> logging.Logger:
    logger = logging.getLogger("motionforge")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    path = repo_root() / "logs" / "motionforge.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    fh = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(fh); logger.addHandler(sh)
    return logger
