from app.environment import Environment
from app.lox_callable import LoxCallable, ReturnValue
from app.parser.ast import Function as FunctionNode

# Forward declaration to avoid circular import
class LoxInstance: pass

class LoxFunction(LoxCallable):
    def __init__(self, declaration: FunctionNode, closure: Environment, is_initializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter, arguments: list):
        # Create a new environment for the function's body.
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as return_value:
            # If this is an init method, return 'this' even if there's an explicit return.
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        # If this is an init method, implicitly return 'this'.
        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    def bind(self, instance: LoxInstance):
        """
        Creates a new environment where 'this' is bound to the instance.
        Returns a new LoxFunction with this new environment as its closure.
        """
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def __repr__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

