"""Case study A - palindromes over {a,b}: nondeterminism is unavoidable without a centre marker."""
from .cfg import Grammar
from .pda import PDA

CFG_TEXT = "S -> a S a | b S b | a | b | eps"
CFG = Grammar(CFG_TEXT, name="palindromes")
MARKER_CFG = Grammar("S -> a S a | b S b | c", name="w c w^R")


def pda_nondeterministic() -> PDA:
    """P = ({q0,q1,q2},{a,b},{a,b,Z},delta,q0,Z,{q2}); the middle is *guessed*."""
    d = {}
    def add(q, a, X, nq, push): d.setdefault((q, a, X), []).append((nq, push))
    for X in "abZ":
        for s in "ab":
            add("q0", s, X, "q0", (s, X))          # push the first half
            add("q0", s, X, "q1", (X,))            # odd length: this symbol is the centre, not pushed
        add("q0", "", X, "q1", (X,))               # even length: guess the middle is here
    for s in "ab":
        add("q1", s, s, "q1", ())                  # match second half against the stack
    add("q1", "", "Z", "q2", ("Z",))               # all matched -> accept
    return PDA({"q0", "q1", "q2"}, "ab", "abZ", d, "q0", "Z", finals={"q2"}, name="palindrome NPDA")


def pda_marker() -> PDA:
    """Deterministic PDA for { w c w^R }: the marker c removes the need to guess."""
    d = {}
    def add(q, a, X, nq, push): d.setdefault((q, a, X), []).append((nq, push))
    for X in "abZ":
        for s in "ab":
            add("q0", s, X, "q0", (s, X))
        add("q0", "c", X, "q1", (X,))
    for s in "ab":
        add("q1", s, s, "q1", ())
    add("q1", "", "Z", "q2", ("Z",))
    return PDA({"q0", "q1", "q2"}, "abc", "abZ", d, "q0", "Z", finals={"q2"}, name="w c w^R DPDA")


def is_palindrome(s): return s == s[::-1]
