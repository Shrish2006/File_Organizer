from typing import Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def get_llm(
    model: str = "gemini-2.5-flash-lite",
    temperature: float = 0,
    **kwargs
):
    """
    Create and return a Google Gemini model instance.
    
    Args:
        model: The Gemini model to use (default: 'gemini-2.5-flash-lite')
        temperature: Controls randomness (0 = deterministic)
        **kwargs: Additional arguments to pass to the model
        
    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    # Get API key from environment variables
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not found. Please set it in your .env file.")
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Validate the model (free tier models)
    free_models = [
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-1.0-flash-latest",
        "gemini-1.0-pro-latest"
    ]
    
    if model not in free_models:
        logger.warning(f"Model {model} may not be in the free tier. Consider using one of: {', '.join(free_models)}")
    
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        **kwargs
    )