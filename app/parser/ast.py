class Expr:
    pass 

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if self.value == 'nil':
            return self.value
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return str(self.value)
    