from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re

class UserType(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    user_type: UserType = UserType.CANDIDATE
    company: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8: raise ValueError('Min 8 characters')
        if not re.search(r'[A-Z]', v): raise ValueError('Need uppercase')
        if not re.search(r'[a-z]', v): raise ValueError('Need lowercase')
        if not re.search(r'\d', v): raise ValueError('Need number')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    user_type: str
    company: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    class Config: from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    success: bool = True
