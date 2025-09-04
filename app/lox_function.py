from app.lox_callable import LoxCallable
from app.environment import Environment
from typing import List, Any

# A custom exception used to unwind the call stack when a 'return' is hit.
class ReturnValue(Exception):
    def __init__(self, value: Any):
        self.value = value

class LoxFunction(LoxCallable):
    """A runtime representation of a user-defined function."""
    def __init__(self, declaration, closure: Environment):
        self.declaration = declaration
        # Capture the environment where the function was declared. This is the closure.
        self.closure = closure

    def arity(self) -> int:
        """Returns the number of parameters the function expects."""
        return len(self.declaration.params)

    def call(self, interpreter, arguments: List[Any]) -> Any:
        """Executes the function."""
        # Create a new environment for the function's scope.
        # It's nested inside the function's closure, allowing access to outer variables.
        environment = Environment(self.closure)
        
        # Bind the arguments passed to the function to its parameters.
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            # Execute the function's body in this new, temporary environment.
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as ret:
            # If a return statement is hit, catch the exception and return its value.
            return ret.value
        
        # If the function body completes without a return statement, implicitly return nil.
        return None

    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"

