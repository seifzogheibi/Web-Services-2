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


## Installation and Setup

Clone the repository:

```bash
git clone https://github.com/seifzogheibi/Web-Services-2.git
cd Web-Services-2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Usage

Start the command-line tool:

```bash
python src/main.py
```

The tool supports the following commands:

### Build the index

```text
build
```

This crawls the target website, builds the inverted index, and saves it to `data/index.json`.

### Load the saved index

```text
load
```

This loads the previously saved index from the file system.

### Print an index entry

```text
print love
```

This prints the inverted index entry for the word `love`, including the pages where it appears, its frequency, and its positions.

### Find pages containing a word

```text
find love
```

This returns all pages containing the word `love`.

### Find pages containing multiple words

```text
find good friends
```

This returns pages containing both `good` and `friends`.

### Exit the tool

```text
exit
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

To run tests with coverage:
```bash
pytest --cov=src tests/
```

# Documentation
## Design Decisions

### Crawler

The crawler starts from the homepage of `quotes.toscrape.com` and follows the website's next-page links until no further page exists. A politeness delay of 6 seconds is used between requests to meet the coursework requirement.

### Text Extraction

The crawler extracts quote text, author names, and tags from each page. These fields were selected because they represent the main searchable content on the target website.

### Inverted Index

The inverted index uses a nested dictionary structure:

```python
{
    "word": {
        "page_url": {
            "frequency": 2,
            "positions": [0, 5]
        }
    }
}
```

This structure allows fast lookup from a word to all pages where it appears. Each page entry stores the word frequency and word positions, which provides useful statistics for search and inspection.

### Search Logic

Search is case-insensitive. Multi-word queries use AND logic, meaning that `find good friends` returns only pages that contain both `good` and `friends`.

Search results are ranked by the combined frequency of the query terms on each page.

### Storage

The index is saved as a JSON file in `data/index.json`. JSON was chosen because it is readable, easy to debug, and simple to load back into Python.


## Dependencies

The main dependencies are:

- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- `pytest` for testing
- `pytest-cov` for test coverage

They can be installed using:
```bash

pip install -r requirements.txt
```


 ## Performance and Complexity

The project uses an inverted index so that search does not need to scan every page at query time.

For a single-word query, lookup is approximately `O(1)` on average because Python dictionaries are used to access the word entry directly.

For a multi-word query, the main cost is set intersection across the pages containing each query term. This is more efficient than scanning every indexed document for every search.

The project also includes a small benchmark script:

```bash
python src/benchmark.py
```

## Testing Strategy

The project includes unit tests for the main components:

- `test_indexer.py` checks tokenisation, frequency counting, word positions, multiple pages, and JSON storage.
- `test_search.py` checks single-word search, multi-word search, case-insensitive queries, punctuation handling, missing words, empty queries, and result ranking.
- `test_crawler.py` checks quote text extraction, author extraction, tag extraction, and next-page detection.
- `test_main.py` checks basic command handling and ensures invalid or incomplete commands do not crash the program.


## GenAI Use

Generative AI was used as a support tool during development. It helped with planning the project structure, explaining inverted index design, suggesting examples of pytest tests, and identifying edge cases to consider.

However, AI-generated suggestions were not accepted without review. For example, one important design decision was whether multi-word search should use OR logic or AND logic. The coursework example states that `find good friends` should return pages containing the words `good` and `friends`, so the implementation uses set intersection to return pages containing all query terms.

AI support was useful for breaking the problem into smaller components, but the final implementation still required manual testing, debugging, and understanding of each function. This was important because the coursework requires that all submitted code can be explained and justified.