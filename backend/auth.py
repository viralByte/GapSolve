import os
import jwt
import hashlib
import secrets
import base64
import boto3

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

SECRET_KEY = "your-super-secret-key-change-this-later"
ALGORITHM = "HS256"

# ---------------------------
# DynamoDB Configuration
# ---------------------------

dynamodb = boto3.resource("dynamodb")
table_name = os.getenv("DYNAMODB_TABLE", "gapsolve_users")
table = dynamodb.Table(table_name)


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

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Fetch user from DynamoDB instead of local json
        response = table.get_item(Key={"email": email})
        if "Item" not in response:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return response["Item"]

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

    email = user.email.lower().strip()

    if not email.endswith("@gmail.com"):
        raise HTTPException(
            status_code=400,
            detail="Access restricted: Only @gmail.com accounts are allowed.",
        )

    # Check if user already exists in DynamoDB
    response = table.get_item(Key={"email": email})
    if "Item" in response:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered.",
        )

    # Save user item to DynamoDB table
    table.put_item(
        Item={
            "email": email,
            "name": user.name,
            "password": hash_password(user.password),
        }
    )

    return {
        "message": "Account created successfully"
    }


# ---------------------------
# Login
# ---------------------------

@router.post("/login")
def login(user: UserLogin):

    email = user.email.lower().strip()

    # Fetch user from DynamoDB table
    response = table.get_item(Key={"email": email})
    db_user = response.get("Item")

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
            "sub": email,
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