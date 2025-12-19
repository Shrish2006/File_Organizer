# file_organizer/tools/path_builder.py
import os
import re
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PathBuilder:
    def __init__(self, base_output_dir: str = "organized_files"):
        """
        Initialize the PathBuilder.
        
        Args:
            base_output_dir: Base directory where all organized files will be stored
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
    def _clean_path_component(self, component: str) -> str:
        """
        Clean a single path component to be filesystem-safe.
        
        Args:
            component: Path component to clean
            
        Returns:
            Cleaned path component
        """
        if not component:
            return "_"
            
        # Remove invalid characters and trim
        cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', component)
        cleaned = cleaned.strip(' .')
        return cleaned or "_"
    
    def _handle_collision(self, path: Path) -> Path:
        """
        Handle filename collisions by appending a number.
        
        Args:
            path: Original path that might have a collision
            
        Returns:
            Path that doesn't collide with existing files
        """
        if not path.exists():
            return path
            
        # If file exists, try appending (1), (2), etc.
        counter = 1
        while True:
            new_path = path.parent / f"{path.stem} ({counter}){path.suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def build_path(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the final filesystem path for the file.
        
        Args:
            text_data: Dictionary containing group_path and new_name
            
        Returns:
            Updated dictionary with final_path
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Get components
            group_path = text_data.get('group_path', '')
            new_name = text_data.get('new_name', 'unnamed_document')
            
            if not group_path or not new_name:
                raise ValueError("Missing required path components")
            
            # Clean and split the group path
            path_parts = [self._clean_path_component(part) 
                         for part in group_path.split('/') if part.strip()]
            
            # Clean the filename and ensure it has an extension
            filename = self._clean_path_component(new_name)
            if not any(filename.lower().endswith(ext) for ext in ['.pdf', '.docx', '.pptx', '.jpg', '.jpeg', '.png']):
                # Try to preserve original extension if possible
                original_path = Path(text_data.get('file_path', ''))
                if original_path.suffix:
                    filename += original_path.suffix.lower()
                else:
                    # Default to .txt if no extension found
                    filename += '.txt'
            
            # Build the full path
            final_path = self.base_output_dir.joinpath(*path_parts, filename)
            
            # Handle any collisions
            final_path = self._handle_collision(final_path)
            
            # Create parent directories if they don't exist
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update the result
            text_data['final_path'] = str(final_path)
            return text_data
            
        except Exception as e:
            logger.error(f"Path building failed: {str(e)}")
            text_data['error'] = f"Path building failed: {str(e)}"
            text_data['success'] = False
            return text_data