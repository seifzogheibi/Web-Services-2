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
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def build_index(pages: dict[str, str]) -> dict[str, dict[str, dict[str, Any]]]:
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


def save_index(index: dict[str, dict[str, dict[str, Any]]], path: Path = DEFAULT_INDEX_PATH) -> None:
    """
    Save the inverted index to the file system as JSON.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(index, file, indent=2)


def load_index(path: Path = DEFAULT_INDEX_PATH) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Load the inverted index from a JSON file.
    """
    if not path.exists():
        raise FileNotFoundError(f"Index file not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
    
    