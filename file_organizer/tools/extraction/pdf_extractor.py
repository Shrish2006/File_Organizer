from .base_extractor import BaseExtractor
from pathlib import Path

class PDFExtractor(BaseExtractor):
    def extract(self, file_path: str) -> str:
        """Extract text from PDF, fall back to OCR if needed."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = "".join(page.get_text() for page in doc)
            return text.strip() or self._extract_with_ocr(file_path)
        except ImportError:
            raise ImportError("Install PyMuPDF: pip install PyMuPDF")

    def _extract_with_ocr(self, file_path: str) -> str:
        """Extract text using OCR."""
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(file_path))
        except ImportError:
            raise ImportError("Install pytesseract and Pillow: pip install pytesseract pillow")