"""
Interface for story analysis functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import plotly.graph_objects as go

class IAnalyzer(ABC):
    """
    Interface for analyzing HackerNews stories.
    """
    
    @abstractmethod
    def get_basic_stats(self) -> Dict:
        """
        Get basic statistics about the stories.
        
        Returns:
            Dictionary containing basic statistics
        """
        pass
    
    @abstractmethod
    def get_trending_topics(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Identify trending topics from story titles.
        
        Args:
            top_n: Number of top topics to return
            
        Returns:
            List of (topic, count) tuples
        """
        pass

    
    @abstractmethod
    def get_trending_domains(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Identify trending domains from story URLs.
        
        Args:
            top_n: Number of top domains to return
            
        Returns:
            List of (domain, count) tuples
        """
        pass
    
    @abstractmethod
    def analyze_post_popularity_by_time(self) -> Dict[int, int]:
        """
        Analyze post popularity by hour of the day.
        
        Returns:
            Dictionary mapping hour to number of posts
        """
        pass
    
    @abstractmethod
    def plot_trending_domains(self) -> Optional[go.Figure]:
        """
        Create a bar plot of trending domains.
        
        Returns:
            Plotly figure object
        """
        pass
    
    @abstractmethod
    def plot_post_distribution_by_hour(self) -> Optional[go.Figure]:
        """
        Create a line plot of post distribution by hour.
        
        Returns:
            Plotly figure object
        """
        pass
    
    @abstractmethod
    def plot_karma_distribution(self) -> Optional[go.Figure]:
        """
        Create a histogram of user karma distribution.
        
        Returns:
            Plotly figure object
        """
        pass
    
    @abstractmethod
    def plot_points_vs_comments(self) -> Optional[go.Figure]:
        """
        Create a scatter plot of points versus comments.
        
        Returns:
            Plotly figure object
        """
        pass
    
    @abstractmethod
    def save_plot(self, fig: go.Figure, filepath: str) -> None:
        """
        Save a Plotly figure to a file.
        
        Args:
            fig: Plotly figure object
            filepath: Path to save the figure
        """
        pass 