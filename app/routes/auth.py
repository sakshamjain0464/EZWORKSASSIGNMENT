from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.utils.auth import hash_password, verify_password
from app.utils.jwt import create_access_token, create_email_verification_token, decode_token
from app.db import db  
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
        "is_verified": False,
        "created_at": datetime.utcnow()
    })

    token = create_email_verification_token(user.email)
    verification_link = f"https://ezworksassignment.onrender.com/verify-email?token={token}"

    return {
        "message": "Signup successful. Please verify your email.",
        "verification_link": verification_link 
    }

@router.post("/ops/login")
def ops_login(user: UserLogin):
    db_user = db.users.find_one({"email": user.email, "role": "ops"})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.email, "role": "ops"})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/verify-email")
def verify_email(token: str = Query(...)):
    try:
        payload = decode_token(token)
        if payload.get("purpose") != "email_verification":
            raise HTTPException(status_code=400, detail="Invalid token purpose")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        result = db.users.update_one({"email": email}, {"$set": {"is_verified": True}})
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="User not found or already verified")

        return {"message": "✅ Email verified successfully!"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token error: {str(e)}")

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
