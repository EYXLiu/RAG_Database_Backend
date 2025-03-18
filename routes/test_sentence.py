from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from typing import List


router = APIRouter()

class SentenceRequest(BaseModel):
    embd: str

@router.get("/sentence")
async def get(request: SentenceRequest):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-base', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.embd)
    return { "embedding": query_embd }

@router.post("/sentence")
async def post(request: SentenceRequest):
    query_embd = request.embd
    return { "embedding": query_embd }