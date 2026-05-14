from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatQuery
from app.services.chat_manager import ChatManager
from app.dependencies import get_db
from app.utils.auth_utils import get_current_active_user
from loguru import logger

router = APIRouter()

@router.post("/query")
async def query(data: ChatQuery, user=Depends(get_current_active_user)):
    try:
        return await ChatManager(get_db()).chat(data.query, user["email"], user["user_id"], data.session_id)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, "Chat failed")

@router.get("/history/{session_id}")
async def history(session_id: str, user=Depends(get_current_active_user)):
    return await ChatManager(get_db()).get_history(session_id)

@router.get("/sessions")
async def sessions(user=Depends(get_current_active_user)):
    return {"sessions": await ChatManager(get_db()).get_sessions(user["user_id"])}
