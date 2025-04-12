#!/usr/bin/env python3
"""
HackerNews Scraper

A comprehensive web scraper for HackerNews that extracts story data,
performs analysis, and offers visualizations.
"""

import os
import sys
import time
import argparse
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Story
from .core.scraper import HackerNewsScraper
from .core.async_scraper import AsyncHackerNewsScraper
from .core.storage import FileStorage
from .core.analysis import StoryAnalyzer
from .core.gui import run_gui
from .config.settings import ScraperConfig, StorageConfig, LoggingConfig
from .exceptions.exceptions import ScraperError, StorageError, AnalysisError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HackerNewsMain')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='HackerNews Scraper and Analyzer'
    )
    
    # Create mutually exclusive group for main actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--scrape', action='store_true', help='Scrape stories')
    action_group.add_argument('--analyze', metavar='FILE', help='Analyze stories from file')
    action_group.add_argument('--gui', action='store_true', help='Run the GUI')
    
    # Scraping options
    parser.add_argument('--pages', type=int, default=1, help='Number of pages to scrape')
    parser.add_argument('--use-async', action='store_true', help='Use async scraper')
    parser.add_argument('--rate-limit', type=float, default=1.0, help='Rate limit in seconds')
    
    # Analysis options
    parser.add_argument('--trending', action='store_true', help='Show trending topics and domains')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    parser.add_argument('--plot-dir', type=Path, default='plots', help='Directory to save plots')
    
    return parser.parse_args()

async def async_scrape_and_save(num_pages: int, config: ScraperConfig) -> List[Story]:
    """Scrape stories asynchronously and save them."""
    try:
        scraper = AsyncHackerNewsScraper(config=config)
        stories = await scraper.scrape_stories(num_pages)
        
        storage = FileStorage()
        storage.save_stories(stories)
        
        return stories
    except Exception as e:
        logging.error(f"Failed to scrape stories: {str(e)}")
        raise

def sync_scrape_and_save(num_pages: int, config: ScraperConfig) -> List[Story]:
    """Scrape stories synchronously and save them."""
    try:
        scraper = HackerNewsScraper(config=config)
        stories = scraper.scrape_stories(num_pages)
        
        storage = FileStorage()
        storage.save_stories(stories)
        
        return stories
    except Exception as e:
        logging.error(f"Failed to scrape stories: {str(e)}")
        raise

def analyze_data(stories: List[Story], args: argparse.Namespace) -> None:
    """Analyze scraped stories."""
    try:
        analyzer = StoryAnalyzer(stories)
        
        # Get basic stats
        stats = analyzer.get_basic_stats()
        print("\nBasic Statistics:")
        print(f"Total stories: {stats['total_stories']}")
        print(f"Average points: {stats['avg_points']:.2f}")
        print(f"Average comments: {stats['avg_comments']:.2f}")
        
        # Show trending if requested
        if args.trending:
            print("\nTrending Topics:")
            for topic, count in analyzer.get_trending_topics():
                print(f"  {topic}: {count}")
            
            print("\nTrending Domains:")
            for domain, count in analyzer.get_trending_domains():
                print(f"  {domain}: {count}")
        
        # Generate plots if requested
        if args.plot:
            args.plot_dir.mkdir(exist_ok=True)
            
            plots = [
                ('trending_domains.png', analyzer.plot_trending_domains),
                ('post_distribution.png', analyzer.plot_post_distribution_by_hour),
                ('karma_distribution.png', analyzer.plot_karma_distribution),
                ('points_vs_comments.png', analyzer.plot_points_vs_comments)
            ]
            
            for filename, plot_func in plots:
                fig = plot_func()
                if fig:
                    analyzer.save_plot(fig, args.plot_dir / filename)
                    print(f"Saved plot: {filename}")
    
    except Exception as e:
        logging.error(f"Failed to analyze stories: {str(e)}")
        raise

def main():
    """Main entry point."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    args = parse_arguments()
    
    # Run GUI if requested
    if args.gui:
        run_gui()
        return
    
    # Configure scraper
    config = ScraperConfig(rate_limit=args.rate_limit)
    
    try:
        if args.scrape:
            # Scrape stories
            if args.use_async:
                stories = asyncio.run(async_scrape_and_save(args.pages, config))
            else:
                stories = sync_scrape_and_save(args.pages, config)
            
            print(f"Successfully scraped {len(stories)} stories")
            
            # Analyze if requested
            if args.trending or args.plot:
                analyze_data(stories, args)
        
        elif args.analyze:
            # Load stories from file
            storage = FileStorage()
            stories = storage.load_stories()
            
            if not stories:
                print("No stories found to analyze")
                return
            
            # Analyze stories
            analyze_data(stories, args)
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
