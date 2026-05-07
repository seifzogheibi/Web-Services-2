import time
from pathlib import Path

from src.indexer import DEFAULT_INDEX_PATH, load_index
from src.search import find_pages


def get_index_statistics(index: dict, index_path: Path = DEFAULT_INDEX_PATH) -> dict:
    """
    Calculate useful statistics about the generated index.
    """
    unique_words = len(index)
    pages = set()
    total_word_occurrences = 0

    for word_entries in index.values():
        for page, stats in word_entries.items():
            pages.add(page)
            total_word_occurrences += stats["frequency"]

    index_file_size = 0

    if index_path.exists():
        index_file_size = index_path.stat().st_size

    return {
        "unique_words": unique_words,
        "pages": len(pages),
        "total_word_occurrences": total_word_occurrences,
        "index_file_size_bytes": index_file_size
    }


def benchmark_search(index: dict, query_terms: list[str], runs: int = 1000) -> float:
    """
    Measure the average search time for a query over several runs.
    """
    start_time = time.perf_counter()

    for _ in range(runs):
        find_pages(index, query_terms)

    end_time = time.perf_counter()
    average_time = (end_time - start_time) / runs

    return average_time


def main():
    index = load_index()
    statistics = get_index_statistics(index)
    average_search_time = benchmark_search(index, ["good", "friends"])

    print("Index statistics")
    print("----------------")
    print(f"Pages indexed: {statistics['pages']}")
    print(f"Unique words: {statistics['unique_words']}")
    print(f"Total word occurrences: {statistics['total_word_occurrences']}")
    print(f"Index file size: {statistics['index_file_size_bytes']} bytes")
    print()
    print("Search benchmark")
    print("----------------")
    print(f"Query: good friends")
    print(f"Average search time over 1000 runs: {average_search_time:.8f} seconds")


if __name__ == "__main__":
    main()
