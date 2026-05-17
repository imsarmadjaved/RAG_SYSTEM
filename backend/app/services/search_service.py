from app.config import settings
from app.dependencies import get_ai, get_pc
from loguru import logger

class SearchService:
    def __init__(self):
        self.client = get_ai()
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def search(self, query_text, email, chunk_types=None, top_k=30):
        try:
            logger.info("Search start: " + query_text[:40] + " email=" + email)
            
            resp = self.client.models.embed_content(
                model="models/gemini-embedding-001", 
                contents=query_text, 
                config={'output_dimensionality': 1536}
            )
            vec = resp.embeddings[0].values
            logger.info("Embed OK, dims=" + str(len(vec)))
            
            results = self.index.query(vector=vec, filter={"email": email}, top_k=top_k, include_metadata=True)
            logger.info("Pinecone matches: " + str(len(results.matches)))
            
            chunks = []
            for m in results.matches:
                meta = m.metadata
                ctype = meta.get('chunk_type', 'general')
                if chunk_types and ctype not in chunk_types: continue
                chunks.append({
                    'id': m.id, 'score': m.score,
                    'text': meta.get('normalized_text', meta.get('raw_text', '')),
                    'chunk_type': ctype, 'skills': meta.get('skills', []),
                    'experience_years': meta.get('experience_years', 0),
                    'chunk_index': meta.get('chunk_index', 0)
                })
            logger.info("Returning " + str(len(chunks)) + " chunks")
            return chunks
        except Exception as e:
            logger.error("Search ERROR: " + type(e).__name__ + " - " + str(e))
            import traceback
            logger.error(traceback.format_exc())
            return []
