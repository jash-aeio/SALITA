"""
==========================================================================
  SALITA Compiler - Syntax Analyzer (Parser)
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  The parser reads the token stream produced by the lexer and validates
  the program structure according to SALITA's context-free grammar.
  It builds an Abstract Syntax Tree (AST) if parsing succeeds.

  Grammar (EBNF):
  ───────────────
    program        → statement_list
    statement_list → statement statement_list | statement
    statement      → declaration | input_stmt | output_stmt | assignment
    declaration    → 'var' IDENTIFIER ';'
    input_stmt     → 'input' IDENTIFIER ';'
    output_stmt    → 'output' IDENTIFIER ';'
    assignment     → IDENTIFIER '=' expression ';'
    expression     → term (( '+' | '-' ) term)*
    term           → factor (( '*' | '/' ) factor)*
    factor         → NUMBER | IDENTIFIER | '(' expression ')'
==========================================================================
"""

from token_types import (
    T_VAR, T_INPUT, T_OUTPUT,
    T_ID, T_NUMBER,
    T_PLUS, T_MINUS, T_MUL, T_DIV, T_ASSIGN,
    T_SEMI, T_LPAREN, T_RPAREN, T_EOF,
)
from lexer import Lexer


# ==============================================================================
# Custom Exception for Syntax Errors
# ==============================================================================
class ParserError(Exception):
    """Raised when the parser encounters a structural / grammatical error."""
    pass


# ==============================================================================
# AST Node Definitions
# ==============================================================================
class AST:
    """Base class for all Abstract Syntax Tree nodes."""
    pass


class Program(AST):
    """Root node containing a list of statements."""
    def __init__(self, statements: list):
        self.statements = statements


class VarDecl(AST):
    """Variable declaration: var <name> ;"""
    def __init__(self, var_node):
        self.var_node = var_node  # Var node holding the identifier


class InputStmt(AST):
    """Input statement: input <name> ;"""
    def __init__(self, var_node):
        self.var_node = var_node


class OutputStmt(AST):
    """Output statement: output <name> ;"""
    def __init__(self, var_node):
        self.var_node = var_node


class Assignment(AST):
    """Assignment: <name> = <expression> ;"""
    def __init__(self, var_node, op_token, expr):
        self.var_node = var_node   # Left-hand side (Var node)
        self.op_token = op_token   # The '=' token
        self.expr = expr           # Right-hand side (expression AST)


class BinOp(AST):
    """Binary operation node: left OP right"""
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right


class Num(AST):
    """Integer literal node."""
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Var(AST):
    """Variable reference node."""
    def __init__(self, token):
        self.token = token
        self.value = token.value   # The variable name string


# ==============================================================================
# Parser Class
# ==============================================================================
class Parser:
    """
    Recursive-descent parser for the SALITA language.

    Builds an AST from the token stream produced by the Lexer. If the
    source code does not conform to the grammar, a ParserError is raised
    with a descriptive message including the offending line number.

    Usage:
        parser = Parser(Lexer(source_code))
        tree   = parser.parse()  # returns a Program AST node
    """

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    # --------------------------------------------------------------------------
    # Helper Methods
    # --------------------------------------------------------------------------
    def error(self, message: str):
        """Raise a ParserError with the current line number."""
        raise ParserError(
            f"Syntax Error (Line {self.current_token.line}): {message}"
        )

    def eat(self, token_type: str):
        """
        Consume the current token if it matches `token_type`; otherwise
        raise a syntax error.
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(
                f"Expected {token_type}, but got "
                f"{self.current_token.type} ('{self.current_token.value}')."
            )


    # --------------------------------------------------------------------------
    # Grammar Rules (each method corresponds to one grammar production)
    # --------------------------------------------------------------------------
    def parse(self) -> Program:
        """Entry point — parse the entire program."""
        node = self.program()
        if self.current_token.type != T_EOF:
            self.error("Unexpected token after end of program.")
        return node

    def program(self) -> Program:
        """program → statement_list"""
        statements = self.statement_list()
        return Program(statements)

    def statement_list(self) -> list:
        """statement_list → statement (statement)*"""
        stmts = []
        while self.current_token.type != T_EOF:
            stmts.append(self.statement())
        return stmts

    def statement(self) -> AST:
        """
        statement → declaration | input_stmt | output_stmt | assignment
        """
        tok = self.current_token

        if tok.type == T_VAR:
            return self.declaration()
        elif tok.type == T_INPUT:
            return self.input_stmt()
        elif tok.type == T_OUTPUT:
            return self.output_stmt()
        elif tok.type == T_ID:
            return self.assignment()
        else:
            self.error(
                f"Expected a statement (var, input, output, or assignment), "
                f"but got '{tok.value}'."
            )

    def declaration(self) -> VarDecl:
        """declaration → 'var' IDENTIFIER ';'"""
        self.eat(T_VAR)
        var_token = self.current_token
        self.eat(T_ID)
        var_node = Var(var_token)
        self.eat(T_SEMI)
        return VarDecl(var_node)

    def input_stmt(self) -> InputStmt:
        """input_stmt → 'input' IDENTIFIER ';'"""
        self.eat(T_INPUT)
        var_token = self.current_token
        self.eat(T_ID)
        var_node = Var(var_token)
        self.eat(T_SEMI)
        return InputStmt(var_node)

    def output_stmt(self) -> OutputStmt:
        """output_stmt → 'output' IDENTIFIER ';'"""
        self.eat(T_OUTPUT)
        var_token = self.current_token
        self.eat(T_ID)
        var_node = Var(var_token)
        self.eat(T_SEMI)
        return OutputStmt(var_node)

    def assignment(self) -> Assignment:
        """assignment → IDENTIFIER '=' expression ';'"""
        var_token = self.current_token
        self.eat(T_ID)
        var_node = Var(var_token)
        op_token = self.current_token
        self.eat(T_ASSIGN)
        expr = self.expression()
        self.eat(T_SEMI)
        return Assignment(var_node, op_token, expr)

    # --------------------------------------------------------------------------
    # Expression Parsing (operator precedence via recursive descent)
    # --------------------------------------------------------------------------
    def expression(self) -> AST:
        """expression → term (( '+' | '-' ) term)*"""
        node = self.term()
        while self.current_token.type in (T_PLUS, T_MINUS):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(left=node, op_token=op, right=self.term())
        return node

    def term(self) -> AST:
        """term → factor (( '*' | '/' ) factor)*"""
        node = self.factor()
        while self.current_token.type in (T_MUL, T_DIV):
            op = self.current_token
            self.eat(op.type)
            node = BinOp(left=node, op_token=op, right=self.factor())
        return node

    def factor(self) -> AST:
        """factor → NUMBER | IDENTIFIER | '(' expression ')'"""
        tok = self.current_token
        if tok.type == T_NUMBER:
            self.eat(T_NUMBER)
            return Num(tok)
        elif tok.type == T_ID:
            self.eat(T_ID)
            return Var(tok)
        elif tok.type == T_LPAREN:
            self.eat(T_LPAREN)
            node = self.expression()
            self.eat(T_RPAREN)
            return node
        else:
            self.error(
                f"Expected a number, identifier, or '(', but got "
                f"'{tok.value}'."
            )


# ==============================================================================
# Utility: Pretty-print the AST (for debugging / GUI display)
# ==============================================================================
def ast_to_string(node, indent: int = 0) -> str:
    """Return a human-readable string representation of the AST."""
    prefix = "  " * indent

    if isinstance(node, Program):
        lines = [f"{prefix}Program"]
        for stmt in node.statements:
            lines.append(ast_to_string(stmt, indent + 1))
        return "\n".join(lines)

    elif isinstance(node, VarDecl):
        return f"{prefix}VarDecl: {node.var_node.value}"

    elif isinstance(node, InputStmt):
        return f"{prefix}InputStmt: {node.var_node.value}"

    elif isinstance(node, OutputStmt):
        return f"{prefix}OutputStmt: {node.var_node.value}"

    elif isinstance(node, Assignment):
        lines = [f"{prefix}Assignment: {node.var_node.value} ="]
        lines.append(ast_to_string(node.expr, indent + 1))
        return "\n".join(lines)

    elif isinstance(node, BinOp):
        lines = [f"{prefix}BinOp: {node.op_token.value}"]
        lines.append(ast_to_string(node.left, indent + 1))
        lines.append(ast_to_string(node.right, indent + 1))
        return "\n".join(lines)

    elif isinstance(node, Num):
        return f"{prefix}Num: {node.value}"

    elif isinstance(node, Var):
        return f"{prefix}Var: {node.value}"

    else:
        return f"{prefix}Unknown node: {type(node).__name__}"
