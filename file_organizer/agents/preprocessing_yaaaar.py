import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PreprocessingAgent:
    def __init__(self):
        # Simple mapping of extensions to extraction methods
        self.extraction_plans = {
            '.pdf': 'pdf_text_then_ocr_if_needed',
            '.png': 'ocr',
            '.jpg': 'ocr',
            '.jpeg': 'ocr',
            '.docx': 'docx',
            '.doc': 'docx',
            '.ppt': 'ppt',
            '.pptx': 'ppt',
        }

    def get_extraction_plan(self, file_path):
        """
        Get extraction plan for a file.
        Returns: {
            'file_path': str,
            'extraction_plan': str or None
        }
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        plan = self.extraction_plans.get(ext)
        
        if not plan:
            logger.warning(f"No extraction plan for: {ext}")
            return {
                'file_path': str(file_path),
                'extraction_plan': None
            }
            
        logger.info(f"Using {plan} for {path.name}")
        return {
            'file_path': str(file_path),
            'extraction_plan': plan
        }