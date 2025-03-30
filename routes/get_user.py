from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import datetime
import redis

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from auth.client import Client

router = APIRouter()

load_dotenv()

REDIS_HOST = os.getenv("NEXT_REDIS_HOST")
REDIS_PORT = os.getenv("NEXT_REDIS_PORT")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

client = Client()

def blacklisted(token):
    return redis_client.exists(f"blacklist:{token}") > 0

class UserDetails(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(request: UserDetails):
    s = Client.signup(request.email, request.password)
    if "error" in s:
        return HTTPException(status_code=500, detail=s['error'])
    s['success'] = "User successfully signed up"
    return s

@router.get("/login")
def login(request: Request):
    email = request.query_params.get("email")
    password = request.query_params.get("password")
    s = Client.login(email, password)
    if "error" in s:
        return HTTPException(status_code=500, detail=s['error'])
    s['success'] = "User successfully logged in"
    return s

class UserLogout(BaseModel):
    email: str
    token: str

@router.post("/logout")
def logout(request: UserLogout):
    s = Client.logout(request.token)
    if "error" in s:
        return HTTPException(status_code=500, detail=s['error'])
    ttl = max(0, s['success'] - datetime.datetime.now(datetime.UTC()))
    redis_client.setex((f"blacklist:{request.token}", ttl))
    return { "success": "User successfully logged out" }


@router.get("/user/get")
def get(request: Request):
    token = request.query_params.get("jwt")
    s = Client.get_data(token)
    if "error" in s:
        return HTTPException(status_code=500, detail=s['error'])
    return s

class JWTToken(BaseModel):
    token: str
    new: str

@router.put("/user/update")
def update(request: JWTToken):
    s = Client.update_data(request.token, request.new)
    if "error" in s:
        return HTTPException(status_code=500, detail=s['error'])
    ttl = max(0, s['prev'] - datetime.datetime.now(datetime.UTC()))
    redis_client.setex((f"blacklist:{request.token}", ttl))
    return s