from src.indexer import tokenize


def find_pages(index: dict, query_terms: list[str]) -> list[str]:
    """
    Find pages that contain all query terms.

    Results are ranked by the combined frequency of the query terms
    on each matching page.
    """
    if not query_terms:
        return []

    normalised_terms = []

    for term in query_terms:
        words = tokenize(term)
        normalised_terms.extend(words)

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

    page_scores = {}

    for page in matching_pages:
        score = 0

        for term in normalised_terms:
            score += index[term][page]["frequency"]

        page_scores[page] = score

    ranked_pages = sorted(
        page_scores,
        key=page_scores.get,
        reverse=True
    )

    return ranked_pages



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