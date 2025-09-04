from app.scan_for.tokens import Token
from typing import Any, Dict

class Environment:
    def __init__(self, enclosing=None):
        self.values: Dict[str, Any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RuntimeError(f"[{name.line}] Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise RuntimeError(f"[{name.line}] Undefined variable '{name.lexeme}'.")

    # --- NEW HELPER METHOD to safely get an ancestor environment ---
    def ancestor(self, distance: int):
        """Walks up the environment chain to find a specific ancestor."""
        environment = self
        for _ in range(distance):
            # This check is the core of the fix.
            if environment.enclosing is None:
                # This should not happen if the resolver is correct, but it's a safeguard.
                return None 
            environment = environment.enclosing
        return environment

    def get_at(self, distance: int, name: str):
        """Gets a variable from a resolved ancestor environment."""
        # Use the new safe helper method.
        env = self.ancestor(distance)
        if env is not None:
            return env.values.get(name)
        return None # Should be unreachable if resolver works.

    def assign_at(self, distance: int, name: Token, value: Any):
        """Assigns a variable in a resolved ancestor environment."""
        # Use the new safe helper method.
        env = self.ancestor(distance)
        if env is not None:
            env.values[name.lexeme] = value

