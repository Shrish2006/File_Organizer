import json
from typing import Dict, Any
import logging
from pydantic import BaseModel, Field
from ..llm.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

class ClassificationResult(BaseModel):
    category: str = Field(..., description="The category that best describes the content")
    confidence: float = Field(..., description="Confidence score between 0 and 1")

class ClassificationAgent:
    def __init__(self, categories: list = None):
        self.categories = categories or [
            "Academics", "Business", "Finance", "Legal", "Medical",
            "Technical", "Creative", "Personal", "Other"
        ]
        self.llm = get_llm()
        self.parser = JsonOutputParser(pydantic_object=ClassificationResult)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert document classifier. Analyze the provided text and metadata,
            then classify the document into one of these categories: {categories}
            
            Return your response as a JSON object with 'category' and 'confidence' fields.
            Example: {{"category": "Technical", "confidence": 0.95}}
            """),
            ("human", """
            Document Content:
            {content}
            
            Metadata:
            {metadata}
            
            Classification:
            """)
        ])
        
        self.chain = self.prompt | self.llm

    def _clean_json_output(self, text: str) -> str:
        """Clean and extract JSON from model output."""
        # Remove any markdown code block markers
        text = text.replace('```json', '').replace('```', '').strip()
        # Extract JSON object
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > 0:
            return text[start:end]
        return text

    def classify(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        if not text_data.get('success', False):
            return text_data
            
        try:
            content = text_data.get('content', '')[:10000]  # Limit content size
            metadata = text_data.get('metadata', {})
            
            # Get raw output from LLM
            raw_output = self.chain.invoke({
                "content": content,
                "metadata": metadata,
                "categories": self.categories
            }).content
            
            # Clean and parse JSON
            cleaned_json = self._clean_json_output(raw_output)
            result = json.loads(cleaned_json)
            
            # Validate result
            if not all(k in result for k in ('category', 'confidence')):
                raise ValueError("Missing required fields in classification result")
                
            if result['category'] not in self.categories:
                result['category'] = 'Other'
                
            text_data['classification'] = {
                'category': result['category'],
                'confidence': min(1.0, max(0.0, float(result['confidence'])))
            }
            return text_data
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            text_data['classification'] = {
                'category': 'Other',
                'confidence': 0.5
            }
            text_data['success'] = True  # Continue processing even if classification fails
            return text_data