from abc import ABC, abstractmethod

class Visitor(ABC):

   @abstractmethod
   def visit_binary(self, node):
       pass
   
   @abstractmethod
   def visit_unary(self, node):
         """Visit a node in the AST."""
         pass
   
   @abstractmethod
   def visit_literal(self, node):
        """Visit a node in the AST."""
        pass
   
   @abstractmethod
   def visit_grouping(self, node):
        """Visit a node in the AST."""
        pass
   
class StmtVisitor(ABC):
     @abstractmethod
     def visit_expression(self, stmt):
           """Visit an expression statement."""
           pass
     
     @abstractmethod
     def visit_print(self, stmt):
           """Visit a print statement."""
           pass
     
