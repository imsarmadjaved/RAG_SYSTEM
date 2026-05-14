from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ["/api/health", "/api/auth/signup", "/api/auth/login", "/api/docs", "/api/redoc", "/openapi.json"]
        
        if request.url.path in public_paths or request.url.path.startswith("/api/docs"):
            return await call_next(request)
        
        response = await call_next(request)
        return response