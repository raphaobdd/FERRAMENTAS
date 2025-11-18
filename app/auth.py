from fastapi import Request, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise Exception("API_KEY missing from .env")

async def verify_api_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
