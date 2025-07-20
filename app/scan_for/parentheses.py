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
        self.advance()

        while self.current_char() and self.current_char() != '"':
            char= self.current_char()
            if char == '\n':
                self.line_number += 1
                self.string += char
            elif char == '\\' and self.peek_next() is not None:
                self.advance()
                esc_char = self.peek_next()
                if esc_char in self.escape_sequences:
                    self.string += self.escape_sequences[esc_char]
                else:
                    self.string += esc_char
            else:
                self.string += char

            self.advance()

        if self.current_char() is None:
            self.has_error = True
            print(f"[line {self.start_line}] Error: Unterminated string", file=sys.stderr)
            return self.add_token("STRING",f'"{self.string}', self.string)
        
        self.advance()  # Skip the closing quote
        return self.add_token("STRING", f'"{self.string}"', self.string)
    

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
    
    def add_token(self, token_type, lexeme, literal=None):
        token = Token(token_type, lexeme, literal, self.line_number)
        self.tokens.append(token)
        return token

    def scan_token(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
        
        if self.current_char() is None:
            raise EOFError("End of file reached")
        
        char = self.current_char()
        
        if char == '\n':
            token = self.add_token("NEWLINE", char)
            self.advance()
            return token
        
        if char == '"':
            return self.string_scanner()
        
        match char:
            case '=':
                if self.peek_next() == '=': 
                   token= self.add_token("EQUAL_EQUAL", "==")
                   self.advance()
                   self.advance()
                else:
                   token = self.add_token("EQUAL", "=")
                   self.advance()
                return 

            case '!':
                if self.peek_next() == '=':
                    token = self.add_token("BANG_EQUAL", "!=")
                    self.advance()
                    self.advance()
                else:
                    token = self.add_token("BANG", "!")
                    self.advance()
                return
            
            case '<':
                if self.peek_next() == '=':
                    token = self.add_token("LESS_EQUAL", "<=")
                    self.advance()
                    self.advance()
                else:
                    token = self.add_token("LESS", "<")
                    self.advance()
                return
            
            case '>':
                if self.peek_next() == '=':
                    token = self.add_token("GREATER_EQUAL", ">=")
                    self.advance()
                    self.advance()
                else:
                    token = self.add_token("GREATER", ">")
                    self.advance()
                return
            
            case '/':
                if self.peek_next() == '/':
                    # Single-line comment
                    while self.current_char() and self.current_char() != '\n':
                        self.advance()
                    return
                else:
                    token = self.add_token("SLASH", "/")
                    self.advance()
                return

        
        if char in self.operations:
            token_type = self.operations[char]
            token = self.add_token(token_type, char)
            self.advance()
            return token 
        else:
            self.has_error = True
            print(f"[line {self.line_number}] Error: Unexpected character: {char}", file=sys.stderr)
            self.advance()
            return None 
        
    def scan_all(self):
        while True:
            try:
                token = self.scan_token()
                if token:
                    print(f"{token.type} {token.lexeme} {token.literal}")
                else:
                    self.has_error = True
                    print(f"[line {self.line_number}] Error: Invalid token", file=sys.stderr)
            except EOFError:
                eof_token = self.add_token("EOF", "")

            return self.tokens