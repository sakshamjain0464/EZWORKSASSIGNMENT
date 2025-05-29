from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from typing import List
from bson.objectid import ObjectId

from app.utils.jwt import create_file_download_token, verify_file_download_token
from app.utils.security import get_current_user  # your existing auth dependency
from app.db import db  # MongoDB client

router = APIRouter(prefix="/client/files", tags=["files"])

@router.get("/", response_model=List[dict])
def list_client_files(current_user = Depends(get_current_user)):
    if current_user.get("role") != "client":
        raise HTTPException(status_code=403, detail="Access denied")

    # Mongo query to fetch files where owner_id == current_user.id
    files_cursor = db.files.find({"email": current_user.get("sub")})

    response = []
    for file_doc in files_cursor:
        file_id_str = str(file_doc["_id"])
        token = create_file_download_token(current_user.get("sub"), file_id_str)
        download_token = token
        response.append({
            "id": file_id_str,
            "filename": file_doc["original_filename"],
            "uploaded_at": file_doc.get("uploaded_at"),
            "download_token": download_token,
            "download_url": f"https://ezworksassignment.onrender.com/client/files/download?token={download_token}"
        })
    return response


@router.get("/download")
def download_file(token: str = Query(...), current_user = Depends(get_current_user)):

    try:
        payload = verify_file_download_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if payload.get("role") != "client":
        raise HTTPException(status_code=403, detail="Invalid role in token")

    if payload.get("user_id") != current_user.get("sub"):   
        raise HTTPException(status_code=403, detail="Token user mismatch")
    print("Payload", payload)
    file_id = payload.get("file_id")

    # Validate and fetch file from MongoDB
    try:
        obj_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file ID")

    file_doc = db.files.find_one({"_id": obj_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = file_doc.get("stored_filename")
    if not file_path:
        raise HTTPException(status_code=500, detail="File path missing")

    return FileResponse("./uploads/"+file_path, filename=file_doc["original_filename"], media_type="application/octet-stream")
