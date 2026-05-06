import re


def tokenize(text):
    """
    Convert text into a list of lowercase words.

    Punctuation is removed and searching is treated as case-insensitive.
    """
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())