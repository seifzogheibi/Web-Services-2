from src.search import find_pages, get_index_entry, find_phrase_pages


def test_find_pages_returns_pages_for_single_word():
    # a single word search should return every page that contains that word
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 1, "positions": [2]}
        }
    }

    result = find_pages(index, ["good"])

    assert set(result) == {"page1", "page2"}


def test_find_pages_returns_intersection_for_multiple_words():
    # multi-word search should only return pages containing all query terms
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
    # if one query term is missing, there should be no matching pages
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, ["missing"])

    assert result == []


def test_find_pages_returns_empty_list_for_empty_query():
    # empty queries should be handled safely
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, [])

    assert result == []


def test_find_pages_is_case_insensitive():
    # uppercase query terms should match lowercase indexed words
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, ["GOOD"])

    assert result == ["page1"]


def test_find_pages_handles_punctuation_in_query():
    # punctuation in the query should be cleaned before searching
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_pages(index, ["good!"])

    assert result == ["page1"]


def test_get_index_entry_returns_entry_for_word():
    # print-style lookup should return the stored entry for an indexed word
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
    # index entry lookup should normalise the requested word
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
    # missing words should return none instead of raising an error
    index = {}

    result = get_index_entry(index, "missing")

    assert result is None


def test_get_index_entry_returns_none_for_invalid_word():
    # invalid input should be cleaned and handled safely
    index = {}

    result = get_index_entry(index, "!!!")

    assert result is None


def test_find_pages_ranks_results_by_tfidf_score():
    # pages with higher query-term frequency should rank higher
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 3, "positions": [0, 2, 4]}
        }
    }

    result = find_pages(index, ["good"])

    assert result == ["page2", "page1"]


def test_find_phrase_pages_returns_page_for_exact_phrase():
    # phrase search should only match consecutive word positions
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
    # words on the same page should not match if their positions are not consecutive
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
    # phrase search should fail safely when part of the phrase is missing
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    result = find_phrase_pages(index, "good friends")

    assert result == []