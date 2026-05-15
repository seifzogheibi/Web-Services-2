from pathlib import Path

import pytest

from src.indexer import build_index, load_index, save_index, tokenize

# unit tests for the tokenizer function to verify that it correctly tokenizes text
# this test checks that the tokenizer converts all text to lowercase and splits it into words, so that searching is case-insensitive and punctuation is removed
def test_tokenize_converts_text_to_lowercase_words():
    result = tokenize("Good FRIENDS good")

    assert result == ["good", "friends", "good"]

# this test checks that the tokenizer removes punctuation from the text and only returns clean words, 
# so that search queries will match regardless of punctuation in the original text
def test_tokenize_removes_punctuation():
    result = tokenize("Hello, world! This is a test.")

    assert result == ["hello", "world", "this", "is", "a", "test"]

# checks that the build_index function correctly counts the frequency of each word on a page
def test_build_index_stores_frequency():
    pages = {
        "page1": "good friends good"
    }

    index = build_index(pages)

    assert index["good"]["page1"]["frequency"] == 2

# checks that the build_index function correctly stores the positions of each word on the page
def test_build_index_stores_positions():
    pages = {
        "page1": "good friends good"
    }

    index = build_index(pages)

    assert index["good"]["page1"]["positions"] == [0, 2]

# checks that the build_index function correctly handles multiple pages and counts frequencies and positions for each word on each page
def test_build_index_handles_multiple_pages():
    pages = {
        "page1": "good friends",
        "page2": "good books"
    }

    # build the index from the test pages and check that the words are indexed correctly with their frequencies and positions for each page
    index = build_index(pages)

    # check that the words "good", "friends", and "books" are in the index and that their frequencies and positions are correct for each page
    assert "page1" in index["good"]
    assert "page2" in index["good"]
    assert index["friends"]["page1"]["frequency"] == 1
    assert index["books"]["page2"]["frequency"] == 1


# check that the save_index function correctly saves the index to a JSON file and that the load_index function can read it back without errors
def test_save_and_load_index(tmp_path):
    pages = {
        "page1": "good friends good"
    }

    index = build_index(pages)
    test_path = tmp_path / "index.json"

    save_index(index, test_path)
    loaded_index = load_index(test_path)

    assert loaded_index == index

# checks that the load_index function raises a FileNotFoundError when trying to load an index from a path that does not exist,
def test_load_index_raises_error_for_missing_file(tmp_path):
    missing_path = tmp_path / "missing_index.json"

    with pytest.raises(FileNotFoundError):
        load_index(missing_path)
