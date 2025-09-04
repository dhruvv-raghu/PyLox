import sys
from enum import Enum, auto
from typing import List, Dict

from app.parser.ast import (
    Expr, Stmt, Visitor, StmtVisitor, Block, Var, Variable, Assign, Function,
    Expression, If, Print, Return, While, Binary, Call, Grouping, Literal,
    Logical, Unary, Class, Get, Set, This
)
from app.scan_for.tokens import Token
from app.evaluation.evaluator import Evaluator

class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()

class ClassType(Enum):
    NONE = auto()
    CLASS = auto()

class Resolver(Visitor, StmtVisitor):
    def __init__(self, evaluator: Evaluator):
        self.evaluator = evaluator
        self.scopes: List[Dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
        self.had_error = False

    def error(self, token: Token, message: str):
        print(f"[line {token.line}] Error: {message}", file=sys.stderr)
        self.had_error = True

    def resolve_statements(self, statements: List[Stmt]):
        for statement in statements:
            if statement: self.resolve_statement(statement)

    def resolve_statement(self, stmt: Stmt):
        stmt.accept(self)

    def resolve_expression(self, expr: Expr):
        expr.accept(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if not self.scopes: return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.error(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes: return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.evaluator.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolve_function(self, function_node: Function, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in function_node.params:
            self.declare(param)
            self.define(param)
        self.resolve_statements(function_node.body)
        self.end_scope()
        self.current_function = enclosing_function

    def visit_block(self, stmt: Block):
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.end_scope()

    def visit_var(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expression(stmt.initializer)
        self.define(stmt.name)

    def visit_variable(self, node: Variable):
        if self.scopes and self.scopes[-1].get(node.name.lexeme) is False:
            self.error(node.name, "Can't read local variable in its own initializer.")
        self.resolve_local(node, node.name)

    def visit_assign(self, node: Assign):
        self.resolve_expression(node.value)
        self.resolve_local(node, node.name)
        
    def visit_class(self, stmt: Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
        self.end_scope()
        self.current_class = enclosing_class

    def visit_function(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression(self, stmt: Expression):
        self.resolve_expression(stmt.expression)

    def visit_if(self, stmt: If):
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_statement(stmt.else_branch)

    def visit_print(self, stmt: Print):
        self.resolve_expression(stmt.expression)

    def visit_return(self, stmt: Return):
        if self.current_function == FunctionType.NONE:
            self.error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                self.error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve_expression(stmt.value)

    def visit_while(self, stmt: While):
        self.resolve_expression(stmt.condition)
        self.resolve_statement(stmt.body)

    def visit_binary(self, node: Binary):
        self.resolve_expression(node.left)
        self.resolve_expression(node.right)

    def visit_call(self, node: Call):
        self.resolve_expression(node.callee)
        for argument in node.arguments:
            self.resolve_expression(argument)

    def visit_grouping(self, node: Grouping):
        self.resolve_expression(node.expression)

    def visit_literal(self, node: Literal):
        pass

    def visit_logical(self, node: Logical):
        self.resolve_expression(node.left)
        self.resolve_expression(node.right)

    def visit_unary(self, node: Unary):
        self.resolve_expression(node.right)

    def visit_get(self, node: Get):
        self.resolve_expression(node.obj)

    def visit_set(self, node: Set):
        self.resolve_expression(node.value)
        self.resolve_expression(node.obj)

    def visit_this(self, node: This):
        if self.current_class == ClassType.NONE:
            self.error(node.keyword, "Can't use 'this' outside of a class.")
            return
        self.resolve_local(node, node.keyword)

