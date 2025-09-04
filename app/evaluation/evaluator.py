import sys
import time
from app.parser.ast import (
    Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Var,
    Variable, Assign, Block, If, Logical, While, Call, Function, Return,
    Class, Get, Set, This
)
from app.evaluation.visitors import Visitor, StmtVisitor
from app.environment import Environment
from app.stringify import stringify
from app.lox_callable import LoxCallable, ReturnValue
from app.lox_function import LoxFunction
from app.lox_class import LoxClass
from app.lox_instance import LoxInstance
from typing import Dict

from app.scan_for.tokens import Token

class NativeClock(LoxCallable):
    def arity(self) -> int: return 0
    def call(self, interpreter, arguments: list) -> float: return time.time()
    def __repr__(self): return "<native fn>"

class Evaluator(Visitor, StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        # --- FIX: Add a dictionary to store resolved variable depths ---
        self.locals: Dict[Expr, int] = {}
        self.environment = self.globals
        self.globals.define("clock", NativeClock())

    # --- FIX: Add the missing 'resolve' method ---
    def resolve(self, expr: Expr, depth: int):
        """
        Stores the resolved scope distance for a variable expression.
        This is called by the Resolver.
        """
        self.locals[expr] = depth

    def evaluate_statements(self, statements: list[Stmt]):
        try:
            for statement in statements:
                if statement: self.execute(statement)
        except RuntimeError as e:
            print(e, file=sys.stderr)
            exit(70)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def evaluate(self, expr: Expr):
        return expr.accept(self)
    
    # --- FIX: New helper to look up variables using resolved data ---
    def _look_up_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            # Fallback for global variables (which are not "resolved")
            return self.globals.get(name)

    def visit_variable(self, node: Variable):
        # Use the new lookup helper
        return self._look_up_variable(node.name, node)

    def visit_assign(self, node: Assign):
        value = self.evaluate(node.value)
        distance = self.locals.get(node)
        if distance is not None:
            self.environment.assign_at(distance, node.name, value)
        else:
            # Fallback for global variables
            self.globals.assign(node.name, value)
        return value

    def visit_class(self, stmt: Class):
        self.environment.define(stmt.name.lexeme, None)
        methods = {}
        for method in stmt.methods:
            is_initializer = method.name.lexeme == "init"
            function = LoxFunction(method, self.environment, is_initializer)
            methods[method.name.lexeme] = function
        
        klass = LoxClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klass)

    def visit_get(self, node: Get):
        obj = self.evaluate(node.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(node.name)
        raise RuntimeError(f"[{node.name.line}] Only instances have properties.")

    def visit_set(self, node: Set):
        obj = self.evaluate(node.obj)
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(f"[{node.name.line}] Only instances have fields.")
        
        value = self.evaluate(node.value)
        obj.set(node.name, value)
        return value

    def visit_this(self, node: This):
        return self._look_up_variable(node.keyword, node)

    def visit_while(self, stmt: While):
        while self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_call(self, node: Call):
        callee = self.evaluate(node.callee)
        arguments = []
        for argument in node.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(f"[{node.paren.line}] Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeError(f"[{node.paren.line}] Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_function(self, stmt: Function):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def visit_return(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnValue(value)

    def visit_logical(self, node: Logical):
        left = self.evaluate(node.left)
        if node.operator.type == 'OR':
            if self._is_truthy(left): return left
        else: # AND
            if not self._is_truthy(left): return left
        return self.evaluate(node.right)

    def visit_var(self, stmt: Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_block(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_if(self, stmt: If):
        if self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
    
    def visit_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def visit_expression(self, stmt: Expression):
        self.evaluate(stmt.expression)
    
    def visit_literal(self, node: Literal):
        return node.value

    def visit_grouping(self, node: Grouping):
        return self.evaluate(node.expression)

    def visit_unary(self, node: Unary):
        right = self.evaluate(node.right)
        op_type = node.operator.type
        if op_type == 'MINUS':
            self._check_number_operand(node.operator, right)
            return -float(right)
        if op_type == 'BANG':
            return not self._is_truthy(right)
        return None

    def visit_binary(self, node: Binary):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op_type = node.operator.type
        if op_type == 'MINUS':
            self._check_number_operands(node.operator, left, right)
            return float(left) - float(right)
        if op_type == 'SLASH':
            self._check_number_operands(node.operator, left, right)
            if float(right) == 0.0:
                raise RuntimeError(f"[{node.operator.line}] Error: Division by zero.")
            return float(left) / float(right)
        if op_type == 'STAR':
            self._check_number_operands(node.operator, left, right)
            return float(left) * float(right)
        if op_type == 'PLUS':
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(f"[{node.operator.line}] Operands must be two numbers or two strings.")
        if op_type == 'GREATER':
            self._check_number_operands(node.operator, left, right)
            return left > right
        if op_type == 'GREATER_EQUAL':
            self._check_number_operands(node.operator, left, right)
            return left >= right
        if op_type == 'LESS':
            self._check_number_operands(node.operator, left, right)
            return left < right
        if op_type == 'LESS_EQUAL':
            self._check_number_operands(node.operator, left, right)
            return left <= right
        if op_type == 'BANG_EQUAL': return not self._is_equal(left, right)
        if op_type == 'EQUAL_EQUAL': return self._is_equal(left, right)
        return None 

    def _is_truthy(self, obj):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def _is_equal(self, a, b):
        if a is None and b is None: return True
        if a is None: return False
        return a == b

    def _check_number_operand(self, operator, operand):
        if isinstance(operand, float): return
        raise RuntimeError(f"[{operator.line}] Operand must be a number.")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(f"[{operator.line}] Operands must be numbers.")

