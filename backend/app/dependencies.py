from motor.motor_asyncio import AsyncIOMotorClient
from pinecone import Pinecone
from openai import AsyncOpenAI
from loguru import logger
from app.config import settings

mongo_db = None
pinecone_client = None
openai_client = None

async def init_db():
    global mongo_db, pinecone_client, openai_client
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
        
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI ready")
    except Exception as e:
        logger.error(f"Init failed: {e}")
        raise

async def close_db():
    global mongo_db
    if mongo_db is not None:
        mongo_db.client.close()
        logger.info("MongoDB closed")

def get_db():
    if mongo_db is None: raise RuntimeError("DB not initialized")
    return mongo_db

def get_pc():
    if pinecone_client is None: raise RuntimeError("Pinecone not initialized")
    return pinecone_client

def get_oai():
    if openai_client is None: raise RuntimeError("OpenAI not initialized")
    return openai_client
