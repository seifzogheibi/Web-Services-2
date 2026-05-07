from src.main import handle_command, print_query_explanation


def test_empty_command_does_nothing():
    current_index, result = handle_command("", None)

    assert current_index is None
    assert result is None


def test_exit_command_returns_exit_signal():
    current_index, result = handle_command("exit", None)

    assert current_index is None
    assert result == "exit"


def test_print_command_without_loaded_index_does_not_crash():
    current_index, result = handle_command("print good", None)

    assert current_index is None
    assert result is None


def test_find_command_without_loaded_index_does_not_crash():
    current_index, result = handle_command("find good", None)

    assert current_index is None
    assert result is None


def test_unknown_command_does_not_crash():
    current_index, result = handle_command("unknown", None)

    assert current_index is None
    assert result is None


def test_find_command_with_loaded_index_keeps_index():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    current_index, result = handle_command("find good", index)

    assert current_index == index
    assert result is None


def test_print_command_with_loaded_index_keeps_index():
    index = {
        "good": {
            "page1": {"frequency": 1, "positions": [0]}
        }
    }

    current_index, result = handle_command("print good", index)

    assert current_index == index
    assert result is None

def test_print_query_explanation_for_standard_search(capsys):
    print_query_explanation("good friends", False)

    output = capsys.readouterr().out

    assert "Query explanation:" in output
    assert "Mode: multi-word AND search" in output
    assert "Ranking: TF-IDF" in output
    assert "Terms: good friends" in output


def test_print_query_explanation_for_phrase_search(capsys):
    print_query_explanation('"good friends"', True)

    output = capsys.readouterr().out

    assert "Query explanation:" in output
    assert "Mode: exact phrase search" in output
    assert "Ranking: TF-IDF" in output
    assert "Phrase: good friends" in output