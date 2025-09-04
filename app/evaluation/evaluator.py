import sys
import time
from app.parser.ast import (
    Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Var,
    Variable, Assign, Block, If, Logical, While, Call, Function, Return,
    Class, Get, Set, This  # <-- Added new AST node imports
)
from app.evaluation.visitors import Visitor, StmtVisitor
from app.environment import Environment
from app.stringify import stringify
from app.lox_callable import LoxCallable, ReturnValue
from app.lox_function import LoxFunction
# --- NEW IMPORTS for runtime class representation ---
from app.lox_class import LoxClass
from app.lox_instance import LoxInstance


class NativeClock(LoxCallable):
    """A native Lox function that returns the current time."""
    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: list) -> float:
        return time.time()

    def __repr__(self):
        return "<native fn>"

class Evaluator(Visitor, StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        # Define native functions in the global scope.
        self.globals.define("clock", NativeClock())

    def evaluate_statements(self, statements: list[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
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

    # --- NEW: visit_class method ---
    def visit_class(self, stmt: Class):
        """Handles a class declaration statement."""
        self.environment.define(stmt.name.lexeme, None)
        methods = {}
        for method in stmt.methods:
            # Check if the method is the class initializer
            is_initializer = method.name.lexeme == "init"
            function = LoxFunction(method, self.environment, is_initializer)
            methods[method.name.lexeme] = function
        
        klass = LoxClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klass)
        return None

    # --- NEW: visit_get method ---
    def visit_get(self, node: Get):
        """Handles property access on an instance."""
        obj = self.evaluate(node.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(node.name)
        raise RuntimeError(f"[line {node.name.line}] Only instances have properties.")

    # --- NEW: visit_set method ---
    def visit_set(self, node: Set):
        """Handles property assignment on an instance."""
        obj = self.evaluate(node.obj)
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(f"[line {node.name.line}] Only instances have fields.")
        
        value = self.evaluate(node.value)
        obj.set(node.name, value)
        return value

    # --- NEW: visit_this method ---
    def visit_this(self, node: This):
        """Handles the 'this' keyword."""
        # The resolver should have already done the hard work.
        # We just look up the variable in the environment.
        return self.environment.get(node.keyword)

    def visit_while(self, stmt: While):
        while self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_call(self, node: Call):
        """Evaluates a function or class instantiation call."""
        callee = self.evaluate(node.callee)

        arguments = []
        for argument in node.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(f"[line {node.paren.line}] Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeError(f"[line {node.paren.line}] Expected {callee.arity()} arguments but got {len(arguments)}.")

        return callee.call(self, arguments)

    def visit_function(self, stmt: Function):
        """Handles a function declaration statement."""
        # For a standard 'fun' declaration, it is NOT an initializer.
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def visit_return(self, stmt: Return):
        """Handles a return statement by raising a special exception."""
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

    def visit_variable(self, node: Variable):
        return self.environment.get(node.name)

    def visit_assign(self, node: Assign):
        value = self.evaluate(node.value)
        self.environment.assign(node.name, value)
        return value

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
                raise RuntimeError(f"[line {node.operator.line}] Error: Division by zero.")
            return float(left) / float(right)
        if op_type == 'STAR':
            self._check_number_operands(node.operator, left, right)
            return float(left) * float(right)
        if op_type == 'PLUS':
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(f"[line {node.operator.line}] Operands must be two numbers or two strings.")
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
        raise RuntimeError(f"[line {operator.line}] Operand must be a number.")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(f"[line {operator.line}] Operands must be numbers.")

