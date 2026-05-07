import math

from src.indexer import tokenize


def _normalise_query_terms(query_terms: list[str]) -> list[str]:
    """
    Convert query input into lowercase searchable terms.
    """
    normalised_terms = []

    for term in query_terms:
        words = tokenize(term)
        normalised_terms.extend(words)

    return normalised_terms


def _get_total_document_count(index: dict) -> int:
    """
    Count the number of unique pages in the index.
    """
    pages = set()

    for word_entries in index.values():
        pages.update(word_entries.keys())

    return len(pages)


def _calculate_tfidf_score(index: dict, page: str, terms: list[str], total_documents: int) -> float:
    """
    Calculate a simple TF-IDF score for a page and query terms.
    """
    score = 0.0

    for term in terms:
        term_frequency = index[term][page]["frequency"]
        document_frequency = len(index[term])

        inverse_document_frequency = math.log((total_documents + 1) / (document_frequency + 1)) + 1
        score += term_frequency * inverse_document_frequency

    return score


def _rank_pages_by_tfidf(index: dict, pages: set[str], terms: list[str]) -> list[str]:
    """
    Rank matching pages using TF-IDF.
    """
    total_documents = _get_total_document_count(index)
    page_scores = {}

    for page in pages:
        page_scores[page] = _calculate_tfidf_score(index, page, terms, total_documents)

    ranked_pages = sorted(
        page_scores,
        key=lambda page: (-page_scores[page], page)
    )

    return ranked_pages


def _page_contains_phrase(index: dict, page: str, phrase_terms: list[str]) -> bool:
    """
    Check whether a page contains the query terms consecutively.

    This uses the word positions stored in the inverted index.
    """
    if not phrase_terms:
        return False

    first_term = phrase_terms[0]

    if first_term not in index:
        return False

    if page not in index[first_term]:
        return False

    starting_positions = index[first_term][page]["positions"]

    for start_position in starting_positions:
        phrase_found = True

        for offset, term in enumerate(phrase_terms[1:], start=1):
            if term not in index:
                phrase_found = False
                break

            if page not in index[term]:
                phrase_found = False
                break

            expected_position = start_position + offset

            if expected_position not in index[term][page]["positions"]:
                phrase_found = False
                break

        if phrase_found:
            return True

    return False


def find_pages(index: dict, query_terms: list[str]) -> list[str]:
    """
    Find pages that contain all query terms.

    Results are ranked using a simple TF-IDF score so that pages with
    more relevant term matches appear first.
    """
    if not query_terms:
        return []

    normalised_terms = _normalise_query_terms(query_terms)

    if not normalised_terms:
        return []

    matching_pages = None

    for term in normalised_terms:
        if term not in index:
            return []

        pages_for_term = set(index[term].keys())

        if matching_pages is None:
            matching_pages = pages_for_term
        else:
            matching_pages = matching_pages.intersection(pages_for_term)

    if matching_pages is None:
        return []

    return _rank_pages_by_tfidf(index, matching_pages, normalised_terms)


def find_phrase_pages(index: dict, phrase: str) -> list[str]:
    """
    Find pages that contain an exact phrase.

    Phrase search uses the word positions stored in the index.
    """
    phrase_terms = tokenize(phrase)

    if not phrase_terms:
        return []

    first_term = phrase_terms[0]

    if first_term not in index:
        return []

    candidate_pages = set(index[first_term].keys())
    matching_pages = set()

    for page in candidate_pages:
        if _page_contains_phrase(index, page, phrase_terms):
            matching_pages.add(page)

    return _rank_pages_by_tfidf(index, matching_pages, phrase_terms)


def get_index_entry(index: dict, word: str):
    """
    Return the index entry for a single word.

    The word is normalised so that search is case-insensitive.
    """
    words = tokenize(word)

    if not words:
        return None

    normalised_word = words[0]

    if normalised_word not in index:
        return None

    return index[normalised_word]