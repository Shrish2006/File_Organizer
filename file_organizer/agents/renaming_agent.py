import re
import logging
from pathlib import Path
from typing import Dict, Any
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

class RenamingAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.3)  # Slightly creative but mostly deterministic
        self.parser = StrOutputParser()
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert at creating clean, descriptive filenames.
            Generate a filename based on the document's content and metadata.
            
            Rules:
            1. Be concise but descriptive (max 5-7 words)
            2. Use underscores instead of spaces
            3. Use only alphanumeric characters and underscores
            4. Keep the original file extension
            5. Make it unique and specific to the content
            
            Examples:
            - "Machine_Learning_Introduction.pdf"
            - "Q1_Financial_Report_2023.xlsx"
            - "Project_Proposal_AI_Implementation.docx"
            """),
            ("human", """
            Document Content:
            {content}
            
            Metadata:
            {metadata}
            
            Original Filename: {original_name}
            
            Generate a clean, descriptive filename (without path):
            """)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser

    def generate_filename(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a clean, descriptive filename.
        
        Args:
            text_data: Dictionary containing 'content', 'metadata', and 'file_path'
            
        Returns:
            Updated dictionary with 'new_name' field
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Get the original filename and extension
            file_path = text_data.get('file_path', 'document')
            original_name = Path(file_path).name
            extension = Path(file_path).suffix.lower()
            
            # Prepare the content (first 2000 chars to avoid context overflow)
            content = text_data.get('content', '')[:2000]
            metadata = text_data.get('metadata', {})
            
            # Get the suggested filename
            suggested = self.chain.invoke({
                "content": content,
                "metadata": metadata,
                "original_name": original_name
            }).strip()
            
            # Clean and validate the filename
            new_name = self._clean_filename(suggested, extension)
            
            # Update the result
            text_data['new_name'] = new_name
            return text_data
            
        except Exception as e:
            logger.error(f"Renaming failed: {str(e)}")
            text_data['error'] = f"Renaming failed: {str(e)}"
            text_data['success'] = False
            return text_data

    def _clean_filename(self, filename: str, extension: str = '') -> str:
        """Clean and validate the filename."""
        # Remove any path components
        filename = Path(filename).name
        
        # Remove the extension if present (we'll add our own)
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]
        
        # Replace invalid characters with underscores
        filename = re.sub(r'[^\w\-]', '_', filename)
        
        # Remove consecutive underscores and trim
        filename = re.sub(r'_+', '_', filename).strip('_')
        
        # Add extension if provided
        if extension and not filename.lower().endswith(extension.lower()):
            filename += extension.lower()
            
        # Ensure we have at least some name
        if not filename.replace('_', '').replace(extension, ''):
            filename = f"document{extension}"
            
        return filename