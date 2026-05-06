from src.indexer import tokenize


def find_pages(index, query_terms):
    """
    Find pages that contain all query terms.

    This uses AND search logic. For example, searching for
    "good friends" returns only pages containing both words.
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

    return sorted(matching_pages)