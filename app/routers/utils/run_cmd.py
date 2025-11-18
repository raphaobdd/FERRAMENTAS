import subprocess
from fastapi import HTTPException

def run_cmd(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(500, result.stderr)
        return result.stdout
    except Exception as e:
        raise HTTPException(500, str(e))
