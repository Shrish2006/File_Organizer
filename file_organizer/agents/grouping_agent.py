import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

class GroupingAgent:
    def __init__(self, max_depth: int = 3):
        """
        Initialize the grouping agent with Gemini.
        
        Args:
            max_depth: Maximum depth of the folder hierarchy (default: 3)
        """
        self.max_depth = max_depth
        self.llm = get_llm(temperature=0.4)  # Slightly higher temp for creativity
        self.parser = StrOutputParser()
        
        # Define the system prompt for Gemini
        self.system_prompt = """
        You are an expert at organizing files into a logical folder structure.
        Your task is to generate a clean, hierarchical folder path based on the document's content and category.
        
        RULES:
        1. Output ONLY the folder path — nothing else
        2. Use forward slashes (/) as separators
        3. Maximum depth: {max_depth} folders
        4. Each folder name should be 1-2 words
        5. Use lowercase letters, numbers, and underscores only
        6. Start with the provided category
        7. Be specific but concise
        
        Examples of good output:
        - academics/computer_science/algorithms
        - business/finance/quarterly_reports
        - personal/taxes/2023
        """
        
        # Define the human prompt
        self.human_prompt = """
        Generate a folder path for this document following these rules:
        - Category: {category}
        - Max depth: {max_depth} levels
        - Content type: {file_type}
        
        Document content (first 2000 chars):
        {content_preview}
        
        IMPORTANT: Return ONLY the folder path, nothing else.
        Example: category/subcategory/specific_topic
        
        Folder path:
        """
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", self.human_prompt)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser
        
        # Compile regex for cleaning folder names
        self.folder_clean_regex = re.compile(r'[^a-z0-9_/]')
        self.multi_underscore_regex = re.compile(r'_{2,}')

    def _clean_path_component(self, component: str) -> str:
        """Clean a single path component."""
        if not component:
            return ""
            
        # Convert to lowercase and replace spaces with underscores
        clean = component.lower().replace(' ', '_')
        # Remove any remaining invalid characters
        clean = re.sub(r'[^a-z0-9_]', '', clean)
        # Remove consecutive underscores
        clean = re.sub(r'_+', '_', clean).strip('_')
        return clean
    
    def _clean_path(self, path: str, category: str) -> str:
        """
        Clean and validate the generated path.
        
        Args:
            path: Raw path from the LLM
            category: The document's category
            
        Returns:
            Cleaned and validated path
        """
        if not path or not isinstance(path, str):
            return self._clean_path_component(category)
            
        # Split into components and clean each one
        components = []
        for comp in path.split('/'):
            clean_comp = self._clean_path_component(comp)
            if clean_comp:  # Skip empty components
                components.append(clean_comp)
        
        # Ensure we don't exceed max depth
        components = components[:self.max_depth]
        
        # Ensure the first component matches the category
        if components and components[0].lower() != category.lower():
            components.insert(0, self._clean_path_component(category))
        
        # Join with forward slashes
        clean_path = '/'.join(components)
        
        # Ensure we have at least the category
        if not clean_path:
            clean_path = self._clean_path_component(category)
            
        return clean_path
    
    def suggest_group_path(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest a folder path for the document using Gemini.
        
        Args:
            text_data: Dictionary containing document data including 'classification' and 'content'
            
        Returns:
            Updated dictionary with 'group_path' added
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Extract relevant information
            classification = text_data.get('classification', {})
            category = classification.get('category', 'other').lower()
            content = text_data.get('content', '')[:2000]  # Limit content size
            file_type = text_data.get('file_type', 'unknown')
            
            # Prepare content preview (first 1000 chars for efficiency)
            content_preview = content[:1000]
            
            # Get the raw path from the LLM
            raw_path = self.chain.invoke({
                "category": category,
                "content_preview": content_preview,
                "max_depth": self.max_depth,
                "file_type": file_type
            }).strip()
            
            # Clean and validate the path
            clean_path = self._clean_path(raw_path, category)
            
            # Add the path to the text data
            text_data['group_path'] = clean_path
            logger.info(f"Generated group path: {clean_path}")
            
            return text_data
            
        except Exception as e:
            logger.error(f"Grouping failed: {str(e)}", exc_info=True)
            # Fallback to just using the category
            fallback_path = self._clean_path_component(
                text_data.get('classification', {}).get('category', 'other')
            )
            text_data['group_path'] = fallback_path
            logger.warning(f"Using fallback path: {fallback_path}")
            return text_data
        
        # Ensure it starts with the category
        if not path.lower().startswith(category.lower()):
            path = f"{category}/{path}" if not path.startswith('/') else f"{category}{path}"
        
        # Clean up the path
        import re
        path = re.sub(r'[^\w/]', '_', path)  # Replace special chars with underscore
        path = re.sub(r'_+', '_', path)      # Remove duplicate underscores
        path = path.strip('_/')              # Remove leading/trailing _ or /
        
        # Limit depth
        parts = path.split('/')
        path = '/'.join(parts[:self.max_depth])
        
        return path