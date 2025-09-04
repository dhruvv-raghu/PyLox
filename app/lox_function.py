from typing import List, Any
from app.parser.ast import Function
from app.environment import Environment
from app.lox_callable import LoxCallable, ReturnValue

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool):
        """
        Initializes a Lox function.

        Args:
            declaration: The Function AST node from the parser.
            closure: The environment in which the function was declared.
            is_initializer: A boolean flag, true if this is an __init__ method.
        """
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter, arguments: List[Any]):
        # Create a new environment for the function's body.
        # It's enclosed by the function's closure, not the caller's environment.
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            # Execute the function body in the new environment.
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as ret:
            # If this is an initializer, always return 'this', even from an empty return.
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return ret.value
        
        # If this is an initializer, implicitly return 'this' at the end of the method.
        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None # Implicitly return nil if no return statement is hit.

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

