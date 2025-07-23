from app.evaluation.visitors import Visitor
from app.evaluation.visitors import StmtVisitor

class Expr:
    def accept(self, visitor: Visitor):
        raise NotImplementedError("Subclasses must implement this method")
    pass

class Stmt:
    def accept(self, visitor: StmtVisitor):
        raise NotImplementedError("Subclasses must implement this method")
    pass

class Binary(Expr):
    """Represents a binary operation like +, -, *, /."""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme} {self.left} {self.right})"
    
    def accept(self, visitor: Visitor):
        return visitor.visit_binary(self)

class Unary(Expr):
    """Represents a unary operation like -5 or !true."""

    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme} {self.right})"

    def accept(self, visitor: Visitor):
        return visitor.visit_unary(self)
    
class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print(self)
    
class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression(self)
        
    
class Literal(Expr):
    """Represents a literal value like a number, string, True, False, or Nil."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if self.value is None:
            return "nil"
        if isinstance(self.value, bool):
            return str(self.value).lower()

        if isinstance(self.value, float):
            if self.value.is_integer():
                return f"{self.value:.1f}"
        return str(self.value)


    def accept(self, visitor: Visitor):
        return visitor.visit_literal(self)
    
class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"(group {self.expression})"

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping(self)