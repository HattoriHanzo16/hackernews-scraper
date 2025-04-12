from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from datetime import datetime
from ..models import Story

class IScraper(ABC):
    """Abstract base class defining the interface for HackerNews scrapers."""
    
    @abstractmethod
    def scrape_page(self, page_num: int = 1) -> List[Story]:
        """Scrape a single page of HackerNews stories."""
        pass
    
    @abstractmethod
    def start_scraping(self, callback: Optional[Callable] = None, num_pages: int = 1) -> None:
        """Start scraping in a background thread."""
        pass
    
    @abstractmethod
    def stop_scraping(self) -> None:
        """Stop the background scraping process."""
        pass
    
    @abstractmethod
    def scrape_stories(self, num_pages: int = 1) -> List[Story]:
        """Scrape multiple pages of stories synchronously."""
        pass 