from abc import ABC, abstractmethod
from typing import Any

class Visitor(ABC):

   @abstractmethod
   def visit_binary(self, node)-> Any:
       pass
   
   @abstractmethod
   def visit_unary(self, node)-> Any:
         """Visit a node in the AST."""
         pass
   
   @abstractmethod
   def visit_literal(self, node):
        """Visit a node in the AST."""
        pass
   
   @abstractmethod
   def visit_assign(self, node):
        pass
   
   @abstractmethod
   def visit_variable(self, node):
        """Visit a variable node in the AST."""
        pass
   
   @abstractmethod
   def visit_grouping(self, node):
        """Visit a node in the AST."""
        pass
       
   @abstractmethod         
   def visit_logical(self, node):
        """Visit a logical expression node in the AST."""
        pass
   
   @abstractmethod
   def visit_call(self, node):
        """Visit a function call node in the AST."""
        pass
         
   @abstractmethod
   def visit_get(self, node):
        """Visit a property access node in the AST."""
        pass
   
   @abstractmethod
   def visit_set(self, node):   
        """Visit a property assignment node in the AST."""
        pass
        
   @abstractmethod
   def visit_this(self, node):
        """Visit a 'this' keyword node in the AST."""
        pass
        
class StmtVisitor(ABC):
    
     @abstractmethod
     def visit_block(self, stmt):
           """Visit a block statement."""
           pass
           
     @abstractmethod
     def visit_expression(self, stmt):
           """Visit an expression statement."""
           pass
     
     @abstractmethod
     def visit_print(self, stmt):
           """Visit a print statement."""
           pass
     
     @abstractmethod
     def visit_var(self, stmt):
           """Visit a variable declaration statement."""
           pass
           
     @abstractmethod
     def visit_if(self, stmt):
           """Visit an if statement."""
           pass
    
     @abstractmethod
     def visit_while(self, stmt):
           """Visit a while statement."""
           pass
     
     @abstractmethod
     def visit_function(self, stmt):
           """Visit a function declaration statement."""
           pass
           
     @abstractmethod
     def visit_return(self, stmt):
           """Visit a return statement."""
           pass
           
     @abstractmethod
     def visit_class(self, stmt):
           """Visit a class declaration"""
           pass
              
