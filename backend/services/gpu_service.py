import subprocess

def gpu_info() -> dict:
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,utilization.gpu,temperature.gpu,memory.total,memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=3, check=True)
        fields = [part.strip() for part in result.stdout.splitlines()[0].split(",")]
        return {"available": True, "name": fields[0], "usage_percent": float(fields[1]), "temperature_c": float(fields[2]), "memory_total_mb": float(fields[3]), "memory_used_mb": float(fields[4])}
    except (OSError, subprocess.SubprocessError, IndexError, ValueError):
        return {"available": False, "name": "No NVIDIA GPU detected", "usage_percent": None, "temperature_c": None, "memory_total_mb": None, "memory_used_mb": None}
