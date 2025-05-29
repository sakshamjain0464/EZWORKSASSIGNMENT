# app/main.py
from fastapi import FastAPI
from app.db import connect_db
from app.routes import auth, upload, files


app = FastAPI()
app.include_router(auth.router)
app.include_router(upload.router) 
app.include_router(files.router)

connect_db()

@app.get("/")
def home():
    return {"message": "Secure File Sharing API Running 🚀"}


