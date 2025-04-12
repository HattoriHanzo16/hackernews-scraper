import re
import time
import random
import logging
import threading
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Dict, Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import robotexclusionrulesparser

from ..interfaces.scraper import IScraper
from ..models import Story
from ..config.settings import ScraperConfig
from ..exceptions.exceptions import ScrapingError, RateLimitError, RobotsTxtError

class HackerNewsScraper(IScraper):
    """
    Implementation of the HackerNews scraper interface.
    Handles scraping of HackerNews stories with rate limiting and robots.txt respect.
    """
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper with configuration.
        
        Args:
            config: Scraper configuration. If None, uses default configuration.
        """
        self.config = config or ScraperConfig()
        self.session = requests.Session()
        self.last_request_time = 0
        self.robot_parser = robotexclusionrulesparser.RobotExclusionRulesParser()
        self._scraping = False
        self._scrape_thread = None
        self._stop_flag = False
        
        self._setup_logging()
        self._load_robots_txt()
        self._rotate_user_agent()
    
    def _setup_logging(self):
        """Configure logging for the scraper."""
        self.logger = logging.getLogger('HackerNewsScraper')
        self.logger.setLevel(logging.DEBUG)
        
        # Add console handler if none exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _load_robots_txt(self) -> None:
        """Load and parse robots.txt."""
        try:
            robots_url = urljoin(self.config.base_url, "robots.txt")
            response = self.session.get(robots_url, timeout=self.config.timeout)
            self.robot_parser.parse(response.text)
        except Exception as e:
            raise RobotsTxtError(f"Failed to load robots.txt: {str(e)}")
    
    def _rotate_user_agent(self) -> None:
        """Rotate the user agent for requests."""
        self.session.headers.update({
            'User-Agent': random.choice(self.config.user_agents)
        })
    
    def _respect_rate_limit(self) -> None:
        """Ensure we respect the rate limit between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.config.rate_limit:
            time.sleep(self.config.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make an HTTP request with retries and rate limiting."""
        for attempt in range(self.config.max_retries):
            try:
                self._respect_rate_limit()
                self.logger.debug(f"Making request to {url} (attempt {attempt + 1}/{self.config.max_retries})")
                response = self.session.get(url, timeout=self.config.timeout)
                response.raise_for_status()
                self.logger.debug(f"Request successful: {response.status_code}")
                return response
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.config.max_retries - 1:
                    raise ScrapingError(f"Failed to fetch {url}: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def scrape_page(self, page_num: int = 1) -> List[Story]:
        """Scrape a single page of HackerNews stories."""
        try:
            url = f"{self.config.base_url}news?p={page_num}"
            self.logger.info(f"Scraping page {page_num} from {url}")
            
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            stories = []
            story_items = soup.select('tr.athing')
            self.logger.info(f"Found {len(story_items)} story items on page {page_num}")
            
            for item in story_items:
                try:
                    story = self._parse_item(item)
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
            raise ScrapingError(f"Failed to scrape page {page_num}: {str(e)}")
    
    def _parse_item(self, item) -> Optional[Story]:
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
    
    def start_scraping(self, callback: Optional[Callable] = None, num_pages: int = 1) -> None:
        """Start scraping in a background thread."""
        if self._scraping:
            raise ScrapingError("Scraping is already in progress")
        
        self._scraping = True
        
        def scrape_thread():
            try:
                stories = self.scrape_stories(num_pages)
                if callback:
                    callback(stories)
            finally:
                self._scraping = False
        
        self._scrape_thread = threading.Thread(target=scrape_thread)
        self._scrape_thread.start()
    
    def stop_scraping(self) -> None:
        """Stop the background scraping process."""
        self._scraping = False
        if self._scrape_thread:
            self._scrape_thread.join()
        self._stop_flag = True
    
    def scrape_stories(self, num_pages: int = 1, progress_callback: Optional[Callable] = None) -> List[Story]:
        """
        Scrape stories from HackerNews.
        
        Args:
            num_pages: Number of pages to scrape
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of Story objects
        """
        stories = []
        stories_scraped = 0
        
        try:
            for page in range(1, num_pages + 1):
                if self._stop_flag:
                    break
                
                # Scrape stories from current page
                page_stories = self.scrape_page(page)
                stories.extend(page_stories)
                stories_scraped += len(page_stories)
                
                # Report progress if callback provided
                if progress_callback:
                    stats = self._calculate_stats(stories)
                    progress_callback(stories_scraped, stats)
                
                # Rate limiting
                if page < num_pages:
                    time.sleep(self.config.rate_limit)
            
            return stories
        
        except Exception as e:
            logging.error(f"Failed to scrape stories: {str(e)}")
            raise ScrapingError(f"Failed to scrape stories: {str(e)}")
    
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