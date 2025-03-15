from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

router = APIRouter()

class SentenceRequest(BaseModel):
    text: str

@router.get("/sentence")
async def get(request: SentenceRequest):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True)
    query_embd = embd.encode(request.text)
    return { "embedding": query_embd.tolist() }