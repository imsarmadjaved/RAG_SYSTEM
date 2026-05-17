from motor.motor_asyncio import AsyncIOMotorClient
from pinecone import Pinecone
from google import genai
from loguru import logger
from app.config import settings

mongo_db = None
pinecone_client = None
genai_client = None

async def init_db():
    global mongo_db, pinecone_client, genai_client
    try:
        mongo = AsyncIOMotorClient(settings.MONGODB_URL)
        mongo_db = mongo[settings.MONGODB_DB_NAME]
        await mongo.admin.command('ping')
        await mongo_db.users.create_index("email", unique=True)
        await mongo_db.documents.create_index("user_id")
        await mongo_db.documents.create_index("task_id", unique=True)
        await mongo_db.tasks.create_index("task_id", unique=True)
        logger.info("MongoDB connected")
        
        pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
        logger.info("Pinecone ready")
        
        genai_client = genai.Client(api_key=settings.OPENAI_API_KEY)
        logger.info("Gemini ready")
    except Exception as e:
        logger.error(f"Init failed: {e}")
        raise

async def close_db():
    if mongo_db: mongo_db.client.close()

def get_db():
    if mongo_db is None: raise RuntimeError("DB not initialized")
    return mongo_db

def get_pc():
    if pinecone_client is None: raise RuntimeError("Pinecone not initialized")
    return pinecone_client

def get_ai():
    if genai_client is None: raise RuntimeError("Gemini not initialized")
    return genai_client
