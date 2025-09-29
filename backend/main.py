# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError

import models, schemas, database, auth
from database import engine
from models import User

# create tables (dev). You can instead run create_tables.py if you prefer.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BragBoard API")

# Allow React dev server (change origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ----------------------
# Register
# ----------------------
@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = auth.hash_password(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        department=user.department
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ----------------------
# Login
# ----------------------
@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = auth.create_access_token(user.email)
    refresh_token = auth.create_refresh_token(user.email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# ----------------------
# Refresh tokens
# ----------------------
class RefreshRequest(schemas.BaseModel if hasattr(schemas, "BaseModel") else object):
    pass
# (we'll declare inline schema below instead of relying on the above hack)

from pydantic import BaseModel
class RefreshReq(BaseModel):
    refresh_token: str

@app.post("/refresh", response_model=schemas.Token)
def refresh_token(req: RefreshReq, db: Session = Depends(database.get_db)):
    try:
        payload = auth.decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token")
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    access_token = auth.create_access_token(email)
    refresh_token = auth.create_refresh_token(email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# ----------------------
# Get current user (protected)
# ----------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = auth.decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.get("/me", response_model=schemas.UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
