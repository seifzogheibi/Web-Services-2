def main():
    print("COMP3011 Search Engine Tool")
    print("Type 'help' to see available commands.")
    
    while True:
        command = input("> ").strip()
        
        if command == "exit":
            print("Goodbye.")
            break
        
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()