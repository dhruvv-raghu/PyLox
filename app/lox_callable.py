from typing import List, Any

class LoxCallable:
    """
    An interface for all Lox objects that can be called like functions.
    """
    def arity(self) -> int:
        """Returns the number of arguments the callable expects."""
        raise NotImplementedError

    def call(self, interpreter, arguments: List[Any]) -> Any:
        """Executes the callable's behavior."""
        raise NotImplementedError
