from typing import List, Dict, Any
from app.lox_callable import LoxCallable
from app.lox_function import LoxFunction
from app.lox_instance import LoxInstance

class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: Dict[str, LoxFunction]):
        self.name = name
        self.methods = methods

    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: List[Any]):
        instance = LoxInstance(self)
        return instance

    def __str__(self):
        return self.name
