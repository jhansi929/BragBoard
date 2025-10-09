from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ----------------------
# User Schemas
# ----------------------
class UserBase(BaseModel):
    name: str
    email: str
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

# ----------------------
# Token Schema
# ----------------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# ----------------------
# Shoutout Schemas
# ----------------------
class ShoutoutBase(BaseModel):
    message: str
    recipient_ids: Optional[List[int]] = []

class ShoutoutCreate(ShoutoutBase):
    department: Optional[str] = None

class ShoutoutResponse(ShoutoutBase):
    id: int
    sender_id: int
    sender_name: str
    sender_role: str
    sender_department: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
