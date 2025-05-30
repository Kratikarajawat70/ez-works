from jose import jwt
from cryptography.fernet import Fernet
import os

SECRET_KEY = "myjwtsecret"
ALGORITHM = "HS256"
fernet = Fernet(Fernet.generate_key())
ALLOWED_EXTENSIONS = {"pptx", "docx", "xlsx"}

def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def encrypt_link(file_id: int):
    return fernet.encrypt(str(file_id).encode()).decode()

def decrypt_link(link: str):
    return int(fernet.decrypt(link.encode()).decode())

def allowed_file(filename):
    return filename.split('.')[-1] in ALLOWED_EXTENSIONS
