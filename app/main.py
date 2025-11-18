from fastapi import FastAPI, Request, Depends
from app.auth import verify_api_key
from app.routers import blast, hmmer, diamond

app = FastAPI()

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    await verify_api_key(request)
    return await call_next(request)

app.include_router(blast.router)
app.include_router(hmmer.router)
app.include_router(diamond.router)

@app.get("/")
def root():
    return {"status": "online"}
