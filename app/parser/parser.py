from app.parser.ast import Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary
from app.scan_for.tokens import Token 
import sys

# A simple custom exception class for signaling a parse error.
# Your main.py script can catch this specific error to exit with code 65.
class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self.current = 0
        # The had_error flag is no longer needed as we stop on the first error.

    def parse(self):
        """
        The main entry point. Parses a list of statements.
        Will raise a ParseError if it encounters invalid syntax.
        """
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())
        return statements

    # No declaration() or synchronize() methods are needed for this simpler error handling.
        
    def statement(self):
        """Parses one statement."""
        if self.match('PRINT'):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self):
        """Parses a print statement: 'print' expression ';'"""
        value = self.expression()
        self.consume('SEMICOLON', "Expect ';' after value.")
        return Print(value)

    def expression_statement(self):
        """Parses an expression statement: expression (';')?"""
        expr = self.expression()
        # --- FIX: Changed consume to match to make the semicolon optional ---
        # This allows for REPL-like evaluation of single expressions without a trailing ';'.
        self.match('SEMICOLON')
        return Expression(expr)

    # --- Expression parsing methods (unchanged) ---
    def expression(self):
        return self.equality()
    
    def equality(self):
        expr = self.comparison()
        while self.match("EQUAL_EQUAL", "BANG_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr 
    
    def comparison(self):
        expr = self.term()
        while self.match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr 
    
    def term(self):
        expr= self.factors()
        while self.match("MINUS", "PLUS"):
            operator = self.previous()
            right = self.factors()
            expr = Binary(expr, operator, right)
        return expr
    
    def factors(self):
        expr = self.unary()
        while self.match("SLASH", "STAR"):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr
    
    def unary(self):
        if self.match("BANG", "MINUS"):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()
    
    def primary(self):
        if self.match("TRUE"): return Literal(True)
        if self.match("FALSE"): return Literal(False)
        if self.match("NIL"): return Literal(None)
        if self.match("NUMBER", "STRING"): return Literal(self.previous().literal)
        if self.match('LEFT_PAREN'):
            expr = self.expression()
            self.consume('RIGHT_PAREN', "Expect ')' after expression")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression.") 

    # --- MODIFIED: The error method now raises the custom ParseError ---
    def error(self, token, message):
        """Reports an error to stderr and returns the ParseError to be raised."""
        if token.type == 'EOF':
            print(f"[line {token.line}] Error at end: {message}", file=sys.stderr)
        else:
            print(f"[line {token.line}] Error at '{token.lexeme}': {message}", file=sys.stderr)
        # Return the exception to be raised by the caller (consume() or primary()).
        return ParseError()

    # --- Helper methods (unchanged) ---
    def consume(self, token_type, error_msg):
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), error_msg)
        
    def check(self, token_type):
        if self.is_at_end(): return False
        return self.peek().type == token_type

    def match(self, *token_types):
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
            
    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()
    
    def peek(self):
        return self.tokens[self.current]
    
    def is_at_end(self):
        return self.peek().type == "EOF"
    
    def previous(self):
        return self.tokens[self.current - 1]
