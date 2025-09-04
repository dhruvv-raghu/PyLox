from abc import ABC, abstractmethod
from typing import List, Any

class ReturnValue(Exception):
    """
    A custom exception used to unwind the stack for 'return' statements.
    It's not a real error, but a control flow mechanism that carries the
    return value back up to the initial call site.
    """
    def __init__(self, value: Any):
        super().__init__()
        self.value = value

class LoxCallable(ABC):
    """
    An interface for all objects that can be called like functions.
    This includes user-defined functions, native functions, and classes.
    By having them all implement this interface, the evaluator's `visit_call`
    method can treat them all polymorphically.
    """
    @abstractmethod
    def arity(self) -> int:
        """Returns the number of arguments the callable expects."""
        pass

    @abstractmethod
    def call(self, interpreter, arguments: List[Any]):
        """Executes the callable's logic."""
        pass

