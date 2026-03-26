# SALITA — Simple Algorithmic Language in Tagalog for Instruction and Teaching Applications

A **Filipino-based programming language** designed to teach beginners programming fundamentals using **Tagalog keywords**. SALITA provides a gentle introduction to compiler design and programming concepts with minimal syntax.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

---

## 🌟 Features

- **Filipino-first Design**: Keywords in Tagalog (`var`, `input`, `output`)
- **Complete Compiler Pipeline**: Full lexical, syntax, semantic, and interpretation phases
- **Interactive GUI IDE**: Tkinter-based IDE with multi-tab output visualization
- **CLI Support**: Run programs directly from command line
- **Rich Error Reporting**: Detailed error messages with line numbers
- **Educational**: Designed to teach compiler fundamentals and programming concepts
- **Lightweight**: No external dependencies beyond standard Python library (Tkinter)

---

## 🚀 Quick Start

### Launch the GUI IDE

```bash
python main.py
```

This opens an interactive IDE where you can:
- Write SALITA code in the editor
- Run the compiler with F5 or the Run button
- View tokens, AST, symbol table, and output in separate tabs
- Load and save `.sl` files

### Run a Program from CLI

```bash
python main.py sample_area.sl
```

Output shows all compiler phases:

```
## TOKENS
  Token(VAR, 'var', 5)
  Token(IDENTIFIER, 'length', 5)
  ...

## PARSING RESULT
  Program structure valid.
  Declaration(Identifier('length'))
  ...

## SEMANTIC RESULT
  No semantic errors.

## PROGRAM OUTPUT
  [program executes here]
```

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Tkinter (included with most Python distributions)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SALITA.git
   cd SALITA
   ```

2. Verify Python installation:
   ```bash
   python --version  # Should be 3.8+
   ```

3. Run the IDE:
   ```bash
   python main.py
   ```

**Note**: No external packages required. Tkinter is included in standard Python installations.

---

## 📝 Language Syntax

### Basic Concepts

SALITA is an **integer-only language** with three keywords and simple syntax:

```salita
var x;              // Declare variable
input x;            // Read integer from user
x = 5 + 3;          // Assignment and arithmetic
output x;           // Display variable value
```

### Keywords

| Keyword | Purpose | Example |
|---------|---------|---------|
| `var` | Declare variable | `var count;` |
| `input` | Read user input | `input count;` |
| `output` | Display output | `output count;` |

### Operators

| Operator | Operation | Example |
|----------|-----------|---------|
| `+` | Addition | `a = b + c;` |
| `-` | Subtraction | `a = b - c;` |
| `*` | Multiplication | `a = b * c;` |
| `/` | Division (floor) | `a = b / c;` |
| `( )` | Parentheses | `a = (b + c) * 2;` |

### Language Rules

1. **Every statement ends with a semicolon** (`;`)
2. **Whitespace is ignored**
3. **Comments use block format**: `/* comment */`
4. **All variables are integers** (whole numbers only)
5. **Variable names** can contain letters, digits, and underscores but cannot start with a digit
6. **Operator precedence**: `*` and `/` bind tighter than `+` and `-`
7. **Assignments don't use a keyword**: `x = 5 + y;` (not `var x = 5 + y;`)

### Example Programs

#### Example 1: Rectangle Area Calculator

```salita
/* Calculate the area of a rectangle */
var length;
var width;
var area;

input length;
input width;

area = length * width;

output area;
```

**Sample Run:**
```
Input length: 5
Input width: 3
15
```

#### Example 2: Sum and Double

```salita
/* Input two numbers, sum them, and double the result */
var x;
var y;
var total;

input x;
input y;

total = (x + y) * 2;

output total;
```

**Sample Run:**
```
Input x: 10
Input y: 20
60
```

#### Example 3: Arithmetic Operations

```salita
/* Demonstrate operator precedence */
var a;
var b;
var c;
var result;

input a;
input b;
input c;

/* Multiplication happens before addition */
result = a + b * c;

output result;
```

---

## 🏗️ Architecture

### Compiler Pipeline

SALITA implements a complete **4-phase compiler**:

```
Source Code (.sl file)
    ↓
[Phase 1] Lexer → Token Stream
    ↓
[Phase 2] Parser → Abstract Syntax Tree (AST)
    ↓
[Phase 3] Semantic Analyzer → Validated AST + Symbol Table
    ↓
[Phase 4] Interpreter → Program Execution
```

### Phase Breakdown

| Phase | Module | Function | Input | Output |
|-------|--------|----------|-------|--------|
| **Lexical** | `lexer.py` | Tokenizes source text | Raw source code | Token stream |
| **Syntax** | `parser.py` | Builds AST using recursive descent | Tokens | AST (tree structure) |
| **Semantic** | `semantic_analyzer.py` | Validates declarations and types | AST | Symbol table |
| **Execution** | `interpreter.py` | Tree-walking interpreter | AST + symbols | Program output |

### Design Patterns Used

- **Visitor Pattern**: Used in semantic analysis and interpretation for AST traversal
- **Recursive Descent Parsing**: Grammar rules map directly to parser methods
- **Symbol Table**: Maintains variable metadata during analysis and execution

---

## 📁 Project Structure

```
SALITA/
├── main.py                    # Entry point (GUI or CLI)
├── lexer.py                   # Lexical analyzer
├── parser.py                  # Syntax analyzer
├── token_types.py             # Token type constants
├── semantic_analyzer.py       # Semantic validator
├── symbol_table.py            # Variable metadata storage
├── interpreter.py             # Tree-walking interpreter
├── gui.py                     # Tkinter IDE
├── CLAUDE.md                  # Developer guidelines
├── DOCUMENTATION.md           # Full language specification
├── README.md                  # This file
├── sample_program.sl          # Sample 1: Sum and double
├── sample_area.sl             # Sample 2: Rectangle area
├── sample_average.sl          # Sample 3: Average calculation
└── sample_complex.sl          # Sample 4: Complex expressions
```

### Key Files

- **`main.py`**: Dispatcher for GUI or CLI mode
- **`lexer.py`**: Converts source text to tokens (regular expressions)
- **`parser.py`**: Recursive descent parser implementing the grammar
- **`token_types.py`**: Token type constants (VAR, INPUT, OUTPUT, etc.)
- **`semantic_analyzer.py`**: Checks variable declarations and detects errors
- **`symbol_table.py`**: Stores variable names and values
- **`interpreter.py`**: Executes the AST
- **`gui.py`**: Tkinter IDE with 6 output tabs

---

## 🖥️ GUI Features

The Tkinter IDE provides:

### Toolbar
- **Load File** (Ctrl+O): Open a `.sl` file
- **Save File** (Ctrl+S): Save current code
- **Run** (F5): Execute the compiler
- **Clear Output**: Reset all output tabs

### Output Tabs

1. **🔤 Tokens** — Token list from lexical analysis
2. **🌳 Parsing** — AST visualization with structure
3. **🔍 Semantic** — Symbol table and validation results
4. **📟 Output** — Program execution output
5. **⚠️ Errors** — Compilation and runtime errors
6. **📊 Symbols** — Final variable state after execution

---

## 🛠️ Development

### Adding a New Operator

To add a new arithmetic operator (e.g., `%` for modulo):

1. **Token Type** (`token_types.py`):
   ```python
   T_MOD = 'MOD'
   ```

2. **Lexer** (`lexer.py`):
   ```python
   elif char == '%':
       self.tokens.append(Token(T_MOD, '%', self.line))
   ```

3. **Parser** (`parser.py`):
   Update the `term()` method to handle modulo with proper precedence

4. **Interpreter** (`interpreter.py`):
   ```python
   elif node.op == '%':
       return left % right
   ```

### Adding a New Keyword

To add a new keyword (e.g., `if` for conditionals):

1. **Token Type** (`token_types.py`):
   ```python
   T_IF = 'IF'
   KEYWORDS = { ..., 'if': T_IF }
   ```

2. **Parser** (`parser.py`):
   Create a new statement method:
   ```python
   def if_stmt(self):
       # Implement if statement parsing
   ```

3. **AST Node** (`parser.py`):
   Create an AST node class for the new statement type

4. **Semantic Analyzer** (`semantic_analyzer.py`):
   Add visit method for the new statement

5. **Interpreter** (`interpreter.py`):
   Implement execution logic

### Testing Changes

Create a test file and run through the CLI to verify all phases:

```bash
python main.py test_file.sl
```

Inspect tokens, AST, symbol table, and output to ensure correctness.

---

## 🔨 Building a Standalone Executable

### Prerequisites

```bash
pip install pyinstaller
```

### Build Command

```bash
pyinstaller --onefile --windowed --name "SALITA_IDE" main.py
```

### Output

- **Windows**: `dist/SALITA_IDE.exe`
- **Linux/macOS**: `dist/SALITA_IDE`

The executable bundles Python, all dependencies, and the SALITA compiler into a single file.

---

## 🐛 Error Handling

SALITA provides detailed error messages with line numbers:

### Error Categories

| Category | Example | Message |
|----------|---------|---------|
| **Lexical** | Invalid character | `Unexpected character '@' at line 5` |
| **Syntax** | Missing semicolon | `Expected ';' after statement at line 3` |
| **Semantic** | Undeclared variable | `Variable 'x' is not declared at line 7` |
| **Semantic** | Duplicate declaration | `Variable 'x' already declared at line 2` |
| **Runtime** | Division by zero | `Division by zero at line 10` |
| **Runtime** | Invalid input | `User cancelled input` |

### Error Flow

1. **Lexer errors** stop compilation immediately
2. **Parser errors** show syntax issues
3. **Semantic errors** catch type and scope issues
4. **Runtime errors** occur during program execution

---

## 📚 Learning Resources

### For Students

- Start with `sample_program.sl` and `sample_area.sl`
- Modify the samples to add more variables or operations
- Read `DOCUMENTATION.md` for full language specification
- Inspect the GUI output tabs to understand each compilation phase

### For Educators

- Use SALITA to teach programming fundamentals
- Show compiler phases visually in the GUI
- Demonstrate operator precedence and variable scope
- Create custom sample programs for your curriculum

### For Developers

- Read `CLAUDE.md` for architecture and design patterns
- Explore `parser.py` for recursive descent parsing example
- Study `semantic_analyzer.py` for symbol table implementation
- Review `interpreter.py` for tree-walking interpreter pattern

---

## 📋 Limitations

- **Integer-only**: All variables are integers; no floating-point or string types
- **No functions**: Cannot define custom functions
- **No control flow**: No if/else, loops, or conditionals
- **Single scope**: No nested scopes or closures
- **No arrays**: Only individual variables
- **Synchronous I/O**: All input/output is blocking

These limitations are intentional to keep the language simple for educational purposes.

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- [ ] Support for floating-point numbers
- [ ] String variables and concatenation
- [ ] Control flow (if/else, while, for loops)
- [ ] Function definitions
- [ ] Array support
- [ ] Better error messages with suggestions
- [ ] Performance optimizations
- [ ] Additional sample programs

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with sample programs
5. Submit a pull request

---

## 📖 Files Reference

### Core Compiler

| File | Lines | Purpose |
|------|-------|---------|
| `lexer.py` | ~150 | Tokenization with regex patterns |
| `parser.py` | ~300 | Recursive descent parser + AST |
| `semantic_analyzer.py` | ~100 | Variable validation and symbol table |
| `interpreter.py` | ~150 | Tree-walking interpreter |
| `symbol_table.py` | ~50 | Variable metadata storage |
| `token_types.py` | ~50 | Token constants and keywords |

### User Interface & Entry

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | ~105 | CLI/GUI dispatcher |
| `gui.py` | ~400+ | Tkinter IDE with 6 tabs |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick start |
| `DOCUMENTATION.md` | Full language specification |
| `CLAUDE.md` | Developer guidelines |

### Samples

| File | Purpose |
|------|---------|
| `sample_program.sl` | Sum and double |
| `sample_area.sl` | Rectangle area calculator |
| `sample_average.sl` | Average calculation |
| `sample_complex.sl` | Complex expressions |

---

## 🎓 Educational Value

SALITA is ideal for teaching:

- **Lexical Analysis**: How source text becomes tokens
- **Parsing**: Building Abstract Syntax Trees
- **Semantic Analysis**: Variable scope and type checking
- **Interpretation**: Executing AST nodes
- **Compiler Design**: Complete pipeline in ~800 lines
- **Programming Fundamentals**: Variables, operators, I/O

All concepts are visualized in the GUI, making compiler phases tangible and understandable.

---

## 📝 License

This project is open source and available under the MIT License. See LICENSE file for details.

---

## 👨‍💻 Author

SALITA was created as an educational tool for teaching programming and compiler design.

---

## 🙏 Acknowledgments

- Inspired by educational languages like BASIC, Scratch, and Logo
- Built with Python and Tkinter for maximum portability
- Designed for Filipino students and educators

---

## 📧 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check DOCUMENTATION.md for language details
- Review CLAUDE.md for architecture questions
- Examine sample programs for usage examples

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Basic syntax (var, input, output)
- ✅ Arithmetic operators
- ✅ Full compiler pipeline
- ✅ GUI IDE
- ✅ CLI mode

### Version 1.1 (Planned)
- [ ] Better error messages
- [ ] Code formatting
- [ ] Sample program templates
- [ ] Execution step-through debugger

### Version 2.0 (Future)
- [ ] If/else conditionals
- [ ] Loops (while, for)
- [ ] Functions
- [ ] Arrays
- [ ] String type

---

**Happy coding with SALITA! 🇵🇭💻**
