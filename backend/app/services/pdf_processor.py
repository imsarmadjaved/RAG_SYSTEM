import asyncio
from datetime import datetime
from app.models.document import DocumentStatus
from app.utils.helpers import generate_task_id, sanitize_filename
from app.utils.errors import AppError, ErrorCode
from app.services.text_extractor import TextExtractor
from app.services.chunker import Chunker
from app.services.normalizer import Normalizer
from app.services.embedding_store import EmbeddingStore
from loguru import logger

class PDFProcessor:
    def __init__(self, db):
        self.db = db
        self.docs = db.documents
        self.tasks = db.tasks
        self.extractor = TextExtractor()
        self.chunker = Chunker()
        self.normalizer = Normalizer()
        self.store = EmbeddingStore()
    
    async def process_pdf(self, file_content, filename, user_id, email):
        if len(file_content) > 10*1024*1024:
            raise AppError(ErrorCode.DOC_001, "File too large")
        if not filename.lower().endswith('.pdf'):
            raise AppError(ErrorCode.DOC_002, "PDF only")
        
        task_id = generate_task_id()
        
        # Insert document
        await self.docs.insert_one({
            "user_id": user_id, "email": email, "filename": sanitize_filename(filename),
            "file_size": len(file_content), "status": DocumentStatus.UPLOADED.value,
            "pinecone_ids": [], "total_chunks": 0, "uploaded_at": datetime.utcnow(),
            "processed_at": None, "error_message": None, "task_id": task_id
        })
        
        await self.tasks.insert_one({
            "task_id": task_id, "status": DocumentStatus.PROCESSING.value,
            "progress": 0.0, "current_stage": "starting", "message": "Starting...",
            "error": None, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
        })
        
        asyncio.create_task(self._run(task_id, file_content, user_id, email))
        return task_id
    
    async def _run(self, task_id, file_content, user_id, email):
        try:
            # Clean old documents
            cursor = self.docs.find({"user_id": user_id, "task_id": {"": task_id}})
            async for old in cursor:
                if old.get("pinecone_ids"):
                    try: await self.store.delete_vectors(old["pinecone_ids"])
                    except: pass
                await self.docs.delete_one({"_id": old["_id"]})
            
            await self._update(task_id, "extracting", 10, "Extracting text...")
            text, quality = await self.extractor.extract_text(file_content)
            if not quality.is_extracted:
                raise AppError(ErrorCode.DOC_003, "No text extracted")
            
            await self._update(task_id, "chunking", 30, "Creating chunks...")
            chunks = await self.chunker.create_chunks(text)
            
            await self._update(task_id, "normalizing", 50, "AI normalizing...")
            normalized = await self.normalizer.normalize_chunks(chunks)
            
            await self._update(task_id, "embedding", 70, "Generating embeddings...")
            emb_data = await self.store.create_embeddings(normalized, email)
            
            await self._update(task_id, "storing", 90, "Storing...")
            ids = await self.store.store_in_pinecone(emb_data)
            
            await self.docs.update_one({"task_id": task_id}, {"$set": {
                "status": DocumentStatus.COMPLETED.value, "pinecone_ids": ids,
                "total_chunks": len(chunks), "processed_at": datetime.utcnow()
            }})
            
            await self._update(task_id, "completed", 100, "Ready!", status=DocumentStatus.COMPLETED.value)
            logger.info(f"Pipeline done: {task_id}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            await self.docs.update_one({"task_id": task_id}, {"$set": {
                "status": DocumentStatus.FAILED.value, "error_message": str(e)
            }})
            await self._update(task_id, "failed", 0, str(e)[:200], status=DocumentStatus.FAILED.value)
    
    async def _update(self, task_id, stage, progress, message, status=None):
        upd = {"current_stage": stage, "progress": progress, "message": message, "updated_at": datetime.utcnow()}
        if status: upd["status"] = status
        await self.tasks.update_one({"task_id": task_id}, {"$set": upd})
    
    async def get_task_status(self, task_id):
        t = await self.tasks.find_one({"task_id": task_id})
        if not t: raise AppError(ErrorCode.DOC_005, "Task not found", 404)
        return {"task_id": task_id, "status": t.get("status"), "progress": t.get("progress",0),
                "current_stage": t.get("current_stage",""), "message": t.get("message",""), "error": t.get("error")}
    
    async def get_user_documents(self, user_id):
        docs = []
        async for d in self.docs.find({"user_id": user_id}).sort("uploaded_at", -1):
            d["_id"] = str(d["_id"])
            docs.append(d)
        return docs
    
    async def delete_document(self, doc_id, user_id):
        from bson import ObjectId
        doc = await self.docs.find_one({"_id": ObjectId(doc_id), "user_id": user_id})
        if not doc: raise AppError(ErrorCode.DOC_005, "Not found", 404)
        if doc.get("pinecone_ids"): await self.store.delete_vectors(doc["pinecone_ids"])
        await self.tasks.delete_one({"task_id": doc.get("task_id")})
        await self.docs.delete_one({"_id": ObjectId(doc_id)})
        return True
