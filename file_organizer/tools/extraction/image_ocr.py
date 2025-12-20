# from .base_extractor import BaseExtractor

# class ImageExtractor(BaseExtractor):
#     def extract(self, file_path: str) -> str:
#         """Extract text from images using OCR."""
#         try:
#             import pytesseract
#             from PIL import Image
#             return pytesseract.image_to_string(Image.open(file_path))
#         except ImportError:
#             raise ImportError("Install pytesseract and Pillow: pip install pytesseract pillow")



from .base_extractor import BaseExtractor
import logging

logger = logging.getLogger(__name__)

class ImageExtractor(BaseExtractor):
    def extract(self, file_path: str) -> dict:
        """
        Extract text from images using OCR.
        
        Returns:
            dict: Dictionary containing 'content', 'success', and 'error' keys
        """
        try:
            import pytesseract
            from PIL import Image
            
            content = pytesseract.image_to_string(Image.open(file_path))
            return {
                'content': content,
                'success': True,
                'file_path': file_path
            }
            
        except ImportError as e:
            error_msg = "Install pytesseract and Pillow: pip install pytesseract pillow"
            logger.error(error_msg)
            return {
                'content': '',
                'success': False,
                'error': error_msg,
                'file_path': file_path
            }
        except Exception as e:
            error_msg = f"Error extracting text from image {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                'content': '',
                'success': False,
                'error': error_msg,
                'file_path': file_path
            }