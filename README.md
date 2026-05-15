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
- Supports exact phrase search using word positions
- Ranks search results using TF-IDF
- Prints query explanations before displaying search results
- Handles missing words, empty queries, and unloaded indexes
- Includes a pytest test suite


## Installation and Setup

Clone the repository:

```bash
git clone https://github.com/seifzogheibi/Web-Services-2.git
cd Web-Services-2
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```


## Usage

Start the command-line tool:

```bash
python3 -m src.main
```

The tool supports the following commands:
```text
build:                      This crawls the target website, builds the inverted index, and saves it to `data/index.json`.
load:                       This loads the previously saved index from the file system.
print <word>:               This prints the inverted index entry for '<word>', including the pages where it appears, its frequency, and its positions.
find <word1> [<word2> ...]: This finds all pages containing the specified words.
find "<exact phrase>":      This finds all pages containing the exact phrase.
exit:                       This exits the tool.
```


## Testing

The project uses `pytest` for unit testing. The test suite includes unit tests for the benchmark utility and uses monkeypatching to test build/load command behaviour without performing live crawls during testing.

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


## Documentation

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

Search results are ranked using a simple TF-IDF score, so pages with more relevant query-term matches are returned first.

The tool also supports exact phrase search using quoted queries such as `find "good friends"`. This uses the word positions stored in the inverted index to check whether the terms appear consecutively.

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


### Query Explanation

The `find` command prints a short explanation before displaying results. This shows whether the query is being processed as a standard multi-word AND search or as an exact phrase search.

Examples:

```text
find good friends
```

uses multi-word AND search with TF-IDF ranking.

```text
find "good friends"
```

uses exact phrase search with TF-IDF ranking.


## Performance and Complexity

The project uses an inverted index so that search does not need to scan every page at query time.

For a single-word query, lookup is approximately `O(1)` on average because Python dictionaries are used to access the word entry directly.

For a multi-word query, the main cost is set intersection across the pages containing each query term. This is more efficient than scanning every indexed document for every search.

The project also includes a small benchmark script:

```bash
python src/benchmark.py
```

This reports:

- Number of indexed pages
- Number of unique words
- Total word occurrences
- Index file size
- Average search time for a sample query


## Testing Strategy

The project includes unit tests for the main components:

- `test_indexer.py` checks tokenisation, frequency counting, word positions, multiple pages, and JSON storage.
- `test_search.py` checks single-word search, multi-word search, case-insensitive queries, punctuation handling, missing words, empty queries, TF-IDF ranking, and exact phrase search.
- `test_crawler.py` checks quote text extraction, author extraction, tag extraction, next-page detection, request handling, crawler error handling, and mocked crawling behaviour.
- `test_main.py` checks basic command handling and ensures invalid or incomplete commands do not crash the program.
- `test_benchmark.py` checks that the benchmark script runs without errors and reports expected metrics.

- `.coveragerc` is included to focus coverage reporting on the `src` directory and show missing lines.
- `.github/workflows/tests.yml` is included to run tests and report coverage on every push to GitHub.


## Novelty and Search Engine Context

This project is intentionally smaller than full search frameworks such as Scrapy or Whoosh, but it applies several ideas from real search engine design in a transparent coursework implementation.

Scrapy supports scalable crawling features such as download delays, concurrency control, and AutoThrottle for crawl politeness. In this project, I implemented a simpler Requests-based crawler with an explicit 6-second politeness delay so the crawling behaviour is easy to inspect and explain.

Whoosh is a more mature Python search library that supports ranking models such as BM25F. My implementation does not attempt to replicate a full search library, but it adds TF-IDF ranking to move beyond basic keyword matching and return results in a relevance-based order.

The main novelty of this implementation is the combination of:

- A polite crawler using Requests and BeautifulSoup
- A positional inverted index storing frequency and word positions
- Multi-word AND search
- TF-IDF ranked retrieval
- Exact phrase search using positional postings
- Query explanation output showing how the query is processed
- Basic benchmarking for index statistics and search time

This makes the tool more advanced than a simple word-to-page lookup while keeping the full search pipeline visible and explainable.


## GenAI Use

Generative AI was used as a support tool during development. It helped with planning the project structure, explaining inverted index design, suggesting examples of pytest tests, and identifying edge cases to consider.

However, AI-generated suggestions were not accepted without review. For example, one important design decision was whether multi-word search should use OR logic or AND logic. The coursework example states that `find good friends` should return pages containing the words `good` and `friends`, so the implementation uses set intersection to return pages containing all query terms.

AI support was useful for breaking the problem into smaller components, but the final implementation still required manual testing, debugging, and understanding of each function. This was important because the coursework requires that all submitted code can be explained and justified.