# In renaming_agent.py
import re
import logging
from pathlib import Path
from typing import Dict, Any
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

class RenamingAgent:
    def __init__(self, max_filename_length: int = 50):
        self.llm = get_llm(temperature=0.3)
        self.parser = StrOutputParser()
        self.max_filename_length = max_filename_length
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a filename generation engine.
            Your job is to output ONLY a single filename.
            Do NOT explain your reasoning.
            Do NOT include sentences, comments, or extra text.
            Do NOT repeat instructions.
            Do NOT include paths or folders.

            If your output contains anything other than a filename, it is INVALID.

            Output format (MANDATORY):
            <filename_with_extension>

            """),
            ("human", """
            Generate a clean, descriptive filename using the rules below.

            STRICT RULES (MUST FOLLOW):
            1. Output ONLY the filename — nothing else
            2. Use 5–7 words maximum
            3. Use underscores (_) instead of spaces
            4. Use ONLY lowercase letters, numbers, and underscores
            5. Keep the original file extension
            6. Total length must be UNDER 50 characters (including extension)
            7. Do NOT include phrases like:
            - based_on
            - i_suggest
            - this_filename
            - document
            - content
            - metadata
            8. Do NOT explain or justify the filename
            9. If unsure, still generate the best short descriptive filename

            GOOD OUTPUT EXAMPLES:
            subject_verb_agreement_rules.pdf  
            ml_intro_notes.pdf  
            finance_q1_2023.xlsx  

            BAD OUTPUT (NEVER DO THIS):
            Here is the filename: xyz.pdf  
            Based_on_the_document_xyz.pdf  
            This_filename_meets_all_rules_xyz.pdf  

            INPUT:
            Document Content:
            {content}

            Metadata:
            {metadata}

            Original Filename:
            {original_name}

            FINAL OUTPUT:

            """)
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    def generate_filename(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        if not text_data.get('success', False):
            return text_data
            
        try:
            file_path = text_data.get('file_path', 'document')
            original_name = Path(file_path).name
            extension = Path(file_path).suffix.lower()
            
            # Limit content size to prevent context overflow
            content = text_data.get('content', '')[:2000]
            metadata = text_data.get('metadata', {})
            
            # Get suggested filename
            suggested = self.chain.invoke({
                "content": content,
                "metadata": metadata,
                "original_name": original_name
            }).strip()
            
            # Clean and validate filename
            new_name = self._clean_filename(suggested, extension)
            
            # Ensure filename isn't too long
            max_base_length = self.max_filename_length - len(extension)
            if len(Path(new_name).stem) > max_base_length:
                base = Path(new_name).stem[:max_base_length-3] + '...'
                new_name = f"{base}{extension}"
            
            text_data['new_name'] = new_name
            return text_data
            
        except Exception as e:
            logger.error(f"Renaming failed: {str(e)}")
            # Fallback to original name if renaming fails
            text_data['new_name'] = original_name
            return text_data

    def _clean_filename(self, filename: str, extension: str = '') -> str:
        """Clean and validate the filename."""
        # Remove any path components
        filename = Path(filename).name
        
        # Remove extension if present
        if '.' in filename:
            filename = filename.rsplit('.', 1)[0]
        
        # Replace invalid characters and clean up
        filename = re.sub(r'[^\w\-]', '_', filename)
        filename = re.sub(r'_+', '_', filename).strip('_')
        
        # Ensure we have a valid name
        if not filename:
            filename = "document"
        
        # Add extension
        if extension:
            filename = f"{filename}{extension.lower()}"
            
        return filename