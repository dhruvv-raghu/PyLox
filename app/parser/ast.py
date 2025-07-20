class Expr:
    pass 

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if not self.value:
            return "nil"
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return str(self.value)
    