from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.utils.auth import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.db import db  # your pymongo db instance
from datetime import datetime

router = APIRouter()

class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/client/signup")
def client_signup(user: UserSignup):
    existing = db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    db.users.insert_one({
        "email": user.email,
        "hashed_password": hashed,
        "role": "client",
        "is_verified": True,
        "created_at": datetime.utcnow()
    })
    # TODO: Send email verification link with encrypted URL
    return {"message": "Signup successful."}

@router.post("/ops/login")
def ops_login(user: UserLogin):
    db_user = db.users.find_one({"email": user.email, "role": "ops"})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.email, "role": "ops"})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/client/login")
def client_login(user: UserLogin):
    db_user = db.users.find_one({"email": user.email, "role": "client"})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not db_user.get("is_verified", False):
        raise HTTPException(status_code=400, detail="Email not verified")
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.email, "role": "client"})
    return {"access_token": token, "token_type": "bearer"}
