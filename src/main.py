from src.crawler import crawl_website
from src.indexer import build_index, load_index, save_index
from src.search import find_pages, get_index_entry, find_phrase_pages


def show_help():
    print("Available commands:")
    print("  build              Crawl website and build the index")
    print("  load               Load the saved index from disk")
    print("  print <word>       Print the index entry for a word")
    print("  find <query>       Find pages containing the query terms")
    print("  help               Show this help message")
    print("  exit               Exit the program")


def print_index_entry(entry):
    """
    Print one word's inverted index entry in a readable format.
    """
    if entry is None:
        print("Word not found in index.")
        return

    for url, stats in entry.items():
        print(f"- {url}")
        print(f"  frequency: {stats['frequency']}")
        print(f"  positions: {stats['positions']}")


def handle_command(command, current_index):
    parts = command.split()

    if not parts:
        return current_index, None

    action = parts[0].lower()
    arguments = parts[1:]

    if action == "help":
        show_help()

    elif action == "exit":
        return current_index, "exit"

    elif action == "build":
        print("Building index...")
        pages = crawl_website()
        current_index = build_index(pages)
        save_index(current_index)
        print("Index built and saved successfully.")

    elif action == "load":
        try:
            current_index = load_index()
            print("Index loaded successfully.")
        except FileNotFoundError as error:
            print(error)

    elif action == "print":
        if not arguments:
            print("Please provide a word to print.")
        elif current_index is None:
            print("No index loaded. Run 'load' or 'build' first.")
        else:
            entry = get_index_entry(current_index, arguments[0])
            print_index_entry(entry)

    elif action == "find":
        if not arguments:
            print("Please provide at least one search term.")
        elif current_index is None:
            print("No index loaded. Run 'load' or 'build' first.")
        else:
            query = " ".join(arguments)

            if query.startswith('"') and query.endswith('"'):
                phrase = query.strip('"')
                pages = find_phrase_pages(current_index, phrase)
            else:
                pages = find_pages(current_index, arguments)
                
                if not pages:
                    print("No matching pages found.")
                else:
                    print("Matching pages:")
                    for page in pages:
                        print(f"- {page}")

    else:
        print(f"Unknown command: {action}")
        print("Type 'help' to see available commands.")

    return current_index, None


def main():
    print("COMP3011 Search Engine Tool")
    print("Type 'help' to see available commands.")

    current_index = None

    while True:
        command = input("> ").strip()
        current_index, result = handle_command(command, current_index)

        if result == "exit":
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()