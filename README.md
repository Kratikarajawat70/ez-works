# EZ Works File Sharing API Task

A secure file sharing system with role-based access using FastAPI and SQLite. Supports two user types: **Ops Users** (uploaders) and **Client Users** (downloaders), featuring secure download links via encrypted URLs and JWT authentication.

---

## Features

- JWT-based authentication
- Ops User: Upload files (`.pptx`, `.docx`, `.xlsx`)
- Client User: Register, verify email, list & securely download files
- Fernet-encrypted download links
- SQLite database (easy setup, no server required)

---

## User Roles

### Ops User
- `/ops/signup` - Sign up as an Ops user
- `/login` - Login
- `/ops/upload` - Upload files (with JWT token)

### Client User
- `/client/signup` - Register
- /ops/signup` - ops Register
- `/client/verify/{token}` - Email verification
- `/login` - Login
- `/client/files` - List available files
- `/client/download/{file_id}` - Get encrypted download link
- `/client/secure-download/{enc}?token=JWT` - Secure file download

---

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLite](https://www.sqlite.org/index.html)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Fernet](https://cryptography.io/en/latest/fernet/)
- [JWT](https://pyjwt.readthedocs.io/)
- [Uvicorn](https://www.uvicorn.org/)

---

## Installation & Setup

### 1. Clone the repo
  git clone https://github.com/yourusername/secure-file-sharing-api.git
  cd secure-file-sharing-api

### 2. Create virtual environment and activate
  python3 -m venv venv
  source venv/bin/activate

### 3. Install dependencies
  pip install -r requirements.txt

### 4. Run the API
  uvicorn main:app --reload
  **Visit: http://127.0.0.1:8000/docs for Swagger UI.**
