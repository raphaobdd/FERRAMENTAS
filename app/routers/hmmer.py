from fastapi import APIRouter, UploadFile, HTTPException
from app.utils.run_cmd import run_cmd
from app.utils.paths import HMMER_BIN, DATABASE_DIR
import uuid, os

router = APIRouter(prefix="/hmmer")

@router.post("/run")
def hmmscan(query: UploadFile, hmm_db: str):
    os.makedirs("/tmp", exist_ok=True)
    path = f"/tmp/{uuid.uuid4()}.faa"
    with open(path, "wb") as f:
        f.write(query.file.read())

    db_path = f"{DATABASE_DIR}{hmm_db}"
    if not os.path.exists(db_path):
        raise HTTPException(status_code=400, detail="HMM database not found.")

    out_path = f"/tmp/{uuid.uuid4()}.tsv"

    cmd = [
        HMMER_BIN,
        "--tblout", out_path,
        db_path,
        path
    ]

    run_cmd(cmd)

    try:
        with open(out_path, "r") as fh:
            return fh.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to read hmmscan output: {e}")
