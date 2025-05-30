from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, File as FileModel
from schemas import UserCreate, UserLogin
from utils import *
import shutil, os

Base.metadata.create_all(bind=engine)
app = FastAPI()
UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/ops/signup")
def ops_signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(
        email=user.email,
        password=user.password,  # ⚠️ You should hash this in production
        is_client=False,         # 🛑 Important: Ops user
        is_verified=True         # No email verification required for Ops
    )
    db.add(new_user)
    db.commit()
    token = create_token({
        "email": new_user.email,
        "id": new_user.id,
        "is_client": new_user.is_client
    })
    return {
        "message": "Ops user created",
        "token": token
    }

# Sign Up (Client Only)
@app.post("/client/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(email=user.email, password=user.password, is_client=True)
    db.add(new_user)
    db.commit()
    link = create_token({"email": user.email})
    return {"verify_url": f"/client/verify/{link}"}

# Email Verification
@app.get("/client/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    data = verify_token(token)
    user = db.query(User).filter_by(email=data["email"]).first()
    if user:
        user.is_verified = True
        db.commit()
    return {"message": "Verified"}

# Login
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(email=user.email, password=user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid")
    token = create_token({"email": db_user.email, "id": db_user.id, "is_client": db_user.is_client})
    return {"token": token}

# Upload File (Ops Only)
@app.post("/ops/upload")
def upload(token: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = verify_token(token)
    if user["is_client"]:
        raise HTTPException(status_code=403, detail="Not allowed")
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db.add(FileModel(filename=file.filename, uploaded_by=user["id"]))
    db.commit()
    return {"message": "Uploaded"}

# List Files (Client)
@app.get("/client/files")
def list_files(token: str, db: Session = Depends(get_db)):
    user = verify_token(token)
    if not user["is_client"]:
        raise HTTPException(status_code=403, detail="Clients only")
    files = db.query(FileModel).all()
    return [{"id": f.id, "name": f.filename} for f in files]

# Generate Download Link
@app.get("/client/download/{file_id}")
def get_link(file_id: int, token: str, db: Session = Depends(get_db)):
    user = verify_token(token)
    if not user["is_client"]:
        raise HTTPException(status_code=403, detail="Clients only")
    encrypted = encrypt_link(file_id)
    return {"download-link": f"/client/secure-download/{encrypted}"}

# Actual File Download
@app.get("/client/secure-download/{enc}")
def secure_download(enc: str, token: str, db: Session = Depends(get_db)):
    user = verify_token(token)
    if not user["is_client"]:
        raise HTTPException(status_code=403, detail="Clients only")
    file_id = decrypt_link(enc)
    file = db.query(FileModel).filter_by(id=file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    path = os.path.join(UPLOAD_DIR, file.filename)
    return FileResponse(path, filename=file.filename)

