from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.services.pdf_processor import PDFProcessor
from app.dependencies import get_db
from app.utils.auth_utils import get_current_active_user
from app.utils.errors import AppError
from loguru import logger

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...), user=Depends(get_current_active_user)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    content = await file.read()
    if len(content) > 10*1024*1024:
        raise HTTPException(400, "File too large (max 10MB)")
    try:
        task_id = await PDFProcessor(get_db()).process_pdf(content, file.filename, user["user_id"], user["email"])
        return {"task_id": task_id, "status": "processing", "message": "Upload started", "filename": file.filename}
    except AppError as e:
        raise HTTPException(e.status_code, detail=e.message)

@router.get("/status/{task_id}")
async def status(task_id: str, user=Depends(get_current_active_user)):
    try:
        return await PDFProcessor(get_db()).get_task_status(task_id)
    except AppError as e:
        raise HTTPException(e.status_code, detail=e.message)

@router.get("/list")
async def list_docs(user=Depends(get_current_active_user)):
    return {"documents": await PDFProcessor(get_db()).get_user_documents(user["user_id"]), "total": len(await PDFProcessor(get_db()).get_user_documents(user["user_id"]))}

@router.delete("/{doc_id}")
async def delete(doc_id: str, user=Depends(get_current_active_user)):
    try:
        await PDFProcessor(get_db()).delete_document(doc_id, user["user_id"])
        return {"message": "Deleted", "success": True}
    except AppError as e:
        raise HTTPException(e.status_code, detail=e.message)
