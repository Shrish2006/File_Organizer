import shutil
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FileMover:
    def __init__(self, copy_instead_of_move: bool = False):
        """
        Initialize the FileMover.
        
        Args:
            copy_instead_of_move: If True, copies files instead of moving them
        """
        self.copy_instead_of_move = copy_instead_of_move
        
    def _ensure_directory_exists(self, filepath: Path) -> None:
        """
        Ensure the parent directory of the given path exists.
        Creates it if it doesn't exist.
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
    def _move_file(self, source: Path, destination: Path) -> bool:
        """
        Move or copy a file from source to destination.
        
        Returns:
            bool: True if operation was successful, False otherwise
        """
        try:
            if self.copy_instead_of_move:
                shutil.copy2(source, destination)
                logger.info(f"Copied: {source} -> {destination}")
            else:
                shutil.move(source, destination)
                logger.info(f"Moved: {source} -> {destination}")
            return True
        except (OSError, shutil.Error) as e:
            logger.error(f"Failed to move/copy {source} to {destination}: {e}")
            return False
            
    def move_file(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Move or copy a file as specified in text_data.
        
        Args:
            text_data: Dictionary containing 'source' and 'destination' paths
            
        Returns:
            Updated dictionary with operation status
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            source = Path(text_data.get('source', ''))
            destination = Path(text_data.get('destination', ''))
            
            if not source.exists():
                raise FileNotFoundError(f"Source file not found: {source}")
                
            if not destination.parent.exists():
                self._ensure_directory_exists(destination)
                
            success = self._move_file(source, destination)
            
            if success:
                text_data['success'] = True
                text_data['moved_to'] = str(destination)
                if self.copy_instead_of_move:
                    text_data['original_location'] = str(source)
            else:
                text_data['success'] = False
                text_data['error'] = f"Failed to move/copy file: {source} -> {destination}"
                
        except Exception as e:
            logger.error(f"File movement failed: {str(e)}")
            text_data['success'] = False
            text_data['error'] = f"File movement failed: {str(e)}"
            
        return text_data