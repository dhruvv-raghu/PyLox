import sys
from app.scan_for.parentheses import ParenthesesScanner
from app.parser.parser import Parser

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "parse":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    scanner = ParenthesesScanner(filename)
    tokens= scanner.scan_all()
 
    parser= Parser(tokens)
    ast = parser.parse()
    print(ast)
    
        
    if scanner.has_error:
        exit(65)

if __name__ == "__main__":
    main()