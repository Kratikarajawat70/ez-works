import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app import models as db_models, helper, auth
from app.database import get_db_session
from app.schemas import FileInfo

router = APIRouter(prefix="/docs", tags=["Documents"])

DOCS_DIR = "uploaded_docs"
os.makedirs(DOCS_DIR, exist_ok=True)

ALLOWED_TYPES = {".pptx", ".docx", ".xlsx"}

def is_valid_extension(name: str) -> bool:
    return any(name.endswith(ext) for ext in ALLOWED_TYPES)

@router.post("/upload")
def handle_upload(
    doc: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user: db_models.User = Depends(auth.require_ops_user)
):
    if not is_valid_extension(doc.filename):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    save_path = os.path.join(DOCS_DIR, f"{datetime.utcnow().timestamp()}_{doc.filename}")
    with open(save_path, "wb") as file_obj:
        file_obj.write(doc.file.read())

    file_record = db_models.File(
        filename=doc.filename,
        filepath=save_path,
        user_id=current_user.id
    )
    db.add(file_record)
    db.commit()
    return {"message": "Upload completed"}

@router.get("/all", response_model=List[FileInfo])
def fetch_files(
    db: Session = Depends(get_db_session),
    current_user: db_models.User = Depends(auth.require_verified_user)
):
    return db.query(db_models.File).all()

@router.get("/get-link")
def prepare_download_link(
    file_id: int,
    db: Session = Depends(get_db_session),
    current_user: db_models.User = Depends(auth.require_verified_user)
):
    target = db.query(db_models.File).filter(db_models.File.id == file_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="File entry not found")

    token_data = f"{file_id}:{current_user.id}"
    encrypted_token = helper.secure_string(token_data)
    link = f"http://localhost:8000/docs/download?token={encrypted_token}"
    return {"download_url": link}

@router.get("/download")
def serve_download(
    token: str,
    request: Request,
    db: Session = Depends(get_db_session)
):
    try:
        raw = helper.retrieve_string(token)
        fid_str, uid_str = raw.split(":")
        file_id = int(fid_str)
        token_uid = int(uid_str)

        jwt = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not jwt:
            raise HTTPException(status_code=401, detail="Token missing")

        payload = helper.decode_token(jwt)
        actual_uid = payload.get("user_id")

        if actual_uid != token_uid:
            raise HTTPException(status_code=403, detail="Access denied")

        file_entry = db.query(db_models.File).filter(db_models.File.id == file_id).first()

        if not file_entry or not os.path.exists(file_entry.filepath):
            raise HTTPException(status_code=404, detail="File unavailable")

        return FileResponse(path=file_entry.filepath, filename=file_entry.filename)

    except Exception as err:
        print("File access error:", err)
        raise HTTPException(status_code=400, detail="Invalid or expired token")
