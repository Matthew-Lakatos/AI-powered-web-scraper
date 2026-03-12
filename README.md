Async Magic

The project asynchronously scrapes web pages, extracts readable text, runs sentiment analysis using a transformer model, and stores results in SQLite.

## Features

- HTTP scraping with `aiohttp` and connection reuse
- Optional JS rendering via headless Chrome (Selenium)
- Readability-based content extraction to be clean
- Transformer-based sentiment analysis (multi-class)
- SQLite storage with indexing and batch inserts
- logging and error handling
- URL de-duplication and concurrency limiting

## Usage

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   export CHROMEDRIVER_PATH=/path/to/chromedriver
   python main.py
   ```
