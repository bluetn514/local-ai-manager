from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
OLLAMA_URL = "http://127.0.0.1:11434"
REQUEST_TIMEOUT = 8.0
