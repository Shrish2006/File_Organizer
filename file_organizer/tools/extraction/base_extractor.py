from abc import ABC, abstractmethod
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> str:
        """Extract text from file. Must be implemented by subclasses."""
        pass