import json
import re
import shutil
import subprocess
import time
from collections.abc import AsyncIterator
import httpx
from backend.core.config import DATA_DIR, OLLAMA_URL, REQUEST_TIMEOUT
from backend.core.logger import record

NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$")
process: subprocess.Popen | None = None
last_connection_state: bool | None = None

def validate_name(name: str) -> str:
    if not NAME_PATTERN.fullmatch(name):
        raise ValueError("Invalid model name")
    return name

async def request(method: str, path: str, payload: dict | None = None, timeout: float = REQUEST_TIMEOUT) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
            response = await client.request(method, OLLAMA_URL + path, json=payload)
            response.raise_for_status()
            return response.json() if response.content else {}
    except (httpx.HTTPError, ValueError) as exc:
        detail = str(exc) or type(exc).__name__
        record("ERROR", f"Ollama API {path}: {detail}")
        raise RuntimeError(f"Ollama request failed: {detail}") from exc

async def status() -> dict:
    global last_connection_state
    installed = shutil.which("ollama") is not None
    try:
        async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
            response = await client.get(OLLAMA_URL + "/api/version")
            response.raise_for_status()
            version = response.json()["version"]
        if last_connection_state is not True:
            record("INFO", "Ollama connected")
        last_connection_state = True
        return {"installed": installed, "running": True, "version": version}
    except (httpx.HTTPError, KeyError, ValueError):
        if last_connection_state is True:
            record("WARNING", "Ollama disconnected")
        last_connection_state = False
        return {"installed": installed, "running": False, "version": None}

async def models() -> list[dict]:
    data = await request("GET", "/api/tags")
    try:
        running = await request("GET", "/api/ps", timeout=5)
        loaded: set[str] | None = {item.get("name") or item.get("model") for item in running.get("models", [])}
    except RuntimeError:
        record("WARNING", "Running model status unavailable; showing installed models")
        loaded = None
    output = []
    for item in data.get("models", []):
        name = item.get("name", "")
        output.append({"name": name, "display_name": name.split(":")[0], "tag": name.split(":", 1)[1] if ":" in name else "latest", "size": item.get("size", 0), "modified_at": item.get("modified_at"), "loaded": name in loaded if loaded is not None else None, "quantization": item.get("details", {}).get("quantization_level")})
    return output

async def load(name: str) -> dict:
    validate_name(name)
    result = await request("POST", "/api/generate", {"model": name, "prompt": "", "keep_alive": "10m", "stream": False}, timeout=120)
    record("INFO", f"Loaded model {name}")
    return {"message": f"Loaded {name}", "details": result.get("done_reason")}

async def unload(name: str) -> dict:
    validate_name(name)
    await request("POST", "/api/generate", {"model": name, "prompt": "", "keep_alive": 0, "stream": False}, timeout=30)
    record("INFO", f"Unloaded model {name}")
    return {"message": f"Unloaded {name}"}

async def delete(name: str) -> dict:
    validate_name(name)
    await request("DELETE", "/api/delete", {"model": name}, timeout=30)
    record("INFO", f"Deleted model {name}")
    return {"message": f"Deleted {name}"}

async def stream_json(path: str, payload: dict, timeout: float = 3600) -> AsyncIterator[dict]:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=5), trust_env=False) as client:
            async with client.stream("POST", OLLAMA_URL + path, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield json.loads(line)
    except (httpx.HTTPError, ValueError) as exc:
        record("ERROR", f"Ollama stream {path}: {exc}")
        yield {"error": str(exc)}

async def pull(name: str) -> AsyncIterator[dict]:
    validate_name(name)
    record("INFO", f"Pull started {name}")
    last_time, last_bytes = time.monotonic(), 0
    async for event in stream_json("/api/pull", {"model": name, "stream": True}):
        now = time.monotonic()
        completed = event.get("completed", 0)
        elapsed = now - last_time
        event["speed_bytes_per_sec"] = max(0, (completed - last_bytes) / elapsed) if elapsed > 0 and completed >= last_bytes else 0
        if completed != last_bytes:
            last_time, last_bytes = now, completed
        yield event
        if event.get("error"):
            record("ERROR", f"Pull failed {name}: {event['error']}")
            return
    record("INFO", f"Pull finished {name}")

async def chat(name: str, message: str) -> AsyncIterator[dict]:
    validate_name(name)
    if not message.strip() or len(message) > 20000:
        raise ValueError("Message must contain 1–20000 characters")
    started = time.perf_counter()
    first_token = None
    async for event in stream_json("/api/chat", {"model": name, "messages": [{"role": "user", "content": message}], "stream": True, "think": False}, timeout=300):
        if event.get("message", {}).get("content") and first_token is None:
            first_token = time.perf_counter() - started
        if event.get("done"):
            event["ttft_seconds"] = first_token
            event["wall_time_seconds"] = time.perf_counter() - started
        yield event

def start() -> dict:
    global process
    executable = shutil.which("ollama")
    if not executable:
        raise RuntimeError("Ollama is not installed or not on PATH")
    if process and process.poll() is None:
        return {"message": "Ollama already started by this app"}
    try:
        log = open(DATA_DIR / "ollama.log", "a", encoding="utf-8")
        process = subprocess.Popen([executable, "serve"], stdout=log, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        log.close()
        record("INFO", "Started Ollama service")
        return {"message": "Ollama start requested"}
    except OSError as exc:
        raise RuntimeError(f"Could not start Ollama: {exc}") from exc

def stop() -> dict:
    global process
    if not process or process.poll() is not None:
        raise RuntimeError("Ollama was not started by this app; stop it from its owning process")
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)
    except OSError as exc:
        raise RuntimeError(f"Could not stop Ollama: {exc}") from exc
    process = None
    record("INFO", "Stopped Ollama service")
    return {"message": "Ollama stopped"}
