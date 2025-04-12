import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from hackernews_scraper.core.scraper import HackerNewsScraper
from hackernews_scraper.models import Story
from hackernews_scraper.config.settings import ScraperConfig


class TestScraper(unittest.TestCase):
    """Test cases for the Scraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        config = ScraperConfig(rate_limit=0.01)  # Use small rate limit for tests
        self.scraper = HackerNewsScraper(config=config)
    
    @patch('hackernews_scraper.core.scraper.requests.Session')
    def test_initialization(self, mock_session):
        """Test that scraper is initialized correctly."""
        # Setup mock
        mock_session.return_value.get.return_value.status_code = 200
        mock_session.return_value.get.return_value.text = "User-agent: *\nAllow: /"
        
        config = ScraperConfig(rate_limit=2.0)
        scraper = HackerNewsScraper(config=config)
        
        # Check that session is created
        self.assertIsNotNone(scraper.session)
        
        # Check that rate limit is set
        self.assertEqual(scraper.config.rate_limit, 2.0)
        
        # Check that robots.txt was loaded
        mock_session.return_value.get.assert_called_once()
    
    @patch('hackernews_scraper.core.scraper.HackerNewsScraper._make_request')
    def test_scrape_page_empty_response(self, mock_make_request):
        """Test scraping with empty response."""
        # Setup mock to return None (failed request)
        mock_make_request.return_value = None
        
        # Try to scrape page
        with self.assertRaises(Exception):
            self.scraper.scrape_page(1)
        
        # Check that request was made
        mock_make_request.assert_called_once()
    
    @patch('hackernews_scraper.core.scraper.HackerNewsScraper._make_request')
    @patch('hackernews_scraper.core.scraper.BeautifulSoup')
    def test_scrape_page_no_stories(self, mock_bs, mock_make_request):
        """Test scraping page with no stories."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"
        mock_make_request.return_value = mock_response
        
        mock_soup = MagicMock()
        mock_soup.select.return_value = []  # No story items
        mock_bs.return_value = mock_soup
        
        # Try to scrape page
        stories = self.scraper.scrape_page(1)
        
        # Check results
        self.assertEqual(len(stories), 0)
        mock_soup.select.assert_called_once_with('tr.athing')
    
    @patch('hackernews_scraper.core.scraper.HackerNewsScraper.scrape_page')
    def test_scrape_stories(self, mock_scrape_page):
        """Test scraping multiple pages."""
        # Setup mock
        mock_story = Story(
            title="Test Story",
            url="https://example.com",
            points=100,
            comment_count=42,
            username="testuser",
            story_id="12345",
            time=datetime.now()
        )
        mock_scrape_page.side_effect = [
            [mock_story, mock_story],  # Page 1: 2 stories
            [mock_story]               # Page 2: 1 story
        ]
        
        # Call method
        stories = self.scraper.scrape_stories(2)
        
        # Check results
        self.assertEqual(len(stories), 3)
        self.assertEqual(mock_scrape_page.call_count, 2)
        
        # Check that the correct page numbers were passed
        mock_scrape_page.assert_any_call(1)
        mock_scrape_page.assert_any_call(2)


if __name__ == "__main__":
    unittest.main() 