"""
==========================================================================
  SALITA Compiler - Token Type Definitions
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  This module defines all token types recognized by the SALITA lexer.
  Tokens are the smallest meaningful units produced by lexical analysis.
==========================================================================
"""

# ==============================================================================
# KEYWORD TOKENS
# ==============================================================================
KEYWORD_VAR    = 'KEYWORD'        # var    -> variable declaration
KEYWORD_INPUT  = 'KEYWORD'        # input  -> input statement
KEYWORD_OUTPUT = 'KEYWORD'        # output -> output statement

# ==============================================================================
# LITERAL AND IDENTIFIER TOKENS
# ==============================================================================
IDENTIFIER = 'IDENTIFIER'         # Variable names (e.g., x, total, my_var1)
NUMBER     = 'NUMBER'             # Integer literals (e.g., 42, 100)

# ==============================================================================
# OPERATOR TOKENS
# ==============================================================================
OPERATOR_PLUS   = 'OPERATOR'      # +  (addition)
OPERATOR_MINUS  = 'OPERATOR'      # -  (subtraction)
OPERATOR_MUL    = 'OPERATOR'      # *  (multiplication)
OPERATOR_DIV    = 'OPERATOR'      # /  (division)
OPERATOR_ASSIGN = 'OPERATOR'      # =  (assignment)

# ==============================================================================
# DELIMITER TOKENS
# ==============================================================================
SEMICOLON   = 'SEMICOLON'        # ;  (statement terminator)
PARENTHESIS = 'PARENTHESIS'      # ( and ) (grouping / precedence)

# ==============================================================================
# SPECIAL TOKENS
# ==============================================================================
COMMENT = 'COMMENT'              # /* ... */ (block comments)
EOF     = 'EOF'                  # End of file / end of input

# ==============================================================================
# INTERNAL TYPE CONSTANTS  (used by lexer/parser logic for precise matching)
# ==============================================================================
# These are the "precise" internal types. The display type above is used for
# the token table shown to the user.
T_VAR      = 'VAR'
T_INPUT    = 'INPUT'
T_OUTPUT   = 'OUTPUT'
T_ID       = 'IDENTIFIER'
T_NUMBER   = 'NUMBER'
T_PLUS     = 'PLUS'
T_MINUS    = 'MINUS'
T_MUL      = 'MUL'
T_DIV      = 'DIV'
T_ASSIGN   = 'ASSIGN'
T_SEMI     = 'SEMICOLON'
T_LPAREN   = 'LPAREN'
T_RPAREN   = 'RPAREN'
T_EOF      = 'EOF'

# ==============================================================================
# KEYWORD MAP  (keyword string -> internal token type)
# ==============================================================================
KEYWORDS = {
    'var':    T_VAR,
    'input':  T_INPUT,
    'output': T_OUTPUT,
}

# ==============================================================================
# DISPLAY TYPE MAP (internal type -> user-facing display type for token table)
# ==============================================================================
DISPLAY_TYPE = {
    T_VAR:      'KEYWORD',
    T_INPUT:    'KEYWORD',
    T_OUTPUT:   'KEYWORD',
    T_ID:       'IDENTIFIER',
    T_NUMBER:   'NUMBER',
    T_PLUS:     'OPERATOR',
    T_MINUS:    'OPERATOR',
    T_MUL:      'OPERATOR',
    T_DIV:      'OPERATOR',
    T_ASSIGN:   'OPERATOR',
    T_SEMI:     'SEMICOLON',
    T_LPAREN:   'PARENTHESIS',
    T_RPAREN:   'PARENTHESIS',
    T_EOF:      'EOF',
}


class Token:
    """
    Represents a single token produced by the lexer.

    Attributes:
        type  (str): Internal token type (e.g., T_BARYABOL, T_ID, T_PLUS).
        value (any): The actual value from source code (keyword string, int, etc.).
        line  (int): Line number in the source code where this token was found.
    """

    def __init__(self, type: str, value, line: int):
        self.type = type
        self.value = value
        self.line = line

    @property
    def display_type(self) -> str:
        """Return the user-facing display type for the token table."""
        return DISPLAY_TYPE.get(self.type, self.type)

    def __repr__(self) -> str:
        return f"[{self.display_type}:{self.value}]"

    def __str__(self) -> str:
        return self.__repr__()
