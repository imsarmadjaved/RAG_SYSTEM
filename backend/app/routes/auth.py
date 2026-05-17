from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.dependencies import get_db
from app.utils.auth_utils import get_current_active_user
from app.utils.errors import AppError
from loguru import logger

router = APIRouter()

@router.post("/signup", status_code=201)
async def signup(data: UserCreate):
    try:
        return await AuthService(get_db()).signup(data)
    except AppError as e:
        raise HTTPException(e.status_code, detail={"code": e.error_code.name, "message": e.message})

@router.post("/login")
async def login(data: UserLogin):
    try:
        return await AuthService(get_db()).login(data)
    except AppError as e:
        raise HTTPException(e.status_code, detail={"code": e.error_code.name, "message": e.message})

@router.post("/logout")
async def logout(user=Depends(get_current_active_user)):
    await AuthService(get_db()).logout(user["user_id"])
    return {"message": "Logged out"}

@router.get("/me")
async def me(user=Depends(get_current_active_user)):
    return await AuthService(get_db()).get_profile(user["user_id"])
