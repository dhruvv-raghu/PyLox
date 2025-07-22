from app.parser.ast import Expr, Binary, Unary, Literal, Grouping
from app.evaluation.visitors import Visitors

class Evaluator(Visitors):
    def evaluate(self, expr: Expr):
        return expr.accept(self)
    
    def visit_literal(self, node: Literal):
        if node.value is None:
            return 'nil'
        return node.value
    
    def visit_grouping(self, node: Grouping):
        return self.evaluate(node.expression)
    
    def visit_binary(self, node: Binary):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        operator = node.operator.type 

        if operator == "PLUS":
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}") 
        
        if operator == "MINUS":
            if isinstance(left, float) and isinstance(right, float):
                return float(left) - float(right)
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}")
        
        if operator == "STAR":
            if isinstance(left, float) and isinstance(right, float):
                return float(left) * float(right)
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}")
        
        if operator == "SLASH":
            if isinstance(left, float) and isinstance(right, float):
                if right == 0:
                    raise RuntimeError("Division by zero")
                return float(left) / float(right)
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}")
        
        if operator == "GREATER":
            if isinstance(left, float) and isinstance(right, float):
                return left > right
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}")
        
        if operator == "GREATER_EQUAL":
            if isinstance(left, float) and isinstance(right, float):
                return left >= right
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}")
        
        if operator == "LESS":
            if isinstance(left, float) and isinstance(right, float):
                return left < right
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}")
        
        if operator == "LESS_EQUAL":
            if isinstance(left, float) and isinstance(right, float):
                return left <= right
            raise RuntimeError(f"Invalid operands for {operator}: {type(left)}, {type(right)}")
        
        if operator == "EQUAL_EQUAL":
            if isinstance(left, float) and isinstance(right, float):
                return left == right
            if isinstance(left, str) and isinstance(right, str):
                return left == right
            if isinstance(left, bool) and isinstance(right, bool):
                return left == right
            if left is None and right is None:
                return True
            return False
        
        if operator == "BANG_EQUAL":
            if isinstance(left, float) and isinstance(right, float):
                return left != right
            if isinstance(left, str) and isinstance(right, str):
                return left != right
            if isinstance(left, bool) and isinstance(right, bool):
                return left != right
            if left is None and right is None:
                return False
            return True
        

    def visit_unary(self, node: Unary):
        right = self.evaluate(node.right)
        operator = node.operator.type

        if operator == "MINUS":
            if isinstance(right, float):
                return -right
            raise RuntimeError(f"Invalid operand for {operator}: {type(right)}")
        
        if operator == "BANG":
            return self.is_truthy(right)

        raise RuntimeError(f"Unknown unary operator: {operator}")    

    def is_truthy(self, obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True