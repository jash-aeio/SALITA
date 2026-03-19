"""
==========================================================================
  SALITA Compiler - Main Entry Point
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  This is the main module that launches the SALITA IDE.

  Usage:
    python main.py              → Launch the GUI
    python main.py <file.sl>    → Run a SALITA file from the command line

  To build a standalone executable:
    pyinstaller --onefile --windowed main.py
==========================================================================
"""

import sys
import os

# Ensure the project directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer, LexerError
from parser import Parser, ParserError, ast_to_string
from semantic_analyzer import SemanticAnalyzer, SemanticError
from interpreter import Interpreter
from interpreter import RuntimeError as SalitaRuntimeError
from token_types import T_EOF


def run_cli(file_path: str):
    """
    Run a SALITA source file from the command line (no GUI).
    Prints tokens, AST, semantic results, and program output to stdout.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    print(f"─── SALITA Compiler ── {os.path.basename(file_path)} ───\n")

    # Phase 1: Lexical Analysis
    print("## TOKENS\n")
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        for tok in tokens:
            print(f"  {tok}")
        print()
    except LexerError as e:
        print(f"  ❌ {e}\n")
        sys.exit(1)

    # Phase 2: Syntax Analysis
    print("## PARSING RESULT\n")
    try:
        parser = Parser(Lexer(source))
        tree = parser.parse()
        print("  Program structure valid.\n")
        print(ast_to_string(tree))
        print()
    except ParserError as e:
        print(f"  ❌ {e}\n")
        sys.exit(1)

    # Phase 3: Semantic Analysis
    print("## SEMANTIC RESULT\n")
    try:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(tree)
        symbol_table = analyzer.symbol_table
        print("  No semantic errors.\n")
    except SemanticError as e:
        print(f"  ❌ {e}\n")
        sys.exit(1)

    # Phase 4: Execution
    print("## PROGRAM OUTPUT\n")
    try:
        interp = Interpreter(tree, symbol_table)
        interp.interpret()
    except SalitaRuntimeError as e:
        print(f"  ❌ {e}\n")
        sys.exit(1)

    print("\n─── Execution Finished ───")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command-line mode: run the specified file
        run_cli(sys.argv[1])
    else:
        # GUI mode
        from gui import launch_gui
        launch_gui()


if __name__ == '__main__':
    main()
