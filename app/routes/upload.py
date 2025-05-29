from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os
from uuid import uuid4
from datetime import datetime
from app.db import db
from app.utils.security import get_current_user


router = APIRouter()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"pptx", "docx", "xlsx", "pdf"}

def allowed_file(filename: str) -> bool:
    return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Only Ops User allowed
    if current_user.get("role") != "ops":
        raise HTTPException(status_code=403, detail="Only Ops users can upload files")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only .pptx, .docx, .xlsx files are allowed")

    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Create unique file name
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid4().hex}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Save metadata to DB
    metadata = {
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "upload_time": datetime.utcnow(),
        "uploaded_by": current_user["email"],
        "file_type": file_ext
    }
    result = db.files.insert_one(metadata)

    return {
        "message": "File uploaded successfully",
        "file_id": str(result.inserted_id),
        "filename": file.filename
    }
