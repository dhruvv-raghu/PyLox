class ParenthesesScanner:
    def __init__(self, file_contents):
        self.file_contents= file_contents
        self.pos= 0
        self.current_char = self.file_contents[self.pos] if self.file_contents else None

        def move_next(self):
            self.pos += 1
            if self.pos < len(self.file_contents):
                self.current_char = self.file_contents[self.pos]
            else:
                self.current_char = None
                raise EOFError("End of file reached")
            
        def paren