"""Case study B - nesting of HTML/XML-style tags checked with a stack of tag names."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from .cfg import Grammar

TAG_RE = re.compile(r"<\s*(/?)\s*([A-Za-z][A-Za-z0-9]*)\b[^<>]*?(/?)\s*>")
VOID = {"br", "hr", "img", "meta", "input"}


@dataclass
class MarkupResult:
    ok: bool
    error: str = ""
    position: int = -1
    steps: list = field(default_factory=list)   # (token, action, stack after)


def tokenize(text: str):
    """Return [(kind, name, position)] kind in {'open','close','void','text'}."""
    out, pos = [], 0
    for m in TAG_RE.finditer(text):
        if text[pos:m.start()].strip():
            out.append(("text", "", pos))
        closing, name, selfc = m.group(1) == "/", m.group(2).lower(), m.group(3) == "/"
        kind = "close" if closing else ("void" if selfc or name in VOID else "open")
        out.append((kind, name, m.start()))
        pos = m.end()
    if text[pos:].strip():
        out.append(("text", "", pos))
    return out


def check_markup(text: str) -> MarkupResult:
    """Deterministic stack machine: push on open, pop+compare on close, accept iff stack empty at end."""
    stack, steps = [], []
    for kind, name, pos in tokenize(text):
        if kind == "open":
            stack.append(name)
            steps.append((f"<{name}>", "push", tuple(stack)))
        elif kind == "close":
            if not stack:
                return MarkupResult(False, f"unexpected closing tag </{name}> with empty stack", pos, steps)
            if stack[-1] != name:
                return MarkupResult(False, f"expected </{stack[-1]}> but found </{name}>", pos, steps)
            stack.pop()
            steps.append((f"</{name}>", "pop", tuple(stack)))
        else:
            steps.append((f"<{name}/>" if kind == "void" else "text", "none", tuple(stack)))
    if stack:
        return MarkupResult(False, f"unclosed tag(s) at end of input: {', '.join('<'+s+'>' for s in reversed(stack))}", len(text), steps)
    return MarkupResult(True, "all tags properly nested", -1, steps)


def check_tokens(tokens) -> bool:
    """Same machine on abstract tokens: '<a>', '</a>', 'T'."""
    st = []
    for t in tokens:
        if t == "T":
            continue
        if t.startswith("</"):
            if not st or st[-1] != t[2:-1]:
                return False
            st.pop()
        else:
            st.append(t[1:-1])
    return not st


def tag_grammar(tags) -> Grammar:
    """CFG over tokens for a FINITE tag set (each tag name = its own terminal pair)."""
    lines = ["Doc -> Elem Doc | eps", "Elem -> T | " + " | ".join(f"<{t}> Doc </{t}>" for t in tags)]
    return Grammar("\n".join(lines), name="markup")
