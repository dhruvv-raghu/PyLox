class ParenthesesScanner:
    def __init__(self, file_contents):
        self.file_contents= file_contents
        self.pos= 0
        

    def move_next(self):
            self.pos += 1
            if self.pos < len(self.file_contents):
                self.current_char = self.file_contents[self.pos]
            else:
                self.current_char = None
                raise EOFError("End of file reached")
            
            return self.current_char
            
    def parentheses(self):
        move_next = self.move_next
        
        if move_next == '(':
            self.move_next()
            print("LPAREN {self.current_char} null")
        elif self.current_char == ')':
            self.move_next()
            print("RPAREN {self.current_char} null")
        elif self.current_char is None:
            print("EOF null")
            return EOFError("End of file reached")
        else:
            raise ValueError(f"Unexpected character: {self.current_char}")