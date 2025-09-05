from __future__ import annotations
from typing import Dict, Any
from app.lox_callable import LoxCallable

from app.lox_function import LoxFunction
from app.lox_instance import LoxInstance

class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass: LoxClass | None, methods: Dict[str, 'LoxFunction']):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def arity(self) -> int:
        initializer = self.find_method("init")
        return initializer.arity() if initializer else 0

    def call(self, interpreter: Any, arguments: list) -> Any:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def find_method(self, name: str) -> 'LoxFunction' | None:
        """Looks for a method, traversing the inheritance chain."""
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

    def __repr__(self) -> str:
        return self.name

