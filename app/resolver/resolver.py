from app.parser.ast import Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Assign, Variable, Var, Block, If, Logical, While, Call, Function, Return
from app.evaluation.visitors import Visitor, StmtVisitor
from typing import List, Dict

# The resolver performs a static analysis pass to resolve all variables.
class Resolver(Visitor, StmtVisitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        # A stack of scopes. Each scope is a dictionary mapping variable names to a boolean.
        # The boolean indicates if the variable has been fully defined and is ready for use.
        self.scopes: List[Dict[str, bool]] = []

    def resolve_statements(self, statements: List[Stmt]):
        """Resolves a list of statements."""
        for statement in statements:
            self._resolve(statement)

    def _resolve(self, item: Stmt | Expr):
        """Helper to dispatch to the correct accept method."""
        item.accept(self)

    def _begin_scope(self):
        """Pushes a new scope onto the stack."""
        self.scopes.append({})

    def _end_scope(self):
        """Pops a scope off the stack."""
        self.scopes.pop()

    def _declare(self, name_token):
        """
        Adds a variable to the innermost scope, marking it as "not ready".
        This handles cases like 'var a = a;'.
        """
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name_token.lexeme in scope:
            # Handle error for re-declaring a variable in the same scope.
            # (Error reporting would go here)
            pass
        scope[name_token.lexeme] = False

    def _define(self, name_token):
        """Marks a variable in the innermost scope as fully defined and ready."""
        if not self.scopes:
            return
        self.scopes[-1][name_token.lexeme] = True

    def _resolve_local(self, expr: Expr, name_token):
        """
        Walks up the scope stack to find which scope a variable belongs to,
        then tells the interpreter how many "hops" it is away.
        """
        for i in range(len(self.scopes) - 1, -1, -1):
            if name_token.lexeme in self.scopes[i]:
                # We found the variable. Tell the interpreter its depth.
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
        # If not found in any local scope, assume it's global.

    # --- Visitor Methods for Statements ---

    def visit_block(self, stmt: Block):
        self._begin_scope()
        self.resolve_statements(stmt.statements)
        self._end_scope()
        return None

    def visit_var(self, stmt: Var):
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)
        return None

    def visit_function(self, stmt: Function):
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt)
        return None

    def _resolve_function(self, function_stmt: Function):
        self._begin_scope()
        for param in function_stmt.params:
            self._declare(param)
            self._define(param)
        self.resolve_statements(function_stmt.body)
        self._end_scope()

    def visit_expression(self, stmt: Expression):
        self._resolve(stmt.expression)
        return None

    def visit_if(self, stmt: If):
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)
        return None

    def visit_print(self, stmt: Print):
        self._resolve(stmt.expression)
        return None

    def visit_return(self, stmt: Return):
        if stmt.value is not None:
            self._resolve(stmt.value)
        return None

    def visit_while(self, stmt: While):
        self._resolve(stmt.condition)
        self._resolve(stmt.body)
        return None

    # --- Visitor Methods for Expressions ---

    def visit_variable(self, node: Variable):
        # Check if the variable is being accessed inside its own initializer.
        if self.scopes and self.scopes[-1].get(node.name.lexeme) is False:
            # Handle error for reading a local variable in its own initializer.
            # (Error reporting would go here)
            pass
        self._resolve_local(node, node.name)
        return None

    def visit_assign(self, node: Assign):
        self._resolve(node.value)
        self._resolve_local(node, node.name)
        return None

    def visit_binary(self, node: Binary):
        self._resolve(node.left)
        self._resolve(node.right)
        return None

    def visit_call(self, node: Call):
        self._resolve(node.callee)
        for argument in node.arguments:
            self._resolve(argument)
        return None

    def visit_grouping(self, node: Grouping):
        self._resolve(node.expression)
        return None

    def visit_literal(self, node: Literal):
        return None

    def visit_logical(self, node: Logical):
        self._resolve(node.left)
        self._resolve(node.right)
        return None

    def visit_unary(self, node: Unary):
        self._resolve(node.right)
        return None
