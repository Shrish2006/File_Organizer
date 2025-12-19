from typing import Dict, Any
import logging
from pydantic import BaseModel, Field
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

# Define the expected output schema
class ClassificationResult(BaseModel):
    category: str = Field(..., description="The category that best describes the content")
    confidence: float = Field(..., description="Confidence score between 0 and 1")

class ClassificationAgent:
    def __init__(self, categories: list = None):
        """
        Initialize the classification agent.
        
        Args:
            categories: List of possible categories (if None, uses default categories)
        """
        self.categories = categories or [
            "Academics", "Business", "Finance", "Legal", "Medical",
            "Technical", "Creative", "Personal", "Other"
        ]
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=ClassificationResult)
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert document classifier. Analyze the provided text and metadata,
            then classify the document into one of these categories: {categories}
            
            Return your response as a JSON object with 'category' and 'confidence' fields.
            """),
            ("human", """
            Document Content:
            {content}
            
            Metadata:
            {metadata}
            
            Classification:
            """)
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser

    def classify(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the document based on its content and metadata.
        
        Args:
            text_data: Dictionary containing 'content' and 'metadata'
            
        Returns:
            Updated dictionary with classification results
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Prepare the input
            content = text_data.get('content', '')
            metadata = text_data.get('metadata', {})
            
            
            # Get the classification
            result = self.chain.invoke({
                "content": content,
                "metadata": metadata,
                "categories": self.categories
            })
            
            # Update the result
            text_data['classification'] = {
                'category': result['category'],
                'confidence': float(result['confidence'])
            }
            
            return text_data
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            text_data['error'] = f"Classification failed: {str(e)}"
            text_data['success'] = False
            return text_data