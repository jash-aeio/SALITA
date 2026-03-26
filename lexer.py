"""
==========================================================================
  SALITA Compiler - Lexical Analyzer (Lexer)
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  The lexer reads raw SALITA source code character-by-character and
  converts it into a stream of tokens. This is the first phase of the
  compiler pipeline.

  Responsibilities:
    - Skip whitespace and comments (/* ... */)
    - Recognize Filipino keywords: baryabol, kuha, ipakita, lagay
    - Recognize identifiers, integer literals, operators, and delimiters
    - Report lexical errors with line numbers
==========================================================================
"""

from token_types import (
    Token, KEYWORDS,
    T_ID, T_NUMBER,
    T_PLUS, T_MINUS, T_MUL, T_DIV, T_ASSIGN,
    T_SEMI, T_LPAREN, T_RPAREN, T_EOF,
    T_VAR, T_INPUT, T_OUTPUT,
)


# ==============================================================================
# Custom Exception for Lexical Errors
# ==============================================================================
class LexerError(Exception):
    """Raised when the lexer encounters an invalid character or unterminated comment."""
    pass


# ==============================================================================
# Lexer Class
# ==============================================================================
class Lexer:
    """
    Lexical Analyzer for the SALITA programming language.

    Usage:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()   # returns a list of Token objects
    """

    def __init__(self, text: str):
        """
        Initialize the lexer with SALITA source code.

        Args:
            text (str): The complete source code string to tokenize.
        """
        self.text = text                            # Full source code
        self.pos = 0                                # Current position in text
        self.current_char = text[0] if text else None  # Current character
        self.line = 1                               # Current line number

    # --------------------------------------------------------------------------
    # Character-Level Helpers
    # --------------------------------------------------------------------------
    def advance(self):
        """Move the cursor one character forward, tracking line numbers."""
        if self.current_char == '\n':
            self.line += 1
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self) -> str | None:
        """Peek at the next character without consuming it."""
        peek_pos = self.pos + 1
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    # --------------------------------------------------------------------------
    # Skip Routines
    # --------------------------------------------------------------------------
    def skip_whitespace(self):
        """Advance past all contiguous whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """
        Skip a block comment delimited by /* and */.
        Raises LexerError if the comment is never closed.
        """
        start_line = self.line
        self.advance()  # skip '/'
        self.advance()  # skip '*'
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == '/':
                self.advance()  # skip '*'
                self.advance()  # skip '/'
                return
            self.advance()
        raise LexerError(
            f"Lexical Error (Line {start_line}): Unterminated comment. "
            f"Expected closing '*/' but reached end of file."
        )

    # --------------------------------------------------------------------------
    # Token Builders
    # --------------------------------------------------------------------------
    def read_number(self) -> Token:
        """Read a contiguous sequence of digits and return a NUMBER token."""
        result = ''
        line = self.line
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token(T_NUMBER, int(result), line)

    def read_identifier_or_keyword(self) -> Token:
        """
        Read an identifier (letters, digits, underscores — cannot start with
        a digit).  If the identifier matches a Filipino keyword, return the
        corresponding keyword token instead.
        """
        result = ''
        line = self.line
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # Check if the identifier is a keyword
        token_type = KEYWORDS.get(result, T_ID)
        return Token(token_type, result, line)

    # --------------------------------------------------------------------------
    # Main Tokenization Methods
    # --------------------------------------------------------------------------
    def get_next_token(self) -> Token:
        """
        Retrieve the next token from the source code. Called repeatedly by the
        parser until an EOF token is returned.
        """
        while self.current_char is not None:
            # ---- Whitespace ----
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # ---- Block Comment ----
            if self.current_char == '/' and self.peek() == '*':
                self.skip_comment()
                continue

            # ---- Number literal ----
            if self.current_char.isdigit():
                return self.read_number()

            # ---- Identifier or Keyword ----
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier_or_keyword()

            # ---- Single-character tokens ----
            char = self.current_char
            line = self.line

            simple_tokens = {
                '+': T_PLUS,
                '-': T_MINUS,
                '*': T_MUL,
                '/': T_DIV,
                '=': T_ASSIGN,
                ';': T_SEMI,
                '(': T_LPAREN,
                ')': T_RPAREN,
            }

            if char in simple_tokens:
                self.advance()
                return Token(simple_tokens[char], char, line)

            # ---- Invalid character ----
            raise LexerError(
                f"Lexical Error (Line {self.line}): "
                f"Invalid character '{self.current_char}'."
            )

        # End of input
        return Token(T_EOF, None, self.line)

    def tokenize(self) -> list:
        """
        Convenience method: tokenize the entire source code and return a
        list of Token objects (excluding EOF).  The list is useful for
        displaying the Token Table in the GUI.
        """
        tokens = []
        self.pos = 0
        self.current_char = self.text[0] if self.text else None
        self.line = 1

        while True:
            token = self.get_next_token()
            if token.type == T_EOF:
                break
            tokens.append(token)

        # Reset state so the lexer can be reused by the parser
        self.pos = 0
        self.current_char = self.text[0] if self.text else None
        self.line = 1

        return tokens
