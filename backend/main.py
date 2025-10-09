from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError

import models, schemas, auth
from database import engine, get_db
from models import User, ShoutOut, ShoutOutRecipient

# ----------------------
# Create tables
# ----------------------
models.Base.metadata.create_all(bind=engine)

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="BragBoard API")

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Auth / Current User
# ----------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

# ----------------------
# Register
# ----------------------
@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = auth.create_access_token(user.email)
    refresh_token = auth.create_refresh_token(user.email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# ----------------------
# Refresh token
# ----------------------
from pydantic import BaseModel
class RefreshReq(BaseModel):
    refresh_token: str

@app.post("/refresh", response_model=schemas.Token)
def refresh_token(req: RefreshReq, db: Session = Depends(get_db)):
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
@app.get("/me", response_model=schemas.UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

# ----------------------
# List users
# ----------------------
@app.get("/users", response_model=List[schemas.UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).all()

# ----------------------
# List shoutouts
# ----------------------
@app.get("/shoutouts", response_model=List[schemas.ShoutoutResponse])
def list_shoutouts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(ShoutOut)
    if current_user.role != "admin" and current_user.department:
        query = query.join(ShoutOut.recipients)\
                     .join(ShoutOutRecipient.recipient)\
                     .filter(User.department == current_user.department)
    shoutouts = query.order_by(ShoutOut.created_at.desc()).all()

    # Attach sender info dynamically
    for s in shoutouts:
        if s.sender:
            s.sender_name = s.sender.name
            s.sender_role = s.sender.role.value if hasattr(s.sender.role, 'value') else s.sender.role
            s.sender_department = s.sender.department
        else:
            s.sender_name = "Unknown"
            s.sender_role = "Unknown"
            s.sender_department = "Unknown"

    return shoutouts

# ----------------------
# Create shoutout
# ----------------------
@app.post("/shoutouts", response_model=schemas.ShoutoutResponse)
def create_shoutout(
    shoutout: schemas.ShoutoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_shoutout = ShoutOut(
        sender_id=current_user.id,
        message=shoutout.message
    )
    db.add(new_shoutout)
    db.commit()
    db.refresh(new_shoutout)

    new_shoutout.department = current_user.department

    recipient_ids = shoutout.recipient_ids
    if not recipient_ids and current_user.department:
        users_in_dept = db.query(User).filter(User.department == current_user.department).all()
        recipient_ids = [u.id for u in users_in_dept]

    if recipient_ids:
        for rid in recipient_ids:
            db.add(ShoutOutRecipient(shoutout_id=new_shoutout.id, recipient_id=rid))
        db.commit()

    # Attach sender info dynamically
    new_shoutout.sender_name = current_user.name
    new_shoutout.sender_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    new_shoutout.sender_department = current_user.department

    return new_shoutout
