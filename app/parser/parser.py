from app.parser.ast import Expr, Print, Stmt, Expression, Literal, Grouping, Unary, Binary
from app.scan_for.tokens import Token 

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())
        
        return statements
    
    def statement(self):
        if self.match("PRINT"):
            return self.print_statement()
        return self.expression_statement()
    
    def print_statement(self):
        expr = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return Print(expr)
    
    def expression_statement(self):
        expr = self.expression()
        self.consume("SEMICOLON", "Expect ';' after expression.")
        return Expression(expr)
        
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
        if self.match("TRUE"):
            return Literal(True)
        elif self.match("FALSE"):
            return Literal(False)
        elif self.match("NIL"):
            return Literal(None)
        
        if self.match("NUMBER", "STRING"):
            return Literal(self.previous().literal)
        
        if self.match('LEFT_PAREN'):
            expr = self.expression()
            self.consume('RIGHT_PAREN', "Expect expression")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.") 

    
    """
    These are helper functions below that help execute the pipeline and 
    help attribute the tokens to appropriate nodes
    """
    def consume(self, token_type, error_msg):
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), error_msg)
        
    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().type == token_type

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
    
    def error(self, token, message):
        raise Exception(f" Error at {token.lexeme}: {message}")