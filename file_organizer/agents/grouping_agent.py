from typing import Dict, Any, List, Optional
import logging
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

logger = logging.getLogger(__name__)

class GroupingAgent:
    def __init__(self, max_depth: int = 3):
        """
        Initialize the grouping agent.
        
        Args:
            max_depth: Maximum depth of the folder hierarchy
        """
        self.max_depth = max_depth
        self.llm = get_llm(temperature=0.2)  # Slightly higher temp for creativity
        self.parser = StrOutputParser()
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert at organizing files into logical folder structures.
            Based on the document's category and content, suggest a folder path.
            
            Rules:
            1. Use forward slashes (/) as path separators
            2. Maximum depth is {max_depth} levels
            3. Keep folder names short (1-2 words)
            4. Use only alphanumeric characters and underscores
            5. Start with the category name
            6. Be specific but concise
            
            Example outputs:
            - "Academics/Computer_Science/Lectures"
            - "Business/Finance/Reports/Q1"
            - "Personal/Taxes/2023"
            """),
            ("human", """
            Category: {category}
            
            Document Content:
            {content}
            
            Suggested folder path ({max_depth} levels max):
            """)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser

    def suggest_group_path(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest a folder path for the document.
        
        Args:
            text_data: Dictionary containing 'category' and 'content'
            
        Returns:
            Updated dictionary with suggested group path
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Prepare the input
            category = text_data.get('classification', {}).get('category', 'Other')
            content = text_data.get('content', '')[:2000]  # Limit content length
            
            # Get the suggested path
            path = self.chain.invoke({
                "category": category,
                "content": content,
                "max_depth": self.max_depth
            }).strip()
            
            # Clean up the path
            path = self._clean_path(path, category)
            
            # Update the result
            text_data['group_path'] = path
            return text_data
            
        except Exception as e:
            logger.error(f"Grouping failed: {str(e)}")
            text_data['error'] = f"Grouping failed: {str(e)}"
            text_data['success'] = False
            return text_data

    def _clean_path(self, path: str, category: str) -> str:
        """Clean and validate the suggested path."""
        # Remove any quotes or special characters
        path = path.strip('"\'')
        
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