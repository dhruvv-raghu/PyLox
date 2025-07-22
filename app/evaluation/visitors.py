from abc import ABC, abstractmethod

class Visitors(ABC):

   @abstractmethod
   def visit_binary(self, node):
       """Visit a node in the AST."""
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
