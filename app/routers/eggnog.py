from fastapi import APIRouter, UploadFile
from app.utils.run_cmd import run_cmd
from app.utils.paths import EGGNOG_BIN

router = APIRouter(prefix="/eggnog")

@router.post("/annotate")
def annotate(query: UploadFile):
    path = f"/tmp/{query.filename}"
    with open(path, "wb") as f:
        f.write(query.file.read())

    cmd = [
        f"{EGGNOG_BIN}emapper.py",
        "-i", path,
        "--cpu", "2",
        "--output", "result"
    ]

    result = run_cmd(cmd)
    return {"result": result}
