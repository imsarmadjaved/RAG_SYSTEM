from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn, time, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings
from app.utils.errors import AppError
from loguru import logger

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting...")
    from app.dependencies import init_db, close_db
    await init_db()
    logger.info("Ready!")
    yield
    await close_db()
    logger.info("Shutdown")

app = FastAPI(title=settings.APP_NAME, docs_url="/api/docs", lifespan=lifespan)

# CORS - MUST be before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {time.time()-start:.2f}s")
    return response

@app.exception_handler(AppError)
async def app_error(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.error_code.name, "message": exc.message}})

from app.routes import auth, documents, chat, recruiter
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(recruiter.router, prefix="/api/recruiter", tags=["Recruiter"])

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "docs": "/api/docs"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)