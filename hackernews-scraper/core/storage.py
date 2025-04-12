"""
File-based storage implementation for HackerNews stories.
"""

import json
from typing import List, Optional
from pathlib import Path

from ..interfaces.storage import IStorage
from ..models.story import Story
from ..config.settings import StorageConfig
from ..exceptions.exceptions import StorageError

class FileStorage(IStorage):
    """
    File-based storage implementation that saves stories to JSON files.
    Implements the IStorage interface.
    """
    
    def __init__(self, config: Optional[StorageConfig] = None):
        """
        Initialize the storage with configuration.
        
        Args:
            config: Storage configuration. If None, uses default configuration.
        """
        self.config = config or StorageConfig()
        self.stories_path = self.config.stories_file
    
    def save_stories(self, stories: List[Story]) -> None:
        """
        Save stories to a JSON file.
        
        Args:
            stories: List of Story objects to save
        """
        try:
            # Convert stories to dictionaries
            stories_data = [story.to_dict() for story in stories]
            
            # Save to JSON file
            with open(self.stories_path, 'w', encoding='utf-8') as f:
                json.dump(stories_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            raise StorageError(f"Failed to save stories: {str(e)}")
    
    def load_stories(self) -> List[Story]:
        """
        Load stories from a JSON file.
        
        Returns:
            List of Story objects
        """
        try:
            # Check if file exists
            if not self.stories_path.exists():
                return []
            
            # Load from JSON file
            with open(self.stories_path, 'r', encoding='utf-8') as f:
                stories_data = json.load(f)
            
            # Convert dictionaries back to Story objects
            stories = [Story.from_dict(data) for data in stories_data]
            return stories
        
        except Exception as e:
            raise StorageError(f"Failed to load stories: {str(e)}")
    
    def get_story_by_id(self, story_id: str) -> Optional[Story]:
        """
        Retrieve a specific story by its ID.
        
        Args:
            story_id: ID of the story to retrieve
            
        Returns:
            Story object if found, None otherwise
        """
        try:
            stories = self.load_stories()
            for story in stories:
                if str(story.story_id) == story_id:
                    return story
            return None
        except Exception as e:
            raise StorageError(f"Failed to get story by ID: {str(e)}")
    
    def clear_storage(self) -> None:
        """Clear all stored stories."""
        try:
            if self.stories_path.exists():
                self.stories_path.unlink()
        except Exception as e:
            raise StorageError(f"Failed to clear storage: {str(e)}")
    
    def get_story_count(self) -> int:
        """
        Get the number of stored stories.
        
        Returns:
            Number of stories in storage
        """
        try:
            stories = self.load_stories()
            return len(stories)
        except Exception as e:
            raise StorageError(f"Failed to get story count: {str(e)}")
    
    def append_stories(self, stories: List[Story]) -> None:
        """
        Append stories to existing storage.
        
        Args:
            stories: List of Story objects to append
        """
        try:
            existing_stories = self.load_stories()
            all_stories = existing_stories + stories
            self.save_stories(all_stories)
        except Exception as e:
            raise StorageError(f"Failed to append stories: {str(e)}")
    
    def get_latest_stories(self, limit: int = 10) -> List[Story]:
        """
        Get the most recently stored stories.
        
        Args:
            limit: Maximum number of stories to return
            
        Returns:
            List of Story objects, sorted by timestamp (newest first)
        """
        try:
            stories = self.load_stories()
            sorted_stories = sorted(stories, key=lambda x: x.timestamp, reverse=True)
            return sorted_stories[:limit]
        except Exception as e:
            raise StorageError(f"Failed to get latest stories: {str(e)}") 