from src.search import find_pages, get_index_entry, find_phrase_pages


def test_find_pages_returns_pages_for_single_word():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 1, "positions": [2]}
        }
    }

    result = find_pages(index, ["good"])

    assert set(result) == {"page1", "page2"}


def test_find_pages_returns_intersection_for_multiple_words():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 1, "positions": [0]}
        },
        "friends": {
            "page2": {"frequency": 1, "positions": [1]}
        }
    }

    result = find_pages(index, ["good", "friends"])

    assert result == ["page2"]


def test_find_pages_returns_empty_list_for_missing_word():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, ["missing"])

    assert result == []


def test_find_pages_returns_empty_list_for_empty_query():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, [])

    assert result == []


def test_find_pages_is_case_insensitive():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, ["GOOD"])

    assert result == ["page1"]


def test_find_pages_handles_punctuation_in_query():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, ["good!"])

    assert result == ["page1"]


def test_get_index_entry_returns_entry_for_word():
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]}
        }
    }

    result = get_index_entry(index, "good")

    assert result == {
        "page1": {"frequency": 2, "positions": [0, 3]}
    }


def test_get_index_entry_is_case_insensitive():
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]}
        }
    }

    result = get_index_entry(index, "GOOD")

    assert result == {
        "page1": {"frequency": 2, "positions": [0, 3]}
    }


def test_get_index_entry_returns_none_for_missing_word():
    index = {}

    result = get_index_entry(index, "missing")

    assert result is None


def test_get_index_entry_returns_none_for_invalid_word():
    index = {}

    result = get_index_entry(index, "!!!")

    assert result is None

def test_find_pages_ranks_results_by_tfidf_score():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 3, "positions": [0, 2, 4]}
        }
    }

    result = find_pages(index, ["good"])

    assert result == ["page2", "page1"]

def test_find_phrase_pages_returns_page_for_exact_phrase():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 1, "positions": [3]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]},
            "page2": {"frequency": 1, "positions": [1]}
        }
    }

    result = find_phrase_pages(index, "good friends")

    assert result == ["page1"]


def test_find_phrase_pages_returns_empty_list_when_words_are_not_consecutive():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [3]}
        }
    }

    result = find_phrase_pages(index, "good friends")

    assert result == []


def test_find_phrase_pages_returns_empty_list_for_missing_phrase_word():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_phrase_pages(index, "good friends")

    assert result == []