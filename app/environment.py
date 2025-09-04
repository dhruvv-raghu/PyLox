class Environment:
    def __init__(self, enclosing= None):
        self.values= {}
        
        self.enclosing= enclosing

    def define(self, name:str, value):
        self.values[name] = value

    def get(self, name_token):
        name = name_token.lexeme
        if name in self.values:
            return self.values[name]
            
        if self.enclosing is not None:
            return self.enclosing.get(name_token)
        
        raise RuntimeError(f"[{name_token.line}] Undefined variable '{name}'.")
    
    def assign(self, name_token, value):
        name= name_token.lexeme
        if name in self.values:
            self.values[name]= value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return 
        
        raise RuntimeError(f"[{name_token.line}] Undefined variable '{name}'.")
        
