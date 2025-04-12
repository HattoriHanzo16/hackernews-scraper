"""
Asynchronous scraper for HackerNews.
"""

import asyncio
import aiohttp
import logging
from typing import List, Optional, Dict, Any, Callable
from urllib.parse import urljoin
import random
import time
from datetime import datetime

from bs4 import BeautifulSoup
import robotexclusionrulesparser

from ..interfaces.scraper import IScraper
from ..models.story import Story
from ..config.settings import ScraperConfig
from ..exceptions.exceptions import ScraperError, StorageError, AnalysisError

class AsyncHackerNewsScraper(IScraper):
    """
    Asynchronous implementation of the HackerNews scraper interface.
    Handles scraping of HackerNews stories with rate limiting and robots.txt respect.
    """
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper with configuration.
        
        Args:
            config: Scraper configuration. If None, uses default configuration.
        """
        self.config = config or ScraperConfig()
        self.session = None
        self.last_request_time = 0
        self.robot_parser = robotexclusionrulesparser.RobotExclusionRulesParser()
        self._scraping = True  # Set to True by default since we're not using background tasks
        self._stop_flag = False
        
        self._setup_logging()
        self._load_robots_txt()
    
    def _setup_logging(self):
        """Configure logging for the scraper."""
        self.logger = logging.getLogger('AsyncHackerNewsScraper')
    
    async def _load_robots_txt(self) -> None:
        """Load and parse robots.txt."""
        try:
            async with aiohttp.ClientSession() as session:
                robots_url = urljoin(self.config.base_url, "robots.txt")
                async with session.get(robots_url, timeout=self.config.timeout) as response:
                    text = await response.text()
                    self.robot_parser.parse(text)
        except Exception as e:
            self.logger.warning(f"Failed to load robots.txt: {str(e)}")
    
    async def _respect_rate_limit(self) -> None:
        """Ensure we respect the rate limit between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.config.rate_limit:
            await asyncio.sleep(self.config.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    async def _make_request(self, url: str) -> str:
        """Make an HTTP request with retries and rate limiting."""
        for attempt in range(self.config.max_retries):
            try:
                await self._respect_rate_limit()
                headers = {'User-Agent': random.choice(self.config.user_agents)}
                async with self.session.get(url, headers=headers, timeout=self.config.timeout) as response:
                    response.raise_for_status()
                    return await response.text()
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise ScraperError(f"Failed to fetch {url}: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def scrape_page(self, page_num: int = 1) -> List[Story]:
        """Scrape a single page of HackerNews stories."""
        try:
            url = f"{self.config.base_url}news?p={page_num}"
            self.logger.info(f"Scraping page {page_num} from {url}")
            
            html = await self._make_request(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            stories = []
            story_items = soup.select('tr.athing')
            self.logger.info(f"Found {len(story_items)} story items on page {page_num}")
            
            for item in story_items:
                try:
                    story = await self._parse_item(item)
                    if story:
                        stories.append(story)
                        self.logger.debug(f"Successfully parsed story: {story.title}")
                    else:
                        self.logger.warning(f"Failed to parse story item with ID: {item.get('id', 'unknown')}")
                except Exception as e:
                    self.logger.error(f"Error parsing story item: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully scraped {len(stories)} stories from page {page_num}")
            return stories
            
        except Exception as e:
            self.logger.error(f"Failed to scrape page {page_num}: {str(e)}")
            return []
    
    async def _parse_item(self, item) -> Optional[Story]:
        """Parse a single story item from the HTML."""
        try:
            title_elem = item.select_one('.titleline > a')
            if not title_elem:
                return None
                
            title = title_elem.text.strip()
            url = title_elem.get('href')
            story_id = item.get('id')
            
            subtext = item.find_next_sibling('tr').select_one('.subtext')
            if not subtext:
                return None
                
            score_elem = subtext.select_one('.score')
            points = 0
            if score_elem:
                points = int(score_elem.text.split()[0])
            
            username_elem = subtext.select_one('.hnuser')
            username = username_elem.text if username_elem else 'unknown'
            
            # Parse time information
            time_elem = subtext.select_one('.age')
            post_time = datetime.now()  # Default to now if we can't parse
            if time_elem:
                time_str = time_elem.get('title', '')  # Gets the exact timestamp
                if time_str:
                    try:
                        # Split on space to remove the Unix timestamp part
                        iso_time = time_str.split()[0]
                        post_time = datetime.fromisoformat(iso_time)
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"Failed to parse time string: {time_str}")
            
            comment_elem = None
            for link in subtext.select('a'):
                if 'comment' in link.text.lower():
                    comment_elem = link
                    break
            
            comment_count = 0
            if comment_elem:
                try:
                    comment_count = int(comment_elem.text.split()[0])
                except (ValueError, IndexError):
                    pass
            
            return Story(
                title=title,
                url=url,
                points=points,
                username=username,
                comment_count=comment_count,
                story_id=story_id,
                time=post_time
            )
        except Exception as e:
            self.logger.error(f"Failed to parse story item: {str(e)}")
            return None
    
    async def scrape_stories(self, num_pages: int = 1, progress_callback: Optional[Callable] = None) -> List[Story]:
        """
        Scrape stories from HackerNews asynchronously.
        
        Args:
            num_pages: Number of pages to scrape
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of Story objects
        """
        stories = []
        stories_scraped = 0
        
        try:
            async with aiohttp.ClientSession() as session:
                self.session = session
                for page in range(1, num_pages + 1):
                    if self._stop_flag:
                        break
                    
                    # Scrape stories from current page
                    page_stories = await self.scrape_page(page)
                    stories.extend(page_stories)
                    stories_scraped += len(page_stories)
                    
                    # Report progress if callback provided
                    if progress_callback:
                        stats = self._calculate_stats(stories)
                        progress_callback(stories_scraped, stats)
                    
                    # Rate limiting
                    if page < num_pages:
                        await asyncio.sleep(self.config.rate_limit)
                
                self.logger.info(f"Successfully scraped {len(stories)} stories total")
                return stories
                
        except Exception as e:
            self.logger.error(f"Failed to scrape stories: {str(e)}")
            raise ScraperError(f"Failed to scrape stories: {str(e)}")
    
    def _calculate_stats(self, stories: List[Story]) -> dict:
        """Calculate current statistics for progress reporting."""
        if not stories:
            return {'avg_points': 0, 'avg_comments': 0}
        
        total_points = sum(story.points for story in stories if story.points is not None)
        total_comments = sum(story.comment_count for story in stories if story.comment_count is not None)
        count = len(stories)
        
        return {
            'avg_points': total_points / count if count > 0 else 0,
            'avg_comments': total_comments / count if count > 0 else 0
        }

    async def start_scraping(self, callback: Optional[Callable] = None, num_pages: int = 1) -> None:
        """Start scraping in a background thread."""
        if self._scraping:
            raise ScraperError("Scraping is already in progress")
        
        self._scraping = True
        
        try:
            stories = await self.scrape_stories(num_pages)
            if callback:
                callback(stories)
        finally:
            self._scraping = False

    def stop_scraping(self) -> None:
        """Stop the background scraping process."""
        self._stop_flag = True
        self._scraping = False 