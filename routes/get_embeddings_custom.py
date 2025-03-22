from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import os
import json
from dotenv import load_dotenv
import numpy as np
import ast
import redis 
import pickle
from datetime import datetime

import sys
sys.path.append('../database')
from database import Database

router = APIRouter()

load_dotenv()

REDIS_HOST = os.getenv("NEXT_REDIS_HOST")
REDIS_PORT = os.getenv("NEXT_REDIS_PORT")

db = Database("custom", columns=['title', 'text', 'embd'], timestamp=True)

class SentenceRequest(BaseModel):
    text: str
    
class SentenceUpload(BaseModel):
    title: str
    text: str
    
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def cache_outdated():
    response = db.get(value='timestamp', sortby='timestamp', desc=True, top=1)
    assert len(response) == 1
    latest_timestamp = response[0]['timestamp']
    cached_timestamp = redis_client.get("last_updated")
    
    if not cached_timestamp:
        return False
    
    return latest_timestamp == cached_timestamp

def update_cache():
    response = db.get()
    embeddings = np.array([np.array(ast.literal_eval(record['embd']), dtype=np.float32) for record in response])
    
    latest = (db.get(value='timestamp', sortby='timestamp', desc=True, top=1))[0]['timestamp']
    
    redis_client.set("embeddings", pickle.dumps((embeddings, response)))
    redis_client.set("last_updated", latest)

@router.get("/dbembeddings")
async def get(request: SentenceRequest):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    
    if cache_outdated():
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

@router.post("/dbembeddings")
async def post(request: SentenceUpload):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    embedding = {
        "title": request.title,
        "text": request.text, 
        "embd": query_embd
    }
    try:
        response = db.post(embedding)
        return response
    except Exception as e:
        return HTTPException(status_code=500, detail=e)
