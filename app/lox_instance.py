from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from app.scan_for.tokens import Token

if TYPE_CHECKING:
    from app.lox_class import LoxClass
    from app.lox_function import LoxFunction

class LoxInstance:
    def __init__(self, klass: 'LoxClass'):
        self.klass = klass
        self.fields: Dict[str, Any] = {}

    def get(self, name: Token):
        """
        Looks for a property on this instance.
        First checks fields, then falls back to methods on the class.
        """
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeError(f"[{name.line}] Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value

    def __repr__(self) -> str:
        return f"{self.klass.name} instance"

