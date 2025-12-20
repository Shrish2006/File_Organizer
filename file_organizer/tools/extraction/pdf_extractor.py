# from .base_extractor import BaseExtractor
# from pathlib import Path

# class PDFExtractor(BaseExtractor):
#     def extract(self, file_path: str) -> str:
#         """Extract text from PDF, fall back to OCR if needed."""
#         try:
#             import fitz  # PyMuPDF
#             doc = fitz.open(file_path)
#             text = "".join(page.get_text() for page in doc)
#             return text.strip() or self._extract_with_ocr(file_path)
#         except ImportError:
#             raise ImportError("Install PyMuPDF: pip install PyMuPDF")

#     def _extract_with_ocr(self, file_path: str) -> str:
#         """Extract text using OCR."""
#         try:
#             import pytesseract
#             from PIL import Image
#             return pytesseract.image_to_string(Image.open(file_path))
#         except ImportError:
#             raise ImportError("Install pytesseract and Pillow: pip install pytesseract pillow")



from .base_extractor import BaseExtractor
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PDFExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        """
        Extract text from PDF, fall back to OCR if needed.
        
        Returns:
            dict: Dictionary containing 'content', 'success', and 'error' keys
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = "".join(page.get_text() for page in doc)
            content = text.strip()
            
            # If no text was extracted, try OCR
            if not content:
                return self._extract_with_ocr(file_path)
                
            return {
                'content': content,
                'success': True,
                'file_path': file_path
            }
            
        except ImportError as e:
            error_msg = "Install PyMuPDF: pip install PyMuPDF"
            logger.error(error_msg)
            return {
                'content': '',
                'success': False,
                'error': error_msg,
                'file_path': file_path
            }
        except Exception as e:
            error_msg = f"Error extracting text from PDF {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'content': '',
                'success': False,
                'error': error_msg,
                'file_path': file_path
            }

    def _extract_with_ocr(self, file_path: str) -> dict:
        """
        Extract text using OCR.
        
        Returns:
            dict: Dictionary containing 'content', 'success', and 'error' keys
        """
        try:
            import pytesseract
            from PIL import Image
            from pdf2image import convert_from_path
            
            # Convert PDF to images
            images = convert_from_path(file_path)
            content = ""
            
            # Extract text from each page
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                content += f"--- Page {i+1} ---\n{page_text}\n"
                
            return {
                'content': content.strip(),
                'success': True,
                'file_path': file_path,
                'ocr_used': True
            }
            
        except ImportError as e:
            error_msg = "Install pytesseract, Pillow, and pdf2image: pip install pytesseract pillow pdf2image"
            logger.error(error_msg)
            return {
                'content': '',
                'success': False,
                'error': error_msg,
                'file_path': file_path
            }
        except Exception as e:
            error_msg = f"Error during OCR processing of {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'content': '',
                'success': False,
                'error': error_msg,
                'file_path': file_path
            }