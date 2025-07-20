import sys
from app.scan_for.parentheses import ParenthesesScanner
from app.parser.parser import Parser

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in ['parse', 'tokenize']:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    if command == 'tokenize':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        
        if scanner.has_error:
            exit(65)

        for token in tokens:
            literal_to_print = token.literal if token.literal is not None else "null"
            print(f"{token.type} {token.lexeme} {literal_to_print}")
        return
    
    if command == 'parse':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        if scanner.has_error:
            exit(65)
        
        parser = Parser(tokens)
        ast = parser.parse()
        print(ast)

if __name__ == "__main__":
    main()