import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.pdf', '.ppt', '.pptx',  # Documents
    '.docx', '.doc',          # Word documents
    '.png', '.jpg', '.jpeg'   # Images
}

class FileOrganizer:
    def __init__(self, input_dir='input_files'):
        """Initialize with input directory."""
        self.input_dir = Path(input_dir)
        self.input_dir.mkdir(exist_ok=True)

    def get_files_to_process(self):
        """Get list of supported files from input directory."""
        return [
            f for f in self.input_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    def process_file(self, file_path):
        """Process a single file through the pipeline."""
        try:
            logger.info(f"\nProcessing: {file_path.name}")
            
            # TODO: Add processing steps here
            # 1. Extract text
            # 2. Classify content
            # 3. Determine new location
            # 4. Move file
            
            return True
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

    def run(self):
        """Run the file organization process."""
        logger.info("\n=== Starting File Organizer ===")
        
        files = self.get_files_to_process()
        if not files:
            logger.info("No supported files found.")
            return
            
        logger.info(f"Found {len(files)} files to process")
        
        for file_path in files:
            self.process_file(file_path)

if __name__ == "__main__":
    FileOrganizer().run()