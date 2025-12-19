from .base_extractor import BaseExtractor

class PPTExtractor(BaseExtractor):
    def extract(self, file_path: str) -> str:
        """Extract text from PowerPoint files."""
        try:
            from pptx import Presentation
            prs = Presentation(file_path)
            return "\n".join(
                shape.text 
                for slide in prs.slides 
                for shape in slide.shapes 
                if hasattr(shape, "text") and shape.text
            )
        except ImportError:
            raise ImportError("Install python-pptx: pip install python-pptx")