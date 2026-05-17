import time, re
from app.config import settings
from app.dependencies import get_oai, get_pc
from loguru import logger

class EmbeddingStore:
    def __init__(self):
        self.oai = get_oai()
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def create_embeddings(self, chunks, email):
        texts = []
        for c in chunks:
            t = c.get('normalized_text', '') or c.get('text', '')
            if not t.strip(): t = c.get('text', 'Resume')
            texts.append(t.strip())
        
        try:
            embeddings = []
            for i in range(0, len(texts), 50):
                batch = texts[i:i+50]
                resp = await self.oai.embeddings.create(model=settings.OPENAI_MODEL_EMBEDDING, input=batch)
                embeddings.extend([e.embedding for e in resp.data])
                if i + 50 < len(texts): time.sleep(0.2)
            
            data = []
            for c, emb in zip(chunks, embeddings):
                extracted = c.get('extracted_data', {})
                
                # Calculate experience
                exp_years = 0
                for exp in extracted.get('experience', []):
                    if isinstance(exp, dict):
                        try: exp_years += float(exp.get('duration_years', 0))
                        except: pass
                
                # Also check text
                if exp_years == 0:
                    years_match = re.findall(r'(\d+)\+?\s*years?', c.get('text', ''), re.IGNORECASE)
                    if years_match:
                        try: exp_years = max(float(y) for y in years_match)
                        except: pass
                
                # Get education text
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
            
            logger.info(f"Created {len(data)} embeddings, exp={exp_years}")
            return data
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise
    
    async def store_in_pinecone(self, data):
        ids = []
        for d in data:
            ids.append(d['id'])
        for i in range(0, len(data), 100):
            self.index.upsert(vectors=data[i:i+100])
        logger.info(f"Stored {len(ids)} vectors")
        return ids
    
    async def delete_vectors(self, ids):
        if ids:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors")
