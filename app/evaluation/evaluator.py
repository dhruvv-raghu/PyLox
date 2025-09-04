from app.parser.ast import Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Assign, Variable, Var, Block, If, Logical, While, Call, Function, Return
from app.evaluation.visitors import Visitor, StmtVisitor
from app.stringify import stringify
from app.environment import Environment
from app.lox_callable import LoxCallable
from app.lox_function import LoxFunction, ReturnValue
import time 

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
        self.environment = Environment()

    def evaluate_statements(self, statements: list[Stmt]):
        """
        Evaluates a list of statements.
        Returns the value of the last expression statement, if any.
        """
        last_value = None
        try:
            for statement in statements:
                # Execute the statement and capture its potential return value.
                result = self.execute(statement)
                # If the statement was an expression, store its value.
                if isinstance(statement, Expression):
                    last_value = result
        except RuntimeError as e:
            # Catch runtime errors and re-raise them to be handled by main.
            raise e
        return last_value
        
        # --- NEW: Visitor method for function declarations ---
    def visit_function(self, stmt: Function):
            # Create a LoxFunction object, capturing the current environment as the closure.
            function = LoxFunction(stmt, self.environment)
            # Define the function in the current environment.
            self.environment.define(stmt.name.lexeme, function)
    
        # --- NEW: Visitor method for return statements ---
    def visit_return(self, stmt: Return):
            value = None
            if stmt.value is not None:
                value = self.evaluate(stmt.value)
            # Raise the custom exception to unwind the stack and carry the return value.
            raise ReturnValue(value)
           
    def evaluate(self, expr:Expr):
        """Evaluates a single expression by accepting a visitor."""
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        return stmt.accept(self)

    def visit_block(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))
        
    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_if(self, stmt: If):
        """Executes an if statement."""
        if self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None
        
    def visit_call(self, node: Call):
            """Evaluates a function call expression."""
            callee = self.evaluate(node.callee)
    
            arguments = []
            for argument in node.arguments:
                arguments.append(self.evaluate(argument))
    
            if not isinstance(callee, LoxCallable):
                raise RuntimeError(f"[line {node.paren.line}] Can only call functions and classes.")
    
            if len(arguments) != callee.arity():
                raise RuntimeError(f"[line {node.paren.line}] Expected {callee.arity()} arguments but got {len(arguments)}.")
    
            return callee.call(self, arguments)
        
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
        # Define the variable in the environment.
        self.environment.define(stmt.name.lexeme, value)
        return None
    
    def visit_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))
        # A print statement has no value, so it implicitly returns None.

    def visit_expression(self, stmt: Expression):
        # Evaluate the expression and return its value.
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
