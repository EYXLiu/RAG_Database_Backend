from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import get_embeddings, get_embeddings_custom, get_user

app = FastAPI()

app.include_router(get_embeddings.router)
app.include_router(get_embeddings_custom.router)
app.include_router(get_user.router)

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