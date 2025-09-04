import sys
from app.parser.ast import (
    Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Assign,
    Variable, Var, Block, If, Logical, While, Function, Return, Call, Class,
    Get, Set, This
)
from app.scan_for.tokens import Token

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            # The main loop now calls declaration, which will raise an error on failure.
            statements.append(self.declaration())
        return statements

    def declaration(self):
        # --- FIX: Removed the internal try/except block ---
        # This will now let ParseError exceptions propagate up to main.py
        if self.match('CLASS'):
            return self.class_declaration()
        if self.match('FUN'):
            return self.function("function")
        if self.match('VAR'):
            return self.var_declaration()
        return self.statement()

    def class_declaration(self):
        name = self.consume('IDENTIFIER', "Expect class name.")
        self.consume('LEFT_BRACE', "Expect '{' before class body.")
        methods = []
        while not self.check('RIGHT_BRACE') and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume('RIGHT_BRACE', "Expect '}' after class body.")
        return Class(name, methods)

    def function(self, kind: str):
        name = self.consume('IDENTIFIER', f"Expect {kind} name.")
        self.consume('LEFT_PAREN', f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check('RIGHT_PAREN'):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume('IDENTIFIER', "Expect parameter name."))
                if not self.match('COMMA'):
                    break
        self.consume('RIGHT_PAREN', "Expect ')' after parameters.")
        self.consume('LEFT_BRACE', f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body)

    def statement(self):
        if self.match('FOR'): return self.for_statement()
        if self.match('IF'): return self.if_statement()
        if self.match('WHILE'): return self.while_statement()
        if self.match('LEFT_BRACE'): return Block(self.block())
        if self.match('PRINT'): return self.print_statement()
        if self.match('RETURN'): return self.return_statement()
        return self.expression_statement()

    def for_statement(self):
        self.consume('LEFT_PAREN', "Expect '(' after 'for'.")
        initializer = None
        if self.match('SEMICOLON'): pass
        elif self.match('VAR'): initializer = self.var_declaration()
        else: initializer = self.expression_statement()
        
        condition = None
        if not self.check('SEMICOLON'): condition = self.expression()
        self.consume('SEMICOLON', "Expect ';' after loop condition.")
        
        increment = None
        if not self.check('RIGHT_PAREN'): increment = self.expression()
        self.consume('RIGHT_PAREN', "Expect ')' after for clauses.")
        
        body = self.statement()
        
        if increment is not None:
            body = Block([body, Expression(increment)])
        
        if condition is None: condition = Literal(True)
        body = While(condition, body)
        
        if initializer is not None:
            body = Block([initializer, body])
        
        return body

    def if_statement(self):
        self.consume('LEFT_PAREN', "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume('RIGHT_PAREN', "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match('ELSE'):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def while_statement(self):
        self.consume('LEFT_PAREN', "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume('RIGHT_PAREN', "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

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

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check('SEMICOLON'):
            value = self.expression()
        self.consume('SEMICOLON', "Expect ';' after return value.")
        return Return(keyword, value)

    def expression_statement(self):
        expr = self.expression()
        self.match('SEMICOLON')
        return Expression(expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()
        if self.match('EQUAL'):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)
            raise self.error(equals, "Invalid assignment target.")
        return expr

    def logic_or(self):
        expr = self.logic_and()
        while self.match('OR'):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.match('AND'):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
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
        expr = self.factor()
        while self.match("MINUS", "PLUS"):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
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
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match('LEFT_PAREN'):
                expr = self.finish_call(expr)
            elif self.match('DOT'):
                name = self.consume('IDENTIFIER', "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee: Expr):
        arguments = []
        if not self.check('RIGHT_PAREN'):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match('COMMA'):
                    break
        paren = self.consume('RIGHT_PAREN', "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self):
        if self.match("TRUE"): return Literal(True)
        if self.match("FALSE"): return Literal(False)
        if self.match("NIL"): return Literal(None)
        if self.match("NUMBER", "STRING"): return Literal(self.previous().literal)
        if self.match("THIS"): return This(self.previous())
        if self.match("IDENTIFIER"): return Variable(self.previous())
        if self.match('LEFT_PAREN'):
            expr = self.expression()
            self.consume('RIGHT_PAREN', "Expect ')' after expression")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")

    def error(self, token, message):
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
    
    # --- FIX: Removed the synchronize method ---

