from pathlib import Path

from src.benchmark import get_index_statistics, benchmark_search, main

# this test checks that the benchmark function correctly calculates statistics about the index, 
# including the number of unique words, pages indexed, total word occurrences, and index file size, based on a known test index and a temporary index file
def test_get_index_statistics_counts_words_pages_and_occurrences(tmp_path):
    # create a test index with known values to verify the statistics calculations
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]},
            "page2": {"frequency": 1, "positions": [5]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]}
        }
    }
    # create a temporary index file to test file size reporting
    index_path = tmp_path / "index.json"
    index_path.write_text("test index content", encoding="utf-8")

    # calculate statistics using the benchmark function
    statistics = get_index_statistics(index, index_path)

    # check that the statistics match the expected values based on the test index
    assert statistics["unique_words"] == 2
    assert statistics["pages"] == 2
    assert statistics["total_word_occurrences"] == 4
    assert statistics["index_file_size_bytes"] > 0

# test that the benchmark function returns a float average time and does not raise errors when running the search benchmark
def test_get_index_statistics_returns_zero_file_size_when_file_missing(tmp_path):
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]}
        }
    }
    # create a temporary index file to test file size reporting, but do not write anything to it to simulate a missing file
    missing_path = tmp_path / "missing_index.json"

    statistics = get_index_statistics(index, missing_path)

    assert statistics["unique_words"] == 1
    assert statistics["pages"] == 1
    assert statistics["total_word_occurrences"] == 2
    assert statistics["index_file_size_bytes"] == 0

# test that the benchmark function returns a float average time and does not raise errors when running the search benchmark
def test_benchmark_search_returns_float_average_time():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    # run the benchmark with a simple query and check that it returns a float average time without errors
    average_time = benchmark_search(index, ["good"], runs=5)

    # we use a small number of runs here to keep the test fast, but the function should still return a valid average time
    assert isinstance(average_time, float)
    assert average_time >= 0

# test that the main function runs without errors and prints the expected statistics and benchmark results based on a mocked index and benchmark function
def test_benchmark_main_prints_statistics(monkeypatch, capsys):
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]}
        }
    }

    # mock the load_index function to return our test index and the benchmark_search function to return a fixed average time, 
    # so we can verify the output without relying on actual file I/O or timing
    monkeypatch.setattr("src.benchmark.load_index", lambda: index)
    monkeypatch.setattr("src.benchmark.benchmark_search", lambda index, query_terms: 0.00012345)

    main()

    output = capsys.readouterr().out

    assert "Index statistics" in output
    assert "Pages indexed: 1" in output
    assert "Unique words: 2" in output
    assert "Total word occurrences: 3" in output
    assert "Search benchmark" in output
    assert "Average search time over 1000 runs: 0.00012345 seconds" in output
