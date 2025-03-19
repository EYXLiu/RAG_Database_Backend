from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import os
import json
from dotenv import load_dotenv
import numpy as np
import ast
import redis 
import pickle
from datetime import datetime

router = APIRouter()

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

REDIS_HOST = os.getenv("NEXT_REDIS_HOST")
REDIS_PORT = os.getenv("NEXT_REDIS_PORT")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SentenceRequest(BaseModel):
    text: str
    
class SentenceUpload(BaseModel):
    title: str
    text: str
    
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def is_cache_stale():
    response = supabase.table("embd").select("last_updated").order("last_updated", desc=True).limit(1).execute()
    if not response.data:
        return True
    
    latest_timestamp = response.data[0]["last_updated"]
    cached_timestamp = redis_client.get("last_updated")
    
    if not cached_timestamp:
        return True
    
    return datetime.fromisoformat(latest_timestamp) > datetime.fromisoformat(cached_timestamp.decode())

def update_cache():
    print("caching")
    response = supabase.table("embd").select("*").execute()
    data = response.data
    embeddings = np.array([np.array(ast.literal_eval(record['embd']), dtype=np.float32) for record in data])
    
    latest = max(record['last_updated'] for record in data)
    
    redis_client.set("embeddings", pickle.dumps((embeddings, data)))
    redis_client.set("last_updated", latest)

@router.get("/sentence")
async def get(request: SentenceRequest):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    
    if is_cache_stale():
        update_cache()
        
    cached = pickle.loads(redis_client.get("embeddings"))
    
    embeddings, data = cached
    
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
