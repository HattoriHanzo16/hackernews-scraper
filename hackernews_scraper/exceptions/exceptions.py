"""
Custom exceptions for the HackerNews scraper.
"""

class ScraperError(Exception):
    """Base exception for scraper-related errors."""
    def __init__(self, message: str = "An error occurred during scraping"):
        self.message = message
        super().__init__(self.message)

class ScrapingError(ScraperError):
    """Exception raised when scraping fails."""
    def __init__(self, message: str = "Failed to scrape the requested data"):
        super().__init__(message)

class RateLimitError(ScraperError):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded. Please wait before making more requests"):
        super().__init__(message)

class RobotsTxtError(ScraperError):
    """Exception raised when robots.txt cannot be parsed or respected."""
    def __init__(self, message: str = "Failed to parse or respect robots.txt rules"):
        super().__init__(message)

class StorageError(Exception):
    """Base exception for storage-related errors."""
    def __init__(self, message: str = "An error occurred during storage operations"):
        self.message = message
        super().__init__(self.message)

class SaveError(StorageError):
    """Exception raised when saving stories fails."""
    def __init__(self, message: str = "Failed to save stories"):
        super().__init__(message)

class LoadError(StorageError):
    """Exception raised when loading stories fails."""
    def __init__(self, message: str = "Failed to load stories"):
        super().__init__(message)

class AnalysisError(Exception):
    """Base exception for analysis-related errors."""
    def __init__(self, message: str = "An error occurred during analysis"):
        self.message = message
        super().__init__(self.message) 