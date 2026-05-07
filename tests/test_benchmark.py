from pathlib import Path

from src.benchmark import get_index_statistics, benchmark_search, main


def test_get_index_statistics_counts_words_pages_and_occurrences(tmp_path):
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]},
            "page2": {"frequency": 1, "positions": [5]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]}
        }
    }

    index_path = tmp_path / "index.json"
    index_path.write_text("test index content", encoding="utf-8")

    statistics = get_index_statistics(index, index_path)

    assert statistics["unique_words"] == 2
    assert statistics["pages"] == 2
    assert statistics["total_word_occurrences"] == 4
    assert statistics["index_file_size_bytes"] > 0


def test_get_index_statistics_returns_zero_file_size_when_file_missing(tmp_path):
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]}
        }
    }

    missing_path = tmp_path / "missing_index.json"

    statistics = get_index_statistics(index, missing_path)

    assert statistics["unique_words"] == 1
    assert statistics["pages"] == 1
    assert statistics["total_word_occurrences"] == 2
    assert statistics["index_file_size_bytes"] == 0


def test_benchmark_search_returns_float_average_time():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    average_time = benchmark_search(index, ["good"], runs=5)

    assert isinstance(average_time, float)
    assert average_time >= 0


def test_benchmark_main_prints_statistics(monkeypatch, capsys):
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]}
        }
    }

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
    