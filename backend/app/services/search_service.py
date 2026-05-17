from typing import List, Dict, Any
import google.generativeai as genai
from app.config import settings
from app.dependencies import get_pc
from loguru import logger

class SearchService:
    def __init__(self):
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def search(self, query_text, email, chunk_types=None, top_k=30):
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query_text,
                task_type="retrieval_query"
            )
            vec = result['embedding']
            
            results = self.index.query(vector=vec, filter={"email": email}, top_k=top_k, include_metadata=True)
            logger.info(f"Found {len(results.matches)} matches for {email}")
            
            chunks = []
            for m in results.matches:
                meta = m.metadata
                ctype = meta.get('chunk_type', 'general')
                if chunk_types and ctype not in chunk_types: continue
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
