"""Case study C - programming-language syntax: the dangling-else ambiguity and its repair."""
from .cfg import Grammar

# tokens: if c then else s      (c = condition, s = simple statement)
AMBIGUOUS = Grammar("""
Stmt -> if c then Stmt | if c then Stmt else Stmt | s
""", name="G1 ambiguous")

# 'else' binds to the NEAREST unmatched 'then' (as in C, Java, Python-like languages)
UNAMBIGUOUS = Grammar("""
Stmt -> Matched | Unmatched
Matched -> if c then Matched else Matched | s
Unmatched -> if c then Stmt | if c then Matched else Unmatched
""", name="G2 unambiguous")

CLASSIC = ["if", "c", "then", "if", "c", "then", "s", "else", "s"]
