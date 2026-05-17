from fastapi import APIRouter, Depends
from app.utils.auth_utils import get_current_active_user
from pinecone import Pinecone
from app.config import settings

router = APIRouter()

@router.get("/debug-pinecone")
async def debug_pinecone(user=Depends(get_current_active_user)):
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    idx = pc.Index(settings.PINECONE_INDEX_CHUNKS)
    
    stats = idx.describe_index_stats()
    r = idx.query(vector=[0]*1536, top_k=5, include_metadata=True, filter={"email": user["email"]})
    
    return {
        "email": user["email"],
        "total_vectors": stats["total_vector_count"],
        "matches_for_email": len(r.matches),
        "samples": [{"id": m.id, "email": m.metadata.get("email"), "type": m.metadata.get("chunk_type")} for m in r.matches]
    }