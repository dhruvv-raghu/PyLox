class Environment:
    def __init__(self):
        self.values= {}

    def define(self, name:str, value):
        self.values[name] = value

    def get(self, name_token):
        name = name_token.lexeme
        if name in self.values:
            return self.values[name]
        
        raise RuntimeError(f"[{name_token.line}] Undefined variable '{name}'.")
    
    def assign(self, name_token, value):
        name= name_token.lexeme
        if name in self.values:
            self.values[name]= value
            return
        
        raise RuntimeError(f"[{name_token.line}] Undefined variable '{name}'.")
        
