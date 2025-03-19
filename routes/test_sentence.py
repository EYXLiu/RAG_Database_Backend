from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import os
import json
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SentenceRequest(BaseModel):
    title: str
    text: str

@router.get("/sentence")
async def get():
    response = supabase.table("embd").select("*").execute()
    return response.data

@router.post("/sentence")
async def post(request: SentenceRequest):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    embedding = {
        "title": request.title,
        "text": request.text, 
        "embd": query_embd
    }
    try:
        response = supabase.table("embd").insert(embedding).execute()
        return response.data
    except Exception as e:
        return HTTPException(status_code=500, detail=e)
