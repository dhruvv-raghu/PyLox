from app.scan_for.operations import Operations
import sys

class ParenthesesScanner:
    def __init__(self, filename):
        self.filename = filename
        try: 
            with open(self.filename, 'r') as file:
                self.file_contents = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.filename} not found.")
        
        self.pos = 0
        self.line_number = 1
        self.has_error = False
        self.operations = Operations

    def current_char(self):
        if self.pos >= len(self.file_contents):
            return None
        return self.file_contents[self.pos]

    def advance(self):
        if self.pos < len(self.file_contents):
            if self.file_contents[self.pos] == '\n':
                self.line_number += 1
            self.pos += 1

    def peek_next(self):
        if self.pos + 1 >= len(self.file_contents):
            return None
        return self.file_contents[self.pos + 1]

    def scan_token(self):
        # Skip whitespace (except newlines, which we handle separately)
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
        
        if self.current_char() is None:
            raise EOFError("End of file reached")
        
        char = self.current_char()
        
        if char == '\n':
            print("NEWLINE \\n null")
            self.advance()
            return
        
        if char == '=':
            if self.peek_next == '=':
                print("EQUAL_EQUAL == null")
                self.advance()
                self.advance()
            else:
                print("EQUAL = null")
                self.advance()

        
        if char in self.operations:
            token_type = self.operations[char]
            print(f"{token_type} {char} null")
            self.advance()
        else:
            self.has_error = True
            print(f"[line {self.line_number}] Error: Unexpected character: {char}", file=sys.stderr)
            self.advance()