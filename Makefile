.PHONY: clean test run scrape analyze gui help

PYTHON = python  # change this to python3.11 if you are using a different version or venv/bin/python if you are using a virtual environment

help:
	@echo "Available targets:"
	@echo "  clean     - Clean up generated files"
	@echo "  test      - Run unit tests"
	@echo "  run       - Run the scraper (default: 1 page)"
	@echo "  scrape    - Run the scraper with custom pages (e.g., make scrape PAGES=3)"
	@echo "  analyze   - Analyze scraped data"
	@echo "  gui       - Launch the GUI"
	@echo "  help      - Show this help message"

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf data/*.csv
	rm -rf data/*.json
	rm -rf plots/*
	@echo "Cleanup complete!"

test:
	@echo "Running tests..."
	$(PYTHON) -m unittest discover -s hackernews_scraper/tests

run:
	$(PYTHON) run.py --scrape --pages 1

scrape:
	$(PYTHON) run.py --scrape --pages $(PAGES)

analyze:
	$(PYTHON) run.py --analyze data/hn_stories --trending --plot

gui:
	$(PYTHON) run.py --gui 