import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetadataGenerator:
    def generate(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate metadata from text content.
        
        Args:
            text_data: Dictionary containing 'content' and other metadata
            
        Returns:
            Updated dictionary with metadata
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            text = text_data.get('content', '')
            metadata = {
                'page_count': self._count_pages(text),
                'has_tables': self._detect_tables(text),
                'word_count': self._count_words(text),
                'line_count': self._count_lines(text),
                'ocr_confidence': text_data.get('ocr_confidence'),
                'file_size': self._get_file_size(text_data.get('file_path'))
            }
            
            # Update the result
            result = text_data.copy()
            result['metadata'] = metadata
            return result
            
        except Exception as e:
            logger.error(f"Error generating metadata: {str(e)}")
            text_data['error'] = f"Metadata generation failed: {str(e)}"
            text_data['success'] = False
            return text_data

    def _count_pages(self, text: str) -> int:
        """Estimate page count based on common page breaks."""
        # Count form feed characters or common page break markers
        page_breaks = text.count('\f')
        # If no explicit page breaks, estimate based on line count
        return max(1, page_breaks if page_breaks > 0 else (text.count('\n') // 50) + 1)

    def _detect_tables(self, text: str) -> bool:
        """Simple table detection based on patterns."""
        # Look for patterns that might indicate a table
        table_patterns = [
            r'\+[-]+\+',  # +-----+
            r'\|.+\|',    # | text |
            r'^\s*\w+(\s{2,}\w+)+\s*$'  # Multiple words with 2+ spaces between
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in table_patterns)

    def _count_words(self, text: str) -> int:
        """Count words in the text."""
        return len(re.findall(r'\w+', text))

    def _count_lines(self, text: str) -> int:
        """Count non-empty lines in the text."""
        return len([line for line in text.splitlines() if line.strip()])

    def _get_file_size(self, file_path: Optional[str]) -> Optional[int]:
        """Get file size in bytes if file exists."""
        if not file_path:
            return None
        try:
            from pathlib import Path
            return Path(file_path).stat().st_size
        except (OSError, AttributeError):
            return None