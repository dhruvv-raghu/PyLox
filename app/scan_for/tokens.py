class Token:
    def __init__(self, type_, lexeme, literal, line):
        self.type = type_
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return f"Token(type={self.type}, lexeme='{self.lexeme}', literal={self.literal}, line={self.line})"