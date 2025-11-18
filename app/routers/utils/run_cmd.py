import subprocess
from fastapi import HTTPException

def run_cmd(cmd: list) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            # inclui stdout/stderr para debug
            raise Exception(f"returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
        return result.stdout
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
