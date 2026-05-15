import time
from pathlib import Path

from src.indexer import DEFAULT_INDEX_PATH, load_index
from src.search import find_pages


def get_index_statistics(index: dict, index_path: Path = DEFAULT_INDEX_PATH) -> dict:
    """
    Calculate useful statistics about the generated index.
    """
    # count how many unique words are stored in the index
    unique_words = len(index)

    # use a set so each indexed page is only counted once
    pages = set()

    # count all word occurrences across all indexed pages
    total_word_occurrences = 0

    for word_entries in index.values():
        for page, stats in word_entries.items():
            pages.add(page)
            total_word_occurrences += stats["frequency"]

    # default to zero if the index file does not exist yet
    index_file_size = 0

    # record the saved index file size when the file is available
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
    # start the timer before running the repeated searches
    start_time = time.perf_counter()

    # repeat the same query to get a more stable average time
    for _ in range(runs):
        find_pages(index, query_terms)

    # stop the timer after all runs have completed
    end_time = time.perf_counter()

    # divide the total time by the number of runs to get the average
    average_time = (end_time - start_time) / runs

    return average_time


def main():
    # load the saved index created by the build command
    index = load_index()

    # calculate summary information about the generated index
    statistics = get_index_statistics(index)

    # benchmark a sample multi-word query
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