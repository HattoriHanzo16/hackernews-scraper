"""
Configuration settings for the HackerNews scraper.
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path

@dataclass
class ScraperConfig:
    """Configuration for the scraper."""
    base_url: str = "https://news.ycombinator.com/"
    rate_limit: float = 1.0
    timeout: int = 30
    max_retries: int = 3
    user_agents: List[str] = None

    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
            ]

@dataclass
class StorageConfig:
    """Configuration for storage."""
    data_dir: str = "data"
    stories_file: str = "stories.json"
    
    def __post_init__(self):
        # Convert data_dir to absolute Path and create it
        self.data_dir = Path(self.data_dir).resolve()
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create data directory: {str(e)}")
        
        # Make stories_file a full path
        self.stories_file = self.data_dir / self.stories_file

@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: str = "hackernews_scraper.log" 