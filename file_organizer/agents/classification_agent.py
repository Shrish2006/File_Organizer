import json
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

class ClassificationResult(BaseModel):
    category: str = Field(..., description="The category that best describes the content")
    confidence: float = Field(..., description="Confidence score between 0 and 1")

class ClassificationAgent:
    def __init__(self, categories: List[str] = None):
        """
        Initialize the ClassificationAgent with Gemini.
        
        Args:
            categories: List of possible categories for classification
        """
        self.categories = categories or [
            "Academics", "Business", "Finance", "Legal", "Medical",
            "Technical", "Creative", "Personal", "Other"
        ]
        
        # Initialize LLM with a slightly higher temperature for better categorization
        self.llm = get_llm(temperature=0.3)
        self.parser = JsonOutputParser(pydantic_object=ClassificationResult)
        
        # Define the system and human prompts for Gemini
        self.system_prompt = """You are an expert document classifier. Your task is to analyze the provided text and metadata,
then classify the document into one of the provided categories.

Instructions:
1. Carefully read and understand the document content
2. Analyze any available metadata
3. Choose the most appropriate category from the provided list
4. Return a JSON object with 'category' and 'confidence' fields
5. Confidence should be between 0 and 1, where 1 is most confident

Example response:
{{"category": "Technical", "confidence": 0.95}}

"""

        self.human_prompt = """Document Content:
{content}

Metadata:
{metadata}

Categories to choose from: {categories}

Return only the JSON object with 'category' and 'confidence' fields. Do not include any other text or markdown formatting."""
        
        # Create the prompt template with proper variable handling
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", self.human_prompt)
        ])
        
        # Update the chain to properly format the output
        self.chain = ({
            "content": lambda x: x["content"],
            "metadata": lambda x: x["metadata"],
            "categories": lambda x: x["categories"]
        }) | self.prompt | self.llm | self.parser

    def classify(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the document based on its content and metadata.
        
        Args:
            text_data: Dictionary containing 'content', 'metadata', and other document info
            
        Returns:
            Updated text_data with classification results
        """
        if not text_data.get('success', False):
            return text_data
            
        try:
            # Limit content size to prevent token limit issues
            content = text_data.get('content', '')[:10000]  
            metadata = text_data.get('metadata', {})
            
            # Get structured output from the LLM
            result = self.chain.invoke({
                "content": content,
                "metadata": json.dumps(metadata, indent=2),
                "categories": ", ".join(self.categories)
            })
            
            # If we got a string instead of a dict, try to parse it
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse LLM response as JSON: {result}")
                    result = {"category": "Other", "confidence": 0.5}
            
            # Ensure we have the expected fields
            if not isinstance(result, dict):
                result = {"category": "Other", "confidence": 0.5}
            
            # Update text_data with classification results
            text_data['category'] = result.get('category', 'Other')
            text_data['confidence'] = float(result.get('confidence', 0.5))
            
            return text_data
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}", exc_info=True)
            # Fallback to default category
            text_data['category'] = 'Other'
            text_data['confidence'] = 0.5
            return text_data