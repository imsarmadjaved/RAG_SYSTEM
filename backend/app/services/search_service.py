from app.config import settings
from app.dependencies import get_ai, get_pc
from loguru import logger

class SearchService:
    def __init__(self):
        self.client = get_ai()
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def search(self, query_text, email, chunk_types=None, top_k=30):
        try:
            logger.info("Search: " + query_text[:50] + " for " + email)
            resp = self.client.models.embed_content(model="models/gemini-embedding-001", contents=query_text, config={'output_dimensionality': 1536})
            vec = resp.embeddings[0].values
            logger.info("Embedding done, querying Pinecone...")
            
            results = self.index.query(vector=vec, filter={"email": email}, top_k=top_k, include_metadata=True)
            logger.info("Pinecone returned " + str(len(results.matches)) + " matches")
            
            chunks = []
            for m in results.matches:
                ...
            return chunks
        except Exception as e:
            logger.error("Search failed: " + str(e))
            return []
