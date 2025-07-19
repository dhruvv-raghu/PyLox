class ParenthesesScanner:
    def __init__(self, file_contents):
        self.file_contents = file_contents
        self.current_char = None
        self.pos = -1
        self.check= {'(': 'LEFT_PAREN', ')': 'RIGHT_PAREN', '{': 'LEFT_BRACE', '}': 'RIGHT_BRACE',
                     '.': 'DOT', ',': 'COMMA', ';': 'SEMICOLON', '/': 'SLASH', '*': 'STAR',
                     '+': 'PLUS', '-': 'MINUS'}

    def move_next(self):
        self.pos += 1
        if self.pos < len(self.file_contents):
            self.current_char = self.file_contents[self.pos]
        else:
            self.current_char = None
            raise EOFError("End of file reached")
        return self.current_char

    def parentheses(self):
        if self.pos+1 >= len(self.file_contents):
            raise EOFError("End of file reached")
            return
        self.move_next()  # Let it raise EOFError naturally if needed
        
        if self.current_char in self.check:
            token_type = self.check[self.current_char]
            print(f"{token_type} {self.current_char} null")
        else:
            raise ValueError(f"Unexpected character: {self.current_char}")
        