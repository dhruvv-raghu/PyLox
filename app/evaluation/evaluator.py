import sys
import time
from app.parser.ast import (
    Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Var,
    Variable, Assign, Block, If, Logical, While, Call, Function, Return,
    Class, Get, Set, This, Super
)
from app.evaluation.visitors import Visitor, StmtVisitor
from app.environment import Environment
from app.stringify import stringify
from app.lox_callable import LoxCallable, ReturnValue
from app.lox_function import LoxFunction
from app.lox_class import LoxClass
from app.lox_instance import LoxInstance
from typing import Dict, Any

class NativeClock(LoxCallable):
    def arity(self) -> int: return 0
    def call(self, interpreter: Any, arguments: list) -> float: return time.time()
    def __repr__(self): return "<native fn>"

class Evaluator(Visitor, StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals: Dict[Expr, int] = {}
        self.globals.define("clock", NativeClock())

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def evaluate_statements(self, statements: list[Stmt]):
        last_value = None
        try:
            for statement in statements:
                if statement:
                    result = self.execute(statement)
                    if isinstance(statement, Expression):
                        last_value = result
        except RuntimeError as e: raise e
        return last_value

    def execute(self, stmt: Stmt): return stmt.accept(self)
    def evaluate(self, expr: Expr): return expr.accept(self)

    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def _look_up_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    # --- MODIFIED: This method now handles inheritance ---
    def visit_class(self, stmt: Class):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(f"[{stmt.superclass.name.line}] Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            # Create a new environment for the class body that encloses the current scope.
            self.environment = Environment(self.environment)
            # Define 'super' in this new environment.
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            is_initializer = method.name.lexeme == "init"
            # The function will capture the environment where 'super' is defined.
            function = LoxFunction(method, self.environment, is_initializer)
            methods[method.name.lexeme] = function
        
        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        
        if superclass is not None:
            # Pop the environment for the class body.
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)

    # --- NEW: This method handles 'super.method()' calls ---
    def visit_super(self, node: Super):
        distance = self.locals.get(node)
        superclass = self.environment.get_at(distance, "super")
        # 'this' is always in the environment just inside the 'super' environment.
        instance = self.environment.get_at(distance - 1, "this")
        method = superclass.find_method(node.method.lexeme)

        if method is None:
            raise RuntimeError(f"[{node.method.line}] Undefined property '{node.method.lexeme}'.")

        return method.bind(instance)

    def visit_variable(self, node: Variable): return self._look_up_variable(node.name, node)
    def visit_assign(self, node: Assign):
        value = self.evaluate(node.value)
        distance = self.locals.get(node)
        if distance is not None: self.environment.assign_at(distance, node.name, value)
        else: self.globals.assign(node.name, value)
        return value

    def visit_get(self, node: Get):
        obj = self.evaluate(node.obj)
        if isinstance(obj, LoxInstance): return obj.get(node.name)
        raise RuntimeError(f"[{node.name.line}] Only instances have properties.")

    def visit_set(self, node: Set):
        obj = self.evaluate(node.obj)
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(f"[{node.name.line}] Only instances have fields.")
        value = self.evaluate(node.value)
        obj.set(node.name, value)
        return value

    def visit_this(self, node: This): return self._look_up_variable(node.keyword, node)
    def visit_while(self, stmt: While):
        while self._is_truthy(self.evaluate(stmt.condition)): self.execute(stmt.body)

    def visit_call(self, node: Call):
        callee = self.evaluate(node.callee)
        arguments = [self.evaluate(arg) for arg in node.arguments]
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(f"[{node.paren.line}] Can only call functions and classes.")
        if len(arguments) != callee.arity():
            raise RuntimeError(f"[{node.paren.line}] Expected {callee.arity()} arguments but got {len(arguments)}.")
        return callee.call(self, arguments)

    def visit_function(self, stmt: Function):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    def visit_return(self, stmt: Return):
        value = None
        if stmt.value is not None: value = self.evaluate(stmt.value)
        raise ReturnValue(value)

    def visit_logical(self, node: Logical):
        left = self.evaluate(node.left)
        if node.operator.type == 'OR':
            if self._is_truthy(left): return left
        else: # AND
            if not self._is_truthy(left): return left
        return self.evaluate(node.right)

    def visit_var(self, stmt: Var):
        value = None
        if stmt.initializer is not None: value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_block(self, stmt: Block): self.execute_block(stmt.statements, Environment(self.environment))
    def visit_if(self, stmt: If):
        if self._is_truthy(self.evaluate(stmt.condition)): self.execute(stmt.then_branch)
        elif stmt.else_branch is not None: self.execute(stmt.else_branch)
    
    def visit_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def visit_expression(self, stmt: Expression): return self.evaluate(stmt.expression)
    def visit_literal(self, node: Literal): return node.value
    def visit_grouping(self, node: Grouping): return self.evaluate(node.expression)

    def visit_unary(self, node: Unary):
        right = self.evaluate(node.right)
        op_type = node.operator.type
        if op_type == 'MINUS':
            self._check_number_operand(node.operator, right)
            return -float(right)
        if op_type == 'BANG': return not self._is_truthy(right)
        return None

    def visit_binary(self, node: Binary):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op_type = node.operator.type
        if op_type == 'MINUS':
            self._check_number_operands(node.operator, left, right)
            return float(left) - float(right)
        if op_type == 'SLASH':
            self._check_number_operands(node.operator, left, right)
            if float(right) == 0.0: raise RuntimeError(f"[{node.operator.line}] Error: Division by zero.")
            return float(left) / float(right)
        if op_type == 'STAR':
            self._check_number_operands(node.operator, left, right)
            return float(left) * float(right)
        if op_type == 'PLUS':
            if isinstance(left, float) and isinstance(right, float): return left + right
            if isinstance(left, str) and isinstance(right, str): return left + right
            raise RuntimeError(f"[{node.operator.line}] Operands must be two numbers or two strings.")
        if op_type == 'GREATER':
            self._check_number_operands(node.operator, left, right)
            return left > right
        if op_type == 'GREATER_EQUAL':
            self._check_number_operands(node.operator, left, right)
            return left >= right
        if op_type == 'LESS':
            self._check_number_operands(node.operator, left, right)
            return left < right
        if op_type == 'LESS_EQUAL':
            self._check_number_operands(node.operator, left, right)
            return left <= right
        if op_type == 'BANG_EQUAL': return not self._is_equal(left, right)
        if op_type == 'EQUAL_EQUAL': return self._is_equal(left, right)
        return None 

    def _is_truthy(self, obj):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def _is_equal(self, a, b):
        if a is None and b is None: return True
        if a is None: return False
        return a == b

    def _check_number_operand(self, operator, operand):
        if isinstance(operand, float): return
        raise RuntimeError(f"[{operator.line}] Operand must be a number.")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(f"[{operator.line}] Operands must be numbers.")

