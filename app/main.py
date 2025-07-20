import sys
# Make sure the import path for your Parser is correct.
# If your parser.py is in the root of an 'app' directory, this might need adjustment.
from app.parser.parser import Parser 
from app.scan_for.parentheses import ParenthesesScanner

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh <command> <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in ['parse', 'tokenize']:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    if command == 'tokenize':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        
        # --- FIX STARTS HERE ---
        # First, we print all the tokens that the scanner was able to find,
        # even if an error was encountered later.
        for token in tokens:
            # We don't want to print the final EOF token in this case.
            if token.type == 'EOF':
                print("EOF  null")
            
            literal_to_print = token.literal
            if isinstance(literal_to_print, float):
                literal_to_print = f"{literal_to_print:.1f}"
            elif literal_to_print is None:
                literal_to_print = "null"

            print(f"{token.type} {token.lexeme} {literal_to_print}")

        # Now, after printing, we check if there was an error and exit if needed.
        if scanner.has_error:
            exit(65)
        # --- FIX ENDS HERE ---
        return
    
    if command == 'parse':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        if scanner.has_error:
            exit(65)
        
        parser = Parser(tokens)
        ast = parser.parse()
        if ast is None: # Or check a parser error flag
            exit(65)
            
        print(ast)

if __name__ == "__main__":
    main()
