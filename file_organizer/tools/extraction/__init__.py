# file_organizer/tools/extraction/__init__.py
from pathlib import Path
from .pdf_extractor import PDFExtractor
from .image_ocr import ImageExtractor
from .docx_extractor import DocxExtractor
from .ppt_extractor import PPTExtractor

class ExtractorFactory:
    @staticmethod
    def get_extractor(extraction_plan: str):
        """Get the appropriate extractor based on the plan."""
        extractors = {
            'pdf_text_then_ocr_if_needed': PDFExtractor(),
            'ocr': ImageExtractor(),
            'docx': DocxExtractor(),
            'ppt': PPTExtractor()
        }
        return extractors.get(extraction_plan)