from pydantic import BaseModel
from typing import Optional, List

class ChatQuery(BaseModel):
    query: str
    session_id: Optional[str] = None

class SourceCitation(BaseModel):
    chunk_id: str
    chunk_text: str
    chunk_type: str
    relevance_score: float

class ChatResponse(BaseModel):
    answer: str
    confidence_score: float
    confidence_level: str
    sources: List[SourceCitation] = []
    session_id: str
