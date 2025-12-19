from .base_extractor import BaseExtractor

class ImageExtractor(BaseExtractor):
    def extract(self, file_path: str) -> str:
        """Extract text from images using OCR."""
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(file_path))
        except ImportError:
            raise ImportError("Install pytesseract and Pillow: pip install pytesseract pillow")