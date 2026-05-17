from datetime import datetime, timedelta
from jose import jwt
import hashlib
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from bson import ObjectId
from app.config import settings

security = HTTPBearer()

def hash_password(password):
    salt = secrets.token_hex(16)
    return salt + ":" + hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(plain, hashed):
    try:
        salt, hash_val = hashed.split(":")
        return hashlib.sha256((plain + salt).encode()).hexdigest() == hash_val
    except:
        return False

def create_token(data, expires_delta=None, token_type="access"):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": token_type})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_access_token(data):
    return create_token(data, token_type="access")

def create_refresh_token(data):
    return create_token(data, timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS), "refresh")

def decode_token(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials=Depends(security)):
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    return {"user_id": payload["sub"], "email": payload["email"], "user_type": payload["user_type"]}

async def get_current_active_user(current_user=Depends(get_current_user)):
    from app.dependencies import get_db
    db = get_db()
    try:
        oid = ObjectId(current_user["user_id"])
    except:
        oid = current_user["user_id"]
    user = await db.users.find_one({"_id": oid})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return current_user
