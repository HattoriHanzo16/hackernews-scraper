import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
from typing import Optional, Callable, List
from pathlib import Path
import webbrowser
from datetime import datetime
import sv_ttk  # For modern Fluent/Sun Valley theme
import time

from ..core.scraper import HackerNewsScraper
from ..core.async_scraper import AsyncHackerNewsScraper
from ..core.storage import FileStorage
from ..core.analysis import StoryAnalyzer
from ..config.settings import ScraperConfig, StorageConfig
from ..exceptions.exceptions import ScraperError, StorageError, AnalysisError
from ..models import Story

class HackerNewsGUI:
    """Modern, professional GUI for the HackerNews scraper."""
    
    def __init__(self):
        """Initialize the GUI with modern styling."""
        self.root = tk.Tk()
        self.root.title("HackerNews Analytics")
        self.root.geometry("1400x900")
        
        # Apply modern theme
        sv_ttk.set_theme("dark")  # Modern dark theme
        
        # Configure custom styles
        self._configure_styles()
        
        # Initialize components
        self.scraper = None
        self.storage = FileStorage()
        self.analyzer = None
        self.stories = []
        
        # Create UI elements
        self._create_widgets()
        
        # Set up event handlers
        self._setup_event_handlers()
    
    def _configure_styles(self):
        """Configure custom ttk styles for a modern look."""
        style = ttk.Style()
        
        # Configure main notebook style
        style.configure("Custom.TNotebook", padding=5)
        style.configure("Custom.TNotebook.Tab", padding=[15, 5], font=('Helvetica', 10))
        
        # Configure Treeview for stories
        style.configure("Custom.Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       font=('Helvetica', 10))
        style.configure("Custom.Treeview.Heading",
                       background="#404040",
                       foreground="white",
                       font=('Helvetica', 10, 'bold'))
        
        # Configure frames
        style.configure("Card.TFrame", background="#333333", relief="raised")
        
        # Configure labels
        style.configure("Header.TLabel", 
                       font=('Helvetica', 14, 'bold'),
                       foreground="#0099ff")
        
        # Configure buttons
        style.configure("Action.TButton",
                       font=('Helvetica', 10),
                       padding=[20, 10])
        
        # Configure entry fields
        style.configure("Custom.TEntry", 
                       font=('Helvetica', 10),
                       padding=[5, 5])
    
    def _create_widgets(self):
        """Create the GUI widgets with modern styling."""
        # Main container
        main_container = ttk.Frame(self.root, padding="10", style="Card.TFrame")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_container, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, 
                 text="HackerNews Analytics Dashboard",
                 style="Header.TLabel").grid(row=0, column=0, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container, style="Custom.TNotebook")
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        scraping_tab = ttk.Frame(self.notebook, padding="20", style="Card.TFrame")
        stories_tab = ttk.Frame(self.notebook, padding="20", style="Card.TFrame")
        analysis_tab = ttk.Frame(self.notebook, padding="20", style="Card.TFrame")
        
        self._create_scraping_tab(scraping_tab)
        self._create_stories_tab(stories_tab)
        self._create_analysis_tab(analysis_tab)
        
        self.notebook.add(scraping_tab, text="🔍 Scraping")
        self.notebook.add(stories_tab, text="📚 Stories")
        self.notebook.add(analysis_tab, text="📊 Analysis")
        
        # Status bar with modern styling
        status_frame = ttk.Frame(main_container, style="Card.TFrame")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(status_frame, 
                             textvariable=self.status_var,
                             font=('Helvetica', 9),
                             foreground="#888888")
        status_bar.grid(row=0, column=0, sticky=(tk.W), padx=10, pady=5)
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
    
    def _create_scraping_tab(self, parent):
        """Create the scraping tab with modern controls."""
        # Main container with padding
        main_container = ttk.Frame(parent, padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=1)
        
        # Control panel with modern styling
        control_panel = ttk.LabelFrame(main_container, text="Scraping Configuration", padding="20")
        control_panel.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        control_panel.columnconfigure(2, weight=1)  # Make the middle column expandable
        
        # Pages control with spinbox
        pages_frame = ttk.Frame(control_panel)
        pages_frame.grid(row=0, column=0, sticky=(tk.W), padx=(0, 20))
        
        ttk.Label(pages_frame, text="Pages to Scrape:", 
                 font=('Helvetica', 10)).grid(row=0, column=0, padx=(0, 10))
        self.pages_var = tk.StringVar(value="1")
        pages_spinbox = ttk.Spinbox(pages_frame, 
                                  from_=1, to=10,
                                  width=5,
                                  textvariable=self.pages_var)
        pages_spinbox.grid(row=0, column=1)
        
        # Async option with modern switch
        self.async_var = tk.BooleanVar(value=True)
        async_switch = ttk.Checkbutton(control_panel,
                                     text="Enable Async Scraping",
                                     variable=self.async_var,
                                     style="Switch.TCheckbutton")
        async_switch.grid(row=0, column=1, padx=20)
        
        # Action buttons
        button_frame = ttk.Frame(control_panel)
        button_frame.grid(row=0, column=2, sticky=(tk.E))
        
        self.scrape_button = ttk.Button(button_frame,
                                      text="Start Scraping",
                                      style="Action.TButton",
                                      command=self._start_scraping)
        self.scrape_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame,
                                    text="Stop",
                                    style="Action.TButton",
                                    command=self._stop_scraping,
                                    state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding="20")
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          mode='determinate',
                                          variable=self.progress_var)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status labels
        status_frame = ttk.Frame(progress_frame)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(status_frame, 
                                    text="Ready",
                                    font=('Helvetica', 10))
        self.status_label.grid(row=0, column=0, sticky=(tk.W))
        
        self.progress_label = ttk.Label(status_frame,
                                      text="0/0 stories",
                                      font=('Helvetica', 10))
        self.progress_label.grid(row=0, column=1, sticky=(tk.E))
        
        # Stats section
        stats_frame = ttk.LabelFrame(main_container, text="Current Session Stats", padding="20")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_frame.columnconfigure((0, 1), weight=1)
        
        # Create modern stat cards
        self.stat_cards = []
        stats_data = [
            ("Stories Scraped", "0"),
            ("Average Points", "0"),
            ("Average Comments", "0"),
            ("Time Elapsed", "00:00")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            card = ttk.Frame(stats_frame, style="Card.TFrame")
            card.grid(row=i//2, column=i%2, sticky=(tk.W, tk.E), padx=10, pady=5)
            
            ttk.Label(card, text=label,
                     font=('Helvetica', 10)).grid(row=0, column=0, pady=(0, 5))
            value_label = ttk.Label(card, text=value,
                                  font=('Helvetica', 16, 'bold'))
            value_label.grid(row=1, column=0)
            
            self.stat_cards.append(value_label)
        
        # Configure weights for main container
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
    
    def _create_stories_tab(self, parent):
        """Create the stories tab with a modern data table."""
        # Search and filter frame
        filter_frame = ttk.Frame(parent, style="Card.TFrame")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="🔍", font=('Helvetica', 12)).grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, 
                               textvariable=self.search_var,
                               width=40,
                               style="Custom.TEntry")
        search_entry.grid(row=0, column=1, padx=5)
        search_entry.bind('<KeyRelease>', self._filter_stories)
        
        # Stories table
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create Treeview with custom style
        columns = ('title', 'points', 'comments', 'author', 'time', 'story_id', 'url')
        self.stories_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview")
        
        # Configure columns
        self.stories_tree.heading('title', text='Title', command=lambda: self._sort_stories('title'))
        self.stories_tree.heading('points', text='Points', command=lambda: self._sort_stories('points'))
        self.stories_tree.heading('comments', text='Comments', command=lambda: self._sort_stories('comments'))
        self.stories_tree.heading('author', text='Author', command=lambda: self._sort_stories('author'))
        self.stories_tree.heading('time', text='Time', command=lambda: self._sort_stories('time'))
        
        # Hide story_id and url columns
        self.stories_tree.heading('story_id', text='ID')
        self.stories_tree.heading('url', text='URL')
        
        self.stories_tree.column('title', width=600)
        self.stories_tree.column('points', width=80)
        self.stories_tree.column('comments', width=100)
        self.stories_tree.column('author', width=120)
        self.stories_tree.column('time', width=150)
        # Hide story_id and url columns
        self.stories_tree.column('story_id', width=0, stretch=False)
        self.stories_tree.column('url', width=0, stretch=False)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.stories_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.stories_tree.xview)
        self.stories_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.stories_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Bind events
        self.stories_tree.bind('<Double-1>', self._on_story_double_click)
        self.stories_tree.bind('<Return>', self._on_story_double_click)
    
    def _create_analysis_tab(self, parent):
        """Create the analysis tab with modern visualization controls."""
        # Analysis options panel
        options_frame = ttk.LabelFrame(parent, text="Analysis Options", padding="20")
        options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Analysis type selection with modern switches
        analysis_frame = ttk.Frame(options_frame)
        analysis_frame.grid(row=0, column=0, sticky=(tk.W))
        
        self.trending_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(analysis_frame,
                        text="Trending Analysis",
                        variable=self.trending_var,
                        style="Switch.TCheckbutton").grid(row=0, column=0, padx=10)
        
        self.plot_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(analysis_frame,
                        text="Interactive Plots",
                        variable=self.plot_var,
                        style="Switch.TCheckbutton").grid(row=0, column=1, padx=10)
        
        analyze_btn = ttk.Button(analysis_frame,
                    text="Run Analysis",
                    style="Action.TButton",
                    command=self._analyze)
        analyze_btn.grid(row=0, column=2, padx=20)
        
        # Create notebook for results
        self.results_notebook = ttk.Notebook(parent, style="Custom.TNotebook")
        self.results_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Stats tab with modern cards
        self.stats_frame = ttk.Frame(self.results_notebook, padding="20", style="Card.TFrame")
        self.results_notebook.add(self.stats_frame, text="📊 Statistics")
        
        # Create modern card layout for stats
        self.stats_cards = []
        for i in range(2):  # Two rows of cards
            row_frame = ttk.Frame(self.stats_frame, style="Card.TFrame")
            row_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5)
            row_frame.columnconfigure((0,1), weight=1)
            for j in range(2):  # Two cards per row
                card = ttk.LabelFrame(row_frame, padding="15", style="Card.TFrame")
                card.grid(row=0, column=j, sticky=(tk.W, tk.E), padx=5)
                self.stats_cards.append(card)
        
        # Trending frame for topics and domains
        self.trending_frame = ttk.Frame(self.stats_frame, style="Card.TFrame")
        self.trending_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Topics and Domains side by side
        topics_frame = ttk.LabelFrame(self.trending_frame, text="Trending Topics", padding="10")
        topics_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.topics_tree = ttk.Treeview(topics_frame, columns=('topic', 'count'), 
                                      show='headings', height=10, style="Custom.Treeview")
        self.topics_tree.heading('topic', text='Topic')
        self.topics_tree.heading('count', text='Count')
        self.topics_tree.column('topic', width=150)
        self.topics_tree.column('count', width=70)
        self.topics_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        domains_frame = ttk.LabelFrame(self.trending_frame, text="Trending Domains", padding="10")
        domains_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.domains_tree = ttk.Treeview(domains_frame, columns=('domain', 'count'), 
                                       show='headings', height=10, style="Custom.Treeview")
        self.domains_tree.heading('domain', text='Domain')
        self.domains_tree.heading('count', text='Count')
        self.domains_tree.column('domain', width=200)
        self.domains_tree.column('count', width=70)
        self.domains_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Plots tab with carousel
        self.plots_frame = ttk.Frame(self.results_notebook, padding="20")
        self.results_notebook.add(self.plots_frame, text="📈 Plots")
        
        # Carousel frame
        carousel_frame = ttk.Frame(self.plots_frame)
        carousel_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        carousel_frame.columnconfigure(1, weight=1)  # Center column expands
        
        # Navigation buttons
        style = ttk.Style()
        style.configure("Carousel.TButton", font=('Helvetica', 16), padding=10)
        
        self.prev_button = ttk.Button(carousel_frame, text="◀",
                                    style="Carousel.TButton",
                                    command=self._prev_plot)
        self.prev_button.grid(row=0, column=0, padx=20, sticky=(tk.W, tk.N, tk.S))
        
        # Plot display area
        self.plot_display = ttk.Frame(carousel_frame, style="Card.TFrame")
        self.plot_display.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.next_button = ttk.Button(carousel_frame, text="▶",
                                    style="Carousel.TButton",
                                    command=self._next_plot)
        self.next_button.grid(row=0, column=2, padx=20, sticky=(tk.E, tk.N, tk.S))
        
        # Plot title
        self.plot_title = ttk.Label(self.plots_frame, 
                                  text="", 
                                  style="Header.TLabel",
                                  font=('Helvetica', 14, 'bold'))
        self.plot_title.grid(row=1, column=0, pady=(10, 0))
        
        # Dot indicators frame
        self.dots_frame = ttk.Frame(self.plots_frame)
        self.dots_frame.grid(row=2, column=0, pady=10)
        
        # Configure weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        self.stats_frame.columnconfigure(0, weight=1)
        self.plots_frame.columnconfigure(0, weight=1)
        self.plots_frame.rowconfigure(0, weight=1)
        self.trending_frame.columnconfigure((0,1), weight=1)
    
    def _filter_stories(self, event=None):
        """Filter stories based on search text."""
        search_text = self.search_var.get().lower()
        for item in self.stories_tree.get_children():
            title = self.stories_tree.item(item)['values'][0].lower()
            if search_text in title:
                self.stories_tree.reattach(item, '', 'end')
            else:
                self.stories_tree.detach(item)
    
    def _sort_stories(self, column):
        """Sort stories in the treeview by the given column."""
        # Store current sort column and order
        if not hasattr(self, '_sort_info'):
            self._sort_info = {'column': None, 'reverse': False}
        
        # Toggle sort order if clicking same column
        if self._sort_info['column'] == column:
            self._sort_info['reverse'] = not self._sort_info['reverse']
        else:
            self._sort_info['column'] = column
            self._sort_info['reverse'] = False
        
        # Get all items with their values
        items = [(self.stories_tree.set(item, column), item) for item in self.stories_tree.get_children('')]
        
        # Convert values for proper sorting
        def convert_value(value):
            try:
                # Try to convert to int for numeric columns
                if column in ('points', 'comments'):
                    return int(value)
                # Return original value for text columns
                return value.lower()
            except (ValueError, AttributeError):
                return value
        
        # Sort items
        items.sort(key=lambda x: convert_value(x[0]), reverse=self._sort_info['reverse'])
        
        # Rearrange items in sorted positions
        for index, (_, item) in enumerate(items):
            self.stories_tree.move(item, '', index)
        
        # Update column headings to show sort direction
        for col in ('title', 'points', 'comments', 'author', 'time'):
            if col == column:
                direction = ' ▼' if self._sort_info['reverse'] else ' ▲'
                self.stories_tree.heading(col, text=col.title() + direction)
            else:
                self.stories_tree.heading(col, text=col.title())
    
    def _on_story_double_click(self, event):
        """Handle double-click on a story to open it in browser."""
        selection = self.stories_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.stories_tree.item(item)['values']
        if values and len(values) >= 7:  # Make sure we have all columns
            url = values[6]  # URL is the last column
            if url:
                webbrowser.open(url)
    
    def _update_stories_table(self, stories: List[Story]):
        """Update the stories table with new data."""
        # Clear existing items
        for item in self.stories_tree.get_children():
            self.stories_tree.delete(item)
        
        # Add new stories
        for story in stories:
            time_str = story.time.strftime('%Y-%m-%d %H:%M') if story.time else 'Unknown'
            self.stories_tree.insert('', 'end', values=(
                story.title,
                story.points,
                story.comment_count,
                story.username,
                time_str,
                story.story_id,  # Hidden column
                story.url        # Hidden column
            ))
    
    def _on_scraping_complete(self, stories: List[Story]):
        """Handle scraping completion."""
        self._reset_scraping()
        self.stories = stories
        self.status_label.config(text="Ready")
        self.progress_var.set(100)  # Ensure progress bar shows complete
        
        # Update stories table
        self._update_stories_table(stories)
        
        # Switch to Stories tab
        self.notebook.select(1)
        
        # Create analyzer
        self.analyzer = StoryAnalyzer(stories)
        
        # Analyze if requested
        if self.trending_var.get() or self.plot_var.get():
            self._analyze()
    
    def _update_stats_cards(self, stats):
        """Update statistics cards with modern styling."""
        # Card 1: Total Stories
        card = self.stats_cards[0]
        for widget in card.winfo_children():
            widget.destroy()
        ttk.Label(card, text="Total Stories", 
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=0, pady=5)
        ttk.Label(card, text=str(stats['total_stories']),
                 font=('Helvetica', 24)).grid(row=1, column=0)
        
        # Card 2: Average Points
        card = self.stats_cards[1]
        for widget in card.winfo_children():
            widget.destroy()
        ttk.Label(card, text="Average Points", 
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=0, pady=5)
        ttk.Label(card, text=f"{stats['avg_points']:.1f}",
                 font=('Helvetica', 24)).grid(row=1, column=0)
        
        # Card 3: Average Comments
        card = self.stats_cards[2]
        for widget in card.winfo_children():
            widget.destroy()
        ttk.Label(card, text="Average Comments",
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=0, pady=5)
        ttk.Label(card, text=f"{stats['avg_comments']:.1f}",
                 font=('Helvetica', 24)).grid(row=1, column=0)
        
        # Card 4: Most Active Time
        card = self.stats_cards[3]
        for widget in card.winfo_children():
            widget.destroy()
        ttk.Label(card, text="Peak Activity",
                 font=('Helvetica', 12, 'bold')).grid(row=0, column=0, pady=5)
        if hasattr(self, 'analyzer') and self.analyzer:
            hour_data = self.analyzer.analyze_post_popularity_by_time()
            if hour_data:
                peak_hour = max(hour_data.items(), key=lambda x: x[1])[0]
                ttk.Label(card, text=f"{peak_hour:02d}:00",
                         font=('Helvetica', 24)).grid(row=1, column=0)
            else:
                ttk.Label(card, text="N/A",
                         font=('Helvetica', 24)).grid(row=1, column=0)

    def _update_trending_tables(self, topics, domains):
        """Update trending tables with modern styling."""
        # Clear existing items
        for item in self.topics_tree.get_children():
            self.topics_tree.delete(item)
        for item in self.domains_tree.get_children():
            self.domains_tree.delete(item)
        
        # Add topics
        for topic, count in topics:
            self.topics_tree.insert('', 'end', values=(topic, count))
        
        # Add domains
        for domain, count in domains:
            self.domains_tree.insert('', 'end', values=(domain, count))

    def _create_dot_indicators(self, num_plots):
        """Create dot indicators for plot carousel."""
        # Clear existing dots
        for widget in self.dots_frame.winfo_children():
            widget.destroy()
        
        # Create new dots
        self.dots = []
        for i in range(num_plots):
            dot = ttk.Label(self.dots_frame, text="○", font=('Helvetica', 12))
            dot.grid(row=0, column=i, padx=5)
            self.dots.append(dot)
        
        # Highlight first dot
        if self.dots:
            self.dots[0].configure(text="●")

    def _update_dot_indicators(self, current_index):
        """Update dot indicators to show current plot."""
        for i, dot in enumerate(self.dots):
            dot.configure(text="●" if i == current_index else "○")

    def _display_plots(self, plots):
        """Display Plotly plots in a carousel."""
        import plotly.io as pio
        from PIL import Image, ImageTk
        import io
        
        self.current_plot_index = 0
        self.plots_data = []
        
        # Generate all plot images
        for name, plot_func in plots:
            fig = plot_func()
            if fig:
                # Convert plot to image
                img_bytes = pio.to_image(fig, format="png", width=800, height=500)
                img = Image.open(io.BytesIO(img_bytes))
                photo = ImageTk.PhotoImage(img)
                self.plots_data.append((name, photo))
        
        # Create dot indicators
        self._create_dot_indicators(len(self.plots_data))
        
        # Show first plot
        self._show_current_plot()

    def _show_current_plot(self):
        """Show the current plot in the carousel."""
        # Clear current plot
        for widget in self.plot_display.winfo_children():
            widget.destroy()
        
        if self.plots_data:
            # Get current plot data
            name, photo = self.plots_data[self.current_plot_index]
            
            # Update plot title
            self.plot_title.configure(text=name)
            
            # Display plot
            label = ttk.Label(self.plot_display, image=photo)
            label.image = photo  # Keep a reference
            label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Update dot indicators
            self._update_dot_indicators(self.current_plot_index)
            
            # Update button states
            self.prev_button.configure(state=tk.NORMAL if self.current_plot_index > 0 else tk.DISABLED)
            self.next_button.configure(state=tk.NORMAL if self.current_plot_index < len(self.plots_data)-1 else tk.DISABLED)

    def _next_plot(self):
        """Show next plot in carousel."""
        if self.current_plot_index < len(self.plots_data) - 1:
            self.current_plot_index += 1
            self._show_current_plot()

    def _prev_plot(self):
        """Show previous plot in carousel."""
        if self.current_plot_index > 0:
            self.current_plot_index -= 1
            self._show_current_plot()

    def _analyze(self):
        """Analyze the scraped data with modern visualization."""
        try:
            if not self.analyzer:
                stories = self.storage.load_stories()
                if not stories:
                    messagebox.showerror("Error", "No stories found to analyze")
                    return
                self.analyzer = StoryAnalyzer(stories)
                self.stories = stories
                self._update_stories_table(stories)
            
            # Get basic stats and update cards
            stats = self.analyzer.get_basic_stats()
            self._update_stats_cards(stats)
            
            # Show trending if requested
            if self.trending_var.get():
                topics = self.analyzer.get_trending_topics()
                domains = self.analyzer.get_trending_domains()
                self._update_trending_tables(topics, domains)
            
            # Generate plots if requested
            if self.plot_var.get():
                plots = [
                    ('Trending Domains', self.analyzer.plot_trending_domains),
                    ('Post Distribution', self.analyzer.plot_post_distribution_by_hour),
                    ('Karma Distribution', self.analyzer.plot_karma_distribution),
                    ('Points vs Comments', self.analyzer.plot_points_vs_comments)
                ]
                self._display_plots(plots)
                
                # Switch to Plots tab
                self.results_notebook.select(1)
        
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    def _start_scraping(self):
        """Start the scraping process."""
        try:
            # Get number of pages
            try:
                num_pages = int(self.pages_var.get())
                if num_pages < 1:
                    raise ValueError("Number of pages must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number of pages")
                return
            
            # Initialize scraper
            scraper_config = ScraperConfig()
            if self.async_var.get():
                self.scraper = AsyncHackerNewsScraper(config=scraper_config)
            else:
                self.scraper = HackerNewsScraper(config=scraper_config)
            
            # Update UI
            self.scrape_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Scraping...")
            
            # Start scraping in a background thread
            thread = threading.Thread(target=self._scrape_thread, args=(num_pages,))
            thread.daemon = True
            thread.start()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scraping: {str(e)}")
            self._reset_scraping()
    
    def _stop_scraping(self):
        """Stop the scraping process."""
        if self.scraper:
            self.scraper.stop_scraping()
            self._reset_scraping()
    
    def _reset_scraping(self):
        """Reset the scraping UI state."""
        self.scrape_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready")
        self.progress_var.set(0)
        self.progress_label.config(text="0/0 stories")
        
        # Reset stat cards
        for card in self.stat_cards:
            card.config(text="0")
    
    def _scrape_thread(self, num_pages: int):
        """Thread function for scraping."""
        try:
            start_time = time.time()
            total_stories = num_pages * 30  # Approximate number of stories per page
            stories_scraped = 0
            
            def update_progress(story_count: int, current_stats: dict = None):
                stats = current_stats or {}
                stats['elapsed_time'] = time.time() - start_time
                self.root.after(0, lambda: self._update_scraping_progress(story_count, total_stories, stats))
            
            # Initialize progress
            update_progress(0)
            self.root.after(0, lambda: self.status_label.config(text="Initializing scraper..."))
            
            if isinstance(self.scraper, AsyncHackerNewsScraper):
                stories = asyncio.run(self.scraper.scrape_stories(num_pages, progress_callback=update_progress))
            else:
                stories = self.scraper.scrape_stories(num_pages, progress_callback=update_progress)
            
            # Save stories
            self.root.after(0, lambda: self.status_label.config(text="Saving stories..."))
            self.storage.save_stories(stories)
            
            # Update UI
            self.root.after(0, lambda: self._on_scraping_complete(stories))
        
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self._on_scraping_error(msg))
    
    def _on_scraping_error(self, error: str):
        """Handle scraping errors."""
        self._reset_scraping()
        messagebox.showerror("Error", f"Scraping failed: {error}")
    
    def _setup_event_handlers(self):
        """Set up event handlers for the GUI."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """Handle window closing."""
        if self.scraper:
            self.scraper.stop_scraping()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

    def _update_scraping_progress(self, current: int, total: int, stats: dict = None):
        """Update the scraping progress UI."""
        # Update progress bar
        progress = (current / total * 100) if total > 0 else 0
        self.progress_var.set(progress)
        
        # Update status labels
        self.progress_label.config(text=f"{current}/{total} stories")
        
        # Update stat cards if stats are provided
        if stats:
            self.stat_cards[0].config(text=str(current))
            self.stat_cards[1].config(text=f"{stats.get('avg_points', 0):.1f}")
            self.stat_cards[2].config(text=f"{stats.get('avg_comments', 0):.1f}")
            
            # Update elapsed time
            if 'elapsed_time' in stats:
                minutes = int(stats['elapsed_time'] // 60)
                seconds = int(stats['elapsed_time'] % 60)
                self.stat_cards[3].config(text=f"{minutes:02d}:{seconds:02d}")

def run_gui():
    """Run the HackerNews scraper GUI."""
    gui = HackerNewsGUI()
    gui.run() 