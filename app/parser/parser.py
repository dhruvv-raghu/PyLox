from app.parser.ast import Var, Print, Expression, Assign, Variable, Literal, Grouping, Unary, Binary, Block, If
import sys

# A simple custom exception class for signaling a parse error.
class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        """
        The main entry point. Parses a list of statements.
        Will raise a ParseError if it encounters invalid syntax.
        """
        statements = []
        while not self.is_at_end():
            # The main loop should call declaration(), which is the highest-level rule.
            statements.append(self.declaration())
        return statements

    def declaration(self):
        """Parses a declaration, dispatching to the correct rule."""
        if self.match('VAR'):
            return self.var_declaration()
        return self.statement()

    def statement(self):
        """Parses one statement. Does not handle var declarations directly anymore."""
        if self.match('IF'):
            return self.if_statement()
        if self.match('LEFT_BRACE'):
            return Block(self.block())
        # The VAR check is removed from here.
        if self.match('PRINT'):
            return self.print_statement()
        return self.expression_statement()

    def if_statement(self):
        self.consume('LEFT_PAREN', "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume('RIGHT_PAREN', "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match('ELSE'):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def block(self):
        statements = []
        while not self.check('RIGHT_BRACE') and not self.is_at_end():
            statements.append(self.declaration())
        self.consume('RIGHT_BRACE', "Expect '}' after block.")
        return statements

    def var_declaration(self):
        name = self.consume('IDENTIFIER', "Expect variable name.")
        initializer = None
        if self.match('EQUAL'):
            initializer = self.expression()
        self.consume('SEMICOLON', "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def print_statement(self):
        value = self.expression()
        self.consume('SEMICOLON', "Expect ';' after value.")
        return Print(value)

    def expression_statement(self):
        """Parses an expression statement. The semicolon is optional."""
        expr = self.expression()
        self.match('SEMICOLON')
        return Expression(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.equality()
        if self.match('EQUAL'):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            raise self.error(equals, "Invalid assignment target.")
        return expr

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
        expr = self.factors()
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
        if self.match("IDENTIFIER"): return Variable(self.previous())
        if self.match('LEFT_PAREN'):
            expr = self.expression()
            self.consume('RIGHT_PAREN', "Expect ')' after expression")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")

    def error(self, token, message):
        """Reports an error to stderr and returns the ParseError to be raised."""
        if token.type == 'EOF':
            print(f"[line {token.line}] Error at end: {message}", file=sys.stderr)
        else:
            print(f"[line {token.line}] Error at '{token.lexeme}': {message}", file=sys.stderr)
        return ParseError()

    def consume(self, token_type, error_msg):
        if self.check(token_type): return self.advance()
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

