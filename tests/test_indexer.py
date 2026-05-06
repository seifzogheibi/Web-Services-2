from pathlib import Path

import pytest

from src.indexer import build_index, load_index, save_index, tokenize


def test_tokenize_converts_text_to_lowercase_words():
    result = tokenize("Good FRIENDS good")

    assert result == ["good", "friends", "good"]


def test_tokenize_removes_punctuation():
    result = tokenize("Hello, world! This is a test.")

    assert result == ["hello", "world", "this", "is", "a", "test"]


def test_build_index_stores_frequency():
    pages = {
        "page1": "good friends good"
    }

    index = build_index(pages)

    assert index["good"]["page1"]["frequency"] == 2


def test_build_index_stores_positions():
    pages = {
        "page1": "good friends good"
    }

    index = build_index(pages)

    assert index["good"]["page1"]["positions"] == [0, 2]


def test_build_index_handles_multiple_pages():
    pages = {
        "page1": "good friends",
        "page2": "good books"
    }

    index = build_index(pages)

    assert "page1" in index["good"]
    assert "page2" in index["good"]
    assert index["friends"]["page1"]["frequency"] == 1
    assert index["books"]["page2"]["frequency"] == 1


def test_save_and_load_index(tmp_path):
    pages = {
        "page1": "good friends good"
    }

    index = build_index(pages)
    test_path = tmp_path / "index.json"

    save_index(index, test_path)
    loaded_index = load_index(test_path)

    assert loaded_index == index


def test_load_index_raises_error_for_missing_file(tmp_path):
    missing_path = tmp_path / "missing_index.json"

    with pytest.raises(FileNotFoundError):
        load_index(missing_path)
