from app.parser.ast import Expr, Stmt, Print, Expression, Literal, Grouping, Unary, Binary, Assign, Variable, Var, Block, If, Logical, While, Function, Return, Call
from app.evaluation.visitors import Visitor, StmtVisitor
from app.stringify import stringify
from app.environment import Environment
from app.lox_callable import LoxCallable
from app.lox_function import LoxFunction, ReturnValue
import time

class NativeClock(LoxCallable):
    def arity(self) -> int:
        return 0
    # --- FIX: Renamed 'evaluator' to 'interpreter' to match the base class contract ---
    def call(self, interpreter, arguments: list):
        return time.time()
    def __str__(self):
        return "<native fn>"

class Evaluator(Visitor, StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {} # Stores resolution data
        self.globals.define("clock", NativeClock())

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth

    def _look_up_variable(self, name, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def evaluate_statements(self, statements: list[Stmt]):
        last_value = None
        try:
            for statement in statements:
                result = self.execute(statement)
                if isinstance(statement, Expression):
                    last_value = result
        except ReturnValue as ret:
            last_value = ret.value
        except RuntimeError as e:
            raise e
        return last_value

    def evaluate(self, expr:Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        return stmt.accept(self)
        
    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_block(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_if(self, stmt: If):
        if self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_while(self, stmt: While):
        while self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_logical(self, node: Logical):
        left = self.evaluate(node.left)
        if node.operator.type == 'OR':
            if self._is_truthy(left): return left
        else: # AND
            if not self._is_truthy(left): return left
        return self.evaluate(node.right)

    def visit_var(self, stmt:Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def visit_expression(self, stmt: Expression):
        return self.evaluate(stmt.expression)
        
    def visit_function(self, stmt: Function):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_return(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnValue(value)

    def visit_assign(self, node: Assign):
        value = self.evaluate(node.value)
        distance = self.locals.get(node)
        if distance is not None:
            self.environment.assign_at(distance, node.name, value)
        else:
            self.globals.assign(node.name, value)
        return value

    def visit_variable(self, node: Variable):
        return self._look_up_variable(node.name, node)
        
    def visit_literal(self, node: Literal):
        return node.value

    def visit_grouping(self, node: Grouping):
        return self.evaluate(node.expression)

    def visit_unary(self, node: Unary):
        right = self.evaluate(node.right)
        op_type = node.operator.type
        if op_type == 'MINUS':
            self._check_number_operand(node.operator, right)
            return -float(right)
        if op_type == 'BANG':
            return not self._is_truthy(right)
        return None

    def visit_call(self, node: Call):
        callee = self.evaluate(node.callee)
        arguments = [self.evaluate(arg) for arg in node.arguments]

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(f"[line {node.paren.line}] Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeError(f"[line {node.paren.line}] Expected {callee.arity()} arguments but got {len(arguments)}.")
            
        return callee.call(self, arguments)

    def visit_binary(self, node: Binary):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op_type = node.operator.type

        if op_type == 'MINUS':
            self._check_number_operands(node.operator, left, right)
            return float(left) - float(right)
        if op_type == 'SLASH':
            self._check_number_operands(node.operator, left, right)
            if float(right) == 0.0:
                raise RuntimeError(f"Error: Division by zero.\n [line {node.operator.line}]")
            return float(left) / float(right)
        if op_type == 'STAR':
            self._check_number_operands(node.operator, left, right)
            return float(left) * float(right)
        if op_type == 'PLUS':
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(f" Operands must be two numbers or two strings.\n [line {node.operator.line}]")
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
        raise RuntimeError(f"[line {operator.line}] Error: Operand must be a number.")

    def _check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float): return
        raise RuntimeError(f"[line {operator.line}] Error: Operands must be numbers.")

