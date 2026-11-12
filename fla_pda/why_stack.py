"""Why finite automata are not enough: a DFA for balanced brackets of depth <= k needs k+2 states."""
from collections import deque


def bounded_depth_dfa_states(k: int) -> int:
    """States = depth 0..k plus a trap. Built explicitly and minimised by reachability+Moore."""
    states = list(range(k + 1)) + ["trap"]
    delta = {}
    for d in range(k + 1):
        delta[(d, "(")] = d + 1 if d < k else "trap"
        delta[(d, ")")] = d - 1 if d > 0 else "trap"
    delta[("trap", "(")] = delta[("trap", ")")] = "trap"
    part = {q: int(q == 0) for q in states}
    cnt = 2
    while True:
        sig = {q: (part[q], part[delta[(q, "(")]], part[delta[(q, ")")]]) for q in states}
        ids = {}
        new = {q: ids.setdefault(sig[q], len(ids)) for q in states}
        if len(ids) == cnt:
            return cnt
        part, cnt = new, len(ids)


def stack_machine_max_depth(word: str):
    """The PDA needs ONE state; only the stack grows. Returns (accepted, max stack height)."""
    h = m = 0
    for ch in word:
        h += 1 if ch == "(" else -1
        if h < 0:
            return False, m
        m = max(m, h)
    return h == 0, m
