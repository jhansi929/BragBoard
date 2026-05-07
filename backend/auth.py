# auth.py
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from jose import jwt, JWTError
from typing import Optional
from datetime import datetime, timedelta, timezone

load_dotenv()

# ----- Configuration -----
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Debug print to confirm what secret the running process sees (server-side)
print("🔑 auth.py loaded. SECRET_KEY (first 6 chars):", (SECRET_KEY[:6] + "...") if SECRET_KEY else "None")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----- Password helpers -----
def hash_password(password: str) -> str:
    """Hash the password before storing in DB."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if entered password matches the stored hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# ----- Token helpers -----


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": str(subject),
        "exp": expire,  # ✅ store datetime object, not timestamp
        "type": "access"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print("🔐 create_access_token created token (first 20 chars):", token[:20], "... exp:", expire)
    return token


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    payload = {
        "sub": str(subject),
        "exp": expire,  # ✅ store datetime directly
        "type": "refresh"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print("🔐 create_refresh_token created token (first 20 chars):", token[:20], "... exp:", expire)
    return token


def decode_token(token: str) -> dict:
    """
    Decode the JWT. Raises jose.JWTError on failure / expiry.
    Returns the payload dict on success.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("🔓 decode_token success. payload sub:", payload.get("sub"), "exp:", payload.get("exp"))
        return payload
    except JWTError as e:
        # debug (server-side)
        print("🔒 decode_token FAILED:", repr(e))
        raise
