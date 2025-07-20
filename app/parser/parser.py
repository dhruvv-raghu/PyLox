from app.parser.ast import Literal
from app.scan_for.tokens import Token 
import sys

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except Exception as e:
            print(f"Error parsing expression: {e}", file=sys.stderr)
            return None
        
    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def expression(self):
        return self.primary()
    
    def primary(self):
        if self.match("TRUE"):
            return Literal(True)
        elif self.match("FALSE"):
            return Literal(False)
        elif self.match("NIL"):
            return Literal(None)
        
        if self.match("NUMBER", "STRING"):
            return Literal(self.previous().literal)
        
    def match(self, *token_types):
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
            
    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def peek(self):
        return self.tokens[self.current]
    
    def is_at_end(self):
        return self.peek().type == "EOF"
    
    def previous(self):
        return self.tokens[self.current - 1]