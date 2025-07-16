class ParenthesesScanner:
    def __init__(self, file_contents):
        self.file_contents = file_contents
        self.current_char = None
        self.pos = -1

    def move_next(self):
        self.pos += 1
        if self.pos < len(self.file_contents):
            self.current_char = self.file_contents[self.pos]
        else:
            self.current_char = None
            raise EOFError("End of file reached")
        return self.current_char

    def parentheses(self):
        self.move_next()  # Let it raise EOFError naturally if needed

        if self.current_char == '(':
            print(f"LEFT_PAREN {self.current_char} null")
        elif self.current_char == ')':
            print(f"RIGHT_PAREN {self.current_char} null")
        else:
            raise ValueError(f"Unexpected character: {self.current_char}")
