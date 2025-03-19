from fastapi import APIRouter, HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/test")
async def get():
    response = supabase.table("embd").select("*").execute()
    return response.data

@router.post("/test")
async def test():
    try:
        response = supabase.table("test").insert({ "value": "this" }).execute()
        return response.data
    except Exception as e:
        return HTTPException(status_code=500, detail=e)

@router.delete("/test")
async def dalete():
    response = supabase.table("test").delete().eq("value", "this").execute()
    return response.data