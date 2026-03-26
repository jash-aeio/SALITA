"""
==========================================================================
  SALITA Compiler - Graphical User Interface (GUI)
  (Simple Algorithmic Language in Tagalog for Instruction and Teaching
   Applications)
==========================================================================
  A Tkinter-based IDE for writing, compiling, and running SALITA programs.

  Features:
    - Source code editor with line numbers and syntax highlighting
    - Load / Save / Run / Clear buttons
    - Output panels: Token Table, Parse Result, Semantic Result,
      Program Output, Error Display
    - Input dialog for the 'kuha' statement
==========================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import os
import threading

from token_types import T_EOF
from lexer import Lexer, LexerError
from parser import Parser, ParserError, ast_to_string
from semantic_analyzer import SemanticAnalyzer, SemanticError
from interpreter import Interpreter
from interpreter import RuntimeError as SalitaRuntimeError
from symbol_table import SymbolTable


# ==============================================================================
# Color Palette & Styling Constants
# ==============================================================================
BG_DARK       = "#1e1e2e"       # Main background
BG_EDITOR     = "#181825"       # Editor background
BG_PANEL      = "#1e1e2e"       # Output panel background
BG_SIDEBAR    = "#11111b"       # Line-number gutter background
FG_TEXT        = "#cdd6f4"       # Default text color
FG_LINE_NUM   = "#585b70"       # Line-number color
FG_KEYWORD    = "#f38ba8"       # Keyword color (pink/red)
FG_NUMBER     = "#fab387"       # Number color (peach)
FG_COMMENT    = "#6c7086"       # Comment color (overlay)
FG_STRING     = "#a6e3a1"       # String color (green, reserved)
FG_OPERATOR   = "#89dceb"       # Operator color (sky)
FG_PAREN      = "#f9e2af"       # Parenthesis color (yellow)
ACCENT        = "#cba6f7"       # Accent / highlight color (mauve)
ACCENT_HOVER  = "#b4befe"       # Accent hover (lavender)
BTN_BG        = "#313244"       # Button background
BTN_FG        = "#cdd6f4"       # Button text
SUCCESS_FG    = "#a6e3a1"       # Green for success
ERROR_FG      = "#f38ba8"       # Red for errors
TAB_ACTIVE    = "#45475a"       # Active tab background
TAB_INACTIVE  = "#313244"       # Inactive tab background
SELECTION_BG  = "#45475a"       # Selection / highlight background
CURSOR_COLOR  = "#f5e0dc"       # Cursor color (rosewater)

FONT_FAMILY   = "Consolas"
FONT_SIZE     = 11
HEADING_FONT  = ("Segoe UI", 11, "bold")
BUTTON_FONT   = ("Segoe UI", 10)
TAB_FONT      = ("Segoe UI", 10)
STATUS_FONT   = ("Segoe UI", 9)

SALITA_KEYWORDS = {"var", "input", "output"}

# ==============================================================================
# Mindmap Layout Constants
# ==============================================================================
MM_NODE_W  = 130
MM_NODE_H  = 36
MM_H_GAP   = 28
MM_V_GAP   = 72
MM_RADIUS  = 8

# Fill, text color per AST node type
MM_COLORS = {
    "Program":    ("#cba6f7", "#11111b"),
    "VarDecl":    ("#a6e3a1", "#11111b"),
    "InputStmt":  ("#89b4fa", "#11111b"),
    "OutputStmt": ("#f9e2af", "#11111b"),
    "Assignment": ("#fab387", "#11111b"),
    "BinOp":      ("#89dceb", "#11111b"),
    "Num":        ("#b5e8e0", "#11111b"),
    "Var":        ("#585b70", "#cdd6f4"),
}
MM_DEFAULT_COLOR = ("#45475a", "#cdd6f4")

# ==============================================================================
# Main Application Class
# ==============================================================================
class SalitaIDE(tk.Tk):
    """
    The main SALITA IDE window.

    Contains the code editor, toolbar, and tabbed output panels.
    """

    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("SALITA IDE — Simple Algorithmic Language in Tagalog")
        self.configure(bg=BG_DARK)

        # Attempt a reasonable initial size
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = min(1280, screen_w - 100)
        win_h = min(800, screen_h - 80)
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.minsize(900, 600)

        # State
        self.current_file_path = None

        # Build the UI
        self._configure_styles()
        self._build_header()
        self._build_toolbar()
        self._build_main_area()
        self._build_status_bar()

        # Key bindings
        self.bind_all("<Control-o>", lambda e: self.load_file())
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<F5>",        lambda e: self.run_compiler())

        # Insert sample code on startup
        self._insert_sample_code()

    # ==========================================================================
    # UI Construction
    # ==========================================================================
    def _configure_styles(self):
        """Configure ttk styles for the Catppuccin-Mocha dark theme."""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure("Dark.TFrame",     background=BG_DARK)
        self.style.configure("Editor.TFrame",   background=BG_EDITOR)
        self.style.configure("Panel.TFrame",    background=BG_PANEL)
        self.style.configure("Sidebar.TFrame",  background=BG_SIDEBAR)

        self.style.configure("Header.TLabel",
                             background=BG_DARK, foreground=ACCENT,
                             font=("Segoe UI", 14, "bold"))
        self.style.configure("SubHeader.TLabel",
                             background=BG_DARK, foreground=FG_TEXT,
                             font=("Segoe UI", 9))

        self.style.configure("Dark.TButton",
                             background=BTN_BG, foreground=BTN_FG,
                             font=BUTTON_FONT, padding=(14, 6),
                             borderwidth=0)
        self.style.map("Dark.TButton",
                       background=[("active", TAB_ACTIVE)])

        self.style.configure("Accent.TButton",
                             background=ACCENT, foreground="#11111b",
                             font=("Segoe UI", 10, "bold"), padding=(16, 6),
                             borderwidth=0)
        self.style.map("Accent.TButton",
                       background=[("active", ACCENT_HOVER)])

        self.style.configure("Status.TLabel",
                             background=BG_SIDEBAR, foreground=FG_LINE_NUM,
                             font=STATUS_FONT, padding=(8, 4))

        # Notebook (tabs)
        self.style.configure("Dark.TNotebook",
                             background=BG_DARK, borderwidth=0)
        self.style.configure("Dark.TNotebook.Tab",
                             background=TAB_INACTIVE, foreground=FG_TEXT,
                             font=TAB_FONT, padding=(12, 6))
        self.style.map("Dark.TNotebook.Tab",
                       background=[("selected", TAB_ACTIVE)],
                       foreground=[("selected", ACCENT)])

    def _build_header(self):
        """Build the title bar / header section."""
        header_frame = ttk.Frame(self, style="Dark.TFrame")
        header_frame.pack(fill=tk.X, padx=16, pady=(12, 0))

        title = ttk.Label(header_frame, text="✦  SALITA IDE",
                          style="Header.TLabel")
        title.pack(side=tk.LEFT)

        sub = ttk.Label(header_frame,
                        text="Simple Algorithmic Language in Tagalog for Instruction and Teaching Applications",
                        style="SubHeader.TLabel")
        sub.pack(side=tk.LEFT, padx=(12, 0))

    def _build_toolbar(self):
        """Build the button toolbar (Load, Save, Run, Clear)."""
        toolbar = ttk.Frame(self, style="Dark.TFrame")
        toolbar.pack(fill=tk.X, padx=16, pady=(10, 6))

        ttk.Button(toolbar, text="📂  Load File",   style="Dark.TButton",
                   command=self.load_file).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="💾  Save File",   style="Dark.TButton",
                   command=self.save_file).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="▶  Run Compiler", style="Accent.TButton",
                   command=self.run_compiler).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="🗑  Clear Output", style="Dark.TButton",
                   command=self.clear_output).pack(side=tk.LEFT, padx=(0, 6))

    def _build_main_area(self):
        """Build the editor + output panel (split view)."""
        # Use a PanedWindow so the user can resize
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK,
                              sashwidth=4, sashrelief=tk.FLAT,
                              bd=0)
        pane.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 6))

        # ---- Left side: Code Editor ----
        editor_frame = tk.Frame(pane, bg=BG_EDITOR, bd=0,
                                highlightthickness=1,
                                highlightbackground="#313244")
        pane.add(editor_frame, width=560)

        # Label
        lbl = tk.Label(editor_frame, text="  Source Code Editor (.sl)",
                       bg=BG_SIDEBAR, fg=ACCENT, font=HEADING_FONT,
                       anchor="w")
        lbl.pack(fill=tk.X)

        # Editor inner frame (line numbers + text)
        editor_inner = tk.Frame(editor_frame, bg=BG_EDITOR)
        editor_inner.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_inner, width=4, bg=BG_SIDEBAR, fg=FG_LINE_NUM,
            font=(FONT_FAMILY, FONT_SIZE), bd=0, padx=6, pady=6,
            takefocus=0, state=tk.DISABLED, cursor="arrow",
            selectbackground=BG_SIDEBAR, selectforeground=FG_LINE_NUM,
            highlightthickness=0, relief=tk.FLAT
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Source code text widget
        self.code_editor = tk.Text(
            editor_inner, bg=BG_EDITOR, fg=FG_TEXT,
            font=(FONT_FAMILY, FONT_SIZE), bd=0, padx=8, pady=6,
            insertbackground=CURSOR_COLOR, insertwidth=2,
            selectbackground=SELECTION_BG, selectforeground=FG_TEXT,
            undo=True, wrap=tk.NONE, highlightthickness=0,
            relief=tk.FLAT, tabs=(f"{4 * 8}p",)
        )
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for the editor
        editor_scroll = tk.Scrollbar(editor_inner, command=self._on_editor_scroll,
                                     bg=BG_DARK, troughcolor=BG_EDITOR,
                                     highlightthickness=0, bd=0)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_editor.config(yscrollcommand=self._on_editor_yscroll(editor_scroll))

        # Bind events for line numbers & syntax highlighting
        self.code_editor.bind("<KeyRelease>", self._on_code_change)
        self.code_editor.bind("<ButtonRelease-1>", self._on_code_change)
        self.code_editor.bind("<MouseWheel>", self._on_code_change)

        # ---- Right side: Output Panels (tabbed) ----
        output_frame = tk.Frame(pane, bg=BG_DARK, bd=0)
        pane.add(output_frame)

        self.notebook = ttk.Notebook(output_frame, style="Dark.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create output tabs
        self.token_output    = self._create_output_tab("🔤 Tokens")
        self.parse_output    = self._create_output_tab("🌳 Parsing")
        self.semantic_output = self._create_output_tab("🔍 Semantic")
        self.program_output  = self._create_output_tab("📟 Output")
        self.error_output    = self._create_output_tab("⚠ Errors")
        self.symbol_output   = self._create_output_tab("📊 Symbols")
        self._create_mindmap_tab()

    def _create_output_tab(self, title: str) -> scrolledtext.ScrolledText:
        """Create a single tab with a read-only ScrolledText widget."""
        frame = tk.Frame(self.notebook, bg=BG_PANEL)
        self.notebook.add(frame, text=title)

        text_widget = scrolledtext.ScrolledText(
            frame, bg=BG_PANEL, fg=FG_TEXT,
            font=(FONT_FAMILY, FONT_SIZE), bd=0, padx=10, pady=8,
            state=tk.DISABLED, wrap=tk.WORD,
            insertbackground=BG_PANEL, highlightthickness=0,
            relief=tk.FLAT, selectbackground=SELECTION_BG,
            selectforeground=FG_TEXT
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure highlight tags for this widget
        text_widget.tag_configure("success",  foreground=SUCCESS_FG)
        text_widget.tag_configure("error",    foreground=ERROR_FG)
        text_widget.tag_configure("accent",   foreground=ACCENT)
        text_widget.tag_configure("heading",  foreground=ACCENT,
                                  font=("Segoe UI", 11, "bold"))
        text_widget.tag_configure("keyword",  foreground=FG_KEYWORD)
        text_widget.tag_configure("number",   foreground=FG_NUMBER)
        text_widget.tag_configure("operator", foreground=FG_OPERATOR)

        return text_widget

    def _create_mindmap_tab(self):
        """Create the interactive AST mindmap Canvas tab."""
        frame = tk.Frame(self.notebook, bg=BG_EDITOR)
        self.notebook.add(frame, text="🗺 AST Map")

        canvas_wrap = tk.Frame(frame, bg=BG_EDITOR)
        canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.mindmap_canvas = tk.Canvas(
            canvas_wrap, bg=BG_EDITOR, bd=0,
            highlightthickness=0, relief=tk.FLAT
        )
        h_bar = tk.Scrollbar(canvas_wrap, orient=tk.HORIZONTAL,
                             command=self.mindmap_canvas.xview,
                             bg=BG_DARK, troughcolor=BG_EDITOR)
        v_bar = tk.Scrollbar(canvas_wrap, orient=tk.VERTICAL,
                             command=self.mindmap_canvas.yview,
                             bg=BG_DARK, troughcolor=BG_EDITOR)
        self.mindmap_canvas.configure(
            xscrollcommand=h_bar.set,
            yscrollcommand=v_bar.set
        )
        h_bar.pack(side=tk.BOTTOM, fill=tk.X)
        v_bar.pack(side=tk.RIGHT,  fill=tk.Y)
        self.mindmap_canvas.pack(fill=tk.BOTH, expand=True)

        # Pan support
        self._mm_pan_start = None
        self.mindmap_canvas.bind("<ButtonPress-2>",   self._mm_pan_start_cb)
        self.mindmap_canvas.bind("<B2-Motion>",       self._mm_pan_cb)
        self.mindmap_canvas.bind("<ButtonPress-1>",   self._mm_pan_start_cb)
        self.mindmap_canvas.bind("<B1-Motion>",       self._mm_pan_cb)

        # Hint label
        hint = tk.Label(frame, text="Drag to pan  •  nodes colored by type",
                        bg=BG_EDITOR, fg=FG_LINE_NUM,
                        font=("Segoe UI", 8))
        hint.pack(side=tk.BOTTOM, anchor="w", padx=8, pady=2)

    def _mm_pan_start_cb(self, event):
        self.mindmap_canvas.scan_mark(event.x, event.y)

    def _mm_pan_cb(self, event):
        self.mindmap_canvas.scan_dragto(event.x, event.y, gain=1)

    # ------------------------------------------------------------------
    # Mindmap: AST → node tree
    # ------------------------------------------------------------------
    class _MNode:
        """Lightweight mindmap node holding label, color, children."""
        __slots__ = ("label", "fill", "fg", "children", "cx", "cy", "subtree_w")
        def __init__(self, label, fill, fg):
            self.label    = label
            self.fill     = fill
            self.fg       = fg
            self.children = []
            self.cx = self.cy = self.subtree_w = 0

    def _ast_to_mnodes(self, node):
        """Recursively convert an AST node to a _MNode tree."""
        from parser import (Program, VarDecl, InputStmt, OutputStmt,
                            Assignment, BinOp, Num, Var)

        def color(kind):
            c = MM_COLORS.get(kind, MM_DEFAULT_COLOR)
            return c[0], c[1]

        def build(n):
            if isinstance(n, Program):
                m = self._MNode("Program", *color("Program"))
                m.children = [build(s) for s in n.statements]
                return m
            elif isinstance(n, VarDecl):
                m = self._MNode(f"var {n.var_node.value}", *color("VarDecl"))
                return m
            elif isinstance(n, InputStmt):
                m = self._MNode(f"input {n.var_node.value}", *color("InputStmt"))
                return m
            elif isinstance(n, OutputStmt):
                m = self._MNode(f"output {n.var_node.value}", *color("OutputStmt"))
                return m
            elif isinstance(n, Assignment):
                m = self._MNode(f"{n.var_node.value} =", *color("Assignment"))
                m.children = [build(n.expr)]
                return m
            elif isinstance(n, BinOp):
                m = self._MNode(n.op_token.value, *color("BinOp"))
                m.children = [build(n.left), build(n.right)]
                return m
            elif isinstance(n, Num):
                return self._MNode(str(n.value), *color("Num"))
            elif isinstance(n, Var):
                return self._MNode(n.value, *color("Var"))
            else:
                return self._MNode(type(n).__name__, *MM_DEFAULT_COLOR)

        return build(node)

    def _calc_subtree_w(self, m):
        if not m.children:
            m.subtree_w = MM_NODE_W
            return MM_NODE_W
        total = sum(self._calc_subtree_w(c) for c in m.children)
        total += MM_H_GAP * (len(m.children) - 1)
        m.subtree_w = max(MM_NODE_W, total)
        return m.subtree_w

    def _assign_positions(self, m, left_x, top_y):
        m.cx = left_x + m.subtree_w / 2
        m.cy = top_y + MM_NODE_H / 2
        if not m.children:
            return
        total_ch = sum(c.subtree_w for c in m.children) + MM_H_GAP * (len(m.children) - 1)
        cx = left_x + (m.subtree_w - total_ch) / 2
        for child in m.children:
            self._assign_positions(child, cx, top_y + MM_NODE_H + MM_V_GAP)
            cx += child.subtree_w + MM_H_GAP

    def _draw_mnode(self, c, m):
        """Draw a single mindmap node on canvas c."""
        x, y = m.cx, m.cy
        hw, hh = MM_NODE_W / 2, MM_NODE_H / 2
        r = MM_RADIUS

        # Rounded rectangle via polygon approximation
        pts = [
            x - hw + r, y - hh,
            x + hw - r, y - hh,
            x + hw,     y - hh + r,
            x + hw,     y + hh - r,
            x + hw - r, y + hh,
            x - hw + r, y + hh,
            x - hw,     y + hh - r,
            x - hw,     y - hh + r,
        ]
        tag = f"node_{id(m)}"
        shape = c.create_polygon(pts, smooth=True,
                                  fill=m.fill, outline="", tags=(tag, "node"))
        # Label
        label = m.label if len(m.label) <= 16 else m.label[:14] + "…"
        text = c.create_text(x, y, text=label, fill=m.fg,
                              font=("Segoe UI", 9, "bold"), tags=(tag, "node"))

        # Hover: brighten outline
        def on_enter(_, s=shape):
            c.itemconfig(s, outline="#ffffff", width=2)
        def on_leave(_, s=shape):
            c.itemconfig(s, outline="", width=1)

        c.tag_bind(tag, "<Enter>", on_enter)
        c.tag_bind(tag, "<Leave>", on_leave)

    def _draw_tree(self, c, m):
        """Recursively draw edges then nodes."""
        for child in m.children:
            # Edge: parent bottom-center → child top-center
            c.create_line(m.cx, m.cy + MM_NODE_H / 2,
                          child.cx, child.cy - MM_NODE_H / 2,
                          fill="#585b70", width=1.5, smooth=True)
            self._draw_tree(c, child)
        self._draw_mnode(c, m)

    def render_mindmap(self, tree):
        """Build and render the mindmap for the given AST."""
        c = self.mindmap_canvas
        c.delete("all")

        if tree is None:
            c.create_text(200, 100, text="No AST to display.",
                          fill=FG_LINE_NUM, font=("Segoe UI", 11))
            return

        root = self._ast_to_mnodes(tree)
        self._calc_subtree_w(root)
        PADDING = 40
        self._assign_positions(root, PADDING, PADDING)

        self._draw_tree(c, root)

        # Update scroll region
        total_w = root.subtree_w + PADDING * 2
        # find max depth
        def max_depth(m, d=0):
            if not m.children:
                return d
            return max(max_depth(ch, d + 1) for ch in m.children)
        depth = max_depth(root)
        total_h = PADDING * 2 + (depth + 1) * (MM_NODE_H + MM_V_GAP)
        c.configure(scrollregion=(0, 0, total_w, total_h))

    def _build_status_bar(self):
        """Build the status bar at the bottom of the window."""
        self.status_var = tk.StringVar(value="Ready  |  Press F5 to run  |  Ctrl+O to open  |  Ctrl+S to save")
        status = ttk.Label(self, textvariable=self.status_var,
                           style="Status.TLabel")
        status.pack(fill=tk.X, side=tk.BOTTOM)

    # ==========================================================================
    # Editor Helpers
    # ==========================================================================
    def _on_editor_scroll(self, *args):
        """Sync line numbers when the editor is scrolled."""
        self.code_editor.yview(*args)
        self.line_numbers.yview(*args)

    def _on_editor_yscroll(self, scrollbar):
        """Return a callback to sync scrollbar + line numbers."""
        def handler(*args):
            scrollbar.set(*args)
            self.line_numbers.yview_moveto(args[0])
        return handler

    def _on_code_change(self, event=None):
        """Called on every keypress / click — updates line numbers and highlighting."""
        self._update_line_numbers()
        self._update_syntax_highlighting()

    def _update_line_numbers(self):
        """Regenerate line number gutter."""
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)

        line_count = int(self.code_editor.index("end-1c").split(".")[0])
        numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state=tk.DISABLED)

    def _update_syntax_highlighting(self):
        """Apply basic syntax highlighting to the code editor."""
        # Remove old tags
        for tag in ("kw", "num", "cmt", "op", "paren"):
            self.code_editor.tag_remove(tag, "1.0", tk.END)

        # Configure tags
        self.code_editor.tag_configure("kw",    foreground=FG_KEYWORD,
                                       font=(FONT_FAMILY, FONT_SIZE, "bold"))
        self.code_editor.tag_configure("num",   foreground=FG_NUMBER)
        self.code_editor.tag_configure("cmt",   foreground=FG_COMMENT,
                                       font=(FONT_FAMILY, FONT_SIZE, "italic"))
        self.code_editor.tag_configure("op",    foreground=FG_OPERATOR)
        self.code_editor.tag_configure("paren", foreground=FG_PAREN)

        code = self.code_editor.get("1.0", tk.END)

        # Highlight keywords
        import re
        for kw in SALITA_KEYWORDS:
            for m in re.finditer(rf'\b{kw}\b', code):
                start = f"1.0+{m.start()}c"
                end   = f"1.0+{m.end()}c"
                self.code_editor.tag_add("kw", start, end)

        # Highlight numbers
        for m in re.finditer(r'\b\d+\b', code):
            start = f"1.0+{m.start()}c"
            end   = f"1.0+{m.end()}c"
            self.code_editor.tag_add("num", start, end)

        # Highlight comments
        for m in re.finditer(r'/\*.*?\*/', code, re.DOTALL):
            start = f"1.0+{m.start()}c"
            end   = f"1.0+{m.end()}c"
            self.code_editor.tag_add("cmt", start, end)

        # Highlight operators
        for m in re.finditer(r'[+\-*/=]', code):
            start = f"1.0+{m.start()}c"
            end   = f"1.0+{m.end()}c"
            self.code_editor.tag_add("op", start, end)

        # Highlight parentheses
        for m in re.finditer(r'[()]', code):
            start = f"1.0+{m.start()}c"
            end   = f"1.0+{m.end()}c"
            self.code_editor.tag_add("paren", start, end)

    def _insert_sample_code(self):
        """Insert a default SALITA example program into the editor."""
        sample = """/* Sample SALITA Program */

var x;
var y;
var total;

input x;
input y;

total = (x + y) * 2;

output total;
"""
        self.code_editor.insert("1.0", sample)
        self._on_code_change()

    # ==========================================================================
    # Output Panel Helpers
    # ==========================================================================
    def _set_output(self, widget: scrolledtext.ScrolledText, text: str,
                    tag: str = None):
        """Set the content of an output panel."""
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        if tag:
            widget.insert(tk.END, text, tag)
        else:
            widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def _append_output(self, widget: scrolledtext.ScrolledText, text: str,
                       tag: str = None):
        """Append text to an output panel."""
        widget.config(state=tk.NORMAL)
        if tag:
            widget.insert(tk.END, text, tag)
        else:
            widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)
        widget.see(tk.END)

    def clear_output(self):
        """Clear all output panels."""
        for widget in (self.token_output, self.parse_output,
                       self.semantic_output, self.program_output,
                       self.error_output, self.symbol_output):
            self._set_output(widget, "")
        self.status_var.set("Output cleared.")

    # ==========================================================================
    # File Operations
    # ==========================================================================
    def load_file(self):
        """Open a .sl (SALITA) source file."""
        path = filedialog.askopenfilename(
            title="Open SALITA Source File",
            filetypes=[("SALITA Files", "*.sl"), ("All Files", "*.*")]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", code)
                self.current_file_path = path
                self._on_code_change()
                self.status_var.set(f"Loaded: {os.path.basename(path)}")
            except Exception as ex:
                messagebox.showerror("File Error", str(ex))

    def save_file(self):
        """Save the current code to a .sl file."""
        path = self.current_file_path
        if not path:
            path = filedialog.asksaveasfilename(
                title="Save SALITA Source File",
                defaultextension=".sl",
                filetypes=[("SALITA Files", "*.sl"), ("All Files", "*.*")]
            )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.get("1.0", tk.END))
                self.current_file_path = path
                self.status_var.set(f"Saved: {os.path.basename(path)}")
            except Exception as ex:
                messagebox.showerror("File Error", str(ex))

    # ==========================================================================
    # Compiler Pipeline
    # ==========================================================================
    def run_compiler(self):
        """
        Execute the full SALITA compiler pipeline:
          1. Lexical Analysis
          2. Syntax Analysis (Parsing)
          3. Semantic Analysis
          4. Interpretation (Execution)
        """
        self.clear_output()
        source = self.code_editor.get("1.0", tk.END).strip()

        if not source:
            self._set_output(self.error_output,
                             "⚠ No source code to compile.", "error")
            self.notebook.select(4)  # Switch to Errors tab
            self.status_var.set("Error: No source code.")
            return

        # ---- Phase 1: Lexical Analysis ----
        self.status_var.set("Phase 1: Lexical Analysis...")
        self.update()

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
        except LexerError as e:
            self._set_output(self.error_output, f"❌ {e}", "error")
            self._set_output(self.token_output,
                             "Lexical analysis failed — see Errors tab.", "error")
            self.notebook.select(4)
            self.status_var.set("Compilation failed (Lexical Error).")
            return

        # Display Token Table
        self._display_tokens(tokens)

        # ---- Phase 2: Syntax Analysis (Parsing) ----
        self.status_var.set("Phase 2: Syntax Analysis...")
        self.update()

        try:
            parser = Parser(Lexer(source))
            tree = parser.parse()
        except ParserError as e:
            self._set_output(self.error_output, f"❌ {e}", "error")
            self._set_output(self.parse_output,
                             "Syntax analysis failed — see Errors tab.", "error")
            self.notebook.select(4)
            self.status_var.set("Compilation failed (Syntax Error).")
            return

        # Display AST
        self._set_output(self.parse_output, "")
        self._append_output(self.parse_output,
                            "✅ Program structure is valid.\n\n", "success")
        self._append_output(self.parse_output,
                            "── Abstract Syntax Tree ──\n\n", "heading")
        self._append_output(self.parse_output, ast_to_string(tree) + "\n")

        # Render interactive mindmap
        self.render_mindmap(tree)

        # ---- Phase 3: Semantic Analysis ----
        self.status_var.set("Phase 3: Semantic Analysis...")
        self.update()

        try:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(tree)
            symbol_table = analyzer.symbol_table
        except SemanticError as e:
            self._set_output(self.error_output, f"❌ {e}", "error")
            self._set_output(self.semantic_output,
                             "Semantic analysis failed — see Errors tab.", "error")
            self.notebook.select(4)
            self.status_var.set("Compilation failed (Semantic Error).")
            return

        self._set_output(self.semantic_output,
                         "✅ No semantic errors found.\n\n", "success")
        self._append_output(self.semantic_output,
                            "All variables are declared before use.\n"
                            "No duplicate declarations detected.\n"
                            "All expressions are valid.\n")

        # Display Symbol Table
        self._display_symbol_table(symbol_table)

        # ---- Phase 4: Interpretation / Execution ----
        self.status_var.set("Phase 4: Executing program...")
        self.update()

        try:
            interp = Interpreter(
                tree, symbol_table,
                input_func=self._gui_input,
                output_func=self._gui_output,
            )
            interp.interpret()
        except SalitaRuntimeError as e:
            self._append_output(self.error_output, f"❌ {e}\n", "error")
            self.notebook.select(4)
            self.status_var.set("Execution failed (Runtime Error).")
            return
        except Exception as e:
            self._append_output(self.error_output,
                                f"❌ Unexpected Error: {e}\n", "error")
            self.notebook.select(4)
            self.status_var.set("Execution failed (Unexpected Error).")
            return

        # Update symbol table after execution (values may have changed)
        self._display_symbol_table(symbol_table)

        # If no errors were appended to error output, show success
        self._set_output(self.error_output,
                         "✅ No errors detected. Program executed successfully.",
                         "success")

        self.notebook.select(3)  # Switch to Output tab
        self.status_var.set("✅ Compilation and execution successful!")

    # --------------------------------------------------------------------------
    # Token Display
    # --------------------------------------------------------------------------
    def _display_tokens(self, tokens):
        """Render the token table in the Tokens output panel."""
        self._set_output(self.token_output, "")
        self._append_output(self.token_output,
                            "── Token Table ──\n\n", "heading")

        header = f"{'#':<5} {'Type':<15} {'Value':<15} {'Line':<5}\n"
        header += "─" * 42 + "\n"
        self._append_output(self.token_output, header)

        for i, tok in enumerate(tokens, 1):
            display_type = tok.display_type
            line = f"{i:<5} {display_type:<15} {str(tok.value):<15} {tok.line:<5}\n"

            tag = None
            if display_type == "KEYWORD":
                tag = "keyword"
            elif display_type == "NUMBER":
                tag = "number"
            elif display_type == "OPERATOR":
                tag = "operator"

            self._append_output(self.token_output, line, tag)

        self._append_output(self.token_output,
                            f"\nTotal tokens: {len(tokens)}\n", "accent")

    # --------------------------------------------------------------------------
    # Symbol Table Display
    # --------------------------------------------------------------------------
    def _display_symbol_table(self, st: SymbolTable):
        """Render the symbol table in the Symbols output panel."""
        self._set_output(self.symbol_output, "")
        self._append_output(self.symbol_output,
                            "── Symbol Table ──\n\n", "heading")

        header = f"{'Variable':<15} {'Type':<12} {'Value':<10}\n"
        header += "─" * 37 + "\n"
        self._append_output(self.symbol_output, header)

        entries = st.get_entries()
        for entry in entries:
            line = f"{entry.name:<15} {entry.type:<12} {str(entry.value):<10}\n"
            self._append_output(self.symbol_output, line)

        if not entries:
            self._append_output(self.symbol_output, "(No variables declared)\n")

    # --------------------------------------------------------------------------
    # GUI I/O Callbacks (for the Interpreter)
    # --------------------------------------------------------------------------
    def _gui_input(self, prompt: str) -> str:
        """Show an input dialog and return the user's response."""
        result = simpledialog.askstring(
            "SALITA — Kuha (Input)",
            prompt,
            parent=self
        )
        if result is not None:
            self._append_output(self.program_output,
                                f"[Input] {prompt}{result}\n", "accent")
        return result

    def _gui_output(self, text: str):
        """Append interpreter output to the Program Output panel."""
        self._append_output(self.program_output, text + "\n")


# ==============================================================================
# Standalone Launch
# ==============================================================================
def launch_gui():
    """Create and start the SALITA IDE."""
    app = SalitaIDE()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
