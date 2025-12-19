# file_organizer/tools/detection/file_type_detector.py
import mimetypes
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileTypeDetector:
    def __init__(self):
        # Initialize MIME types
        mimetypes.init()
        
    def detect(self, file_path):
        """
        Detect file type using both extension and MIME type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: {
                'file_path': str,
                'file_type': str or None,
                'mime_type': str or None
            }
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return {
                'file_path': str(file_path),
                'file_type': None,
                'mime_type': None
            }

        # Get file extension (without dot)
        ext = path.suffix.lower()[1:] if path.suffix else None
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # For our purposes, we'll use the extension as the primary type
        # since it's more reliable for our known file types
        return {
            'file_path': str(file_path),
            'file_type': ext,
            'mime_type': mime_type
        }