from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.auth.oauth2 import get_current_user  # Your auth dependency
from typing import List
import os
from uuid import uuid4
from app.database import file_collection  # Your MongoDB collection

router = APIRouter()

ALLOWED_EXTENSIONS = {"pptx", "docx", "xlsx"}
UPLOAD_DIR = "uploads"  # Ensure this folder exists or create it at startup

def allowed_file(filename: str) -> bool:
    return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # Only Ops User allowed (you can check user role here)
    if current_user.get("role") != "ops":
        raise HTTPException(status_code=403, detail="Only Ops users can upload files")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")

    # Create uploads folder if not exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save file with a unique name to avoid conflicts
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid4().hex}.{file_ext}"
    file_location = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file to disk
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    # Save file metadata to DB (example schema)
    file_metadata = {
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "upload_time":  datetime.utcnow(),
        "uploaded_by": current_user["email"],
        "file_type": file_ext,
        # Add other info as needed, like access permissions
    }
    result = await file_collection.insert_one(file_metadata)

    return {"message": "File uploaded successfully", "file_id": str(result.inserted_id)}
