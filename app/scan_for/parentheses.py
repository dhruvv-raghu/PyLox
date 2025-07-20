from app.scan_for.operations import Operations
import sys
from app.scan_for.tokens import Token
from app.scan_for.escseq import EscapeSequences
from app.scan_for.keywords import Keywords


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
        self.keywords = Keywords
        self.operations = Operations
        self.escape_sequences = EscapeSequences
        self.tokens= []
    
    def identifier_scanner(self):
        start_pos= self.pos
        while self.peek_next() and (self.peek_next().isalnum() or self.peek_next() == '_'):
            self.advance()

        lexeme = self.file_contents[start_pos:self.pos+1]
        
        token_type = self.keywords.get(lexeme, 'IDENTIFIER')
        literal = None
        if token_type == 'IDENTIFIER':
            literal = lexeme
        
        return self.add_token(token_type, lexeme, literal)
            
    def number_scanner(self):
        start_pos = self.pos
        while self.peek_next() and self.peek_next().isdigit():
            self.advance()

        if self.peek_next() == '.' and self.peek_next_next() and self.peek_next_next().isdigit():
            self.advance()
            while self.peek_next() and self.peek_next().isdigit():
                self.advance()

        lexeme= self.file_contents[start_pos:self.pos+1]

        try:
            literal = float(lexeme)
        except ValueError:
            self.has_error = True
            print(f"[line {self.line_number}] Error: Invalid number literal: {lexeme}", file=sys.stderr)
            return None
        
        return self.add_token("NUMBER", lexeme, literal)



    def string_scanner(self):
        self.string= ""
        self.start_line = self.line_number
        
        while self.peek_next() and self.peek_next() != '"':
            self.advance()
            char = self.current_char()
            if char == '\n':
                self.line_number += 1
            
            if char == '\\' and self.peek_next() is not None:
                self.advance()
                next_char = self.current_char()
                escape_map = EscapeSequences
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
    
    def peek_next_next(self):
        if self.pos + 2 >= len(self.file_contents):
            return None
        return self.file_contents[self.pos + 2]
    
    def add_token(self, token_type, lexeme, literal=None):
        if token_type == "STRING" and lexeme.startswith('"') and lexeme.endswith('"'):
             literal = lexeme[1:-1]
        
        token = Token(token_type, lexeme, literal, self.line_number)
        self.tokens.append(token)
        return token

    def scan_token(self):
        char = self.advance()

        if char is None:
            return None

        while char in ' \t\r\n':
            if char == '\n':
                self.line_number += 1
            char = self.advance()
            if char is None:
                return None
            
        if char.isalpha() or char == '_':
            return self.identifier_scanner()
            
        if char.isdigit():
            return self.number_scanner()
        
        if char == '!':
            if self.peek_next() == '=':
                self.advance()
                return self.add_token('BANG_EQUAL', '!=')
            return self.add_token('BANG', '!')
        
        if char == '=':
            if self.peek_next() == '=':
                self.advance()
                return self.add_token('EQUAL_EQUAL', '==')
        
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
            return self.string_scanner()

        if char in self.operations:
            token_type = self.operations[char]
            return self.add_token(token_type, char)

        self.has_error = True
        print(f"[line {self.line_number}] Error: Unexpected character: {char}", file=sys.stderr)
        return None

    def scan_all(self):

        self.pos = -1
        while self.pos < len(self.file_contents) - 1:
            token = self.scan_token()
            if token:
                literal_to_print = token.literal if token.literal is not None else "null"
                print(f"{token.type} {token.lexeme} {literal_to_print}")
