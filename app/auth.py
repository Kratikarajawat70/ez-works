from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app import models as db_models, schemas as api_schemas, utils as helper
from app.database import get_db_session
from app.config import settings as config_settings

router = APIRouter(prefix="/auth", tags=["User Auth"])

def trigger_email_verification(recipient: str, token_id: str):
    verification_url = f"http://127.0.0.1:8000/auth/verify-email?token={token_id}"
    print(f"[Email Verification] Send to {recipient}: {verification_url}")

@router.post("/signup", response_model=api_schemas.Token)
def register_user(payload: api_schemas.UserCreate, bg_tasks: BackgroundTasks, db: Session = Depends(get_db_session)):
    if db.query(db_models.User).filter(db_models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="This email is already in use.")
    
    hashed_pass = helper.hash_password(payload.password)
    new_user = db_models.User(
        email=payload.email,
        name=payload.name,
        hashed_password=hashed_pass,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = helper.create_verification_token(new_user.email)
    bg_tasks.add_task(trigger_email_verification, new_user.email, token)

    return helper.create_auth_token(new_user)

@router.get("/verify-email")
def confirm_email_token(token: str, db: Session = Depends(get_db_session)):
    user_email = helper.decode_verification_token(token)
    user_entry = db.query(db_models.User).filter(db_models.User.email == user_email).first()

    if not user_entry:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    user_entry.is_verified = True
    db.commit()

    return {"message": "Email successfully verified!"}

@router.post("/login", response_model=api_schemas.Token)
def login_user(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    user = db.query(db_models.User).filter(db_models.User.email == credentials.username).first()

    if not user or not helper.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify to proceed.")
    
    return helper.create_auth_token(user)
