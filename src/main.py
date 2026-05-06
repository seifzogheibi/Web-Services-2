def show_help():
    print("Available commands:")
    print("  build              Crawl website and build the index")
    print("  load               Load the saved index from disk")
    print("  print <word>       Print the index entry for a word")
    print("  find <query>       Find pages containing the query terms")
    print("  help               Show this help message")
    print("  exit               Exit the program")


def main():
    print("COMP3011 Search Engine Tool")
    print("Type 'help' to see available commands.")
    
    while True:
        command = input("> ").strip()
        
        if command == "help":
            show_help()
        elif command == "exit":
            print("Goodbye.")
            break
        elif command == "":
            continue
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' to see available commands.")


if __name__ == "__main__":
    main()