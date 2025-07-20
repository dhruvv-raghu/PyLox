from app.scan_for.operations import Operations
import sys
from app.scan_for.tokens import Token
from app.scan_for.escseq import EscapeSequences
from app.scan_for.characters import CharacterSet

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
        self.characters = CharacterSet
        self.escape_sequences = EscapeSequences
        self.tokens= []
    

    def string_scanner(self):
        self.string= ""
        self.start_line = self.line_number
        
        # Loop until we see the closing quote or the end of the file
        while self.peek_next() and self.peek_next() != '"':
            self.advance()
            char = self.current_char()
            if char == '\n':
                self.line_number += 1
            
            if char == '\\' and self.peek_next() is not None:
                self.advance()
                next_char = self.current_char()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"'}
                if next_char in escape_map:
                    self.string += escape_map[next_char]
                else:
                    self.string += next_char
            else:
                self.string += char

        # Check for unterminated string
        if self.peek_next() is None:
            self.has_error = True
            print(f"[line {self.start_line}] Error: Unterminated string.", file=sys.stderr)
            self.pos = len(self.file_contents)
            return None

        self.advance() # Consume the closing quote
        
        return self.add_token("STRING", f'"{self.string}"', self.string)

    def current_char(self):
        if self.pos >= len(self.file_contents):
            return None
        return self.file_contents[self.pos]

    def advance(self):
        if self.pos < len(self.file_contents):
            self.pos += 1
        return self.current_char()


    def peek_next(self):
        if self.pos + 1 >= len(self.file_contents):
            return None
        return self.file_contents[self.pos + 1]
    
    def add_token(self, token_type, lexeme, literal=None):
        if token_type == "STRING" and lexeme.startswith('"') and lexeme.endswith('"'):
             literal = lexeme[1:-1]
        
        token = Token(token_type, lexeme, literal, self.line_number)
        self.tokens.append(token)
        return token

    def scan_token(self):
        # --- FIX STARTS HERE ---
        # The original logic mixed advancing and whitespace skipping in a way
        # that could cause errors. This new structure is more robust.
        # First, we advance the position.
        char = self.advance()

        # If advancing took us past the end of the file, we're done.
        if char is None:
            return None

        # Now, skip any whitespace characters.
        while char in ' \t\r\n':
            if char == '\n':
                self.line_number += 1
            char = self.advance()
            # If we hit the end of the file while skipping whitespace, stop.
            if char is None:
                return None
        
        # --- FIX ENDS HERE ---
        # At this point, 'char' is guaranteed to be the first non-whitespace character.

        # --- Multi-character and special tokens first ---
        if char == '!':
            if self.peek_next() == '=':
                self.advance()
                return self.add_token('BANG_EQUAL', '!=')
            return self.add_token('BANG', '!')
        
        if char == '=':
            if self.peek_next() == '=':
                self.advance()
                return self.add_token('EQUAL_EQUAL', '==')
            # The single '=' is handled by the dictionary lookup below
        
        if char == '<':
            if self.peek_next() == '=':
                self.advance()
                return self.add_token('LESS_EQUAL', '<=')
            return self.add_token('LESS', '<')

        if char == '>':
            if self.peek_next() == '=':
                self.advance()
                return self.add_token('GREATER_EQUAL', '>=')
            return self.add_token('GREATER', '>')

        if char == '/':
            if self.peek_next() == '/':
                while self.peek_next() and self.peek_next() != '\n':
                    self.advance()
                return None
            else:
                return self.add_token('SLASH', '/')

        if char == '"':
            # We don't advance before string_scanner because it expects to be on the opening quote
            return self.string_scanner()

        # --- Use the Operations dictionary for single-character tokens ---
        if char in self.operations:
            token_type = self.operations[char]
            return self.add_token(token_type, char)

        # --- Unrecognized character ---
        self.has_error = True
        print(f"[line {self.line_number}] Error: Unexpected character: {char}", file=sys.stderr)
        return None

    def scan_all(self):
        # Start at position -1 so the first advance() in scan_token moves to position 0
        self.pos = -1
        # Loop until we have processed all characters
        while self.pos < len(self.file_contents) - 1:
            token = self.scan_token()
            if token:
                literal_to_print = token.literal if token.literal is not None else "null"
                print(f"{token.type} {token.lexeme} {literal_to_print}")
