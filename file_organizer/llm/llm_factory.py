from langchain_ollama import ChatOllama
from typing import Optional

def get_llm(
    model: str = "llama3.1:8b",
    temperature: float = 0,
    **kwargs
):
    """
    Create and return a ChatOllama instance.
    
    Args:
        model: The Ollama model to use
        temperature: Controls randomness (0 = deterministic)
        **kwargs: Additional arguments to pass to ChatOllama
        
    Returns:
        Configured ChatOllama instance
    """
    return ChatOllama(
        model=model,
        temperature=temperature,
        **kwargs
    )