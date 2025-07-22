# This file defines the classes for our Abstract Syntax Tree (AST).

class Expr:
    """Base class for all expression nodes."""
    pass

class Binary(Expr):
    """Represents a binary operation like +, -, *, /."""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme} {self.left} {self.right})"

class Unary(Expr):
    """Represents a unary operation like -5 or !true."""
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme} {self.right})"

class Literal(Expr):
    """Represents a literal value like a number, string, True, False, or Nil."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if self.value is None:
            return "nil"
        if isinstance(self.value, bool):
            return str(self.value).lower()
        # Correctly format floats to show .0 for whole numbers
        if isinstance(self.value, float):
            if self.value.is_integer():
                return f"{self.value:.1f}"
        return str(self.value)

class Grouping(Expr):
    """Represents an expression wrapped in parentheses."""
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        # --- FIX: The string format must be "(group ...)" ---
        return f"(group {self.expression})"
