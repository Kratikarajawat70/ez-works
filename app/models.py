from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    is_client = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    uploaded_by = Column(Integer)
