import fitz
from app.models.document import ExtractionQuality
from app.utils.errors import AppError, ErrorCode
from loguru import logger

class TextExtractor:
    async def extract_text(self, file_content):
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            total_pages = len(doc)
            pages = []
            
            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    pages.append(text)
            
            doc.close()
            
            full_text = "\n\n".join(pages)
            confidence = len(pages) / max(total_pages, 1)
            quality = ExtractionQuality(
                is_extracted=len(pages) > 0,
                confidence_score=round(confidence, 2),
                warnings=[]
            )
            
            logger.info(f"Extracted {len(pages)}/{total_pages} pages, {len(full_text)} chars")
            return full_text, quality
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise AppError(ErrorCode.DOC_003, str(e))
