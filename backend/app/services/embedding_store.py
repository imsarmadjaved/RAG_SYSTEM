import time, re
import google.generativeai as genai
from app.config import settings
from app.dependencies import get_pc
from loguru import logger

class EmbeddingStore:
    def __init__(self):
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def create_embeddings(self, chunks, email):
        texts = []
        for c in chunks:
            t = c.get('normalized_text', '') or c.get('text', '')
            if not t.strip(): t = c.get('text', 'Resume')
            texts.append(t.strip())
        
        try:
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
                time.sleep(0.1)
            
            data = []
            for c, emb in zip(chunks, embeddings):
                extracted = c.get('extracted_data', {})
                exp_years = 0
                for exp in extracted.get('experience', []):
                    if isinstance(exp, dict):
                        try: exp_years += float(exp.get('duration_years', 0))
                        except: pass
                
                if exp_years == 0:
                    years = re.findall(r'(\d+)\+?\s*years?', c.get('text', ''), re.IGNORECASE)
                    if years:
                        try: exp_years = max(float(y) for y in years)
                        except: pass
                
                edu = ""
                for e in extracted.get('education', []):
                    if isinstance(e, dict):
                        edu = f"{e.get('degree','')} {e.get('institution','')}".strip()
                        break
                
                data.append({
                    'id': f"chunk_{c['chunk_index']}_{int(time.time())}",
                    'values': emb,
                    'metadata': {
                        'email': email,
                        'chunk_type': c.get('chunk_type', 'general'),
                        'chunk_index': c['chunk_index'],
                        'normalized_text': c.get('normalized_text', c.get('text', '')),
                        'raw_text': c.get('text', ''),
                        'skills': extracted.get('skills', []),
                        'experience_years': float(exp_years),
                        'education': edu
                    }
                })
            
            logger.info(f"Created {len(data)} embeddings")
            return data
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise
    
    async def store_in_pinecone(self, data):
        ids = [d['id'] for d in data]
        for i in range(0, len(data), 100):
            self.index.upsert(vectors=data[i:i+100])
        logger.info(f"Stored {len(ids)} vectors")
        return ids
    
    async def delete_vectors(self, ids):
        if ids:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors")
