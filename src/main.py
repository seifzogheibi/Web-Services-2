def show_help():
    print("Available commands:")
    print("  build              Crawl website and build the index")
    print("  load               Load the saved index from disk")
    print("  print <word>       Print the index entry for a word")
    print("  find <query>       Find pages containing the query terms")
    print("  help               Show this help message")
    print("  exit               Exit the program")


def handle_command(command):
    parts = command.split()

    if not parts:
        return

    action = parts[0].lower()
    arguments = parts[1:]

    if action == "help":
        show_help()

    elif action == "exit":
        return "exit"

    elif action == "build":
        print("Build command selected.")

    elif action == "load":
        print("Load command selected.")

    elif action == "print":
        if not arguments:
            print("Please provide a word to print.")
        else:
            print(f"Print command selected for word: {arguments[0]}")

    elif action == "find":
        if not arguments:
            print("Please provide at least one search term.")
        else:
            query = " ".join(arguments)
            print(f"Find command selected for query: {query}")

    else:
        print(f"Unknown command: {action}")
        print("Type 'help' to see available commands.")


def main():
    print("COMP3011 Search Engine Tool")
    print("Type 'help' to see available commands.")

    while True:
        command = input("> ").strip()
        result = handle_command(command)

        if result == "exit":
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()