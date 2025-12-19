import os
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ZipBuilder:
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the ZipBuilder.
        
        Args:
            output_dir: Directory where the ZIP file will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_all_files(self, directory: Path) -> List[Path]:
        """Recursively get all files in a directory."""
        files = []
        for item in directory.rglob('*'):
            if item.is_file():
                files.append(item)
        return files
        
    def _create_zip(self, source_dir: Path, zip_path: Path) -> bool:
        """
        Create a ZIP file from a directory.
        
        Args:
            source_dir: Directory to compress
            zip_path: Path where to save the ZIP file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self._get_all_files(source_dir):
                    # Get the relative path for the ZIP archive
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
                    logger.debug(f"Added to ZIP: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create ZIP: {str(e)}")
            return False
            
    def create_zip(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a ZIP file from the organized directory.
        
        Args:
            text_data: Dictionary containing 'organized_dir' path
            
        Returns:
            Updated dictionary with ZIP file path
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Get the organized directory path
            organized_dir = Path(text_data.get('organized_dir', ''))
            if not organized_dir.exists() or not organized_dir.is_dir():
                raise NotADirectoryError(f"Organized directory not found: {organized_dir}")
                
            # Create output filename based on the directory name
            zip_filename = f"{organized_dir.name}.zip"
            zip_path = self.output_dir / zip_filename
            
            # Create the ZIP file
            success = self._create_zip(organized_dir, zip_path)
            
            if success:
                text_data['zip_path'] = str(zip_path)
                logger.info(f"Created ZIP archive: {zip_path}")
            else:
                text_data['success'] = False
                text_data['error'] = f"Failed to create ZIP archive: {zip_path}"
                
        except Exception as e:
            logger.error(f"ZIP creation failed: {str(e)}")
            text_data['success'] = False
            text_data['error'] = f"ZIP creation failed: {str(e)}"
            
        return text_data