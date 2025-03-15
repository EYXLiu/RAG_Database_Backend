from fastapi import APIRouter, HTTPException
from sentence_transformers import SentenceTransformer

router = APIRouter()

@router.get("/sentence")
async def get():
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-base', trust_remote_code=True)
    query = "Yes"
    query_embd = embd.encode(query)
    return query_embd