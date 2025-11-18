from fastapi import APIRouter, File, UploadFile
from app.utils.run_cmd import run_cmd
from app.utils.paths import BLAST_BIN, DATABASE_DIR
import os

router = APIRouter(prefix="/blast")

@router.post("/makeblastdb")
def make_blast_db(fasta: UploadFile):
    path = f"{DATABASE_DIR}{fasta.filename}"
    with open(path, "wb") as f:
        f.write(fasta.file.read())

    return {"status": "ok", "db": path}

@router.post("/run")
def run_blast(query: UploadFile, db_name: str):
    query_path = f"/tmp/{query.filename}"
    with open(query_path, "wb") as f:
        f.write(query.file.read())

    db_path = f"{DATABASE_DIR}{db_name}"

    cmd = [
        f"{BLAST_BIN}blastp",
        "-query", query_path,
        "-db", db_path,
        "-outfmt", "6"
    ]

    result = run_cmd(cmd)
    return {"result": result}
