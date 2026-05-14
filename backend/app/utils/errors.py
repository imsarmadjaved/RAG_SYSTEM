from enum import Enum
from typing import Optional, Any, Dict

class ErrorCode(str, Enum):
    AUTH_001 = "Invalid credentials"
    AUTH_002 = "Token expired"
    AUTH_003 = "Insufficient permissions"
    AUTH_004 = "User already exists"
    AUTH_005 = "Invalid token"
    
    DOC_001 = "File too large (max 10MB)"
    DOC_002 = "Invalid file format (PDF only)"
    DOC_003 = "PDF text extraction failed"
    DOC_004 = "Document processing failed"
    DOC_005 = "Document not found"
    
    CHAT_001 = "No resume found"
    CHAT_002 = "Query too vague"
    CHAT_003 = "No relevant information found"
    
    SEARCH_001 = "Invalid search parameters"
    SEARCH_002 = "No candidates match criteria"
    
    SYS_001 = "Pinecone service error"
    SYS_002 = "OpenAI API error"
    SYS_003 = "Database connection error"
    SYS_004 = "Internal server error"

class AppError(Exception):
    def __init__(self, error_code: ErrorCode, message: Optional[str] = None, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.message = message or error_code.value
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)