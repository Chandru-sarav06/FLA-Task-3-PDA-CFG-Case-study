"""python -m fla_pda.cli pal abba | marker abcba | tags "<a><b></b></a>" | ifelse if c then s"""
import sys
from .palindromes import pda_nondeterministic, pda_marker, CFG
from .markup import check_markup
from .dangling_else import AMBIGUOUS, UNAMBIGUOUS


def main(argv=None):
    a = (argv if argv is not None else sys.argv)[1:]
    if len(a) < 2:
        print(__doc__); return 2
    kind, rest = a[0], a[1:]
    if kind in ("pal", "marker"):
        pda = pda_nondeterministic() if kind == "pal" else pda_marker()
        ok, trace = pda.run(rest[0])
        print("ACCEPT" if ok else "REJECT", "| deterministic PDA:", pda.is_deterministic)
        for q, rem, st in trace:
            print(f"  state={q}  remaining={''.join(rem) or 'ε'}  stack(top→)={''.join(st)}")
        if kind == "pal":
            d = CFG.leftmost_derivation(rest[0])
            if d: print("leftmost derivation:", " ⇒ ".join(" ".join(f) or "ε" for f in d))
    elif kind == "tags":
        r = check_markup(rest[0])
        print("ACCEPT" if r.ok else f"REJECT at char {r.position}: {r.error}")
        for tok, act, st in r.steps:
            print(f"  {tok:<8} {act:<5} stack={list(st)}")
    elif kind == "ifelse":
        toks = rest if len(rest) > 1 else rest[0].split()
        print("G1 parses:", AMBIGUOUS.count_parses(toks), "| G2 parses:", UNAMBIGUOUS.count_parses(toks))
    else:
        print(__doc__); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
