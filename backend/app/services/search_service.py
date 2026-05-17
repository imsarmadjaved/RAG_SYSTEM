from app.config import settings
from app.dependencies import get_oai, get_pc
from loguru import logger

class SearchService:
    def __init__(self):
        self.oai = get_oai()
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def search(self, query_text, email, chunk_types=None, top_k=30):
        try:
            emb = await self.oai.embeddings.create(model=settings.OPENAI_MODEL_EMBEDDING, input=query_text)
            vec = emb.data[0].embedding
            
            results = self.index.query(vector=vec, filter={"email": email}, top_k=top_k, include_metadata=True)
            logger.info(f"Found {len(results.matches)} matches for {email}")
            
            chunks = []
            for m in results.matches:
                meta = m.metadata
                ctype = meta.get('chunk_type', 'general')
                if chunk_types and ctype not in chunk_types:
                    continue
                chunks.append({
                    'id': m.id, 'score': m.score,
                    'text': meta.get('normalized_text', meta.get('raw_text', '')),
                    'chunk_type': ctype,
                    'skills': meta.get('skills', []),
                    'experience_years': meta.get('experience_years', 0),
                    'chunk_index': meta.get('chunk_index', 0)
                })
            return chunks
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
