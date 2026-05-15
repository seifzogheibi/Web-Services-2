import re
import json
from pathlib import Path
from typing import Any


DEFAULT_INDEX_PATH = Path("data/index.json")


def tokenize(text: str) -> list[str]:
    """
    Convert text into a list of lowercase words.

    Punctuation is removed and searching is treated as case-insensitive.
    """
    # split the text into words and normalise everything to lowercase
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def build_index(pages: dict[str, str]) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Build an inverted index from a dictionary of page URLs to page text.

    The index maps each word to the pages it appears in, storing frequency
    and word positions for each page.
    """
    # this dictionary will store each word and the pages where it appears
    index = {}

    # go through each crawled page one at a time
    for url, text in pages.items():
        # turn the page text into clean, searchable words (tokenization)
        words = tokenize(text)

        # keep track of each word's position within the page
        for position, word in enumerate(words):
            # add the word to the index the first time we see it
            if word not in index:
                index[word] = {}

            # add the current page under this word if needed
            if url not in index[word]:
                index[word][url] = {
                    "frequency": 0,
                    "positions": []
                }

            # update how often the word appears on this page
            index[word][url]["frequency"] += 1

            # store where the word appeared in the page text
            index[word][url]["positions"].append(position)

    return index


def save_index(index: dict[str, dict[str, dict[str, Any]]], path: Path = DEFAULT_INDEX_PATH) -> None:
    """
    Save the inverted index to the file system as JSON.
    """
    # make sure the data folder exists before saving the file
    path.parent.mkdir(parents=True, exist_ok=True)

    # write the index in a readable json format
    with open(path, "w", encoding="utf-8") as file:
        json.dump(index, file, indent=2)


def load_index(path: Path = DEFAULT_INDEX_PATH) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Load the inverted index from a JSON file.
    """
    # stop early if the index has not been created yet
    if not path.exists():
        raise FileNotFoundError(f"Index file not found: {path}")

    # read the saved json index back into memory
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)