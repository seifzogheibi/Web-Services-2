# COMP3011 Search Engine Tool

A Python command-line search engine for crawling quotes.toscrape.com, building an inverted index, and searching for pages containing specific words or multi-word queries.

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
