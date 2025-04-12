"""
Analysis module for HackerNews stories.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from typing import List, Dict, Tuple, Optional
import re
from urllib.parse import urlparse

from ..models.story import Story
from ..interfaces.analysis import IAnalyzer
from ..exceptions.exceptions import AnalysisError

class StoryAnalyzer(IAnalyzer):
    """
    Analyzes HackerNews stories for trends and patterns.
    Implements the IAnalyzer interface.
    """
    
    def __init__(self, stories: List[Story]):
        """
        Initialize the analyzer with a list of stories.
        
        Args:
            stories: List of Story objects to analyze
        """
        self.stories = stories
        self.df = pd.DataFrame([story.to_dict() for story in stories])
    
    def get_basic_stats(self) -> Dict:
        """
        Get basic statistics about the stories.
        
        Returns:
            Dictionary containing basic statistics
        """
        try:
            return {
                'total_stories': len(self.stories),
                'avg_points': self.df['points'].mean(),
                'avg_comments': self.df['comment_count'].mean(),
                'max_points': self.df['points'].max(),
                'max_comments': self.df['comment_count'].max()
            }
        except Exception as e:
            raise AnalysisError(f"Failed to calculate basic stats: {str(e)}")
    
    def get_trending_topics(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Identify trending topics from story titles.
        
        Args:
            top_n: Number of top topics to return
            
        Returns:
            List of (topic, count) tuples
        """
        try:
            # Extract words from titles
            words = []
            for title in self.df['title']:
                words.extend(re.findall(r'\w+', title.lower()))
            
            # Count word frequencies
            word_counts = Counter(words)
            
            # Remove common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            for word in common_words:
                word_counts.pop(word, None)
            
            return word_counts.most_common(top_n)
        except Exception as e:
            raise AnalysisError(f"Failed to identify trending topics: {str(e)}")
    
    def get_trending_domains(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Identify trending domains from story URLs.
        
        Args:
            top_n: Number of top domains to return
            
        Returns:
            List of (domain, count) tuples
        """
        try:
            # Extract domains from URLs
            domains = []
            for url in self.df['url']:
                try:
                    domain = urlparse(url).netloc
                    if domain:
                        domains.append(domain)
                except:
                    continue
            
            # Count domain frequencies
            domain_counts = Counter(domains)
            return domain_counts.most_common(top_n)
        except Exception as e:
            raise AnalysisError(f"Failed to identify trending domains: {str(e)}")
    
    def analyze_post_popularity_by_time(self) -> Dict[int, int]:
        """
        Analyze post popularity by hour of the day.
        
        Returns:
            Dictionary mapping hour to number of posts
        """
        try:
            if 'timestamp' not in self.df.columns:
                return {}
            
            # Extract hour from timestamps
            self.df['hour'] = pd.to_datetime(self.df['timestamp']).dt.hour
            
            # Count posts by hour
            hour_counts = self.df['hour'].value_counts().sort_index()
            return dict(zip(hour_counts.index, hour_counts.values))
        except Exception as e:
            raise AnalysisError(f"Failed to analyze post popularity by time: {str(e)}")
    
    def plot_trending_domains(self) -> Optional[go.Figure]:
        """
        Create a bar plot of trending domains.
        
        Returns:
            Plotly figure object
        """
        try:
            domains, counts = zip(*self.get_trending_domains())
            
            fig = go.Figure(data=[
                go.Bar(x=domains, y=counts)
            ])
            
            fig.update_layout(
                title='Trending Domains',
                xaxis_title='Domain',
                yaxis_title='Number of Stories',
                showlegend=False
            )
            
            return fig
        except Exception as e:
            raise AnalysisError(f"Failed to create trending domains plot: {str(e)}")
    
    def plot_post_distribution_by_hour(self) -> Optional[go.Figure]:
        """
        Create a line plot of post distribution by hour.
        
        Returns:
            Plotly figure object
        """
        try:
            hour_data = self.analyze_post_popularity_by_time()
            if not hour_data:
                return None
            
            hours = list(hour_data.keys())
            counts = list(hour_data.values())
            
            fig = go.Figure(data=[
                go.Scatter(x=hours, y=counts, mode='lines+markers')
            ])
            
            fig.update_layout(
                title='Post Distribution by Hour',
                xaxis_title='Hour of Day',
                yaxis_title='Number of Posts',
                showlegend=False
            )
            
            return fig
        except Exception as e:
            raise AnalysisError(f"Failed to create post distribution plot: {str(e)}")
    
    def plot_karma_distribution(self) -> Optional[go.Figure]:
        """
        Create a histogram of user karma distribution.
        
        Returns:
            Plotly figure object
        """
        try:
            fig = px.histogram(self.df, x='points', nbins=50)
            
            fig.update_layout(
                title='Karma Distribution',
                xaxis_title='Points',
                yaxis_title='Number of Stories',
                showlegend=False
            )
            
            return fig
        except Exception as e:
            raise AnalysisError(f"Failed to create karma distribution plot: {str(e)}")
    
    def plot_points_vs_comments(self) -> Optional[go.Figure]:
        """
        Create a scatter plot of points versus comments.
        
        Returns:
            Plotly figure object
        """
        try:
            fig = go.Figure(data=[
                go.Scatter(
                    x=self.df['points'],
                    y=self.df['comment_count'],
                    mode='markers',
                    text=self.df['title'],
                    hoverinfo='text'
                )
            ])
            
            fig.update_layout(
                title='Points vs Comments',
                xaxis_title='Points',
                yaxis_title='Number of Comments',
                showlegend=False
            )
            
            return fig
        except Exception as e:
            raise AnalysisError(f"Failed to create points vs comments plot: {str(e)}")
    
    def save_plot(self, fig: go.Figure, filepath: str) -> None:
        """
        Save a Plotly figure to a file.
        
        Args:
            fig: Plotly figure object
            filepath: Path to save the figure
        """
        try:
            fig.write_image(filepath)
        except Exception as e:
            raise AnalysisError(f"Failed to save plot: {str(e)}") 