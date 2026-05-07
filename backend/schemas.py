from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ===============================
# USER SCHEMAS
# ===============================

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
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ===============================
# TOKEN SCHEMA
# ===============================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    role: str                # ✅ added
    name: str                # ✅ added
    message: Optional[str] = None  # ✅ added

    class Config:
        orm_mode = True



# ===============================
# SHOUTOUT SCHEMAS
# ===============================

class ShoutoutBase(BaseModel):
    message: str
    recipient_ids: List[int] = Field(default_factory=list)
    image_url: Optional[str] = None  # ✅ Added for returning image path


class ShoutoutCreate(ShoutoutBase):
    department: Optional[str] = None


class ShoutoutResponse(ShoutoutBase):
    id: int
    sender_id: int
    sender_name: str
    sender_role: Optional[str] = None
    sender_department: Optional[str] = None
    created_at: Optional[datetime] = None
    recipient_names: List[str] = Field(default_factory=list)

    # New fields for reactions
    reactions: Dict[str, int] = Field(default_factory=dict)  # e.g., {"like": 3, "clap": 1}
    user_reactions: List[str] = Field(default_factory=list)  # e.g., ["like"]

    class Config:
        orm_mode = True


# ===============================
# COMMENT SCHEMAS
# ===============================
# in schemas.py
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    password: Optional[str] = None

# ===============================
# COMMENT SCHEMAS
# ===============================

class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    shoutout_id: int  # ✅ include shoutout id


class CommentResponse(CommentBase):
    id: int
    shoutout_id: int
    user_id: int
    user_name: str
    created_at: datetime

    class Config:
        orm_mode = True


# ===============================
# REACTION SCHEMA
# ===============================
class ReactionResponse(BaseModel):
    id: int
    type: str
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
