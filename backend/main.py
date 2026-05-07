# main.py
# main.py
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError
from datetime import date
from sqlalchemy import func
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import uuid
from pathlib import Path
import json
import shutil  # fallback for file writing
from schemas import CommentCreate, CommentResponse
from schemas import UpdateProfileRequest
from schemas import ReactionResponse  # kept import (safe)
import aiofiles
from fastapi import status 
from models import Report
from fastapi.responses import Response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


import models, schemas, auth
from database import engine, Base, get_db
from auth import decode_token
from models import User, ShoutOut, ShoutOutRecipient, Comment, Reaction
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")

# ---------------- Setup ----------------

app = FastAPI(title="BragBoard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ---------------- Helper ----------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id_int = int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise credentials_exception
    return user

# ---------------- Register (Employee) ----------------
@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pw,
        department=user_data.department,
        role="employee",  # default role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ---------------- Register Admin ----------------
@app.post("/register-admin", response_model=schemas.UserResponse, status_code=201)
def register_admin(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new admin user. Only allowed if no admin exists yet OR existing admin creates.
    """
    existing_admin = db.query(User).filter(User.role == "admin").first()
    if existing_admin:
        raise HTTPException(status_code=403, detail="Admin already exists. Contact system admin.")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user_data.password)
    new_admin = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pw,
        department=user_data.department,
        role="admin",
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# ---------------- Login ----------------
@app.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not auth.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth.create_access_token(subject=str(user.id))
    refresh_token = auth.create_refresh_token(subject=str(user.id))

    # ✅ Include role and name so frontend knows if it's admin
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "name": user.name,
        "message": "Login successful"
    }


# ---------------- /me ----------------
@app.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user




# ---------------- users/department ----------------
@app.get("/users/department", response_model=List[schemas.UserResponse])
def get_users_in_department(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.department:
        raise HTTPException(status_code=400, detail="User has no department set")

    users = (
        db.query(User)
        .filter(User.department == current_user.department, User.id != current_user.id)
        .all()
    )
    return users


# ---------------- Post shoutout with file upload ----------------
@app.post("/shoutouts", response_model=schemas.ShoutoutResponse, status_code=201)
async def post_shoutout(
    message: str = Form(...),
    recipient_ids: Optional[str] = Form("[]"),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts form-data:
      - message (str)
      - recipient_ids (JSON string of list of ints, e.g. "[1,2]")
      - file (optional upload)
    """
    recipient_ids_list = []
    try:
        recipient_ids_list = json.loads(recipient_ids)
        if not isinstance(recipient_ids_list, list):
            recipient_ids_list = []
    except Exception:
        recipient_ids_list = []

    # Save uploaded file if present (async)
    image_url = None
    if file:
        # sanitize filename by taking base name and prefixing with uuid
        filename = Path(file.filename).name
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    await out_file.write(chunk)
            image_url = f"/uploads/{unique_name}"
        except Exception:
            # fallback to blocking write (should rarely happen)
            file.file.seek(0)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_url = f"/uploads/{unique_name}"

    new_shoutout = ShoutOut(
        message=message, sender_id=current_user.id, image_url=image_url
    )
    db.add(new_shoutout)
    db.commit()
    db.refresh(new_shoutout)

    if recipient_ids_list:
        for rid in recipient_ids_list:
            try:
                rid_int = int(rid)
            except (TypeError, ValueError):
                continue
            db.add(ShoutOutRecipient(shoutout_id=new_shoutout.id, recipient_id=rid_int))
        db.commit()

    recipients = (
        db.query(User)
        .join(ShoutOutRecipient, User.id == ShoutOutRecipient.recipient_id)
        .filter(ShoutOutRecipient.shoutout_id == new_shoutout.id)
        .all()
    )
    recipient_names = [r.name for r in recipients]

    return schemas.ShoutoutResponse(
        id=new_shoutout.id,
        message=new_shoutout.message,
        sender_id=current_user.id,
        sender_name=current_user.name,
        sender_role=current_user.role,
        sender_department=current_user.department,
        created_at=new_shoutout.created_at,
        recipient_names=recipient_names,
        image_url=image_url,
        reactions={},  # empty initially
        user_reactions=[],
    )


# ---------------- Get shoutouts (feed) ----------------
@app.get("/shoutouts", response_model=List[schemas.ShoutoutResponse])
def get_shoutouts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shoutouts = (
        db.query(ShoutOut)
        .join(User, ShoutOut.sender_id == User.id)
        .filter(User.department == current_user.department)
        .order_by(ShoutOut.created_at.desc())
        .all()
    )

    response = []
    for s in shoutouts:
        sender = db.query(User).filter(User.id == s.sender_id).first()
        recipients = (
            db.query(User)
            .join(ShoutOutRecipient, User.id == ShoutOutRecipient.recipient_id)
            .filter(ShoutOutRecipient.shoutout_id == s.id)
            .all()
        )
        recipient_names = [r.name for r in recipients]

        # reactions for this shoutout
        reactions_objs = db.query(Reaction).filter(Reaction.shoutout_id == s.id).all()
        reactions_counts = {}
        user_reacts = []
        for r in reactions_objs:
            reactions_counts[r.type] = reactions_counts.get(r.type, 0) + 1
            if r.user_id == current_user.id:
                user_reacts.append(r.type)

        response.append(
            schemas.ShoutoutResponse(
                id=s.id,
                message=s.message,
                sender_id=s.sender_id,
                sender_name=(sender.name if sender else "Unknown"),
                sender_role=(sender.role if sender else "Unknown"),
                sender_department=(sender.department if sender else None),
                created_at=s.created_at,
                recipient_names=recipient_names,
                image_url=s.image_url,
                reactions=reactions_counts,
                user_reactions=user_reacts,
            )
        )
    return response


# ---------------- Dashboard & Others (unchanged) ----------------
# ---------------- Dashboard stats ----------------
@app.get("/dashboard-stats")
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()

    print("🟡 Logged in user:", current_user.id, current_user.name, current_user.department)

    my_total_shoutouts = (
        db.query(ShoutOut)
        .filter(ShoutOut.sender_id == current_user.id)
        .count()
    )

    my_today_shoutouts = (
        db.query(ShoutOut)
        .filter(
            ShoutOut.sender_id == current_user.id,
            func.date(ShoutOut.created_at) == today
        )
        .count()
    )

    team_today_shoutouts = (
        db.query(ShoutOut)
        .join(User, ShoutOut.sender_id == User.id)
        .filter(
            User.department == current_user.department,
            ShoutOut.sender_id != current_user.id,
            func.date(ShoutOut.created_at) == today
        )
        .count()
    )

    team_members = (
    db.query(User)
    .filter(
        User.department == current_user.department,
        User.id != current_user.id
    )
    .count()
)

   

    recent_shoutouts = (
        db.query(ShoutOut)
        .join(User, ShoutOut.sender_id == User.id)
        .filter(User.department == current_user.department)
        .order_by(ShoutOut.created_at.desc())
        .limit(5)
        .all()
    )

    
    return {
    "total_shoutouts": my_total_shoutouts,
    "posts_today": my_today_shoutouts + team_today_shoutouts,
    "team_members": team_members,  # ✅ renamed field
    "recent_activity": [
        {
            "sender_name": db.query(User).filter(User.id == s.sender_id).first().name,
            "message": s.message,
            "created_at": s.created_at.isoformat(),
        }
        for s in recent_shoutouts
    ],
}


# ---------------- Reaction endpoint (toggle) (kept for backward compatibility) ----------------
@app.post("/react/{shoutout_id}")
def react_to_shoutout(shoutout_id: int, payload: dict = Body(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Toggle a reaction for the current user on a shoutout.
    Body: {"reaction": "like"}  # allowed values: "like", "clap", "star" (frontend decides)
    Response: latest reaction counts + user's reactions for this shoutout
    """
    reaction_type = (payload.get("reaction") or "").strip()
    if not reaction_type:
        raise HTTPException(status_code=400, detail="Reaction type required")

    shoutout = db.query(ShoutOut).filter(ShoutOut.id == shoutout_id).first()
    if not shoutout:
        raise HTTPException(status_code=404, detail="ShoutOut not found")

    # Check if user already has this reaction on this shoutout
    existing = (
        db.query(Reaction)
        .filter(Reaction.shoutout_id == shoutout_id, Reaction.user_id == current_user.id, Reaction.type == reaction_type)
        .first()
    )

    if existing:
        # toggle off -> delete
        db.delete(existing)
        db.commit()
    else:
        # add reaction
        new_react = Reaction(type=reaction_type, user_id=current_user.id, shoutout_id=shoutout_id)
        db.add(new_react)
        db.commit()

    # return latest counts and user's reactions
    reactions_objs = db.query(Reaction).filter(Reaction.shoutout_id == shoutout_id).all()
    reactions_counts = {}
    user_reacts = []
    for r in reactions_objs:
        reactions_counts[r.type] = reactions_counts.get(r.type, 0) + 1
        if r.user_id == current_user.id:
            user_reacts.append(r.type)

    # return shape frontend expects
    return {"counts": reactions_counts, "user_reacted": user_reacts}


# ---------------- New: GET reactions for a shoutout (matches frontend getReactionsFor) ----------------
@app.get("/reactions/{shoutout_id}")
def get_reactions(shoutout_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns a summary for the shoutout:
      { counts: { like: n, ... }, user_reacted: ["like", ...] }
    This matches the frontend helper getReactionsFor(shoutoutId).
    """
    shoutout = db.query(ShoutOut).filter(ShoutOut.id == shoutout_id).first()
    if not shoutout:
        raise HTTPException(status_code=404, detail="ShoutOut not found")

    reactions_objs = db.query(Reaction).filter(Reaction.shoutout_id == shoutout_id).order_by(Reaction.created_at.asc()).all()

    reactions_counts = {}
    user_reacted = []
    for r in reactions_objs:
        reactions_counts[r.type] = reactions_counts.get(r.type, 0) + 1
        if r.user_id == current_user.id:
            user_reacted.append(r.type)

    return {"counts": reactions_counts, "user_reacted": user_reacted}


# ---------------- New: Toggle reaction (matches frontend toggleReaction) ----------------
@app.post("/reactions/toggle")
def toggle_reaction(payload: dict = Body(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Frontend expects:
      POST /reactions/toggle
      body: { shoutout_id: <int>, type: "<like|clap|star>" }
    This endpoint toggles the specified reaction for the current user.
    Returns latest counts and user's reactions for the shoutout.
    """
    shoutout_id = payload.get("shoutout_id")
    reaction_type = (payload.get("type") or "").strip()
    if not shoutout_id or not reaction_type:
        raise HTTPException(status_code=400, detail="shoutout_id and type are required")

    # ensure shoutout exists
    shoutout = db.query(ShoutOut).filter(ShoutOut.id == shoutout_id).first()
    if not shoutout:
        raise HTTPException(status_code=404, detail="ShoutOut not found")

    # normalize reaction_type (do not alter semantics used elsewhere)
    reaction_type = reaction_type

    # find existing reaction of this type by this user on this shoutout
    existing = (
        db.query(Reaction)
        .filter(Reaction.shoutout_id == shoutout_id, Reaction.user_id == current_user.id, Reaction.type == reaction_type)
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()
    else:
        new_react = Reaction(type=reaction_type, user_id=current_user.id, shoutout_id=shoutout_id)
        db.add(new_react)
        db.commit()

    # build counts and user_reactions
    reactions_objs = db.query(Reaction).filter(Reaction.shoutout_id == shoutout_id).all()
    reactions_counts = {}
    user_reacts = []
    for r in reactions_objs:
        reactions_counts[r.type] = reactions_counts.get(r.type, 0) + 1
        if r.user_id == current_user.id:
            user_reacts.append(r.type)

    # return shape frontend expects
    return {"counts": reactions_counts, "user_reacted": user_reacts}


# ---------------- Update profile ----------------

@app.put("/update-profile", response_model=schemas.UserResponse)
def update_profile(
    payload: UpdateProfileRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if payload.name:
            current_user.name = payload.name
        if payload.department:
            current_user.department = payload.department
        if payload.password:
            current_user.password = auth.hash_password(payload.password)

        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        print("❌ Error updating profile:", e)
        raise HTTPException(status_code=500, detail="Error updating profile")

from fastapi import Body

@app.post("/refresh", response_model=schemas.Token)
def refresh_token(
    refresh_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token missing")

    try:
        payload = auth.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = auth.create_access_token(subject=str(user.id))
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        print("❌ Refresh token error:", e)
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

# ---------------- Delete account ----------------
@app.delete("/delete-account")
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}
# ---------------- COMMENTS FEATURE ----------------


@app.post("/comments", response_model=CommentResponse)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not comment.content or not comment.shoutout_id:
        raise HTTPException(status_code=400, detail="Missing comment content or shoutout_id")

    shoutout = db.query(ShoutOut).filter(ShoutOut.id == comment.shoutout_id).first()
    if not shoutout:
        raise HTTPException(status_code=404, detail="ShoutOut not found")

    new_comment = Comment(
        content=comment.content,
        user_id=current_user.id,
        shoutout_id=comment.shoutout_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentResponse(
        id=new_comment.id,
        shoutout_id=comment.shoutout_id,
        content=new_comment.content,
        user_id=current_user.id,
        user_name=current_user.name,
        created_at=new_comment.created_at,
    )


@app.get("/comments/{shoutout_id}", response_model=List[CommentResponse])
def get_comments(shoutout_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(Comment)
        .join(User, Comment.user_id == User.id)
        .filter(Comment.shoutout_id == shoutout_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return [
        CommentResponse(
            id=c.id,
            shoutout_id=shoutout_id,
            content=c.content,
            user_id=c.user_id,
            user_name=c.user.name,
            created_at=c.created_at,
        )
        for c in comments
    ]
# ---------------- Admin Dashboard: Top Contributors & Most Tagged ----------------
# ---------------- Admin Dashboard: Top Contributors & Most Tagged ----------------
@app.get("/admin/dashboard")
def admin_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # ✅ Only allow admin users
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    # ---- Top Contributors: users who sent the most shoutouts ----
    top_contributors = (
        db.query(User.name, func.count(ShoutOut.id).label("total_shoutouts"))
        .outerjoin(ShoutOut, User.id == ShoutOut.sender_id)
        .group_by(User.id)
        .having(func.count(ShoutOut.id) > 0)  # only show users with shoutouts
        .order_by(func.count(ShoutOut.id).desc())
        .limit(5)
        .all()
    )

    # ---- Most Tagged: users who are recipients the most times ----
    most_tagged = (
        db.query(User.name, func.count(ShoutOutRecipient.id).label("times_tagged"))
        .outerjoin(ShoutOutRecipient, User.id == ShoutOutRecipient.recipient_id)
        .group_by(User.id)
        .having(func.count(ShoutOutRecipient.id) > 0)  # only show users who were tagged
        .order_by(func.count(ShoutOutRecipient.id).desc())
        .limit(5)
        .all()
    )

    # Convert query results into plain dicts for frontend
    return {
        "top_contributors": [
            {"name": name, "total_shoutouts": total} for name, total in top_contributors
        ],
        "most_tagged": [
            {"name": name, "times_tagged": total} for name, total in most_tagged
        ],
    }
# Delete shoutout
# Delete shoutout


@app.delete("/shoutouts/{shoutout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shoutout(shoutout_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shoutout = db.query(ShoutOut).filter(ShoutOut.id == shoutout_id).first()
    if not shoutout:
        raise HTTPException(status_code=404, detail="Shoutout not found")
    
    if shoutout.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.query(Comment).filter(Comment.shoutout_id == shoutout_id).delete(synchronize_session=False)
    db.delete(shoutout)
    db.commit()
    return

@app.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(comment)
    db.commit()
    return 


@app.post("/reports", status_code=201)
def report_shoutout(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shoutout_id = payload.get("shoutout_id")
    reason = payload.get("reason", "Inappropriate content")

    # Validate shoutout
    shoutout = db.query(ShoutOut).filter(ShoutOut.id == shoutout_id).first()
    if not shoutout:
        raise HTTPException(status_code=404, detail="Shoutout not found")

    # Prevent reporting own post
    if shoutout.sender_id == current_user.id:
        raise HTTPException(status_code=403, detail="You cannot report your own shoutout")

    # Prevent duplicate reports
    existing = (
        db.query(Report)
        .filter(Report.shoutout_id == shoutout_id, Report.reporter_id == current_user.id)
 # ✅ fixed
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You already reported this shoutout")

    # Save report
    report = Report(
    shoutout_id=shoutout_id,
    reporter_id=current_user.id,  # ✅ Correct
    reason=reason
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {"message": "✅ Report submitted successfully"}

# --- Admin: View all reported shoutouts ---
@app.get("/reports")
def get_reported_shoutouts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    from models import Report

    reports = (
        db.query(Report)
        .join(ShoutOut, Report.shoutout_id == ShoutOut.id)
        .order_by(Report.created_at.desc())
        .all()
    )

    if not reports:
        return []

    result = []
    for report in reports:
        s = report.shoutout
        sender = db.query(User).filter(User.id == s.sender_id).first()
        recipients = (
            db.query(User)
            .join(ShoutOutRecipient, User.id == ShoutOutRecipient.recipient_id)
            .filter(ShoutOutRecipient.shoutout_id == s.id)
            .all()
        )
        recipient_names = [r.name for r in recipients]

        result.append(
            {
                "id": s.id,
                "message": s.message,
                "sender_name": sender.name if sender else "Unknown",
                "created_at": s.created_at,
                "image_url": s.image_url,
                "recipient_names": recipient_names,
                "reason": report.reason,
                "reporter_name": report.reporter.name,
            }
        )
    return result


# --- Admin: Delete a reported shoutout (resolve report) ---
@app.delete("/reports/{shoutout_id}/resolve", status_code=204)
def resolve_report(
    shoutout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    shoutout = db.query(ShoutOut).filter(ShoutOut.id == shoutout_id).first()
    if not shoutout:
        raise HTTPException(status_code=404, detail="Shoutout not found")

    # Delete related data
    db.query(Comment).filter(Comment.shoutout_id == shoutout_id).delete(synchronize_session=False)
    db.query(Report).filter(Report.shoutout_id == shoutout_id).delete(synchronize_session=False)
    db.delete(shoutout)
    db.commit()

    return 
from fastapi.responses import Response
from io import StringIO, BytesIO
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# -------------------- EXPORT ADMIN DASHBOARD DATA --------------------

@app.get("/admin/export/csv")
def export_admin_data_csv(db: Session = Depends(get_db)):
    """Export admin dashboard data (top contributors + most tagged users) as CSV."""

    # --- Fetch top contributors ---
    top_contributors = (
        db.query(User.name, func.count(ShoutOut.id).label("total_shoutouts"))
        .join(ShoutOut, ShoutOut.sender_id == User.id)
        .group_by(User.id)
        .order_by(func.count(ShoutOut.id).desc())
        .limit(10)
        .all()
    )

    # --- Fetch most tagged users ---
    most_tagged = (
        db.query(User.name, func.count(ShoutOutRecipient.id).label("times_tagged"))
        .join(ShoutOutRecipient, ShoutOutRecipient.recipient_id == User.id)
        .group_by(User.id)
        .order_by(func.count(ShoutOutRecipient.id).desc())
        .limit(10)
        .all()
    )

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Top Contributors"])
    writer.writerow(["Username", "Posts Count"])
    for row in top_contributors:
        writer.writerow([row.name, row.total_shoutouts])

    writer.writerow([])  # empty line
    writer.writerow(["Most Tagged Users"])
    writer.writerow(["Username", "Times Tagged"])
    for row in most_tagged:
        writer.writerow([row.name, row.times_tagged])

    output.seek(0)
    filename = "admin_dashboard_report.csv"

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/admin/export/pdf")
def export_admin_data_pdf(db: Session = Depends(get_db)):
    """Export admin dashboard data (top contributors + most tagged users) as PDF."""

    # --- Fetch data ---
    top_contributors = (
        db.query(User.name, func.count(ShoutOut.id).label("total_shoutouts"))
        .join(ShoutOut, ShoutOut.sender_id == User.id)
        .group_by(User.id)
        .order_by(func.count(ShoutOut.id).desc())
        .limit(10)
        .all()
    )

    most_tagged = (
        db.query(User.name, func.count(ShoutOutRecipient.id).label("times_tagged"))
        .join(ShoutOutRecipient, ShoutOutRecipient.recipient_id == User.id)
        .group_by(User.id)
        .order_by(func.count(ShoutOutRecipient.id).desc())
        .limit(10)
        .all()
    )

    # --- Create PDF ---
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Admin Dashboard Report")
    y -= 40

    # --- Top Contributors ---
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Top Contributors")
    y -= 20
    p.setFont("Helvetica", 11)
    for row in top_contributors:
        p.drawString(60, y, f"{row.name} - {row.total_shoutouts} posts")
        y -= 15
    y -= 20

    # --- Most Tagged Users ---
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Most Tagged Users")
    y -= 20
    p.setFont("Helvetica", 11)
    for row in most_tagged:
        p.drawString(60, y, f"{row.name} - {row.times_tagged} times")
        y -= 15

    p.save()
    buffer.seek(0)

    filename = "admin_dashboard_report.pdf"
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
