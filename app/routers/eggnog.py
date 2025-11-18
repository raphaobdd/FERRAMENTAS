from fastapi import APIRouter, UploadFile, Form, HTTPException
from app.utils.run_cmd import run_cmd
from app.utils.paths import DIAMOND_BIN, EGGNOG_BIN, DATABASE_DIR
import os, uuid, shutil

router = APIRouter(prefix="/eggnog")

def save_to_path(upload_file: UploadFile, dest_path: str) -> str:
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(upload_file.file.read())
    return dest_path

@router.post("/makedb")
def make_db(fasta: UploadFile, name: str = Form(...)):
    """
    Cria um banco DIAMOND a partir de um FASTA de proteínas.
    - fasta: arquivo .faa
    - name: prefixo do DB (será salvo como /data/databases/{name}.dmnd)
    """
    # paths
    fasta_path = os.path.join(DATABASE_DIR, f"{name}.faa")
    db_prefix = os.path.join(DATABASE_DIR, name)  # diamond makedb -d prefix
    os.makedirs(DATABASE_DIR, exist_ok=True)

    # salvar fasta
    save_to_path(fasta, fasta_path)

    # comando diamond makedb
    cmd = [DIAMOND_BIN, "makedb", "--in", fasta_path, "-d", db_prefix]
    try:
        out = run_cmd(cmd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"diamond makedb failed: {e}")

    return {"status": "ok", "db_prefix": db_prefix, "diamond_stdout": out}

@router.post("/annotate")
def annotate(
    query: UploadFile,
    db_name: str = Form(...),
    max_targets: int = Form(5),
    use_emapper: bool = Form(False)
):
    """
    Faz busca com DIAMOND contra o DB custom e (opcional) tenta rodar emapper.py se instalado.
    - query: arquivo FASTA com suas sequências
    - db_name: prefixo do DB criado (ex: nome usado em /makedb)
    - max_targets: máximo de hits por sequência (diamond)
    - use_emapper: se True, tentará rodar emapper.py apontando para /data/databases
    """
    os.makedirs("/tmp", exist_ok=True)
    query_tmp = f"/tmp/{uuid.uuid4()}.faa"
    with open(query_tmp, "wb") as f:
        f.write(query.file.read())

    db_prefix = os.path.join(DATABASE_DIR, db_name)
    if not os.path.exists(db_prefix + ".dmnd") and not os.path.exists(db_prefix + ".dmnd.index") and not os.path.exists(db_prefix + ".00"): 
        # .dmnd is the typical Diamond suffix; different diamond versions may produce different files, this is a naive check
        raise HTTPException(status_code=400, detail=f"diamond DB not found for prefix: {db_prefix}")

    diamond_out = f"/tmp/diamond_out_{uuid.uuid4()}.m8"
    diamond_cmd = [
        DIAMOND_BIN, "blastp",
        "-d", db_prefix,
        "-q", query_tmp,
        "-o", diamond_out,
        "-f", "6",
        "--max-target-seqs", str(max_targets)
    ]

    try:
        diamond_stdout = run_cmd(diamond_cmd)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"diamond search failed: {e}")

    response = {
        "diamond_tsv_path": diamond_out,
        "diamond_stdout": diamond_stdout
    }

    # Se o usuário pedir, tenta rodar o emapper.py (se estiver disponível no container)
    if use_emapper and os.path.exists(EGGNOG_BIN):
        emapper_outdir = f"/tmp/emapper_out_{uuid.uuid4()}"
        os.makedirs(emapper_outdir, exist_ok=True)
        emapper_cmd = [
            EGGNOG_BIN,
            "-i", query_tmp,
            "--dbtype", "diamond",
            "--data_dir", DATABASE_DIR,
            "--output_dir", emapper_outdir,
            "--cpu", "2"
        ]
        try:
            emapper_stdout = run_cmd(emapper_cmd)
            response["emapper_stdout"] = emapper_stdout
            # listar arquivos gerados
            response["emapper_files"] = os.listdir(emapper_outdir)
        except Exception as e:
            response["emapper_error"] = str(e)

    # opcional: ler e devolver os primeiros N bytes do arquivo diamond_out para resposta
    try:
        with open(diamond_out, "r") as fh:
            sample = "".join([next(fh) for _ in range(50)]) if os.path.getsize(diamond_out) > 0 else ""
            response["diamond_preview"] = sample
    except Exception:
        response["diamond_preview"] = ""

    return response
