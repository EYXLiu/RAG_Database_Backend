from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from typing import List


router = APIRouter()

class SentenceRequest(BaseModel):
    embd: List[str]

@router.get("/sentence")
async def get(request: SentenceRequest):
    query_embd = request.embd
    print(query_embd)
    return { "embedding": query_embd }

@router.post("/sentence")
async def post(request: SentenceRequest):
    query_embd = request.embd
    return { "embedding": query_embd }