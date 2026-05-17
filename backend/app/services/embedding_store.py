import time, re
from app.config import settings
from app.dependencies import get_ai, get_pc
from loguru import logger

class EmbeddingStore:
    def __init__(self):
        self.client = get_ai()
        self.index = get_pc().Index(settings.PINECONE_INDEX_CHUNKS)
    
    async def create_embeddings(self, chunks, email):
        texts = [c.get('normalized_text', c.get('text', 'Resume')).strip()[:2000] for c in chunks]
        try:
            embeddings = []
            for text in texts:
                result = self.client.models.embed_content(
                    model='models/gemini-embedding-001',
                    contents=text,
                    config={'output_dimensionality': 1536}
                )
                embeddings.append(result.embeddings[0].values)
                time.sleep(0.05)
            data = []
            for c, emb in zip(chunks, embeddings):
                extracted = c.get('extracted_data', {})
                exp_years = 0
                for exp in extracted.get('experience', []):
                    if isinstance(exp, dict):
                        try:
                            exp_years += float(exp.get('duration_years', 0))
                        except:
                            pass
                edu = ''
                for e in extracted.get('education', []):
                    if isinstance(e, dict):
                        edu = e.get('degree', '') + ' ' + e.get('institution', '')
                        break
                data.append({
                    'id': 'chunk_' + str(c['chunk_index']) + '_' + str(int(time.time())),
                    'values': emb,
                    'metadata': {
                        'email': email,
                        'chunk_type': c.get('chunk_type', 'general'),
                        'chunk_index': c['chunk_index'],
                        'normalized_text': c.get('normalized_text', c.get('text', '')),
                        'raw_text': c.get('text', ''),
                        'skills': extracted.get('skills', []),
                        'experience_years': float(exp_years),
                        'education': edu.strip()
                    }
                })
            logger.info('Created ' + str(len(data)) + ' embeddings')
            return data
        except Exception as e:
            logger.error('Embedding failed: ' + str(e))
            raise
    
    async def store_in_pinecone(self, data):
        ids = [d['id'] for d in data]
        for i in range(0, len(data), 100):
            self.index.upsert(vectors=data[i:i+100])
        return ids
    
    async def delete_vectors(self, ids):
        if ids:
            self.index.delete(ids=ids)
