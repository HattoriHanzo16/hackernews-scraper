from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Story

class IStorage(ABC):
    """Abstract base class defining the interface for story storage."""
    
    @abstractmethod
    def save_stories(self, stories: List[Story]) -> None:
        """Save a list of stories to storage."""
        pass
    
    @abstractmethod
    def load_stories(self) -> List[Story]:
        """Load all stories from storage."""
        pass
    
    @abstractmethod
    def get_story_by_id(self, story_id: str) -> Optional[Story]:
        """Retrieve a specific story by its ID."""
        pass
    
    @abstractmethod
    def clear_storage(self) -> None:
        """Clear all stored stories."""
        pass 