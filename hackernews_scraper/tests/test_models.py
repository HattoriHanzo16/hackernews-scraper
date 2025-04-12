import unittest
from datetime import datetime
from hackernews_scraper.models import Story


class TestStoryModel(unittest.TestCase):
    """Test cases for the Story model class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_story = Story(
            title="Test Story",
            url="https://example.com/test",
            points=100,
            comment_count=42,
            username="testuser",
            story_id="12345",
            time=datetime(2023, 10, 18, 12, 30, 0)
        )
    
    def test_story_initialization(self):
        """Test that a Story object is initialized correctly."""
        self.assertEqual(self.sample_story.title, "Test Story")
        self.assertEqual(self.sample_story.url, "https://example.com/test")
        self.assertEqual(self.sample_story.points, 100)
        self.assertEqual(self.sample_story.comment_count, 42)
        self.assertEqual(self.sample_story.username, "testuser")
        self.assertEqual(self.sample_story.time, datetime(2023, 10, 18, 12, 30, 0))
        self.assertEqual(self.sample_story.story_id, "12345")
    
    def test_domain_extraction(self):
        """Test that domain is correctly extracted from URL."""
        self.assertEqual(self.sample_story.domain, "example.com")
        
        # Test with None URL
        story_no_url = Story(
            title="Test Story No URL",
            url=None,
            points=100,
            comment_count=42,
            username="testuser",
            story_id="12346",
            time=datetime.now()
        )
        self.assertEqual(story_no_url.domain, "news.ycombinator.com")  # Default URL is used
        
        # Test with invalid URL
        story_invalid_url = Story(
            title="Test Story Invalid URL",
            url="not-a-url",
            points=100,
            comment_count=42,
            username="testuser",
            story_id="12347",
            time=datetime.now()
        )
        self.assertEqual(story_invalid_url.domain, "")
    
    def test_to_dict(self):
        """Test conversion of Story object to dictionary."""
        story_dict = self.sample_story.to_dict()
        
        self.assertIsInstance(story_dict, dict)
        self.assertEqual(story_dict["title"], "Test Story")
        self.assertEqual(story_dict["url"], "https://example.com/test")
        self.assertEqual(story_dict["points"], 100)
        self.assertEqual(story_dict["comment_count"], 42)
        self.assertEqual(story_dict["username"], "testuser")
        self.assertEqual(story_dict["story_id"], "12345")
        self.assertEqual(story_dict["domain"], "example.com")
        
        # Check that time is serialized correctly
        self.assertEqual(story_dict["time"], "2023-10-18T12:30:00")
    
    def test_from_dict(self):
        """Test creation of Story object from dictionary."""
        data = {
            "title": "Restored Story",
            "url": "https://example.org/restored",
            "points": 200,
            "comment_count": 10,
            "username": "restoreduser",
            "time": "2023-10-19T15:45:00",
            "story_id": "67890"
        }
        
        restored_story = Story.from_dict(data)
        
        self.assertEqual(restored_story.title, "Restored Story")
        self.assertEqual(restored_story.url, "https://example.org/restored")
        self.assertEqual(restored_story.points, 200)
        self.assertEqual(restored_story.comment_count, 10)
        self.assertEqual(restored_story.username, "restoreduser")
        self.assertEqual(restored_story.time, datetime(2023, 10, 19, 15, 45, 0))
        self.assertEqual(restored_story.story_id, "67890")
        self.assertEqual(restored_story.domain, "example.org")
    
    def test_from_dict_with_missing_fields(self):
        """Test creation of Story object from dictionary with missing fields."""
        data = {
            "title": "Minimal Story",
            "url": "https://example.net/minimal",
            "points": 50,
            "comment_count": 5,
            "username": "minimaluser",
            "story_id": "12348",
            "time": datetime.now().isoformat()
        }
        
        minimal_story = Story.from_dict(data)
        
        self.assertEqual(minimal_story.title, "Minimal Story")
        self.assertEqual(minimal_story.url, "https://example.net/minimal")
        self.assertEqual(minimal_story.points, 50)
        self.assertEqual(minimal_story.comment_count, 5)
        self.assertEqual(minimal_story.username, "minimaluser")
        self.assertEqual(minimal_story.domain, "example.net")
        self.assertEqual(minimal_story.story_id, "12348")
        
        # Check that time is set to a datetime
        self.assertIsInstance(minimal_story.time, datetime)


if __name__ == "__main__":
    unittest.main() 