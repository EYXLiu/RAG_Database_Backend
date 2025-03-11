from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import wikipediaapi
from dotenv import load_dotenv

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hello from FastAPI!"}