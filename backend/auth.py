import json
import os
import jwt
import hashlib
import secrets
import base64

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

SECRET_KEY = "your-super-secret-key-change-this-later"
ALGORITHM = "HS256"

DB_FILE = "users_db.json"


# ---------------------------
# Database Helpers
# ---------------------------

def load_db():
    if not os.path.exists(DB_FILE):
        return {}

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)


# ---------------------------
# Password Hashing
# ---------------------------

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
    )

    return base64.b64encode(salt + key).decode()


def verify_password(password: str, stored_password: str) -> bool:
    try:
        decoded = base64.b64decode(stored_password.encode())

        salt = decoded[:16]
        stored_key = decoded[16:]

        new_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            100000,
        )

        return secrets.compare_digest(stored_key, new_key)

    except Exception:
        return False


# ---------------------------
# Models
# ---------------------------

class UserSignup(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# ---------------------------
# Authentication Dependency
# ---------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")

        db = load_db()

        if email is None or email not in db:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return db[email]

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please sign in again.",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token.",
        )


# ---------------------------
# Signup
# ---------------------------

@router.post("/signup")
def signup(user: UserSignup):

    if not user.email.lower().endswith("@gmail.com"):
        raise HTTPException(
            status_code=400,
            detail="Access restricted: Only @gmail.com accounts are allowed.",
        )

    db = load_db()

    if user.email in db:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered.",
        )

    db[user.email] = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
    }

    save_db(db)

    return {
        "message": "Account created successfully"
    }


# ---------------------------
# Login
# ---------------------------

@router.post("/login")
def login(user: UserLogin):

    db = load_db()

    db_user = db.get(user.email)

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
        )

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
        )

    expire = datetime.now(timezone.utc) + timedelta(hours=24)

    token = jwt.encode(
        {
            "sub": user.email,
            "exp": expire,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "token": token,
        "user": {
            "name": db_user["name"],
            "email": db_user["email"],
        },
    }


# ---------------------------
# Current User
# ---------------------------

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "name": current_user["name"],
        "email": current_user["email"],
    }