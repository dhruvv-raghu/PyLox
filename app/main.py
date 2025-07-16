import sys
from scan_for.parentheses import ParenthesesScanner

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    print("Logs from your program will appear here!", file=sys.stderr)


    if file_contents:
       scanner= ParenthesesScanner(file_contents)
       try:
        while True:
                scanner.parentheses()
       except EOFError:
            print()



if __name__ == "__main__":
    main()
