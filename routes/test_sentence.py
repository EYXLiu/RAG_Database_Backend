from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import os
import json
from dotenv import load_dotenv
import numpy as np
import ast

router = APIRouter()

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SentenceRequest(BaseModel):
    text: str
    
class SentenceUpload(BaseModel):
    title: str
    text: str

@router.get("/sentence")
async def get(request: SentenceRequest):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    response = supabase.table('embd').select("*").execute()
    
    data = response.data
    
    embeddings = np.array([np.array(ast.literal_eval(record['embd']), dtype=np.float32) for record in data])
    
    def cosine_score(a, b):
        norm_a = np.linalg.norm(a) 
        norm_b = np.linalg.norm(b, axis=1)
        dot_product = np.dot(b, a) 
        scores = dot_product / (norm_b * norm_a)
        sorted_indices = np.argsort(scores)[::-1]  
        b = b[sorted_indices]
        top_n = min(5, len(sorted_indices))
        return [(data[i], float(scores[i])) for i in sorted_indices[:top_n]]
        
    query_embd = np.array(query_embd)
    
    cos = cosine_score(query_embd, embeddings)
    
    return {"matches": [{"text": match[0]['text'], "score": match[1]} for match in cos]}

@router.post("/sentence")
async def post(request: SentenceUpload):
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
