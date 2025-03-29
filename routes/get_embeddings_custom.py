from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import numpy as np
import redis 
import pickle
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.database import Database

router = APIRouter()

load_dotenv()

REDIS_HOST = os.getenv("NEXT_REDIS_HOST")
REDIS_PORT = os.getenv("NEXT_REDIS_PORT")
    
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

db = Database("custom", columns=['title', 'text', 'embd'], timestamp=True)

def cache_outdated():
    response = db.get(value='timestamp', sortby='timestamp', desc=True, top=1)
    
    if len(response) == 0:
        return False
    
    latest_timestamp = response[0]['timestamp']
    cached_timestamp = redis_client.get("last_updated")
    
    if not cached_timestamp:
        return False
    
    return latest_timestamp == cached_timestamp

def update_cache():
    response = db.get()
    embeddings = np.array([np.array((list(record.values())[0]['embd']), dtype=np.float32) for record in response])
    
    if len(response) == 0:
        latest = datetime.now().isoformat()
    else:
        latest = (db.get(value='timestamp', sortby='timestamp', desc=True, top=1))[0]['timestamp']
    
    redis_client.set("embeddings", pickle.dumps((embeddings, response)))
    redis_client.set("last_updated", latest)

class SentenceGet(BaseModel):
    text: str
    
@router.get("/dbembeddings")
async def get(request: SentenceGet):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    
    if not cache_outdated():
        update_cache()
        
    cached = pickle.loads(redis_client.get("embeddings"))
    
    embeddings, data = cached
    
    if len(data) == 0:
        return {}
    
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
    
    return {"matches": [{"text": list(match[0].values())[0]['text'], "score": match[1]} for match in cos]}


class SentencePost(BaseModel):
    title: str
    text: str

@router.post("/dbembeddings")
async def post(request: SentencePost):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    
    embedding = {
        "title": request.title,
        "text": request.text, 
        "embd": query_embd
    }
    try:
        db.post(embedding)
        return request
    except Exception as e:
        return HTTPException(status_code=500, detail=e)


class SentenceUpdate(BaseModel):
    key: int
    title: str
    text: str

@router.put("/dbembeddings")
async def update(request: SentenceUpdate):
    embd = SentenceTransformer(model_name_or_path='Lajavaness/bilingual-embedding-small', trust_remote_code=True, device='cpu')
    query_embd = embd.encode(request.text).tolist()
    
    embedding = {
        "title": request.title,
        "text": request.text, 
        "embd": query_embd
    }
    try:
        db.update(request.key, embedding)
        return request
    except Exception as e:
        return HTTPException(status_code=500, detail=e)


class SentenceDelete(BaseModel):
    key: int
    
@router.delete("/dbembeddings")
async def delete(request: SentenceDelete):
    try:
        response = db.delete(request.key)
        return response
    except Exception as e:
        return HTTPException(status_code=500, detail=e)