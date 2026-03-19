"""
==========================================================================
  SALITA Compiler - Semantic Analyzer
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  The semantic analyzer walks the AST produced by the parser and performs
  contextual validation that cannot be expressed by the context-free
  grammar alone.

  Checks performed:
    1. Variable declared before use
    2. No duplicate variable declarations
    3. Assignment targets must refer to declared variables
    4. Expressions must contain only numeric values and declared variables
==========================================================================
"""

from parser import (
    AST, Program, VarDecl, InputStmt, OutputStmt,
    Assignment, BinOp, Num, Var,
)
from symbol_table import SymbolTable


# ==============================================================================
# Custom Exception for Semantic Errors
# ==============================================================================
class SemanticError(Exception):
    """Raised when the semantic analyzer detects a contextual error."""
    pass


# ==============================================================================
# AST Visitor Base Class (Visitor Design Pattern)
# ==============================================================================
class NodeVisitor:
    """
    Generic AST visitor that dispatches to `visit_<NodeClass>` methods.
    Subclasses override the specific visit methods they care about.
    """

    def visit(self, node: AST):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: AST):
        raise Exception(
            f"No visit_{type(node).__name__} method defined in "
            f"{type(self).__name__}."
        )


# ==============================================================================
# Semantic Analyzer Class
# ==============================================================================
class SemanticAnalyzer(NodeVisitor):
    """
    Walks the AST and checks semantic rules.

    After a successful analysis, the `symbol_table` attribute contains all
    declared variables (ready for use by the interpreter).

    Usage:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast_tree)        # raises SemanticError on failure
        symbol_table = analyzer.symbol_table
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: list[str] = []      # Collect all errors before raising

    def analyze(self, tree: Program):
        """
        Run semantic analysis on the AST. Raises SemanticError if any
        issues are found.
        """
        self.errors = []
        self.symbol_table.reset()
        self.visit(tree)

        if self.errors:
            raise SemanticError("\n".join(self.errors))

    # --------------------------------------------------------------------------
    # Visitor Methods
    # --------------------------------------------------------------------------
    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDecl(self, node: VarDecl):
        var_name = node.var_node.value
        line = node.var_node.token.line
        if not self.symbol_table.declare(var_name):
            self.errors.append(
                f"Semantic Error (Line {line}): "
                f"Variable '{var_name}' is already declared."
            )

    def visit_InputStmt(self, node: InputStmt):
        var_name = node.var_node.value
        line = node.var_node.token.line
        if not self.symbol_table.is_declared(var_name):
            self.errors.append(
                f"Semantic Error (Line {line}): "
                f"Variable '{var_name}' used in 'kuha' but not declared."
            )

    def visit_OutputStmt(self, node: OutputStmt):
        var_name = node.var_node.value
        line = node.var_node.token.line
        if not self.symbol_table.is_declared(var_name):
            self.errors.append(
                f"Semantic Error (Line {line}): "
                f"Variable '{var_name}' used in 'ipakita' but not declared."
            )

    def visit_Assignment(self, node: Assignment):
        var_name = node.var_node.value
        line = node.var_node.token.line
        if not self.symbol_table.is_declared(var_name):
            self.errors.append(
                f"Semantic Error (Line {line}): "
                f"Variable '{var_name}' used in 'lagay' but not declared."
            )
        # Check right-hand side expression
        self.visit(node.expr)

    def visit_BinOp(self, node: BinOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Num(self, node: Num):
        # Integer literals are always valid — nothing to check.
        pass

    def visit_Var(self, node: Var):
        var_name = node.value
        line = node.token.line
        if not self.symbol_table.is_declared(var_name):
            self.errors.append(
                f"Semantic Error (Line {line}): "
                f"Variable '{var_name}' not declared before use."
            )
