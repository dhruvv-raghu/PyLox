from app.evaluation.visitors import Visitor, StmtVisitor
from typing import List, Optional

# --- Base Classes ---
class Expr:
    def accept(self, visitor: Visitor):
        raise NotImplementedError("Subclasses must implement this method")

class Stmt:
    def accept(self, visitor: StmtVisitor):
        raise NotImplementedError("Subclasses must implement this method")
class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
                self.statements = statements
        
    def accept(self, visitor: StmtVisitor):
                return visitor.visit_block(self)
                
class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: 'StmtVisitor'):
        return visitor.visit_if(self)

# --- Statement Node Classes ---

class Var(Stmt):
    def __init__(self, name, initializer=None):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var(self)
    
    

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

    def __repr__(self):
        """Delegates the string representation to the expression it holds."""
        return str(self.expression)

# --- Expression Node Classes ---

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_assign(self)
    
class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor: Visitor):
        return visitor.visit_variable(self)
    
class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme} {self.left} {self.right})"
    
    def accept(self, visitor: Visitor):
        return visitor.visit_binary(self)

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme} {self.right})"

    def accept(self, visitor: Visitor):
        return visitor.visit_unary(self)
    
class Literal(Expr):
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
