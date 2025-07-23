import sys
from app.parser.parser import Parser 
from app.scan_for.parentheses import ParenthesesScanner
from app.evaluation.evaluator import Evaluator
from app.stringify import stringify

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh <command> <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in ['parse', 'tokenize', 'evaluate', 'run']:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    if command == 'tokenize':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        
        for token in tokens:
            
            literal_to_print = token.literal
            if isinstance(literal_to_print, float):
                literal_to_print = f"{literal_to_print}"
            elif literal_to_print is None:
                literal_to_print = "null"

            print(f"{token.type} {token.lexeme} {literal_to_print}")

    
        if scanner.has_error:
            exit(65)

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

    if command == 'evaluate':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        if scanner.has_error:
            exit(65)
        
        parser = Parser(tokens)
        ast = parser.parse()
        if ast is None:
            exit(65)

        evaluator = Evaluator()
        try:
           result = evaluator.evaluate(ast)
        except RuntimeError:
            exit(70)

    if command == 'run':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()

        if scanner.has_error:
            exit(65)

        parser = Parser(tokens)
        ast = parser.parse()
        if ast is None:
            exit(65)

        evaluator = Evaluator()
        try:
            result = evaluator.evaluate_statements(ast)
        except RuntimeError as e:
            print(f"Runtime error: {e}", file=sys.stderr)
            exit(70)

if __name__ == "__main__":
    main()
