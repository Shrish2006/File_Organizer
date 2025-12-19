import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TextCleaner:
    def clean(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize text content.
        
        Args:
            text_data: Dictionary containing 'content' key with text to clean
            
        Returns:
            Dictionary with cleaned text and metadata
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            text = text_data['content']
            if not text:
                return text_data
                
            # Apply cleaning steps
            text = self._remove_page_numbers(text)
            text = self._remove_headers_footers(text)
            text = self._normalize_whitespace(text)
            text = self._remove_repeated_newlines(text)
            text = text.strip()
            
            # Update the result
            result = text_data.copy()
            result['content'] = text
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            text_data['error'] = f"Text cleaning failed: {str(e)}"
            text_data['success'] = False
            return text_data

    def _remove_page_numbers(self, text: str) -> str:
        """Remove page numbers (e.g., 'Page 1', '1/10', etc.)."""
        # Remove "Page X" or "Page X of Y" patterns
        text = re.sub(r'Page\s+\d+(?:\s+of\s+\d+)?', '', text, flags=re.IGNORECASE)
        # Remove standalone numbers at the beginning/end of lines
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        return text

    def _remove_headers_footers(self, text: str) -> str:
        """Remove common headers and footers."""
        # Remove lines that are ALL CAPS (potential headers)
        text = re.sub(r'^\s*[A-Z0-9\s]+\s*$', '', text, flags=re.MULTILINE)
        # Remove lines that are too short and likely not content
        text = re.sub(r'^\s*\S{1,3}\s*$', '', text, flags=re.MULTILINE)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize all whitespace characters."""
        # Replace all whitespace sequences with a single space
        text = re.sub(r'\s+', ' ', text)
        return text

    def _remove_repeated_newlines(self, text: str) -> str:
        """Replace multiple consecutive newlines with at most two."""
        return re.sub(r'\n{3,}', '\n\n', text)