from app.parser.ast import Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Assign, Variable, Var, Block, If, Logical, While, Call, Function, Return
from app.evaluation.visitors import Visitor, StmtVisitor
from app.stringify import stringify
from app.environment import Environment
from app.lox_callable import LoxCallable
from app.lox_function import LoxFunction, ReturnValue
import time  # Import the time module for our native function

# --- NEW: A class to represent our native clock() function ---
class ClockNative(LoxCallable):
    """A native Lox function that returns the current time in seconds."""
    def arity(self) -> int:
        # clock() takes 0 arguments.
        return 0

    def call(self, interpreter, arguments):
        # Return the current Unix timestamp.
        return float(time.time())

    def __repr__(self):
        return "<native fn>"

class Evaluator(Visitor, StmtVisitor):
    def __init__(self):
        # The 'globals' environment holds all top-level variables.
        self.globals = Environment()
        self.environment = self.globals
        
        # --- FIX: Define the native clock function in the global scope ---
        self.globals.define("clock", ClockNative())

    def evaluate_statements(self, statements: list[Stmt]):
        last_value = None
        try:
            for statement in statements:
                result = self.execute(statement)
                if isinstance(statement, Expression):
                    last_value = result
        except RuntimeError as e:
            raise e
        return last_value
        
    def evaluate(self, expr:Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        return stmt.accept(self)
        
    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_block(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))
        
    def visit_call(self, expr: Call):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(f"Can only call functions and classes.\n[line {expr.paren.line}]")

        if len(arguments) != callee.arity():
            raise RuntimeError(f"Expected {callee.arity()} arguments but got {len(arguments)}.\n[line {expr.paren.line}]")

        return callee.call(self, arguments)

    def visit_function(self, stmt: Function):
        # Create a LoxFunction, capturing the current environment as its closure.
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_return(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        # Use a custom exception to unwind the stack and return the value.
        raise ReturnValue(value)

    def visit_if(self, stmt: If):
        if self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None
        
    def visit_while(self, stmt: While):
        while self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
    
    def visit_logical(self, node: Logical):
        left = self.evaluate(node.left)
        
        if node.operator.type == 'OR':
            if self._is_truthy(left):
                return left # Short-circuit
        else: # AND
            if not self._is_truthy(left):
                return left # Short-circuit

        return self.evaluate(node.right)

    def visit_var(self, stmt:Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None
    
    def visit_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def visit_expression(self, stmt: Expression):
        return self.evaluate(stmt.expression)
    
    def visit_assign(self, node: Assign):
        value = self.evaluate(node.value)
        self.environment.assign(node.name, value)
        return value
    
    def visit_variable(self, node):
        return self.environment.get(node.name)
        
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
        
        return None # Should be unreachable

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
                raise RuntimeError(f"Error: Division by zero.\n [line {node.operator.line}]")
            return float(left) / float(right)
        if op_type == 'STAR':
            self._check_number_operands(node.operator, left, right)
            return float(left) * float(right)
        if op_type == 'PLUS':
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(f" Operands must be two numbers or two strings.\n [line {node.operator.line}]")

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
        raise RuntimeError(f"[line {operator.line}] Error: Operand must be a number.")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(f"[line {operator.line}] Error: Operands must be numbers.")

