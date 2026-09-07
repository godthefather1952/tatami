import os

def is_codespaces() -> bool:
    return os.getenv("CODESPACES", "").lower() == "true"

def environment_name() -> str:
    return "GitHub Codespaces" if is_codespaces() else "Linux/local"

def browser_mode() -> str:
    return "forwarded-port" if is_codespaces() else "local-browser"
