from src.main import handle_command, print_query_explanation, print_index_entry, show_help


def test_empty_command_does_nothing():
    # empty input should be ignored without changing the current index
    current_index, result = handle_command("", None)

    assert current_index is None
    assert result is None


def test_exit_command_returns_exit_signal():
    # exit should return a signal so the main loop can stop cleanly
    current_index, result = handle_command("exit", None)

    assert current_index is None
    assert result == "exit"


def test_print_command_without_loaded_index_does_not_crash():
    # print should not crash if the user has not loaded or built an index yet
    current_index, result = handle_command("print good", None)

    assert current_index is None
    assert result is None


def test_find_command_without_loaded_index_does_not_crash():
    # find should not crash if there is no active index
    current_index, result = handle_command("find good", None)

    assert current_index is None
    assert result is None


def test_unknown_command_does_not_crash():
    # unsupported commands should be handled safely
    current_index, result = handle_command("unknown", None)

    assert current_index is None
    assert result is None


def test_find_command_with_loaded_index_keeps_index():
    # running a search should not modify the loaded index
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    current_index, result = handle_command("find good", index)

    assert current_index == index
    assert result is None


def test_print_command_with_loaded_index_keeps_index():
    # printing an index entry should not modify the loaded index
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    current_index, result = handle_command("print good", index)

    assert current_index == index
    assert result is None


def test_print_query_explanation_for_standard_search(capsys):
    # standard queries should be explained as multi-word and search
    print_query_explanation("good friends", False)

    output = capsys.readouterr().out

    assert "Query explanation:" in output
    assert "Mode: multi-word AND search" in output
    assert "Ranking: TF-IDF" in output
    assert "Terms: good friends" in output


def test_print_query_explanation_for_phrase_search(capsys):
    # quoted queries should be explained as exact phrase searches
    print_query_explanation('"good friends"', True)

    output = capsys.readouterr().out

    assert "Query explanation:" in output
    assert "Mode: exact phrase search" in output
    assert "Ranking: TF-IDF" in output
    assert "Phrase: good friends" in output


def test_show_help_prints_available_commands(capsys):
    # help should show all commands required by the coursework brief
    show_help()

    output = capsys.readouterr().out

    assert "Available commands:" in output
    assert "build" in output
    assert "load" in output
    assert "print <word>" in output
    assert "find <query>" in output
    assert "exit" in output


def test_print_index_entry_prints_word_statistics(capsys):
    # print should show the page, frequency, and stored word positions
    entry = {
        "page1": {
            "frequency": 2,
            "positions": [0, 3]
        }
    }

    print_index_entry(entry)

    output = capsys.readouterr().out

    assert "- page1" in output
    assert "frequency: 2" in output
    assert "positions: [0, 3]" in output


def test_print_index_entry_handles_missing_entry(capsys):
    # missing words should produce a clear message instead of an error
    print_index_entry(None)

    output = capsys.readouterr().out

    assert "Word not found in index." in output


def test_handle_command_help_prints_help(capsys):
    # the help command should call the help output from the cli
    current_index, result = handle_command("help", None)

    output = capsys.readouterr().out

    assert current_index is None
    assert result is None
    assert "Available commands:" in output


def test_handle_command_print_without_word(capsys):
    # print without a word should ask the user to provide one
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    current_index, result = handle_command("print", index)

    output = capsys.readouterr().out

    assert current_index == index
    assert result is None
    assert "Please provide a word to print." in output


def test_handle_command_find_without_query(capsys):
    # find without a query should ask the user for at least one term
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    current_index, result = handle_command("find", index)

    output = capsys.readouterr().out

    assert current_index == index
    assert result is None
    assert "Please provide at least one search term." in output


def test_handle_command_find_missing_word_prints_no_matches(capsys):
    # searching for a missing word should explain the query and return no matches
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    current_index, result = handle_command("find missing", index)

    output = capsys.readouterr().out

    assert current_index == index
    assert result is None
    assert "Query explanation:" in output
    assert "No matching pages found." in output


def test_handle_command_find_phrase_search_prints_results(capsys):
    # phrase search should use positions and print matching pages
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]}
        }
    }

    current_index, result = handle_command('find "good friends"', index)

    output = capsys.readouterr().out

    assert current_index == index
    assert result is None
    assert "Query explanation:" in output
    assert "Mode: exact phrase search" in output
    assert "Matching pages:" in output
    assert "- page1" in output


def test_handle_command_print_existing_word_prints_entry(capsys):
    # print should display the stored index entry for an existing word
    index = {
        "good": {
            "page1": {"frequency": 2, "positions": [0, 3]}
        }
    }

    current_index, result = handle_command("print good", index)

    output = capsys.readouterr().out

    assert current_index == index
    assert result is None
    assert "- page1" in output
    assert "frequency: 2" in output
    assert "positions: [0, 3]" in output


def test_handle_command_unknown_command_prints_message(capsys):
    # unknown commands should give a helpful message instead of failing
    current_index, result = handle_command("banana", None)

    output = capsys.readouterr().out

    assert current_index is None
    assert result is None
    assert "Unknown command: banana" in output
    assert "Type 'help' to see available commands." in output


def test_handle_command_load_success(monkeypatch, capsys):
    # mock load_index so this test does not depend on a real index file
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    monkeypatch.setattr("src.main.load_index", lambda: index)

    current_index, result = handle_command("load", None)

    output = capsys.readouterr().out

    assert current_index == index
    assert result is None
    assert "Index loaded successfully." in output


def test_handle_command_load_missing_file(monkeypatch, capsys):
    # simulate a missing index file without touching the real file system
    def fake_load_index():
        raise FileNotFoundError("Index file not found")

    monkeypatch.setattr("src.main.load_index", fake_load_index)

    current_index, result = handle_command("load", None)

    output = capsys.readouterr().out

    assert current_index is None
    assert result is None
    assert "Index file not found" in output


def test_handle_command_build_uses_crawler_indexer_and_save(monkeypatch, capsys):
    # mock the build pipeline so the test does not crawl the live website
    pages = {
        "page1": "good friends"
    }

    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        },
        "friends": {
            "page1": {"frequency": 1, "positions": [1]}
        }
    }

    saved_indexes = []

    monkeypatch.setattr("src.main.crawl_website", lambda: pages)
    monkeypatch.setattr("src.main.build_index", lambda crawled_pages: index)
    monkeypatch.setattr("src.main.save_index", lambda built_index: saved_indexes.append(built_index))

    current_index, result = handle_command("build", None)

    output = capsys.readouterr().out

    assert current_index == index
    assert result is None
    assert saved_indexes == [index]
    assert "Building index..." in output
    assert "Index built and saved successfully." in output