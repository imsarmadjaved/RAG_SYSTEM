import re, tiktoken
from app.config import settings
from loguru import logger

class Chunker:
    def __init__(self):
        self.enc = tiktoken.get_encoding("cl100k_base")
        self.size = settings.PDF_CHUNK_SIZE
    
    async def create_chunks(self, text):
        # Pre-process: split pipe-separated skills
        text = self._normalize_skills_text(text)
        
        lines = text.split('\n')
        sections = []
        current_type = "general"
        current_lines = []
        
        patterns = [
            (r'(?i)^(SKILLS|TECHNICAL SKILLS)', 'skills'),
            (r'(?i)^(EXPERIENCE|WORK|EMPLOYMENT|PROFESSIONAL)', 'experience'),
            (r'(?i)^(EDUCATION|ACADEMIC)', 'education'),
            (r'(?i)^(PROJECTS)', 'projects'),
            (r'(?i)^(SUMMARY|PROFILE|ABOUT)', 'summary'),
        ]
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            found = False
            for pat, stype in patterns:
                if re.search(pat, line):
                    if current_lines:
                        sections.append((current_type, '\n'.join(current_lines)))
                    current_type = stype
                    current_lines = [line]
                    found = True
                    break
            if not found:
                current_lines.append(line)
        
        if current_lines:
            sections.append((current_type, '\n'.join(current_lines)))
        
        chunks = []
        idx = 0
        for stype, stext in sections:
            tokens = self.enc.encode(stext)
            if len(tokens) > self.size:
                for i in range(0, len(tokens), self.size - 50):
                    chunk_tokens = tokens[i:i+self.size]
                    chunks.append({"text": self.enc.decode(chunk_tokens), "chunk_type": stype, "chunk_index": idx})
                    idx += 1
            else:
                chunks.append({"text": stext, "chunk_type": stype, "chunk_index": idx})
                idx += 1
        
        logger.info(f"Created {len(chunks)} chunks from {len(sections)} sections")
        return chunks
    
    def _normalize_skills_text(self, text):
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            if '|' in line and not line.startswith('http'):
                parts = line.split('|')
                new_lines.append(parts[0].strip() + ': ' + ', '.join(p.strip() for p in parts[1:]))
            else:
                new_lines.append(line)
        return '\n'.join(new_lines)
