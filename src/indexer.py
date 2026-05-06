import re


def tokenize(text):
    """
    Convert text into a list of lowercase words.

    Punctuation is removed and searching is treated as case-insensitive.
    """
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def build_index(pages):
    """
    Build an inverted index from a dictionary of page URLs to page text.

    The index maps each word to the pages it appears in, storing frequency
    and word positions for each page.
    """
    index = {}

    for url, text in pages.items():
        words = tokenize(text)

        for position, word in enumerate(words):
            if word not in index:
                index[word] = {}

            if url not in index[word]:
                index[word][url] = {
                    "frequency": 0,
                    "positions": []
                }

            index[word][url]["frequency"] += 1
            index[word][url]["positions"].append(position)

    return index