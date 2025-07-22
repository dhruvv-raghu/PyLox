class Expr:
    pass 

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if self.value == None:
            return 'nil'
        if isinstance(self.value, bool):
            return str(self.value).lower()
        if isinstance(self.value, float):
            if isinstance(self.value, int):
                return f"{self.value:.1f}"
        return str(self.value)
    
class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"({self.expression})"

class Unary(Expr):
    def __init__(self, right, operator):
        self.right= right 
        self.operator= operator 

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme} {self.left} {self.right})"
    