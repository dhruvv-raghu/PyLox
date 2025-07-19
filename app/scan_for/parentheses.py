from app.scan_for.operations import Operations

class ParenthesesScanner:
    def __init__(self, filename):
        self.filename= filename
        try: 
            with open(self.filename, 'r') as file:
                self.file_contents = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.filename} not found.")
        self.current_char = None
        self.pos = -1
        self.check= Operations
        self.move_next()
        self.line_number = 1

    def move_next(self):
        self.pos += 1
        if self.pos < len(self.file_contents):
            self.current_char = self.file_contents[self.pos]
            if self.current_char == '\n':
                self.line_number += 1
        
        else:
            self.current_char = None
            raise EOFError("End of file reached")
        return self.current_char

    def parentheses(self):
        if self.pos+1 >= len(self.file_contents):
            raise EOFError("End of file reached")
            return
        self.move_next() 
        
        try:
         if self.current_char in self.check:
            token_type = self.check[self.current_char]
            print(f"{token_type} {self.current_char} null")
         else:
            raise ValueError(f"[line {self.line_number}] Error: Unexpected character: {self.current_char}")
        except ValueError as e:
            raise ValueError(f"[line {self.line_number}] Error: Unexpected character: {self.current_char}")
            