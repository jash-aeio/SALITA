"""
==========================================================================
  SALITA Compiler - Symbol Table
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  The symbol table stores information about every declared variable in
  the SALITA program.  It is shared between the semantic analyzer (which
  populates it) and the interpreter (which reads/writes values).

  Each entry tracks:
    - name  : variable name (string)
    - type  : data type (always 'INTEGER' in SALITA)
    - value : current runtime value (int or None before initialization)
==========================================================================
"""


class SymbolEntry:
    """
    A single symbol table entry representing a declared variable.

    Attributes:
        name  (str):         The variable identifier.
        type  (str):         The data type — always 'INTEGER' in SALITA.
        value (int | None):  The runtime value, or None if not yet assigned.
    """

    def __init__(self, name: str, var_type: str = 'INTEGER', value=None):
        self.name = name
        self.type = var_type
        self.value = value

    def __repr__(self) -> str:
        return f"SymbolEntry(name={self.name!r}, type={self.type!r}, value={self.value!r})"


class SymbolTable:
    """
    Manages all declared symbols (variables) for a SALITA program.

    Methods:
        declare(name)       — Register a new variable.
        is_declared(name)   — Check if a variable has been declared.
        set_value(name, v)  — Update the runtime value of a variable.
        get_value(name)     — Retrieve the runtime value of a variable.
        get_entries()       — Return a list of all SymbolEntry objects.
        reset()             — Clear the table entirely.
    """

    def __init__(self):
        self._symbols: dict[str, SymbolEntry] = {}

    # --------------------------------------------------------------------------
    # Declaration
    # --------------------------------------------------------------------------
    def declare(self, name: str) -> bool:
        """
        Declare a new variable. Returns True if successful, False if the
        variable was already declared (duplicate).
        """
        if name in self._symbols:
            return False
        self._symbols[name] = SymbolEntry(name, 'INTEGER', value=0)
        return True

    def is_declared(self, name: str) -> bool:
        """Check whether a variable name has been declared."""
        return name in self._symbols

    # --------------------------------------------------------------------------
    # Runtime Value Access
    # --------------------------------------------------------------------------
    def set_value(self, name: str, value: int):
        """Set the runtime value of a declared variable."""
        if name not in self._symbols:
            raise KeyError(f"Variable '{name}' is not declared.")
        self._symbols[name].value = value

    def get_value(self, name: str) -> int:
        """
        Get the current value of a variable.  Returns 0 if the variable
        has not been assigned yet (default initialization).
        """
        if name not in self._symbols:
            raise KeyError(f"Variable '{name}' is not declared.")
        val = self._symbols[name].value
        return val if val is not None else 0

    # --------------------------------------------------------------------------
    # Inspection
    # --------------------------------------------------------------------------
    def get_entries(self) -> list:
        """Return a list of all SymbolEntry objects (for GUI display)."""
        return list(self._symbols.values())

    def reset(self):
        """Clear all entries from the symbol table."""
        self._symbols.clear()

    def __repr__(self) -> str:
        header = f"{'Variable':<15} {'Type':<10} {'Value':<10}\n"
        header += "-" * 35 + "\n"
        rows = ""
        for entry in self._symbols.values():
            rows += f"{entry.name:<15} {entry.type:<10} {str(entry.value):<10}\n"
        return header + rows if rows else header + "(empty)\n"
