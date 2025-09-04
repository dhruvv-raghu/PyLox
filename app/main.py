import sys
from app.parser.parser import Parser, ParseError
# --- FIX: Import the Expression AST node ---
from app.parser.ast import Expression
from app.scan_for.parentheses import ParenthesesScanner
from app.evaluation.evaluator import Evaluator
from app.stringify import stringify
from app.resolver.resolver import Resolver 

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
        try:
            ast = parser.parse()
        except ParseError:
            exit(65)
        
        if ast:
            print(ast[0])
        return

    if command == 'evaluate':
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        if scanner.has_error:
            exit(65)
        
        parser = Parser(tokens)
        try:
            statements = parser.parse()
        except ParseError:
            exit(65)

        evaluator = Evaluator()
        try:
            result = evaluator.evaluate_statements(statements)
            
            # --- FIX: Check if the last statement was an expression ---
            # This correctly handles printing 'nil' while suppressing output
            # for non-expression statements.
            if statements and isinstance(statements[-1], Expression):
                print(stringify(result))

        except RuntimeError as e:
            print(e, file=sys.stderr)
            exit(70)
        return

    if command == 'run':
        # Step 1: Scanning
        scanner = ParenthesesScanner(filename)
        tokens = scanner.scan_all()
        if scanner.has_error:
            exit(65)

        # Step 2: Parsing
        parser = Parser(tokens)
        try:
            statements = parser.parse()
        except ParseError:
            exit(65)

        # Create the interpreter instance that will run the code.
        evaluator = Evaluator()

        # Step 3: Resolution
        resolver = Resolver(evaluator)
        resolver.resolve_statements(statements)
        
        # Step 4: Evaluation (Interpretation)
        try:
            evaluator.evaluate_statements(statements)
        except RuntimeError as e:
            print(e, file=sys.stderr)
            exit(70)

if __name__ == "__main__":
    main()

