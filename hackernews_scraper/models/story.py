"""
Story model for the HackerNews scraper.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

@dataclass
class Story:
    """
    Represents a HackerNews story.
    
    Attributes:
        title: The title of the story
        url: The URL of the story
        points: The number of points (upvotes) the story has received
        username: The username of the story submitter
        comment_count: The number of comments on the story
        story_id: The unique identifier of the story on HackerNews
        time: When the story was posted
    """
    title: str
    url: str
    points: int
    username: str
    comment_count: int
    story_id: str
    time: datetime
    
    @property
    def domain(self) -> Optional[str]:
        """Get the domain from the URL."""
        if not self.url:
            return None
        try:
            parsed = urlparse(self.url)
            return parsed.netloc
        except Exception:
            return ""
    
    def __post_init__(self):
        """Validate the story data after initialization."""
        if not self.title:
            raise ValueError("Story title cannot be empty")
        if not self.url:
            self.url = f"https://news.ycombinator.com/item?id={self.story_id}"
        if self.points < 0:
            self.points = 0
        if not self.username:
            self.username = 'unknown'
        if self.comment_count < 0:
            self.comment_count = 0
        if not self.story_id:
            raise ValueError("Story ID cannot be empty")
    
    def to_dict(self) -> dict:
        """
        Convert the story to a dictionary.
        
        Returns:
            Dictionary representation of the story
        """
        return {
            'title': self.title,
            'url': self.url,
            'points': self.points,
            'username': self.username,
            'comment_count': self.comment_count,
            'story_id': self.story_id,
            'time': self.time.isoformat() if self.time else None,
            'domain': self.domain
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Story':
        """
        Create a story from a dictionary.
        
        Args:
            data: Dictionary containing story data
            
        Returns:
            Story instance
        """
        # Remove domain from data since it's a computed property
        data = {k: v for k, v in data.items() if k != 'domain'}
        
        if 'time' in data and data['time']:
            data['time'] = datetime.fromisoformat(data['time'])
        return cls(**data) 