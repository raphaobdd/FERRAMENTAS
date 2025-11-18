from fastapi import APIRouter, UploadFile
from app.utils.run_cmd import run_cmd
from app.utils.paths import HMMER_BIN, DATABASE_DIR

router = APIRouter(prefix="/hmmer")

@router.post("/run")
def hmmscan(query: UploadFile, hmm_db: str):
    path = f"/tmp/{query.filename}"
    with open(path, "wb") as f:
        f.write(query.file.read())

    db_path = f"{DATABASE_DIR}{hmm_db}"

    cmd = [
        f"{HMMER_BIN}hmmscan",
        db_path,
        path
    ]

    result = run_cmd(cmd)
    return {"result": result}
