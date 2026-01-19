import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

class RenamingAgent:
    def __init__(self, max_filename_length: int = 50):
        """
        Initialize the RenamingAgent with Gemini.
        
        Args:
            max_filename_length: Maximum allowed length for filenames (default: 50)
        """
        self.llm = get_llm(temperature=0.3)  # Lower temperature for more consistent results
        self.parser = StrOutputParser()
        self.max_filename_length = max_filename_length
        
        # Define the system prompt for Gemini
        self.system_prompt = """
        You are a filename generation assistant. Your task is to create clean, descriptive filenames 
        based on document content and metadata. Follow these guidelines:
        
        1. Output ONLY the filename with extension, nothing else
        2. Use 3-5 descriptive words maximum
        3. Separate words with underscores (_)
        4. Use only lowercase letters, numbers, and underscores
        5. Keep the original file extension
        6. Total length must be under {max_length} characters
        7. Be concise but descriptive
        8. Do not include path information
        
        Examples of good filenames:
        - machine_learning_tutorial.pdf
        - q1_financial_report_2023.xlsx
        - project_proposal_draft.docx
        """
        
        # Define the human prompt
        self.human_prompt = """
        Generate a clean, descriptive filename based on the following information:
        
        Document Type: {file_type}
        Original Filename: {original_name}
        
        Document Content (first 1000 chars):
        {content_preview}
        
        Metadata:
        {metadata_str}
        
        Generate a filename that is descriptive of the content while following all the rules.
        Only output the filename with extension, nothing else.
        """
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", self.human_prompt)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser
        
        # Compile regex patterns for filename cleaning
        self.invalid_chars = re.compile(r'[^a-z0-9_.-]')
        self.multi_underscore = re.compile(r'_{2,}')
        self.leading_trailing_chars = re.compile(r'^[_.-]+|[_.-]+$')

    def generate_filename(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a clean, descriptive filename for the document.
        
        Args:
            text_data: Dictionary containing document data
            
        Returns:
            Updated dictionary with 'new_name' field
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Extract file information
            file_path = text_data.get('file_path', 'document')
            original_name = Path(file_path).name
            extension = Path(file_path).suffix.lower()
            file_type = text_data.get('file_type', 'document')
            
            # Prepare content preview (first 1000 chars for efficiency)
            content = text_data.get('content', '')[:1000]
            
            # Format metadata for the prompt
            metadata = text_data.get('metadata', {})
            metadata_str = '\n'.join(f"{k}: {v}" for k, v in metadata.items() if v)
            
            # Get suggested filename from the LLM
            suggested = self.chain.invoke({
                "content_preview": content,
                "metadata_str": metadata_str,
                "original_name": original_name,
                "file_type": file_type,
                "max_length": self.max_filename_length
            }).strip()
            
            logger.info(f"Suggested filename: {suggested}")
            
            # Clean and validate the filename
            clean_name = self._clean_filename(suggested, extension)
            
            # Ensure we don't exceed max length
            if len(clean_name) > self.max_filename_length:
                clean_name = clean_name[:self.max_filename_length]
                
            # Add to text_data
            text_data['new_name'] = clean_name
            logger.info(f"Generated clean filename: {clean_name}")
            
            return text_data
            
        except Exception as e:
            logger.error(f"Filename generation failed: {str(e)}", exc_info=True)
            # Fallback to sanitized original name
            clean_name = self._clean_filename(Path(file_path).name, extension)
            text_data['new_name'] = clean_name
            logger.warning(f"Using fallback filename: {clean_name}")
            return text_data
    
    def _clean_filename(self, filename: str, extension: str) -> str:
        """
        Clean and sanitize a filename.
        
        Args:
            filename: The original filename
            extension: The file extension to ensure is present
            
        Returns:
            Cleaned and sanitized filename
        """
        if not filename:
            return f"unnamed_document{extension}"
        
        # Remove any path components
        name = Path(filename).stem
        
        # Clean the name
        name = name.lower()
        name = self.invalid_chars.sub('_', name)  # Replace invalid chars with underscore
        name = self.multi_underscore.sub('_', name)  # Remove duplicate underscores
        name = self.leading_trailing_chars.sub('', name)  # Remove leading/trailing special chars
        
        # Ensure we have a valid name
        if not name:
            name = "unnamed_document"
            
        # Ensure the name isn't too long (leave room for extension)
        max_name_length = self.max_filename_length - len(extension)
        if len(name) > max_name_length:
            name = name[:max_name_length].rstrip('_')
            
        # Add the extension if it's not already there
        if not name.lower().endswith(extension.lower()):
            name += extension
            
        return name