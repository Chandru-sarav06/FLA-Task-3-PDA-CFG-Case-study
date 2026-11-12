"""Context-free grammar toolkit: parsing from text, parse-tree counting
(ambiguity), leftmost derivations, string generation, grammar->PDA."""
from __future__ import annotations

import itertools
from collections import defaultdict
from functools import lru_cache

from .pda import PDA


class Grammar:
    """Productions given as text lines:  'S -> a S b | eps'.
    Symbols are whitespace separated; a symbol is a nonterminal iff it appears on a LHS."""

    def __init__(self, text: str, start: str | None = None, name: str = ""):
        self.name = name
        self.prods: dict[str, list[tuple[str, ...]]] = defaultdict(list)
        order = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            lhs, rhs = line.split("->")
            lhs = lhs.strip()
            if lhs not in order:
                order.append(lhs)
            for alt in rhs.split("|"):
                syms = tuple(s for s in alt.split() if s not in ("eps", "ε"))
                self.prods[lhs].append(syms)
        self.start = start or order[0]
        self.nonterminals = set(self.prods)
        self.terminals = {s for rs in self.prods.values() for r in rs for s in r if s not in self.nonterminals}
        self._minlen = self._compute_minlen()

    # ---- helpers
    def _compute_minlen(self):
        INF = 10 ** 9
        m = {A: INF for A in self.nonterminals}
        changed = True
        while changed:
            changed = False
            for A, rules in self.prods.items():
                for r in rules:
                    v = sum(m[s] if s in self.nonterminals else 1 for s in r)
                    if v < m[A]:
                        m[A], changed = v, True
        return m

    def minlen(self, sym):
        return self._minlen[sym] if sym in self.nonterminals else 1

    def productions_text(self):
        lines = []
        for A, rules in self.prods.items():
            lines.append(f"{A} -> " + " | ".join(" ".join(r) if r else "ε" for r in rules))
        return "\n".join(lines)

    # ---- parse-tree counting (ambiguity oracle); works for any CFG without ε-cycles
    def count_parses(self, tokens) -> int:
        toks = tuple(tokens)
        n = len(toks)
        in_progress = set()

        @lru_cache(maxsize=None)
        def sym(X, i, j):
            if X not in self.nonterminals:
                return 1 if j == i + 1 and toks[i] == X else 0
            if self.minlen(X) > j - i:
                return 0
            key = (X, i, j)
            if key in in_progress:      # cyclic derivation: ignore (no such cycles in our grammars)
                return 0
            in_progress.add(key)
            total = sum(seq(r, 0, i, j) for r in self.prods[X])
            in_progress.discard(key)
            return total

        def seq(rhs, p, i, j):
            if p == len(rhs):
                return 1 if i == j else 0
            rest = sum(self.minlen(s) for s in rhs[p + 1:])
            total = 0
            for k in range(i, j - rest + 1):
                a = sym(rhs[p], i, k)
                if a:
                    total += a * seq(rhs, p + 1, k, j)
            return total

        return sym(self.start, 0, n)

    def accepts(self, tokens) -> bool:
        return self.count_parses(tokens) > 0

    def parse_trees(self, tokens, limit=10):
        """Explicit parse trees as nested tuples (symbol, [children]); terminals are plain strings."""
        toks = tuple(tokens)

        def sym(X, i, j):
            if X not in self.nonterminals:
                if j == i + 1 and toks[i] == X:
                    yield X
                return
            if self.minlen(X) > j - i:
                return
            for r in self.prods[X]:
                for ch in seq(r, 0, i, j):
                    yield (X, ch)

        def seq(rhs, p, i, j):
            if p == len(rhs):
                if i == j:
                    yield []
                return
            rest = sum(self.minlen(s) for s in rhs[p + 1:])
            for k in range(i, j - rest + 1):
                for a in sym(rhs[p], i, k):
                    for b in seq(rhs, p + 1, k, j):
                        yield [a] + b

        return list(itertools.islice(sym(self.start, 0, len(toks)), limit))

    # ---- leftmost derivation of one parse (first found)
    def leftmost_derivation(self, tokens, limit=60):
        """Return list of sentential forms (each a tuple) for one leftmost derivation, or None."""
        toks = tuple(tokens)

        def search(form, depth):
            # form: tuple of symbols; find leftmost nonterminal
            idx = next((k for k, s in enumerate(form) if s in self.nonterminals), None)
            prefix = form[:idx] if idx is not None else form
            if prefix != toks[: len(prefix)]:
                return None
            if idx is None:
                return [form] if form == toks else None
            if depth > limit or sum(self.minlen(s) for s in form) > len(toks):
                return None
            for r in self.prods[form[idx]]:
                nf = form[:idx] + r + form[idx + 1:]
                res = search(nf, depth + 1)
                if res is not None:
                    return [form] + res
            return None

        return search((self.start,), 0)

    # ---- language enumeration up to a length
    def generate(self, max_len):
        """All terminal strings of length <= max_len (BFS over leftmost sentential forms)."""
        seen_forms, out = set(), set()
        todo = [(self.start,)]
        while todo:
            form = todo.pop()
            if form in seen_forms:
                continue
            seen_forms.add(form)
            if sum(self.minlen(s) for s in form) > max_len:
                continue
            idx = next((k for k, s in enumerate(form) if s in self.nonterminals), None)
            if idx is None:
                out.add(form)
                continue
            for r in self.prods[form[idx]]:
                todo.append(form[:idx] + r + form[idx + 1:])
        return out

    # ---- CFG -> PDA (single state, empty-stack acceptance)
    def to_pda(self) -> PDA:
        delta = defaultdict(list)
        for A, rules in self.prods.items():
            for r in rules:
                delta[("q", "", A)].append(("q", r))
        for t in self.terminals:
            delta[("q", t, t)].append(("q", ()))
        return PDA(states={"q"}, input_alphabet=self.terminals, stack_alphabet=self.nonterminals | self.terminals,
                   delta=delta, start="q", start_stack=self.start, accept_mode="empty",
                   weight=self.minlen, name=f"PDA({self.name or 'G'})")
