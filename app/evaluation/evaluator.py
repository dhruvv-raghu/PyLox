from app.parser.ast import Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Assign, Variable, Var
from app.evaluation.visitors import Visitor, StmtVisitor
from app.stringify import stringify
from app.environment import Environment

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
           
    def evaluate(self, expr:Expr):
        """Evaluates a single expression by accepting a visitor."""
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        """Executes a single statement by accepting a visitor."""
        # Return the result from the visitor method to pass values up.
        return stmt.accept(self)

    # --- FIX: Renamed methods to match the Visitor base class conventions ---

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
    
    def visit_assign(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value
    
    def visit_variable(self, node):
        return self.environment.get(node.name)
       
    def visit_literal(self, expr: Literal):
        return expr.value

    def visit_grouping(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_unary(self, expr: Unary):
        right = self.evaluate(expr.right)
        op_type = expr.operator.type

        if op_type == 'MINUS':
            self._check_number_operand(expr.operator, right)
            return -float(right)
        if op_type == 'BANG':
            return not self._is_truthy(right)
        
        return None # Should be unreachable

    def visit_binary(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        op_type = expr.operator.type

        if op_type == 'MINUS':
            self._check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        if op_type == 'SLASH':
            self._check_number_operands(expr.operator, left, right)
            if float(right) == 0.0:
                raise RuntimeError(f"Error: Division by zero.\n [line {expr.operator.line}]")
            return float(left) / float(right)
        if op_type == 'STAR':
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        if op_type == 'PLUS':
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(f" Operands must be two numbers or two strings.\n [line {expr.operator.line}]")

        if op_type == 'GREATER':
            self._check_number_operands(expr.operator, left, right)
            return left > right
        if op_type == 'GREATER_EQUAL':
            self._check_number_operands(expr.operator, left, right)
            return left >= right
        if op_type == 'LESS':
            self._check_number_operands(expr.operator, left, right)
            return left < right
        if op_type == 'LESS_EQUAL':
            self._check_number_operands(expr.operator, left, right)
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
