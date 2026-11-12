"""Nondeterministic PDA simulator (breadth-first over configurations).

delta: (state, input_symbol_or_'' , stack_top) -> list of (new_state, push_tuple)
push_tuple is written TOP-FIRST, e.g. ('a','Z') pushes a on top of Z.
accept_mode: 'final' (input consumed and state in finals) or 'empty' (input consumed, stack empty)."""
from __future__ import annotations

from collections import deque


class PDA:
    def __init__(self, states, input_alphabet, stack_alphabet, delta, start, start_stack,
                 finals=(), accept_mode="final", weight=None, name=""):
        self.states, self.input_alphabet, self.stack_alphabet = set(states), set(input_alphabet), set(stack_alphabet)
        self.delta = {k: list(v) for k, v in delta.items()}
        self.start, self.start_stack = start, start_stack
        self.finals, self.accept_mode, self.name = set(finals), accept_mode, name
        self.weight = weight or (lambda s: 0)   # lower bound of input symbols a stack symbol still needs
        self.is_deterministic = self._check_det()

    def _check_det(self):
        for (q, a, X), moves in self.delta.items():
            if len(moves) > 1:
                return False
            if a == "" and any((q, b, X) in self.delta for b in self.input_alphabet):
                return False
        return True

    def run(self, tokens, max_configs=200_000, want_trace=True):
        """Return (accepted, trace). trace = list of (state, remaining_input, stack_top_first) IDs of one accepting run."""
        toks = tuple(tokens)
        n = len(toks)
        init = (self.start, 0, (self.start_stack,))
        parent = {init: None}
        todo = deque([init])
        count = 0
        while todo:
            cfg = todo.popleft()
            q, i, st = cfg
            count += 1
            if count > max_configs:
                return None, []                     # budget exhausted: unknown
            if i == n and ((self.accept_mode == "empty" and not st) or
                           (self.accept_mode == "final" and q in self.finals)):
                trace = []
                while cfg is not None:
                    trace.append((cfg[0], toks[cfg[1]:], cfg[2]))
                    cfg = parent[cfg]
                return True, trace[::-1]
            top = st[0] if st else None
            cand = []
            if top is not None:
                for (nq, push) in self.delta.get((q, "", top), ()):
                    cand.append((nq, i, push + st[1:]))
                if i < n:
                    for (nq, push) in self.delta.get((q, toks[i], top), ()):
                        cand.append((nq, i + 1, push + st[1:]))
            for c in cand:
                # prune: stack needs more input than remains
                if sum(self.weight(s) for s in c[2]) > n - c[1]:
                    continue
                if c not in parent:
                    parent[c] = cfg
                    todo.append(c)
        return False, []

    def accepts(self, tokens, **kw):
        return self.run(tokens, **kw)[0]
