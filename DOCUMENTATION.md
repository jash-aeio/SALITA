# SALITA Compiler — Documentation

**Simple Algorithmic Language in Tagalog for Instruction and Teaching Applications**

---

## Table of Contents

1. [Language Design](#1-language-design)
2. [Comparison with Existing Languages](#2-comparison-with-existing-languages)
3. [Grammar Definition](#3-grammar-definition)
4. [Compiler Architecture](#4-compiler-architecture)
5. [Lexical Analysis](#5-lexical-analysis)
6. [Syntax Analysis (Parsing)](#6-syntax-analysis-parsing)
7. [Semantic Analysis](#7-semantic-analysis)
8. [Interpretation / Execution](#8-interpretation--execution)
9. [Error Handling](#9-error-handling)
10. [GUI Design](#10-gui-design)
11. [Building the Executable](#11-building-the-executable)
12. [Sample Execution Outputs](#12-sample-execution-outputs)

---

## 1. Language Design

SALITA is a **Filipino-based programming language** designed to help beginners learn programming concepts using **Tagalog keywords** instead of English syntax. The language models constructs found in C, Python, and Java, making it a familiar stepping stone into those languages.

### Keywords

| Function           | Keyword    | Description                        |
|--------------------|------------|------------------------------------|
| Variable declaration| `var`      | Declares a new integer variable    |
| Input              | `input`    | Reads an integer from the console  |
| Output             | `output`   | Displays the value of a variable   |

### Language Rules

1. Every statement must end with a **semicolon** (`;`).
2. **Whitespace** is ignored.
3. **Comments** use block format: `/* comment */`.
4. All variables are **integers** (whole numbers).
5. **Allowed arithmetic operators**: `+`, `-`, `*`, `/`.
6. **Parentheses** `( )` can be used to control operator precedence.
7. **Variable names**: can contain letters, digits, and underscores (`_`), but **cannot start with a digit**.
8. **Assignments** use the `=` operator without a keyword: `variable = expression;`

### Example Program

```
var x;
var y;
var total;

input x;
input y;

total = (x + y) * 2;

output total;
```

---

## 2. Comparison with Existing Languages

| Feature                | C               | Python            | SALITA               |
|------------------------|-----------------|-------------------|----------------------|
| Variable declaration   | `int x;`        | `x = 0`           | `var x;`             |
| User input             | `scanf("%d",&x)`| `x = int(input())`| `input x;`           |
| Print output           | `printf("%d",x)`| `print(x)`        | `output x;`          |
| Assignment             | `x = 5 + y;`   | `x = 5 + y`       | `x = 5 + y;`         |
| Statement terminator   | `;`             | Newline            | `;`                  |
| Comments               | `/* comment */` | `# comment`        | `/* comment */`      |
| Data types             | Multiple        | Dynamic            | Integer only         |
| Compilation model      | Compiled        | Interpreted        | Interpreted (AST)    |

**Key Design Decision**: SALITA uses explicit declaration with `baryabol` (like C/Java) rather than implicit declaration (like Python). This teaches beginners the concept of variable scope and type awareness.

---

## 3. Grammar Definition

The SALITA language follows a **context-free grammar (CFG)** written in EBNF notation:

```
program        → statement_list

statement_list → statement statement_list
               | statement

statement      → declaration
               | input_stmt
               | output_stmt
               | assignment

declaration    → 'var' IDENTIFIER ';'

input_stmt     → 'input' IDENTIFIER ';'

output_stmt    → 'output' IDENTIFIER ';'

assignment     → IDENTIFIER '=' expression ';'

expression     → term (('+' | '-') term)*

term           → factor (('*' | '/') factor)*

factor         → NUMBER
               | IDENTIFIER
               | '(' expression ')'
```

### Grammar Classification

- **Type**: Context-Free Grammar (CFG)
- **Parsing Strategy**: Recursive Descent (top-down, predictive)
- **Ambiguity**: None — the grammar is unambiguous. Operator precedence is encoded in the grammar structure (`expression` → `term` → `factor`).

---

## 4. Compiler Architecture

The SALITA compiler follows a **four-phase pipeline**:

```
Source Code (.sl)
       │
       ▼
┌─────────────────────┐
│  1. LEXICAL ANALYSIS │  →  Token Stream
│     (Lexer)          │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  2. SYNTAX ANALYSIS  │  →  Abstract Syntax Tree (AST)
│     (Parser)         │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  3. SEMANTIC ANALYSIS│  →  Validated AST + Symbol Table
│     (Analyzer)       │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  4. INTERPRETATION   │  →  Program Output
│     (Interpreter)    │
└─────────────────────┘
```

### Module Organization

| File                   | Purpose                                      |
|------------------------|----------------------------------------------|
| `token_types.py`       | Token type constants and Token class          |
| `lexer.py`             | Lexical analyzer (tokenization)               |
| `parser.py`            | Syntax analyzer (AST construction)            |
| `symbol_table.py`      | Symbol table data structure                   |
| `semantic_analyzer.py` | Semantic validation                           |
| `interpreter.py`       | Program execution engine                      |
| `gui.py`               | Tkinter-based IDE interface                   |
| `main.py`              | Application entry point                       |

---

## 5. Lexical Analysis

### Theory: Tokenization

**Tokenization** (also called **lexical analysis** or **scanning**) is the process of converting a sequence of characters into a sequence of **tokens** — the smallest meaningful units in the language.

The lexer performs:
- **Character scanning**: Reads source code character by character
- **Pattern matching**: Identifies keywords, identifiers, numbers, operators
- **Whitespace/comment removal**: Strips non-significant characters
- **Line tracking**: Records the source line for error reporting

### Token Types Recognized

| Token Type    | Examples               | Description                    |
|---------------|------------------------|--------------------------------|
| `KEYWORD`     | baryabol, kuha, etc.   | Reserved Filipino keywords     |
| `IDENTIFIER`  | x, total, my_var       | User-defined variable names    |
| `NUMBER`      | 42, 100, 0             | Integer literals               |
| `OPERATOR`    | +, -, *, /, =          | Arithmetic and assignment ops  |
| `SEMICOLON`   | ;                      | Statement terminator           |
| `PARENTHESIS` | (, )                   | Grouping delimiters            |
| `COMMENT`     | /* ... */              | Block comments (skipped)       |

### Example Token Output

For the input `lagay total = (x + y) * 2;`:

```
[KEYWORD:lagay]
[IDENTIFIER:total]
[OPERATOR:=]
[PARENTHESIS:(]
[IDENTIFIER:x]
[OPERATOR:+]
[IDENTIFIER:y]
[PARENTHESIS:)]
[OPERATOR:*]
[NUMBER:2]
[SEMICOLON:;]
```

---

## 6. Syntax Analysis (Parsing)

### Theory: Abstract Syntax Trees

The parser validates the token stream against the context-free grammar and constructs an **Abstract Syntax Tree (AST)**. The AST is a hierarchical data structure that represents the logical structure of the program, discarding syntactic sugar like semicolons and keywords.

### Parsing Strategy: Recursive Descent

SALITA uses a **recursive-descent parser**, where each grammar rule corresponds to a method in the `Parser` class:

| Grammar Rule    | Parser Method    |
|-----------------|------------------|
| `program`       | `program()`      |
| `statement`     | `statement()`    |
| `declaration`   | `declaration()`  |
| `input_stmt`    | `input_stmt()`   |
| `output_stmt`   | `output_stmt()`  |
| `assignment`    | `assignment()`   |
| `expression`    | `expression()`   |
| `term`          | `term()`         |
| `factor`        | `factor()`       |

### AST Node Types

| Node        | Represents                          |
|-------------|-------------------------------------|
| `Program`   | Root node with list of statements   |
| `VarDecl`   | Variable declaration                |
| `InputStmt` | Input statement                     |
| `OutputStmt`| Output statement                    |
| `Assignment`| Variable assignment with expression |
| `BinOp`     | Binary arithmetic operation         |
| `Num`       | Integer literal                     |
| `Var`       | Variable reference                  |

### Example AST

For `lagay total = (x + y) * 2;`:

```
Assignment: total =
  BinOp: *
    BinOp: +
      Var: x
      Var: y
    Num: 2
```

---

## 7. Semantic Analysis

### Theory: Contextual Validation

Semantic analysis checks properties that **cannot be expressed by the grammar alone**. While the parser ensures the program is *syntactically* correct, the semantic analyzer ensures it is *meaningfully* correct.

### Checks Performed

1. **Variable declared before use**: Every variable must be declared with `baryabol` before it appears in `kuha`, `ipakita`, `lagay`, or an expression.

2. **No duplicate declarations**: A variable name cannot be declared more than once.

3. **Valid assignment targets**: The left-hand side of `lagay` must be a declared variable.

4. **Numeric expressions**: All expressions must evaluate to integers.

### Symbol Table

The semantic analyzer maintains a **symbol table** — a data structure that maps variable names to their metadata:

| Variable | Type    | Value |
|----------|---------|-------|
| x        | INTEGER | 0     |
| y        | INTEGER | 0     |
| total    | INTEGER | 0     |

The symbol table is populated during semantic analysis and updated during interpretation.

---

## 8. Interpretation / Execution

The SALITA interpreter is a **tree-walking interpreter** that traverses the validated AST using the **Visitor design pattern**.

### Execution Flow

1. **VarDecl**: Variable is already initialized to 0 in the symbol table.
2. **InputStmt**: Prompts the user for an integer and stores it.
3. **Assignment**: Evaluates the right-hand expression and stores the result.
4. **OutputStmt**: Retrieves the variable's value and displays it.
5. **BinOp**: Recursively evaluates left and right operands, applies the operator.

### Integer Division

Since all variables in SALITA are integers, division uses **floor division** (truncates toward zero), similar to integer division in C.

---

## 9. Error Handling

The SALITA compiler detects and reports three categories of errors:

### Lexical Errors

Detected during tokenization:
- Invalid characters
- Unterminated comments

```
Lexical Error (Line 5): Invalid character '@'.
Lexical Error (Line 1): Unterminated comment. Expected closing '*/' but reached end of file.
```

### Syntax Errors

Detected during parsing:
- Missing semicolons
- Unexpected tokens
- Malformed statements

```
Syntax Error (Line 4): Expected SEMICOLON, but got IDENTIFIER ('y').
Syntax Error (Line 7): Expected a number, identifier, or '(', but got ';'.
```

### Semantic Errors

Detected during semantic analysis:
- Undeclared variables
- Duplicate declarations

```
Semantic Error (Line 3): Variable 'z' not declared before use.
Semantic Error (Line 5): Variable 'x' is already declared.
```

### Runtime Errors

Detected during execution:
- Division by zero
- Input cancellation

```
Runtime Error (Line 6): Division by zero.
Runtime Error: Input cancelled for variable 'x'.
```

Every error message includes the **line number**, **error type**, and **description**.

---

## 10. GUI Design

The SALITA IDE is built using **Tkinter** with a dark theme inspired by Catppuccin Mocha.

### Interface Components

1. **Header**: Application title and description
2. **Toolbar**: Load File, Save File, Run Compiler, Clear Output
3. **Source Code Editor**: Text editor with line numbers and syntax highlighting
4. **Output Tabs**:
   - 🔤 **Tokens**: Displays the token table from lexical analysis
   - 🌳 **Parsing**: Shows parsing result and AST visualization
   - 🔍 **Semantic**: Shows semantic analysis results
   - 📟 **Output**: Displays program output (from `ipakita`)
   - ⚠ **Errors**: Shows all error messages
   - 📊 **Symbols**: Displays the symbol table
5. **Status Bar**: Shows current operation status

### Keyboard Shortcuts

| Shortcut   | Action          |
|------------|-----------------|
| `Ctrl+O`   | Load file       |
| `Ctrl+S`   | Save file       |
| `F5`       | Run compiler    |

---

## 11. Building the Executable

To create a standalone `.exe` file that runs without Python installed:

### Prerequisites

```bash
pip install pyinstaller
```

### Build Command

```bash
pyinstaller --onefile --windowed --name "SALITA_IDE" main.py
```

### Flags Explained

| Flag          | Purpose                                      |
|---------------|----------------------------------------------|
| `--onefile`   | Package everything into a single .exe file   |
| `--windowed`  | Suppress the console window (GUI app)        |
| `--name`      | Set the output executable name               |

The executable will be created in the `dist/` folder.

---

## 12. Sample Execution Outputs

### Example 1: Basic Program

**Input program:**
```
var x;
var y;
var total;

input x;
input y;

total = (x + y) * 2;

output total;
```

**User inputs**: x = 5, y = 10

**Expected output**:

```
## TOKENS

  [KEYWORD:var]
  [IDENTIFIER:x]
  [SEMICOLON:;]
  [KEYWORD:var]
  [IDENTIFIER:y]
  [SEMICOLON:;]
  ...

## PARSING RESULT

  Program structure valid.

## SEMANTIC RESULT

  No semantic errors.

## PROGRAM OUTPUT

  30
```

**Explanation**: `(5 + 10) * 2 = 30`

### Example 2: Area Calculation

**Input program:**
```
var length;
var width;
var area;

input length;
input width;

area = length * width;

output area;
```

**User inputs**: length = 7, width = 4

**Expected output**: `28`

### Example 3: Operator Precedence

**Input program:**
```
var a;
var b;
var c;
var result1;
var result2;

input a;
input b;
input c;

result1 = a + b * c;
result2 = (a + b) * c;

output result1;
output result2;
```

**User inputs**: a = 2, b = 3, c = 4

**Expected output**:
```
14
20
```

**Explanation**:
- `result1 = 2 + 3 * 4 = 2 + 12 = 14` (multiplication first)
- `result2 = (2 + 3) * 4 = 5 * 4 = 20` (parentheses override)

---

## Compiler Theory Concepts Used

| Concept                    | Implementation                     |
|----------------------------|-------------------------------------|
| **Tokenization**           | `lexer.py` — character-by-character scanning |
| **Context-Free Grammar**   | EBNF grammar definition → `parser.py` |
| **Abstract Syntax Trees**  | AST node classes in `parser.py`    |
| **Recursive Descent**      | Top-down predictive parsing        |
| **Symbol Tables**          | `symbol_table.py` — variable tracking |
| **Semantic Checking**      | `semantic_analyzer.py` — Visitor pattern |
| **Tree-Walking Interpreter** | `interpreter.py` — AST evaluation |
| **Visitor Design Pattern** | Used in both semantic analysis and interpretation |

---

*SALITA Compiler — Developed for CS Compiler Design / Programming Language Translation*
