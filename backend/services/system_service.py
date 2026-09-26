import platform
import psutil
import subprocess
from functools import lru_cache
from backend.services.gpu_service import gpu_info

@lru_cache(maxsize=1)
def cpu_name() -> str:
    try:
        result = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"], capture_output=True, text=True, timeout=4, check=True)
        return result.stdout.strip() or platform.processor()
    except (OSError, subprocess.SubprocessError):
        return platform.processor() or "Unknown CPU"

def snapshot() -> dict:
    memory = psutil.virtual_memory()
    return {"os": f"{platform.system()} {platform.release()}", "cpu": {"name": cpu_name(), "usage_percent": psutil.cpu_percent(interval=0.1)}, "memory": {"total_bytes": memory.total, "used_bytes": memory.used, "usage_percent": memory.percent}, "gpu": gpu_info()}
