# COMP3011 Search Engine Tool

A Python command-line search engine for crawling [quotes.toscrape.com](https://quotes.toscrape.com/), building an inverted index, and searching for pages containing single or multi-word queries.

## Overview

This project was developed for COMP3011 Web Services and Web Data Coursework 2.

The tool crawls the target website, extracts searchable text from each page, builds an inverted index, stores the index in the file system, and allows users to search the index through a command-line interface.

## Features

- Crawls all pages from quotes.toscrape.com
- Respects a 6-second politeness delay between requests
- Extracts quote text, author names, and tags
- Builds a case-insensitive inverted index
- Stores word frequency and word positions
- Saves and loads the index from JSON
- Supports single-word and multi-word search queries
- Handles missing words, empty queries, and unloaded indexes
- Includes a pytest test suite

## Installation

Clone the repository:

```bash
git clone https://github.com/seifzogheibi/Web-Services-2.git
cd Web-Services-2
pip install -r requirements.txt
python3 -m venv venv
source venv/bin/activate
```

## Testing

The project uses `pytest` for unit testing.

To run all tests:
```bash
pytest
```

To run a specific test file:
```bash
pytest tests/test_indexer.py
```

To run a specific test function:
```bash
pytest tests/test_indexer.py::test_tokenize
```

To run tests with coverage:
```bash
pytest --cov=src tests/
```
