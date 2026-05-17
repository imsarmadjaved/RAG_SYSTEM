from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExtractionQuality(BaseModel):
    is_extracted: bool
    confidence_score: float
    warnings: List[str] = []

class UploadResponse(BaseModel):
    task_id: str
    status: str = "processing"
    message: str = "Upload started"
    filename: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float = 0.0
    current_stage: str = ""
    message: str = ""
    error: Optional[str] = None
