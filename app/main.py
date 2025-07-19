import sys
from app.scan_for.parentheses import ParenthesesScanner

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)



    scanner = ParenthesesScanner(filename)
    try:
        while True:
            scanner.parentheses()
    except EOFError:
            print("EOF  null")

if __name__ == "__main__":
    main()
