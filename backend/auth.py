import json
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ---> This is the line that was missing! <---
router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

# Standard hashing and JWT config
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-super-secret-key-change-this-later"
ALGORITHM = "HS256"

# JSON Database configuration
DB_FILE = "users_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Dependency to check the token on protected routes
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        db = load_db()
        if email is None or email not in db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return db[email]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

@router.post("/signup")
def signup(user: UserSignup):
    # Enforce the Gmail-only rule
    if not user.email.lower().endswith("@gmail.com"):
        raise HTTPException(status_code=400, detail="Access restricted: Only @gmail.com accounts are allowed.")
    
    db = load_db()
    if user.email in db:
        raise HTTPException(status_code=400, detail="This email is already registered.")
    
    hashed_password = pwd_context.hash(user.password)
    db[user.email] = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }
    save_db(db)
    return {"message": "Account created successfully"}

@router.post("/login")
def login(user: UserLogin):
    db = load_db()
    db_user = db.get(user.email)
    
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    
    # Generate the JWT token
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    token = jwt.encode({"sub": user.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    
    # Return the exact JSON structure your frontend expects
    return {
        "token": token,
        "user": {"name": db_user["name"], "email": db_user["email"]}
    }

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"name": current_user["name"], "email": current_user["email"]}