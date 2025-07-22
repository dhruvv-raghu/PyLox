from app.parser.ast import Expr, Literal, Grouping, Unary, Binary
from app.evaluation.visitors import Visitor

class Evaluator(Visitor):
    def evaluate(self, expr: Expr):
        return expr.accept(self)

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
                raise Exception(f"[line {expr.operator.line}] Error: Division by zero.")
            return float(left) / float(right)
        if op_type == 'STAR':
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        if op_type == 'PLUS':
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise Exception(f"[line {expr.operator.line}] Error: Operands must be two numbers or two strings.")

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
        raise RuntimeError(f"Operand must be a number. \n [line {operator.line}] ")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise Exception(f"[line {operator.line}] Error: Operands must be numbers.")

