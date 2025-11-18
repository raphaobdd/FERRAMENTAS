from fastapi import APIRouter, UploadFile, HTTPException, Form
from app.utils.paths import DIAMOND_BIN, DATABASE_DIR
from app.utils.run_cmd import run_cmd
import uuid, os

router = APIRouter(prefix="/diamond")

@router.post("/run")
def run_diamond(query: UploadFile, db_name: str = Form(...)):
    os.makedirs("/tmp", exist_ok=True)
    query_path = f"/tmp/{uuid.uuid4()}.faa"
    with open(query_path, "wb") as f:
        f.write(query.file.read())

    db_prefix = os.path.join(DATABASE_DIR, db_name)

    if not os.path.exists(db_prefix + ".dmnd"):
        raise HTTPException(status_code=400, detail="DIAMOND database not found.")

    out_path = f"/tmp/{uuid.uuid4()}.tsv"

    cmd = [
        DIAMOND_BIN, "blastp",
        "-d", db_prefix,
        "-q", query_path,
        "-o", out_path,
        "-f", "6"
    ]

    run_cmd(cmd)

    try:
        with open(out_path, "r") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to read diamond output: {e}")
