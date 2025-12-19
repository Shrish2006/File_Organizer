import logging
from pathlib import Path
from typing import Dict, Any

# Import all the components
from file_organizer.agents.preprocessing_yaaaar import PreprocessingAgent
from file_organizer.agents.classification_agent import ClassificationAgent
from file_organizer.agents.grouping_agent import GroupingAgent
from file_organizer.agents.renaming_agent import RenamingAgent
from file_organizer.tools.detection.file_type_detector import FileTypeDetector
from file_organizer.tools.extraction import ExtractorFactory
from file_organizer.tools.cleaning.text_cleaner import TextCleaner
from file_organizer.tools.metadata.metadata_generator import MetadataGenerator
from file_organizer.tools.filesystem.path_builder import PathBuilder
from file_organizer.tools.filesystem.file_mover import FileMover
from file_organizer.tools.filesystem.zip_builder import ZipBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileOrganizer:
    def __init__(self, input_dir: str = "input_files", output_dir: str = "organized_files"):
        """
        Initialize the File Organizer pipeline.
        
        Args:
            input_dir: Directory containing files to organize
            output_dir: Base directory where organized files will be stored
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize all components
        self.preprocessor = PreprocessingAgent()
        self.type_detector = FileTypeDetector()
        self.text_cleaner = TextCleaner()
        self.metadata_generator = MetadataGenerator()
        self.classifier = ClassificationAgent()
        self.grouper = GroupingAgent()
        self.renamer = RenamingAgent()
        self.path_builder = PathBuilder(output_dir)
        self.file_mover = FileMover()
        self.zip_builder = ZipBuilder()
        
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single file through the entire pipeline.
        
        Returns:
            Dictionary containing processing results and metadata
        """
        # Initialize text_data with file path
        text_data = {
            'file_path': str(file_path),
            'success': True
        }

        # so pehle text_data = {
        #     'file_path': str(file_path),
        #     'success': True
        # }

        try:
            # 1. Preprocessing
            text_data.update(self.preprocessor.get_extraction_plan(str(file_path)))
            if not text_data['success']:
                return text_data
                
#         {
#     'file_path': '/path/to/original/file.pdf',
#     'success': True,
#     'extraction_plan': 'ppt'  # or other plan based on file extension
# }

            # 2. File Type Detection
            text_data.update(self.type_detector.detect(str(file_path)))
            if not text_data['success']:
                return text_data
                
# {
#     'file_path': '/path/to/original/file.pdf',
#     'success': True,
#     'extraction_plan': 'ppt',
#     'file_type': 'ppt',
#     'mime_type': 'application/ppt'
# }


            # 3. Content Extraction
            extractor = ExtractorFactory.get_extractor(text_data['extraction_plan'])
            text_data.update(extractor.extract(str(file_path)))
            if not text_data['success']:
                return text_data

# {
#     'file_path': '/path/to/original/file.pdf',
#     'success': True,
#     'extraction_plan': 'ppt',
#     'file_type': 'ppt',
#     'mime_type': 'application/pt',
#     'content': 'Extracted text from the ppt...',
#     'ocr_confidence': 0.95  # if OCR was used for pdfs
# }

                
            # 4. Text Cleaning
            text_data = self.text_cleaner.clean(text_data)
            if not text_data['success']:
                return text_data
                

# {
#     # ... previous fields ...
#     'content': 'Cleaned text content...',  # Cleaned version
#     # ... other fields ...
# }

            # 5. Metadata Generation
            text_data = self.metadata_generator.generate(text_data)
            if not text_data['success']:
                return text_data
                

# {
#     # ... previous fields ...
#     'metadata': {
#         'page_count': 5,
#         'has_tables': True,
#         'word_count': 1245,
#         'line_count': 89,
#         'ocr_confidence': 0.95,
#         'file_size': 245678
#     }
# }


            # 6. Classification
            text_data = self.classifier.classify(text_data)
            if not text_data['success']:
                return text_data
                

# {
#     # ... previous fields ...
#     'classification': {
#         'category': 'Academics',
#         'confidence': 0.92
#     }
# }



            # 7. Grouping
            text_data = self.grouper.suggest_group_path(text_data)
            if not text_data['success']:
                return text_data


# {
#     # ... previous fields ...
#     'group_path': 'Academics/Computer Science/Operating Systems'
# }

                
            # 8. Renaming
            text_data = self.renamer.generate_filename(text_data)
            if not text_data['success']:
                return text_data
                

# {
#     # ... previous fields ...
#     'new_name': 'Operating_Systems_Process_Management.pdf'
# }


            # 9. Path Building
            text_data = self.path_builder.build_path(text_data)
            if not text_data['success']:
                return text_data


# {
#     # ... previous fields ...
#     'final_path': '/organized/Academics/Computer Science/Operating Systems/Operating_Systems_Process_Management.pdf'
# }

                
            # 10. File Moving
            text_data.update({
                'source': str(file_path),
                'destination': text_data['final_path']
            })
            text_data = self.file_mover.move_file(text_data)
            
            return text_data


# {
#     # ... previous fields ...
#     'moved_to': '/organized/Academics/Computer Science/Operating Systems/Operating_Systems_Process_Management.pdf'
# }

            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            text_data.update({
                'success': False,
                'error': str(e)
            })
            return text_data
    
    def run(self) -> Dict[str, Any]:
        """
        Run the file organization pipeline on all files in the input directory.
        
        Returns:
            Dictionary containing results and statistics
        """
        results = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Get all files in input directory (non-recursive)
        files = [f for f in self.input_dir.glob('*') if f.is_file()]
        results['total_files'] = len(files)
        
        if not files:
            logger.warning(f"No files found in {self.input_dir}")
            return results
            
        # Process each file
        for file_path in files:
            logger.info(f"Processing file: {file_path.name}")
            result = self.process_file(file_path)
            
            if result['success']:
                results['successful'] += 1
                logger.info(f"Successfully processed: {file_path.name}")
            else:
                results['failed'] += 1
                error_msg = f"Failed to process {file_path.name}: {result.get('error', 'Unknown error')}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        # Create a ZIP archive of the organized files

# {"zip_path" : "..........................................."}



        if results['successful'] > 0:
            zip_result = self.zip_builder.create_zip({
                'success': True,
                'organized_dir': str(self.output_dir)
            })
            
            if 'zip_path' in zip_result:
                results['zip_path'] = zip_result['zip_path']
                logger.info(f"Created ZIP archive: {zip_result['zip_path']}")
        
        return results

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Organize files using AI-powered classification and renaming.')
    parser.add_argument('--input_dir', default = 'input_files',help='Directory containing files to organize')
    parser.add_argument('--output-dir', default='organized_files', 
                       help='Directory where organized files will be stored (default: organized_files)')
    
    args = parser.parse_args()
    
    # Run the organizer
    organizer = FileOrganizer(input_dir=args.input_dir, output_dir=args.output_dir)
    results = organizer.run()
    
    # Print summary
    print("\n=== Organization Complete ===")
    print(f"Total files processed: {results['total_files']}")
    print(f"Successfully organized: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    if 'zip_path' in results:
        print(f"\nCreated ZIP archive: {results['zip_path']}")
    
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors']:
            print(f"- {error}")