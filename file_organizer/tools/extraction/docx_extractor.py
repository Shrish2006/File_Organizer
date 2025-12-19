# file_organizer/tools/extraction/docx_extractor.py
from .base_extractor import BaseExtractor

class DocxExtractor(BaseExtractor):
    def extract(self, file_path: str) -> str:
        """Extract text from Word documents."""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs if para.text)
        except ImportError:
            raise ImportError("Install python-docx: pip install python-docx")