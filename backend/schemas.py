# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: Optional[str] = None
    role: str

    class Config:
        # orm_mode for pydantic v1; if you run pydantic v2 this may not be required,
        # but it's compatible with most FastAPI setups.
        orm_mode = True
        # keep from_attributes for setups using Pydantic v2 (harmless in v1)
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

