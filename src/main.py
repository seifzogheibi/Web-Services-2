from src.crawler import crawl_website
from src.indexer import build_index, load_index, save_index
from src.search import find_pages, get_index_entry, find_phrase_pages


def show_help():
    # show the available shell commands to the user
    print("Available commands:")
    print("  build              Crawl website and build the index")
    print("  load               Load the saved index from disk")
    print("  print <word>       Print the index entry for a word")
    print("  find <query>       Find pages containing the query terms")
    print("  help               Show this help message")
    print("  exit               Exit the program")


def print_query_explanation(query, is_phrase_search):
    """
    Print a short explanation of how the query will be processed.
    """
    # explain the search mode before showing the results
    print("Query explanation:")

    if is_phrase_search:
        # quoted queries are treated as exact phrase searches
        phrase = query.strip('"')
        print("- Mode: exact phrase search")
        print("- Ranking: TF-IDF")
        print(f"- Phrase: {phrase}")
    else:
        # normal find queries use and search across all query terms
        print("- Mode: multi-word AND search")
        print("- Ranking: TF-IDF")
        print(f"- Terms: {query}")


def print_index_entry(entry):
    """
    Print one word's inverted index entry in a readable format.
    """
    # handle words that are not stored in the index
    if entry is None:
        print("Word not found in index.")
        return

    # print each page where the word appears with its stored statistics
    for url, stats in entry.items():
        print(f"- {url}")
        print(f"  frequency: {stats['frequency']}")
        print(f"  positions: {stats['positions']}")


def handle_command(command, current_index):
    # split the command into the main action and any extra arguments
    parts = command.split()

    # ignore empty input so the shell does not crash or show an error
    if not parts:
        print()
        return current_index, None

    action = parts[0].lower()
    arguments = parts[1:]

    # show the list of supported commands
    if action == "help":
        show_help()
        print()

    # return a signal so the main loop can stop cleanly
    elif action == "exit":
        print()
        return current_index, "exit"

    # crawl the website, build the index, and save it to disk
    elif action == "build":
        print("Building index...")
        pages = crawl_website()
        current_index = build_index(pages)
        save_index(current_index)
        print("Index built and saved successfully.")
        print()

    # load a previously saved index from the data folder
    elif action == "load":
        try:
            current_index = load_index()
            print("Index loaded successfully.")
        except FileNotFoundError as error:
            print(error)
        print()

    # print the inverted index entry for one word
    elif action == "print":
        if not arguments:
            print("Please provide a word to print.")
        elif current_index is None:
            print("No index loaded. Run 'load' or 'build' first.")
        else:
            entry = get_index_entry(current_index, arguments[0])
            print_index_entry(entry)
        print()

    # search for pages containing a word, multiple words, or an exact phrase
    elif action == "find":
        if not arguments:
            print("Please provide at least one search term.")
        elif current_index is None:
            print("No index loaded. Run 'load' or 'build' first.")
        else:
            query = " ".join(arguments)

            # quoted queries are handled as phrase search
            is_phrase_search = query.startswith('"') and query.endswith('"')

            print_query_explanation(query, is_phrase_search)

            if is_phrase_search:
                # remove quotes before searching for the exact phrase
                phrase = query.strip('"')
                pages = find_phrase_pages(current_index, phrase)
            else:
                # normal searches return pages containing all query terms
                pages = find_pages(current_index, arguments)

            # show either the matching pages or a clear no-results message
            if not pages:
                print("No matching pages found.")
            else:
                print("Matching pages:")
                for page in pages:
                    print(f"- {page}")
        print()

    # handle unsupported commands without stopping the shell
    else:
        print(f"Unknown command: {action}")
        print("Type 'help' to see available commands.")
        print()

    return current_index, None

def main():
    print("COMP3011 Search Engine Tool")
    print("Type 'help' to see available commands.")

    # this stores the active index after build or load is used
    current_index = None

    # keep accepting commands until the user enters exit
    while True:
        command = input("> ").strip()
        current_index, result = handle_command(command, current_index)

        if result == "exit":
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()