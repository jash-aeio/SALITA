"""
==========================================================================
  SALITA Compiler - Interpreter (Execution Engine)
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  The interpreter walks the validated AST and executes the program by:
    - Evaluating arithmetic expressions
    - Storing / retrieving variables in the symbol table
    - Handling user input (kuha)
    - Producing program output (ipakita)

  Because SALITA is embedded in a GUI environment, the interpreter does
  not use Python's built-in input()/print().  Instead, it accepts
  callback functions for I/O so that the GUI can intercept them.
==========================================================================
"""

from parser import (
    Program, VarDecl, InputStmt, OutputStmt,
    Assignment, BinOp, Num, Var,
)
from semantic_analyzer import NodeVisitor
from symbol_table import SymbolTable
from token_types import T_PLUS, T_MINUS, T_MUL, T_DIV


# ==============================================================================
# Custom Exception for Runtime Errors
# ==============================================================================
class RuntimeError(Exception):
    """Raised when a runtime error occurs during interpretation."""
    pass


# ==============================================================================
# Interpreter Class
# ==============================================================================
class Interpreter(NodeVisitor):
    """
    Tree-walking interpreter for the SALITA language.

    Constructor args:
        tree          — The AST root (Program node) from the parser.
        symbol_table  — A pre-populated SymbolTable from semantic analysis.
        input_func    — A callable that takes a prompt string and returns
                        a string (the user's input).  If None, uses
                        Python's built-in input().
        output_func   — A callable that takes a string to display.
                        If None, uses Python's built-in print().
    """

    def __init__(self, tree: Program, symbol_table: SymbolTable,
                 input_func=None, output_func=None):
        self.tree = tree
        self.symbol_table = symbol_table
        self.input_func = input_func or input
        self.output_func = output_func or print
        self.output_lines: list[str] = []  # Captured output for GUI display

    # --------------------------------------------------------------------------
    # Public Entry Point
    # --------------------------------------------------------------------------
    def interpret(self):
        """Execute the entire SALITA program."""
        self.output_lines = []
        self.visit(self.tree)

    # --------------------------------------------------------------------------
    # Visitor Methods
    # --------------------------------------------------------------------------
    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDecl(self, node: VarDecl):
        # Variable already declared in the symbol table during semantic
        # analysis; nothing extra to do at runtime.
        pass

    def visit_InputStmt(self, node: InputStmt):
        """Read an integer from the user via the input callback."""
        var_name = node.var_node.value
        while True:
            try:
                raw = self.input_func(f"Ilagay ang halaga para sa '{var_name}': ")
                if raw is None:
                    # User cancelled the input dialog
                    raise RuntimeError(
                        f"Runtime Error: Input cancelled for variable '{var_name}'."
                    )
                value = int(raw)
                self.symbol_table.set_value(var_name, value)
                break
            except ValueError:
                self.output_func(
                    f"[Error] Hindi wastong numero. Mag-input muli para sa '{var_name}'."
                )

    def visit_OutputStmt(self, node: OutputStmt):
        """Display the value of a variable via the output callback."""
        var_name = node.var_node.value
        value = self.symbol_table.get_value(var_name)
        line = f"{value}"
        self.output_lines.append(line)
        self.output_func(line)

    def visit_Assignment(self, node: Assignment):
        """Evaluate the right-hand expression and store in the symbol table."""
        var_name = node.var_node.value
        value = self.visit(node.expr)
        self.symbol_table.set_value(var_name, value)

    def visit_BinOp(self, node: BinOp) -> int:
        """Evaluate a binary arithmetic operation."""
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)

        op = node.op_token.type

        if op == T_PLUS:
            return left_val + right_val
        elif op == T_MINUS:
            return left_val - right_val
        elif op == T_MUL:
            return left_val * right_val
        elif op == T_DIV:
            if right_val == 0:
                raise RuntimeError(
                    f"Runtime Error (Line {node.op_token.line}): "
                    f"Division by zero."
                )
            return left_val // right_val  # Integer division (all vars are integers)
        else:
            raise RuntimeError(
                f"Runtime Error (Line {node.op_token.line}): "
                f"Unknown operator '{node.op_token.value}'."
            )

    def visit_Num(self, node: Num) -> int:
        """Return the integer value of a number literal."""
        return node.value

    def visit_Var(self, node: Var) -> int:
        """Look up the variable's current value in the symbol table."""
        return self.symbol_table.get_value(node.value)
